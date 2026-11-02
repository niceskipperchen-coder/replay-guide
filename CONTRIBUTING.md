# Contributing

Open an issue for a reproducible bug or focused feature, or fork the repository, make a change on a branch and open a pull request. Please explain the user-visible behavior and how you verified it.

Run `python3 -m unittest discover -s tests -v`. FFmpeg/ffprobe enable the real-media integration test. Keep the helper compatible with Python 3.10+ and dependency-free. The HTML template lives in `skills/replay-guide/assets/tutorial.html`; rebuild an example after changing it.

For reader changes, check 320px and 390px widths plus desktop, long text, keyboard focus, image enlargement, navigation and replay. Do not describe desktop viewport emulation as a physical-device test.

Use synthetic or your own sanitized recordings. Never include credentials, personal messages or someone else's private footage in an issue or PR. If you adapt third-party code/assets, preserve their license and attribution.

Useful contributions: a reproducible codec failure, an accessible mobile interaction improvement, or a documented agent setup tested with an actual recording. Keep model-generated instructions grounded in source evidence; uncertainty should remain visible.
