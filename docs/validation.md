# Validation — 2 November 2026

## Executed

- Python 3.14: 8 unittest cases passed, including real FFmpeg frame/audio extraction from a generated H.264/AAC clip, embedded-image output, optional video copy, malformed timestamps, highlight bounds, path traversal/symlink rejection, existing-output preservation and script-data escaping.
- A regression reproduced template-marker text corrupting embedded JSON; replacing the page-title slot before inserting data fixed it.
- Independent review ran the tests and used only copied screenshots/manifest (not the example answer) to author and build a separate two-step guide.
- Real Chrome desktop and 390 × 844 / 320 × 760 viewport checks: no horizontal page overflow; navigation buttons measure 48px high; next/previous, contents index, review badge, finish/restart, saved position after reload, code copy and screenshot enlargement work.
- Escape closes the screenshot dialog and restores focus; changing steps focuses the new heading.
- Optional replay started at 5 seconds and paused at approximately 7.17 seconds for a 7-second end bound (timeupdate is not frame-accurate). Clicking replay then immediately navigating leaves video paused and hidden. Pending replay requests are invalidated on navigation.
- Removed screenshot max-height containment so percentage highlights track the image rectangle for portrait screenshots as well as landscape.

## Limits

No physical iPhone/Android, Safari or screen-reader test has been performed. Reduced-motion CSS disables animation/transitions, but a simulated OS preference was not tested. Automated checks do not prove tutorial instruction accuracy. The included tutorial remains a draft with one timing step explicitly marked for review; the original app's workflow was not independently replayed.

The helper does not perform video understanding or transcription. An agent must inspect the source and author steps. No comparative benchmark of model accuracy or automatic discovery across all agent products is claimed.

FFmpeg operations time out after 120 seconds each. The 30-minute duration bound does not guarantee processing speed on a particular computer. Audio extraction is available but the included demo has no speech-transcription evaluation.

Public GitHub Pages deployment completed and the live tutorial loaded in Chrome. Python 3.10/3.14 Linux matrix also runs in repository CI; consult Actions for current results.
