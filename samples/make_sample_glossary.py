#!/usr/bin/env python3
"""Generate the sample glossary PDF that ships in data/.

The text is written for this project, so the file carries no third-party licence
obligation and can be committed. Its purpose is to give the RAG vector tier
(`rag.py` -> PyPDFDirectoryLoader(data_dir) -> ChromaDB) something to ingest on a
fresh clone, so a reviewer can exercise retrieval without the licensed RSMeans
corpus.

Run from anywhere:  python3 samples/make_sample_glossary.py
"""

import os
import pymupdf

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "PlanRead-Sample-Glossary.pdf")

TITLE = "PlanRead Sample Construction Glossary"
SUBTITLE = ("Sample retrieval corpus for the PlanRead demonstration build. "
            "Definitions written for this project and released under the MIT licence; "
            "this file is not the RSMeans Illustrated Construction Dictionary.")

SECTIONS = [
    ("Reading a plan set", [
        "A construction plan set is an ordered collection of sheets that together describe "
        "one building. The cover sheet carries the project title, the list of sheets, the "
        "design loads and the general notes. Architectural sheets follow, usually numbered "
        "A-0 upward, then structural, mechanical, electrical and plumbing disciplines each "
        "with their own prefix.",
        "Floor plans are drawn as a horizontal cut through the building at roughly four feet "
        "above the floor, so that doors, windows and partitions all appear in the same view. "
        "Walls are cut and therefore drawn heavy, with a solid or hatched fill between two "
        "parallel lines. Anything above the cut plane, such as roof framing or the outline "
        "of upper cabinets, is drawn with a lighter dashed or thin line.",
        "Elevations show the outside faces of the building; sections show a vertical cut, "
        "usually keyed to a section mark on the plan. Detail callouts enlarge a small part of "
        "a plan or section at a larger scale, and the callout bubble tells the reader which "
        "sheet and which detail number to turn to.",
    ]),
    ("Common line and annotation conventions", [
        "Dimension strings are drawn as a continuous line with tick marks at each end and the "
        "measured value written above the line, normally in feet and inches. Dimensions read "
        "from the bottom or the right of the sheet wherever possible, so a dimension set at "
        "ninety degrees to normal reading direction is a sign that the view has been rotated.",
        "A keyed note is a short leader line ending in a dot or arrow on the object, with the "
        "text at the other end. A schedule is a table that lists repeated objects, such as "
        "doors, windows or rooms, by tag; the tag on the plan is a short code that points into "
        "the table, so the plan stays uncluttered and the detail lives in one place.",
        "A specification is the written counterpart to the drawings. Where the two disagree, "
        "the specification usually governs materials and workmanship, and the drawing governs "
        "geometry and location. The general notes on the cover sheet state which document "
        "takes precedence for that project.",
    ]),
    ("Term definitions", [
        "LINTEL. A horizontal structural member spanning an opening such as a door or window, "
        "carrying the load of the construction above and transferring it to the walls on "
        "either side. On a drawing the lintel is usually shown as a heavy line across the "
        "opening, often with a keyed note giving its material and size.",
        "SILL. The horizontal bottom member of a window or door frame, or the sloping member "
        "at the base of a wall that sheds water away from the building. On a window schedule "
        "the sill height is normally given as a dimension from finished floor, because it "
        "controls both daylight and fall protection.",
        "HEADER. A horizontal member that collects loads over an opening and distributes them "
        "to adjacent framing, structurally similar to a lintel but in wood-frame construction "
        "usually built up from multiple plies. A header schedule lists the span, the number of "
        "plies and the jack studs required for each opening size.",
        "FOOTING. The widened concrete base at the bottom of a foundation wall or column that "
        "spreads the building load over a larger soil area. Footings are dimensioned on the "
        "foundation plan with width, depth and reinforcing, and their depth below grade is "
        "governed by frost line requirements.",
        "JAMB. The vertical side member of a door or window opening, forming the face that the "
        "door leaf closes against. On an enlarged plan or door schedule the jamb detail "
        "indicates the frame type, the rough opening and how the frame meets the wall finish.",
        "SOFFIT. The underside of a projecting element, most commonly the underside of an "
        "eave, a beam or an overhanging cabinet run. A soffit is usually called out where two "
        "planes meet and the joint must be closed against weather or where a finish surface "
        "changes.",
        "RISER. The vertical face of a stair step, measured from the top of one tread to the "
        "top of the next. Riser height and tread depth together determine stair geometry, and "
        "building codes cap the riser height and the variation between consecutive risers.",
        "TREAD. The horizontal walking surface of a stair step, measured from the front edge "
        "of one riser to the front edge of the next, excluding any nosing. Stair dimensions on "
        "a plan are normally given as a run and a rise for the whole flight, with the "
        "individual tread and riser noted once.",
        "REBAR. Reinforcing bar embedded in concrete to carry tensile stress, specified by bar "
        "size, spacing and cover. On a foundation or slab plan, reinforcing is called out with "
        "a leader to the region it applies to, together with the required clear cover from the "
        "concrete face.",
        "FLASHING. A thin impervious material installed to prevent water from penetrating at a "
        "junction, such as a roof-to-wall intersection, a parapet or a window head. Flashing "
        "details always show a lap and an uphill turn, because the material only works if "
        "water is directed back toward the drainage surface.",
        "EAVE. The lower edge of a sloping roof that overhangs the wall, consisting of the "
        "fascia, the soffit and the roof edge. On a section the eave detail shows the "
        "ventilation path into the attic and how the roofing terminates over the wall.",
        "RIDGE. The highest horizontal line of a sloping roof, where two opposing roof planes "
        "meet. The ridge is shown on the roof plan as a heavy line, and the ridge board or "
        "beam that supports the rafters at that line is detailed in the framing section.",
        "STUD. A vertical framing member in a wall, typically spaced at sixteen or twenty-four "
        "inches on centre. Stud spacing, size and grade are usually stated in a general note "
        "or a wall type legend rather than repeated on every wall of the plan.",
        "JOIST. A horizontal framing member that carries floor or ceiling loads between beams "
        "or bearing walls, repeated at regular spacing. Floor framing plans show joist "
        "direction with an arrow and give the size, spacing and span in a single note.",
        "SHEATHING. The panel material fastened over studs or joists to provide a nailing "
        "surface and to brace the frame, such as plywood or oriented strand board. Sheathing "
        "thickness and rating appear in the wall section or the structural notes, not on the "
        "floor plan.",
        "GRADE BEAM. A concrete beam cast at or near grade that ties foundation walls or "
        "pile caps together and carries loads across weak or expansive soil. It is drawn on "
        "the foundation plan with its width, depth and reinforcing called out separately from "
        "the wall footing.",
        "CONTROL JOINT. A deliberate plane of weakness formed or sawed into a concrete slab or "
        "wall to control where cracking occurs. Control joints are shown on the plan as a "
        "dashed line with a note giving spacing and depth, because the crack will happen "
        "whether or not the joint is drawn.",
        "WEEP HOLE. A small opening left in a mortar joint or a cladding system to let "
        "trapped water drain out of a cavity wall or above a flashing. Weep holes are drawn "
        "on masonry elevations as a short gap at the base course, usually at regular spacing.",
        "SPECIFICATION. The written project document that sets out materials, products, "
        "execution and quality standards for each work item, organised by division. A "
        "drawing note that says 'see specification' points to a numbered section there, and "
        "the drawing is not complete without it.",
        "SCHEDULE. A table on a drawing sheet that lists repeated elements with their "
        "attributes, such as doors, windows, rooms or finishes. The plan carries a short tag "
        "for each element and the schedule carries the full description, so a change is made "
        "once in the table rather than in every occurrence.",
        "LEGEND. A key on the sheet that explains the symbols, hatch patterns, line types and "
        "abbreviations used on that drawing. A legend is sheet-specific in many offices, so "
        "the same symbol may mean different things on architectural and structural sheets.",
        "DETAIL CALLOUT. A circular or oval symbol placed on a plan or section that refers to "
        "an enlarged drawing elsewhere in the set. The top of the bubble gives the detail "
        "number and the bottom gives the sheet number, so the reader can follow the reference "
        "without searching the whole set.",
        "SECTION MARK. A symbol, usually a circle bisected by a line with a letter or number "
        "at each end, that shows where a building section is cut and which direction the "
        "section looks. The matching section drawing carries the same tag so the two can be "
        "read together.",
        "PLAN VIEW. An orthographic projection looking down on the building, showing layout in "
        "the horizontal plane. A floor plan is a plan view cut at a fixed height, while a roof "
        "plan is a plan view from above the roof, and the two are not interchangeable.",
    ]),
]


def main():
    doc = pymupdf.open()
    W, H = 612, 792                      # US Letter, points
    L, R, T, B = 62, 62, 62, 62
    heading_gap, para_gap = 10, 7

    page = doc.new_page(width=W, height=H)
    y = T

    def new_page():
        nonlocal page, y
        page = doc.new_page(width=W, height=H)
        y = T

    def put(text, size=9.5, leading=13.2, space_after=para_gap, font="helv", color=(0, 0, 0)):
        nonlocal y
        for attempt in range(2):
            if y > H - B - 24:            # no room even for one line
                new_page()
            rect = pymupdf.Rect(L, y, W - R, H - B)
            spare = page.insert_textbox(rect, text, fontname=font, fontsize=size,
                                        lineheight=leading / size, color=color, align=0)
            if spare >= 0:
                y = (H - B) - spare + space_after
                return
            if attempt == 0:
                new_page()                # did not fit: retry on a clean page
        raise RuntimeError(f"block does not fit on an empty page: {text[:40]!r}")

    # cover block
    page.insert_textbox(pymupdf.Rect(L, y, W - R, y + 60), TITLE,
                        fontname="hebo", fontsize=20, color=(0, 0, 0))
    y += 34
    put(SUBTITLE, size=8.5, leading=11.5, space_after=16, color=(0.25, 0.25, 0.25))

    for title, paras in SECTIONS:
        put(title, size=12, leading=15, space_after=heading_gap, font="hebo")
        for p in paras:
            put(p)

    doc.set_metadata({
        "title": TITLE,
        "author": "PlanRead authors",
        "subject": "Sample retrieval corpus (MIT licensed project-authored text)",
        "keywords": "construction plan reading, glossary, RAG sample corpus",
    })
    doc.save(OUT, garbage=4, deflate=True)
    doc.close()

    size = os.path.getsize(OUT)
    chk = pymupdf.open(OUT)
    words = len(" ".join(pg.get_text() for pg in chk).split())
    print(f"wrote {OUT}")
    print(f"  pages={chk.page_count} words={words} bytes={size}")
    chk.close()


if __name__ == "__main__":
    main()
