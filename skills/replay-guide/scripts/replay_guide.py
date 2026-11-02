#!/usr/bin/env python3
"""Local media preparation and portable tutorial builder. Python 3.10+, no pip deps."""
import argparse
import base64
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

MAX_DURATION = 1800
MAX_STEPS = 48


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number')
    return value


def text(value, label, limit=12000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{label} must be nonempty text, at most {limit} characters')
    return value


def run(args):
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True, timeout=120).stdout
    except FileNotFoundError:
        raise ValueError(f'{args[0]} is required on PATH') from None
    except subprocess.CalledProcessError as exc:
        raise ValueError(f'{args[0]} failed: {exc.stderr[-1000:]}') from None
    except subprocess.TimeoutExpired:
        raise ValueError(f'{args[0]} exceeded the 120-second processing limit') from None


def probe(source):
    result = json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]))
    duration = number(float(result.get('format',{}).get('duration',0)), 'duration')
    if not 0 < duration <= MAX_DURATION:
        raise ValueError('Recording must be longer than zero and at most 30 minutes')
    return duration, result.get('streams',[])


def new_output(path):
    path = Path(path)
    if path.exists():
        raise ValueError(f'Output already exists: {path}; choose a new directory')
    path.mkdir(parents=True, exist_ok=False)
    return path


def prepare(args):
    source = Path(args.recording).resolve(strict=True)
    duration, streams = probe(source)
    if not any(s.get('codec_type') == 'video' for s in streams):
        raise ValueError('A screen recording with a video stream is required')
    if args.at:
        try:
            times = [float(t.strip()) for t in args.at.split(',')]
        except ValueError:
            raise ValueError('--at must contain comma-separated seconds') from None
    else:
        if not 1 <= args.frames <= MAX_STEPS:
            raise ValueError('--frames must be between 1 and 48')
        times = [round(i * max(0, duration - .15) / max(1,args.frames-1), 3) for i in range(args.frames)]
    if not 1 <= len(times) <= MAX_STEPS or any(not math.isfinite(t) or t < 0 or t >= duration for t in times):
        raise ValueError('Use 1–48 timestamps, each at least zero and less than the video duration')
    times = sorted(set(times))
    out = new_output(args.out)
    frames = []
    for i, timestamp in enumerate(times):
        filename = f'frame-{i+1:02d}-{timestamp:.3f}s.jpg'
        target = out/filename
        run(['ffmpeg','-v','error','-ss',str(timestamp),'-i',str(source),'-frames:v','1','-vf',"scale=1280:1280:force_original_aspect_ratio=decrease",'-q:v','3',str(target)])
        if not target.exists() or not target.stat().st_size:
            raise ValueError(f'No decoded frame at {timestamp}s; retry at an earlier timestamp in a new output folder')
        frames.append({'time':timestamp,'file':filename})
    audio = None
    if args.audio and any(s.get('codec_type') == 'audio' for s in streams):
        run(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','1','-ar','16000',str(out/'audio.wav')])
        audio = 'audio.wav'
    manifest = {'duration':duration,'frames':frames,'audio':audio,
                'note':'Sampled frames are evidence, not automatic action detection. No transcription was performed.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'Prepared {len(frames)} frames: {out}/manifest.json')


def image_data(base, value):
    relative = Path(text(value,'image',1000))
    if relative.is_absolute():
        raise ValueError('image must be a relative path inside the tutorial JSON directory')
    target = (base/relative).resolve(strict=True)
    if not target.is_relative_to(base):
        raise ValueError('image path escapes the tutorial JSON directory')
    if target.stat().st_size > 8 * 1024 * 1024:
        raise ValueError('Each screenshot must be at most 8 MB')
    raw = target.read_bytes()
    if raw.startswith(b'\x89PNG\r\n\x1a\n'): mime = 'image/png'
    elif raw.startswith(b'\xff\xd8\xff'): mime = 'image/jpeg'
    elif raw.startswith(b'RIFF') and raw[8:12] == b'WEBP': mime = 'image/webp'
    else: raise ValueError('Screenshot must be PNG, JPEG or WebP (SVG/HTML are not accepted)')
    return f'data:{mime};base64,' + base64.b64encode(raw).decode('ascii')


def validate(data, base):
    if not isinstance(data,dict): raise ValueError('Tutorial must be a JSON object')
    result = {k:text(data.get(k),k,300 if k == 'title' else 2000) for k in ('title','summary')}
    duration = number(data.get('duration'),'duration')
    if not 0 < duration <= MAX_DURATION: raise ValueError('duration must be within 0–1800 seconds')
    result['duration'] = duration
    if not isinstance(data.get('steps'),list) or not 1 <= len(data['steps']) <= MAX_STEPS:
        raise ValueError('Tutorial must contain 1–48 steps')
    steps = []
    previous = -1
    for i, step in enumerate(data['steps']):
        if not isinstance(step,dict): raise ValueError(f'Step {i+1} must be an object')
        clean = {k:text(step.get(k),f'Step {i+1} {k}') for k in ('title','body','alt')}
        start = number(step.get('start'),'start'); end = number(step.get('end'),'end')
        if not 0 <= start < end <= duration or start < previous:
            raise ValueError('Steps need chronological starts and 0 <= start < end <= duration')
        previous = start
        status = step.get('status')
        if status not in ('observed','needs-review'): raise ValueError('status must be observed or needs-review')
        clean.update(start=start,end=end,status=status,image=image_data(base,step.get('image')))
        for key in ('code','note'):
            if key in step: clean[key] = text(step[key],key)
        if 'highlight' in step:
            h = step['highlight']
            if not isinstance(h,dict) or set(h) != {'x','y','width','height'}: raise ValueError('highlight needs x, y, width, height percentages')
            h = {k:number(v,f'highlight {k}') for k,v in h.items()}
            if not (0 <= h['x'] < 100 and 0 <= h['y'] < 100 and 0 < h['width'] <= 100-h['x'] and 0 < h['height'] <= 100-h['y']):
                raise ValueError('highlight must fit inside the screenshot (percentages 0–100)')
            clean['highlight'] = h
        steps.append(clean)
    result['steps'] = steps
    return result


def build(args):
    path = Path(args.tutorial).resolve(strict=True)
    if path.stat().st_size > 1024*1024: raise ValueError('Tutorial JSON must be at most 1 MB')
    data = validate(json.loads(path.read_text(encoding='utf-8')),path.parent)
    video = None
    if args.video:
        video = Path(args.video).resolve(strict=True)
        duration,streams = probe(video)
        if video.suffix.lower() != '.mp4' or not any(s.get('codec_type') == 'video' and s.get('codec_name') == 'h264' for s in streams):
            raise ValueError('--video needs a browser-compatible H.264 MP4; transcode other formats first')
        if abs(duration-data['duration']) > .25: raise ValueError('Video duration does not match tutorial duration')
        data['video'] = 'recording.mp4'
    else: data['video'] = None
    template = (Path(__file__).resolve().parents[1]/'assets/tutorial.html').read_text(encoding='utf-8')
    # Escape all HTML-significant characters in script data; UI inserts textContent only.
    payload = json.dumps(data,ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    output = template.replace('TUTORIAL_PAGE_TITLE',html.escape(data['title'])).replace('/*TUTORIAL_DATA*/',payload)
    out = new_output(args.out)
    (out/'index.html').write_text(output,encoding='utf-8')
    if video: shutil.copyfile(video,out/'recording.mp4')
    print(f'Built {len(data["steps"])} steps: {out}/index.html')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    prep = sub.add_parser('prepare',help='Extract local timestamped screenshots; no interpretation or transcription')
    prep.add_argument('recording'); prep.add_argument('--out',required=True)
    prep.add_argument('--frames',type=int,default=12); prep.add_argument('--at',help='Comma-separated timestamps in seconds')
    prep.add_argument('--audio',action='store_true',help='Extract mono WAV if an audio stream exists')
    prep.set_defaults(func=prepare)
    render = sub.add_parser('build',help='Build portable HTML from an agent-authored tutorial JSON')
    render.add_argument('tutorial'); render.add_argument('--out',required=True)
    render.add_argument('--video',help='Optional H.264 MP4 to copy alongside the HTML for replay')
    render.set_defaults(func=build)
    args = parser.parse_args()
    try: args.func(args)
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        parser.exit(2,f'Error: {exc}\n')

if __name__ == '__main__': main()
