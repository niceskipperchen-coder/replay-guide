import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'skills/replay-guide/scripts/replay_guide.py'

class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        # A genuine tiny PNG, also used for format validation.
        import base64
        (self.root / 'screen.png').write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aK1sAAAAASUVORK5CYII='))
        self.data = {'title':'Make a stack', 'summary':'A short walkthrough.', 'duration':10,
                     'steps':[{'title':'Start', 'body':'Press Run.', 'start':0, 'end':3,
                               'image':'screen.png', 'alt':'Editor and Run button', 'status':'observed'}]}
    def tearDown(self):
        self.tmp.cleanup()
    def run_build(self, data=None, out='out'):
        (self.root / 'tutorial.json').write_text(json.dumps(self.data if data is None else data))
        return subprocess.run(['python3',str(SCRIPT),'build',str(self.root/'tutorial.json'),'--out',str(self.root/out)],capture_output=True,text=True)
    def test_embeds_image_and_no_external_dependencies(self):
        result = self.run_build()
        self.assertEqual(result.returncode,0,result.stderr)
        html = (self.root/'out/index.html').read_text()
        self.assertIn('data:image/png;base64,',html)
        self.assertNotIn('<script src=',html)
        self.assertNotIn('fonts.googleapis',html)
    def test_hostile_text_cannot_close_data_script(self):
        self.data['title'] = '</script><script>alert("bad")</script>'
        result = self.run_build()
        self.assertEqual(result.returncode,0,result.stderr)
        html = (self.root/'out/index.html').read_text()
        self.assertNotIn('</script><script>alert',html)
        payload=html.split('<script type="application/json" id="tutorial-data">')[1].split('</script>')[0]
        self.assertEqual(json.loads(payload)['title'],self.data['title'])
    def test_template_markers_in_content_are_preserved(self):
        self.data['title'] = 'First line\nSecond line /*TUTORIAL_DATA*/'
        self.data['steps'][0]['body'] = 'TUTORIAL_PAGE_TITLE /*TUTORIAL_DATA*/'
        result = self.run_build()
        self.assertEqual(result.returncode,0,result.stderr)
        content=(self.root/'out/index.html').read_text().split('<script type="application/json" id="tutorial-data">')[1].split('</script>')[0]
        self.assertEqual(json.loads(content)['steps'][0]['body'], self.data['steps'][0]['body'])
        self.assertIn('First line\nSecond line /*TUTORIAL_DATA*/</title>', (self.root/'out/index.html').read_text().replace(' · Replay Guide',''))
    def test_rejects_bad_timing_and_incomplete_steps(self):
        for field,value in [('start',-1),('end',11),('start',float('nan')),('end',0),('image','missing.png'),('status','verified-by-magic')]:
            with self.subTest(field=field,value=value):
                data=json.loads(json.dumps(self.data)); data['steps'][0][field]=value
                self.assertNotEqual(self.run_build(data).returncode,0)
                self.assertFalse((self.root/'out').exists())
    def test_rejects_path_escape_and_symlink(self):
        with tempfile.TemporaryDirectory() as other:
            outside=pathlib.Path(other)/'private.png'; outside.write_bytes((self.root/'screen.png').read_bytes())
            (self.root/'escape.png').symlink_to(outside)
            for path in [str(outside),'../private.png','escape.png']:
                self.data['steps'][0]['image']=path
                self.assertNotEqual(self.run_build().returncode,0)
    def test_does_not_overwrite(self):
        (self.root/'out').mkdir(); (self.root/'out/keep').write_text('mine')
        self.assertNotEqual(self.run_build().returncode,0)
        self.assertEqual((self.root/'out/keep').read_text(),'mine')
    def test_invalid_highlights(self):
        self.data['steps'][0]['highlight']={'x':90,'y':10,'width':20,'height':10}
        self.assertNotEqual(self.run_build().returncode,0)

class MediaTests(unittest.TestCase):
    def test_prepare_real_video_and_build_with_replay(self):
        import shutil
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'): self.skipTest('FFmpeg unavailable')
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder); source=root/'source.mp4'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=size=320x240:rate=10','-f','lavfi','-i','sine=frequency=440:sample_rate=16000','-t','2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(source)],check=True)
            result=subprocess.run(['python3',str(SCRIPT),'prepare',str(source),'--out',str(root/'frames'),'--at','0,1','--audio'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            manifest=json.loads((root/'frames/manifest.json').read_text())
            self.assertEqual([x['time'] for x in manifest['frames']],[0,1])
            self.assertEqual(len(list((root/'frames').glob('*.jpg'))),2)
            self.assertEqual(manifest['audio'],'audio.wav')
            self.assertTrue((root/'frames/audio.wav').stat().st_size > 1000)
            for at in ['-1','nan','2']:
                bad=subprocess.run(['python3',str(SCRIPT),'prepare',str(source),'--out',str(root/'bad'),'--at='+at],capture_output=True,text=True)
                self.assertNotEqual(bad.returncode,0)
                self.assertFalse((root/'bad').exists())
            data={'title':'Demo','summary':'Demo','duration':2,'steps':[{'title':'View','body':'See test pattern.','start':0,'end':1,'image':manifest['frames'][0]['file'],'alt':'Test pattern','status':'observed'}]}
            path=root/'frames/tutorial.json';path.write_text(json.dumps(data))
            result=subprocess.run(['python3',str(SCRIPT),'build',str(path),'--out',str(root/'site'),'--video',str(source)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((root/'site/recording.mp4').exists())
