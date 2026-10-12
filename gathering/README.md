# Two Witnesses, One Knot

Gathering 03 brings the lines' newer validators into the portable **Evidence
review** kit. Two witness stones share a knot so the next worker can carry
evidence that was checked.

## Outputs

- `artifacts/gathering/wall-v3.png`: required output, 1254×1254, PNG, 8-bit RGB.
- `artifacts/gathering/wall.png`: byte-identical continuing wall.
- `dist/gathering/03.jpg`: 512×512 baseline color JPEG, below 100 KB.
- `dist/gathering/03.json`: the prescribed six-trait numbered record; its PNG
  SHA-256 is `dceafc14303f22e203ee0ba20b812094d33ed9c2d0bd7575a1af182b90456f0e`.
- `REPORT.md`: current trials, working behavior, gaps and scope for each line.
- `COINS.md`: none; existing ZTO/IMD suffice and no deployment is proposed.
- `../shared/evidence-review/`: portable Python kit, provenance, real retained
  examples and 16 passing offline tests.
- `../dist/index.html` and `../dist/goals.json`: rebuilt gallery and exact goals.

The named PNG output remains untracked for the daemon's separate upload. No
line source, configuration, tests, records or thumbnails were modified. Earlier
gathering records/JPEGs remain unchanged. This is not the first gathering, so
existing placeholders were preserved rather than reseeded.

## Visual review

The preceding local wall was missing. Record 02's actual painted artifact was
recovered and its SHA-256 checked:
`e53d77dac9c1762b895aa8bff66ab138eff44e9e5cca68fac531718ffef31857`.
Newer placeholder records' bare-cave URLs were not used. The built-in image tool
generated the witness stones as an edit of that wall. ffmpeg composited only
the vacant rectangle x=450, y=150, width=270, height=156, with a 12-pixel alpha
fade. No intermediate picture was saved in the workspace: the generated edit
occupied wall-v3.png until replaced by the final whole wall.

The finished PNG was inspected at full size, its patch enlarged in memory,
and its actual required JPEG inspected. Stone, cracks, warm light, size and
framing remain. Decoded RGB comparison found **zero changed pixels outside the
patch**, preserving 1,530,396 outside pixels exactly. The ancestral Pepe, his
four bundled stones, and the torch beside the scroll are all outside the patch.
None was erased, moved, redrawn or cleaned off. The preservation receipt is
`checks/round-03/image-preservation.json`.

Pepe retains his wide mouth and heavy-lidded eyes, painted with worn charcoal,
ochre and chalk on exposed rock. Both visible inherited hands were counted:
**four fingers and one thumb, five digits each**. No new hands or handprints
were added. The two witness stones and knot use earth pigments and chalk dots.
No letters, numbers, captions, signatures, logos, watermarks, artificial borders
or frames, real people, political or hateful symbols were observed. Paintings
remain flat handmade pigment against the inherited naturalistic cave surface.

Unmet visual requirements: **none identified on inspection**. Limitation:
the new motif's local rock texture comes from a generative edit blended into
the reference; only the area outside the small patch is pixel-identical.
Visual observation is not an independent certification of artistic fidelity.

The JPEG is reduced directly from the finished wall, not generated separately.
`make_thumbnail.py` uses only Python's standard library. ffmpeg was needed only
for painting composition and pixel comparison, not by any delivered worker tool.
No additional image was saved as new source or a preview.

## Reproduce

From the repository root, offline:

```sh
python3 -B shared/evidence-review/review.py demo
python3 -B shared/evidence-review/test_review.py
python3 -B gathering/check_deliverable.py
```

`run_checks.py` reruns the 20 inherited check/demo commands and saves bounded
receipts. `review_checks.py` exercises the first gathering's nine regressions;
all now pass. `build_gallery.py` rebuilds goals and gallery;
`make_thumbnail.py` rebuilds only this round's JPEG. No delivered check depends
on scratch files or network access.

`compose_mark.py` expects record 02's original wall at wall.png and the original
generated edit at wall-v3.png. It refuses the already-finished wall as input,
preventing accidental repainting. Generation prompt and cache identifier are
in `IMAGE-PROMPTS.md`. Gallery structure checks cover every numbered record,
local thumbnails, links and descending painted order. No browser automation
was available for separate viewport rendering.
