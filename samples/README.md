# Sample data

Small, non-confidential samples that ship with the repository so the application
can be run out of the box.

## Sample term dictionary

    data/RSMeans_Illustrated_Construction_Dictionary/terms.json

A hand-written sample of common construction plan-reading terms (24 entries:
lintel, sill, header, footing, jamb, soffit, riser, tread, rebar, flashing, eave,
ridge, stud, joist, sheathing, grade beam, control joint, weep hole,
specification, schedule, legend, detail callout, section mark, plan view). It
exists so the retrieval-augmented explanation path works after a fresh clone.
The definitions were written for this project and contain no third-party content.

To use the full dictionary instead, replace this file with the real `terms.json`
(generated from a dictionary you are licensed to use) and add the matching
`images/` directory alongside it. Both paths are gitignored, so your replacement
will not be committed.

## Sample plan set

    samples/plan-set/A-0-cover.jpg
    samples/plan-set/A-1-foundation-and-floor-plans.jpg
    samples/plan-set/A-2-elevations-and-details.jpg
    samples/plan-set/A-3-sections-and-details.jpg

A four-sheet residential plan set ("The Manchester") used to exercise the upload,
OCR, callout-detection and detail-navigation paths. Each sheet is 3300 x 2200 px
and carries real drawing text: room names, dimension strings, general notes,
wall and header schedules, detail callouts and a title block.

| File | Sheet | Content |
| --- | --- | --- |
| `A-0-cover.jpg` | A-0 | Cover: render, list of sheets, design loads, header and girder schedules, general notes |
| `A-1-foundation-and-floor-plans.jpg` | A-1 | Foundation plan, first and second floor plans, typical details |
| `A-2-elevations-and-details.jpg` | A-2 | Four elevations, typical stair, railing and deck details |
| `A-3-sections-and-details.jpg` | A-3 | Section details, chimney detail, column and beam details |

Open the app, upload one or more of these sheets, and click any detected term to
read the retrieval-augmented explanation. Uploading two sheets (A-1 and A-3) lets
you follow a detail callout from the floor plan to the section it references.

### Provenance and licence

These four images are a vendor's publicly posted sample plan set, downloaded from
<https://gmfplus.com/stock-plans/sample-plan-set/> (GMF+ Architects, sheet set
"The Manchester", (c) 2012 G.M. Frech and Associates). They are **not** covered by
this repository's MIT license: they are redistributed unmodified, with the
vendor's sample watermark intact, solely as bundled test input for the software.
See `samples/plan-set/NOTICE.txt`.

Anyone reusing these images for anything beyond testing PlanRead needs permission
from the copyright holder. To use your own drawings instead, replace the files in
`samples/plan-set/`; drawings from real projects are usually proprietary or
confidential and must not be committed.
