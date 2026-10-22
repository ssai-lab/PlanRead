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

## Sample retrieval corpus

    data/PlanRead-Sample-Glossary.pdf

A three-page glossary written for this project (about 1,500 words), covering sheet
organisation, line and annotation conventions, and prose definitions of the same
24 terms as the sample dictionary. It exists because the RAG pipeline has two
tiers: exact lookup against `terms.json`, and a vector-search fallback built by
`PyPDFDirectoryLoader` over the PDFs in `data/`. Without a PDF in `data/` the
fallback ingests nothing and quietly returns no context, so explanations lose
their dictionary grounding for any term outside the 24. This file gives that tier
something to chew on straight after a clone.

It is also the reason the negation rules in `.gitignore` exist: `data/` and
`*.pdf` are ignored wholesale, so this one file is excepted explicitly.

Regenerate it with:

    python3 samples/make_sample_glossary.py

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
