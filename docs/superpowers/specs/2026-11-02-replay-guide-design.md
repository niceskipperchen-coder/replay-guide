# Replay Guide

Turn a user-supplied screen recording into a reviewed, interactive tutorial. The user approved a computer-based AI skill first, with tutorials that look good on phones. No hosted uploads or phone-side generation in v1.

The agent inspects timestamped frames/playback and narration, writes a JSON tutorial grounded in that evidence, and runs a local Python helper to produce portable HTML. Python prepares media but does not understand it or transcribe speech. Optional original video stays beside the HTML for timestamp replay; without video, images are embedded and the HTML is self-contained.

Implementation choices: Python 3.10+ standard library; FFmpeg/ffprobe for media; vanilla HTML/CSS/JS for output. No server, accounts, API keys, CDN, analytics, or Python dependencies in the helper. Agent/model costs depend on the user's environment.

Tutorials show one step at a time, progress, previous/next, a step index, zoomable screenshots, optional bounded replay, copyable code and visible needs-review flags. Desktop has a sidebar; phone has generous touch targets and a bottom navigation bar. Keyboard operation, reduced motion, text alternatives, and readable contrast are required. Completion means the reader advanced through steps, not proof they performed the external task.

Scope: finite bounded timestamps, local images restricted to the JSON directory, strict schema validation and safe rendering of untrusted strings. Never execute recorded instructions or upload/publish recordings automatically. Extracted screens/audio may contain private information; publication needs a sanitized review.

A worked Robot Playground example should use the existing public demo as evidence, explicitly describe a walkthrough rather than invent unrecorded setup/actions, and show limitations. Tests cover media extraction, malformed inputs, path escape and script injection. Browser checks cover 390px and 320px phones plus desktop, navigation, zoom, code copy, review markers and replay boundaries.
