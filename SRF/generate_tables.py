# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "polars",
#     "great-tables>=0.23",
#     "fastexcel",
#     "nokap",
# ]
# ///
"""Regenerate the great_tables fragments embedded in SRF.qmd.

The tables live outside the document so that SRF.qmd contains no Python and
renders without a Jupyter kernel. Run this after editing the workbook:

    uv run SRF/generate_tables.py

Two renderings are produced per table:

* HTML gets great_tables' own markup, so the fills and striping are exactly as
  generated.
* typst (PDF) and docx get a PNG of the same table. Raw HTML in the document
  body is dropped or flattened by the typst writer, and a pandoc grid table
  would lose the colour fills, so a picture is the only rendering that survives
  with the formatting intact.

PNG export goes through great_tables' `.gtsave()`, which drives a headless
Chrome via the `nokap` package — no selenium, no Pillow — and crops to the
table element. Chrome or Chromium must be installed on the machine running
this script; the Python side is declared in the script metadata above.

Each PNG is printed with the height it will occupy on the page, so it is
obvious when a table has grown past what fits and needs splitting.
"""

from pathlib import Path

import polars as pl
from great_tables import GT, md, style, loc

HERE = Path(__file__).parent
OUT = HERE / "_tables"
WORKBOOK = HERE / "Response-level SRF (draft).xlsx"

class_colors = {"Core": "#1b7837", "Optional": "#999999"}
tier_colors = {1: "#1b7837", 2: "#f4a261", 3: "#999999"}

# Print geometry. The typst page is us-letter with 1.25in margins, so the text
# block is 432pt (6in) wide and 612pt (8.5in) tall.
TEXT_WIDTH_PT = 432
TEXT_HEIGHT_IN = 8.5

# Each image is emitted at width=100%, i.e. stretched to the 432pt text block.
# That means the on-page size of the type is fixed by how many CSS pixels wide
# the table is, not by the font size on its own: rendering the table into a
# narrower viewport makes it wrap more and come out *larger* in print.
#
# So the viewport is derived from the point size we want rather than chosen by
# hand — vwidth = font_px * 432 / target_pt. The SRF field list is six columns
# of long text and only fits a portrait page at the smaller target.
RENDER_FONT_PX = 16
TARGET_PT = 10
TARGET_PT_DENSE = 8

# Raster scale. 3x keeps the type clean once typst scales the PNG to the text
# block; the files stay a few hundred KB each.
PNG_ZOOM = 3


def tbl_sources() -> GT:
    sources = pl.DataFrame({
        "Source": [
            "IOM",
            "WFP",
            "Cash Consortium (CC)",
            "Emergency Rapid Response Mechanism (ERRM)",
            "UNHCR–WFP Minimum Core Assistance Delivery Dataset",
        ],
        "Type": [
            "Registration form",
            "Registration form",
            "Consortium registration form",
            "Consortium registration form",
            "Policy / reference",
        ],
        "Member orgs / scope": [
            "IOM (DTM and operational programmes)",
            "WFP",
            "Chaired by SCI; partner agencies delivering multi-purpose cash",
            "NRC and DRC (rapid response in newly accessible / displaced locations)",
            "Joint UNHCR–WFP — minimum data items for delivering core assistance to affected populations",
        ],
        "Principal contribution to SRF": [
            "Metadata and Biometrics fields; closest to the IDEHA pilot draft",
            "Other / payment fields; targeting and contact details",
            "Household survey fields; vulnerability and consent",
            "Biographic and minimum-viable Household survey fields",
            "Constraint on the SRF (must not contradict), rather than a source of fields",
        ],
    })

    return (
        GT(sources, id="gt-sources")
        .tab_header(
            title="Sources reviewed",
            subtitle="Registration forms and reference documents informing the SRF",
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns=["Source"]),
        )
        .tab_style(
            style=style.fill(color="#f5f5f5"),
            locations=loc.body(columns=["Source"]),
        )
        .opt_row_striping()
    )


def tbl_categories() -> GT:
    section_defs = pl.DataFrame({
        "Category": [
            "Consent",
            "Metadata",
            "Biographic",
            "Household survey",
            "Individual survey",
            "Biometrics",
            "Other",
        ],
        "What it covers": [
            "Informed consent to collect, use, share, and refer case data.",
            "Form, project and process data: registration date, enumerator, IDs, source.",
            "Person and place data: names, sex, DOB, location, nationality, civil ID.",
            "Household-level questions: size, sex-age cohort, disability screen, drivers of displacement.",
            "Individual-level questions: disability / accessibility, special needs.",
            "Fingerprints and photos used for identity matching.",
            "Payment instrument data (account / wallet, expiry).",
        ],
    })

    return (
        GT(section_defs, id="gt-categories")
        .tab_header(
            title="Categories",
            subtitle="The category each SRF field is grouped under",
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns=["Category"]),
        )
        .tab_style(
            style=style.fill(color="#f5f5f5"),
            locations=loc.body(columns=["Category"]),
        )
        .opt_row_striping()
    )


def tbl_classification() -> GT:
    classes = pl.DataFrame({
        "Class": ["Core", "Optional"],
        "Meaning": [
            "Required for the SRF to do its job: identify the household, enable referral, and support deduplication.",
            "Conditional, programme-specific, or sensitive. Only collected when the operation actually needs it.",
        ],
        "Behaviour on the form": [
            "Always shown. Cannot be skipped.",
            "Hidden by default. Switched on per programme / per modality.",
        ],
    })

    return (
        GT(classes, id="gt-classification")
        .tab_header(
            title="Field classification",
            subtitle="Two tiers determine whether a field is shown by default",
        )
        .tab_style(
            style=style.fill(color=class_colors["Core"]),
            locations=loc.body(columns=["Class"], rows=pl.col("Class") == "Core"),
        )
        .tab_style(
            style=style.fill(color=class_colors["Optional"]),
            locations=loc.body(columns=["Class"], rows=pl.col("Class") == "Optional"),
        )
        .tab_style(
            style=style.text(weight="bold", color="white"),
            locations=loc.body(columns=["Class"]),
        )
    )


def _srf_fields_data() -> pl.DataFrame:
    return (
        pl.read_excel(WORKBOOK, sheet_name="Fields")
        .select([
            "Field ID",
            "Field label",
            "Category",
            "Record level",
            "Core / Optional",
            "Sources",
        ])
        .with_columns(pl.col("Record level").fill_null("—").replace({"-": "—"}))
    )


def tbl_srf_fields(categories: list[str] | None = None, part: str | None = None) -> GT:
    """The SRF field list, optionally restricted to a subset of categories.

    The full table is 46 rows and cannot page-break once it is a PNG, so the
    print rendering is emitted in parts (see SRF_FIELD_PARTS). `categories`
    selects the rows; `part` is appended to the subtitle so each image says
    which slice of the form it shows.
    """
    srf_fields = _srf_fields_data()
    total = srf_fields.height
    if categories is not None:
        srf_fields = srf_fields.filter(pl.col("Category").is_in(categories))

    subtitle = f"All {total} fields proposed for the Single Registration Form, grouped by category"
    if part is not None:
        subtitle = f"{subtitle} — {part}"

    return (
        GT(srf_fields, groupname_col="Category", id="gt-srf-fields")
        .tab_header(
            title="Draft Single Registration Form — data fields",
            subtitle=subtitle,
        )
        .tab_style(
            style=style.fill(color=class_colors["Core"]),
            locations=loc.body(columns=["Core / Optional"], rows=pl.col("Core / Optional") == "Core"),
        )
        .tab_style(
            style=style.fill(color=class_colors["Optional"]),
            locations=loc.body(columns=["Core / Optional"], rows=pl.col("Core / Optional") == "Optional"),
        )
        .tab_style(
            style=style.text(weight="bold", color="white"),
            locations=loc.body(columns=["Core / Optional"]),
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns=["Field ID"]),
        )
        .tab_style(
            style=style.fill(color="#f5f5f5"),
            locations=loc.row_groups(),
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.row_groups(),
        )
        .cols_align(align="center", columns=["Field ID", "Record level", "Core / Optional"])
        .cols_align(align="left", columns=["Field label", "Sources"])
        .tab_source_note(
            source_note=md("Source: `Response-level SRF (draft).xlsx`, sheet `Fields`."),
        )
        .opt_row_striping()
    )


def tbl_dedup_ladder() -> GT:
    ladder = pl.DataFrame({
        "Tier": [1, 2, 3],
        "Status": ["Preferred", "Fallback", "Last fallback"],
        "Method": [
            "Two-thumb biometric capture",
            "Photo biometric capture",
            "Data-field based matching",
        ],
        "When to use it": [
            "Default at any registration site that has working biometric capture devices",
            "When fingerprint capture is not possible — fingerprints unreadable, amputation, equipment failure, or unavailable hardware",
            "When neither fingerprints nor a usable photo can be captured. Matching is then performed on combinations of biographic fields (name, DOB, location, phone, civil ID, household composition).",
        ],
    })

    return (
        GT(ladder, id="gt-dedup-ladder")
        .tab_header(
            title="Deduplication fallback ladder",
            subtitle="Two-thumb biometric is preferred; photo is the fallback; data-field matching is the last resort",
        )
        .tab_style(
            style=style.fill(color=tier_colors[1]),
            locations=loc.body(columns=["Tier", "Status"], rows=pl.col("Tier") == 1),
        )
        .tab_style(
            style=style.fill(color=tier_colors[2]),
            locations=loc.body(columns=["Tier", "Status"], rows=pl.col("Tier") == 2),
        )
        .tab_style(
            style=style.fill(color=tier_colors[3]),
            locations=loc.body(columns=["Tier", "Status"], rows=pl.col("Tier") == 3),
        )
        .tab_style(
            style=style.text(color="white", weight="bold"),
            locations=loc.body(columns=["Tier", "Status"]),
        )
        .tab_style(
            style=style.text(),
            locations=loc.body(columns=["Method"]),
        )
        .cols_align(align="center", columns=["Tier"])
        .cols_align(align="left", columns=["Status", "Method", "When to use it"])
    )


def tbl_hoh_vs_all() -> GT:
    tradeoff = pl.DataFrame({
        "Dimension": [
            "Registration time per HH",
            "Deduplication strength",
            "Data protection surface",
            "Targeting / referral",
            "Cross-agency reuse",
            "Vulnerability to splitting",
        ],
        "Head-of-household only": [
            "Short",
            "Weaker — relies on HoH match + HH attributes",
            "Smaller dataset to safeguard",
            "Adequate for HH-level transfers",
            "Limited — hard to follow individuals across agencies",
            "High — a household can split between agencies undetected",
        ],
        "All members roster": [
            "Significantly longer",
            "Stronger — every member becomes a matchable record",
            "Larger dataset; child data and sensitive attributes at scale",
            "Required for child-focused, nutrition, or per-person assistance",
            "High — supports member-level case management",
            "Low — individuals re-appear under a known name / DOB",
        ],
    })

    return (
        GT(tradeoff, id="gt-hoh-vs-all")
        .tab_header(
            title="Head-of-household only vs. all members",
            subtitle="Tradeoffs to resolve before the SRF is locked",
        )
        .tab_spanner(
            label="Registration option",
            columns=["Head-of-household only", "All members roster"],
        )
        .tab_style(
            style=style.text(weight="bold"),
            locations=loc.body(columns=["Dimension"]),
        )
        .tab_style(
            style=style.fill(color="#f5f5f5"),
            locations=loc.body(columns=["Dimension"]),
        )
        .opt_row_striping()
    )


# The SRF field list is split for print: a single 46-row PNG is far taller than
# a page and an image cannot break across pages. Three parts, split on category
# boundaries, each comfortably inside the 8.5in text block.
SRF_FIELD_PARTS = [
    ("part1", ["Consent", "Metadata"], "part 1 of 3: consent and metadata"),
    ("part2", ["Biographic"], "part 2 of 3: biographic"),
    ("part3", ["Biometrics", "Individual survey", "Household survey"], "part 3 of 3: biometrics, individual and household survey"),
]

TABLES = {
    "tbl-sources": tbl_sources,
    "tbl-categories": tbl_categories,
    "tbl-classification": tbl_classification,
    "tbl-srf-fields": tbl_srf_fields,
    "tbl-dedup-ladder": tbl_dedup_ladder,
    "tbl-hoh-vs-all": tbl_hoh_vs_all,
}

# Tables whose print rendering is a set of PNGs rather than one, and tables
# that need the smaller target point size to fit the page.
PRINT_PARTS = {"tbl-srf-fields": SRF_FIELD_PARTS}
DENSE = {"tbl-srf-fields"}


def _png_size(path: Path) -> tuple[int, int]:
    """Width and height of a PNG, read straight out of the IHDR chunk."""
    blob = path.read_bytes()
    return int.from_bytes(blob[16:20], "big"), int.from_bytes(blob[20:24], "big")


def _render(table: GT, path: Path, target_pt: int) -> float:
    """Render a table to PNG; return the height it will occupy, in inches.

    `gtsave` drives headless Chrome through the `nokap` package, cropping to
    the table element. It replaces the deprecated `save`, which needed selenium
    and Pillow.
    """
    vwidth = round(RENDER_FONT_PX * TEXT_WIDTH_PT / target_pt)
    # vheight is generous so a long table is never clipped to the viewport.
    (
        table.tab_options(table_font_size=f"{RENDER_FONT_PX}px")
        .gtsave(str(path), zoom=PNG_ZOOM, vwidth=vwidth, vheight=6000, expand=0)
    )

    width, height = _png_size(path)
    height_in = TEXT_WIDTH_PT / 72 * height / width
    flag = "  << TALLER THAN THE TEXT BLOCK, SPLIT IT" if height_in > TEXT_HEIGHT_IN else ""
    print(f"wrote {path.relative_to(HERE.parent)} — {height_in:.2f}in tall at {target_pt}pt{flag}")
    return height_in


def as_include(name: str, table: GT) -> str:
    """Build one include file holding both renderings of a table.

    HTML gets great_tables' own markup, so the fills and striping are exactly
    as generated. typst and docx get PNGs, written alongside this file and
    referenced relative to SRF.qmd.

    Blank lines are stripped from the HTML because pandoc's markdown reader
    ends an HTML block at the first one, which would split the table apart.
    """
    html = "\n".join(line for line in table.as_raw_html().splitlines() if line.strip())

    target_pt = TARGET_PT_DENSE if name in DENSE else TARGET_PT
    images = []
    for suffix, categories, part in PRINT_PARTS.get(name, [(None, None, None)]):
        stem = name if suffix is None else f"{name}-{suffix}"
        part_table = table if suffix is None else TABLES[name](categories=categories, part=part)
        _render(part_table, OUT / f"{stem}.png", target_pt)
        images.append(f"![](_tables/{stem}.png){{width=100%}}")

    return (
        '::: {.content-visible when-format="html"}\n\n'
        f"{html}\n\n"
        ":::\n\n"
        '::: {.content-hidden when-format="html"}\n\n'
        + "\n\n".join(images)
        + "\n\n:::\n"
    )


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, build in TABLES.items():
        target = OUT / f"{name}.md"
        target.write_text(as_include(name, build()))
        print(f"wrote {target.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
