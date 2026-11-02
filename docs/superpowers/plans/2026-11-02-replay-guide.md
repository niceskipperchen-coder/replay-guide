# Replay Guide Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task-by-task.

**Goal:** A reusable recording-to-tutorial skill and mobile-friendly HTML builder.
**Architecture:** Agent-authored evidence JSON feeds a validating Python builder; inline template renders escaped data. A separate prepare command extracts local media.
**Tech Stack:** Python 3.10+, FFmpeg, vanilla HTML/CSS/JS.
**Spec:** ../specs/2026-11-02-replay-guide-design.md

## Global constraints
- Local helper, no service/API key required; no implicit upload/publish.
- Original video optional; image-only HTML self-contained.
- Python helper does not interpret or transcribe recordings.

## Review focus
- Reject nonfinite/reversed/out-of-duration timestamps and malformed fields.
- Reject image paths escaping the input directory, including symlinks.
- Render hostile recording-derived text as text, never script/HTML.
- New output directories only; never overwrite an existing tutorial.
- Mobile controls remain reachable with long content and reduced motion.

## Tasks
- [x] 1. Write failing unittest coverage for validation, embedding, injection, output preservation and FFmpeg integration; run RED.
- [x] 2. Implement scripts/replay_guide.py with prepare and build subcommands. prepare emits timestamped frames/manifest; build consumes references/tutorial-format.md JSON, embeds images and optionally copies a supplied MP4. Run GREEN.
- [x] 3. Implement assets/tutorial.html: responsive reader, index, progress, screenshot zoom, code copy, bounded replay. Verify in real Chrome at phone/desktop widths.
- [x] 4. Write SKILL.md, schema reference, README, MIT license, contribution guide and synthetic/real evidence examples. Validate skill metadata; forward-test skill on a recording with an independent reviewer.
- [ ] 5. Review, run all checks, create a portable example and ZIP, commit locally. Public repository creation/push can follow the user's existing open-source request once reviewed, if authentication permits.

## Execution record
User approved the concrete workflow in chat and instructed building it. New project has its own directory/repository; no existing project branch is changed. Implement inline. Do not claim automatic interpretation, broad agent compatibility, or phone testing on physical devices.

Review fixes: preserve literal template markers in source content; use intrinsic image height for highlight alignment; invalidate pending replay requests on navigation. Full unittest suite: 8 passing. Skill validator run separately. Browser checks/limits recorded in docs/validation.md.
