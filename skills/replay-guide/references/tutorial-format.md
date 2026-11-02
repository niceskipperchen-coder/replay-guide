# Tutorial JSON format (v1)

Place JSON beside the extracted screenshots. UTF-8; no Markdown rendering. Strings are displayed as plain text, with paragraph breaks preserved. The builder accepts no remote image URLs and never runs code snippets.

```json
{
  "title": "Export your first report",
  "summary": "A short walkthrough of the recorded export flow.",
  "duration": 12.5,
  "steps": [
    {
      "title": "Open the export menu",
      "body": "Choose Export in the top toolbar. The export options appear.",
      "start": 1.2,
      "end": 4.5,
      "image": "frame-01-1.200s.jpg",
      "alt": "Report toolbar with the Export menu open",
      "status": "observed",
      "note": "Optional context, caveat or review question.",
      "code": "Optional copyable code, displayed verbatim.",
      "highlight": {"x": 65, "y": 10, "width": 15, "height": 12}
    }
  ]
}
```

Required: title (up to 300 characters), summary (up to 2000), duration (>0 to 1800 seconds), 1–48 steps. Every step requires title, body, start, end, image, alt, status. Step text fields are nonempty, at most 12,000 characters. Optional code/note are also nonempty when provided.

Timing: finite numbers in seconds; `0 <= start < end <= duration`. Starts are chronological; intervals may overlap when explaining the same moment. Use exact manifest duration; optional replay recording must match within 0.25 seconds.

Images: relative PNG/JPEG/WebP paths inside the JSON directory, including subdirectories. Absolute paths, symlink escapes, HTML/SVG and images over 8 MB are rejected. Image bytes are embedded in HTML, so keep screenshot count/size proportionate.

Highlights: optional bounding rectangle, percentages of the whole image. x/y >=0; width/height >0; rectangle must stay within 100% on both axes. View the screenshot before choosing coordinates. The outline does not replace descriptive instructions or alt text.

Status: `observed` means supported by viewed evidence; `needs-review` means ambiguous and should include a specific note. Neither claims that the generated guide was replayed in the original app.

Unknown keys are ignored. Do not include private source paths or credentials. There is no external-link/action execution field.
