"""Regenerate the great_tables HTML fragments embedded in SRF.qmd.

The tables live outside the document so that SRF.qmd contains no Python and
renders without a Jupyter kernel. Run this after editing the workbook:

    uv run python SRF/generate_tables.py
"""

import subprocess
from pathlib import Path

import polars as pl
from great_tables import GT, md, style, loc

HERE = Path(__file__).parent
OUT = HERE / "_tables"
WORKBOOK = HERE / "Response-level SRF (draft).xlsx"

class_colors = {"Core": "#1b7837", "Optional": "#999999"}
tier_colors = {1: "#1b7837", 2: "#f4a261", 3: "#999999"}


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


def tbl_srf_fields() -> GT:
    srf_fields = (
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

    return (
        GT(srf_fields, groupname_col="Category", id="gt-srf-fields")
        .tab_header(
            title="Draft Single Registration Form — data fields",
            subtitle=f"All {srf_fields.height} fields proposed for the Single Registration Form, grouped by category",
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


TABLES = {
    "tbl-sources": tbl_sources,
    "tbl-categories": tbl_categories,
    "tbl-classification": tbl_classification,
    "tbl-srf-fields": tbl_srf_fields,
    "tbl-dedup-ladder": tbl_dedup_ladder,
    "tbl-hoh-vs-all": tbl_hoh_vs_all,
}


def _to_markdown(html: str) -> str:
    """Convert a table's HTML into a pandoc grid table.

    Quarto only turns HTML tables into native tables for computational cell
    output — raw HTML in the document body is dropped entirely by the typst and
    docx writers. Doing the conversion here, with the same pandoc Quarto
    renders with, is what the old Jupyter pipeline was getting for free.
    """
    result = subprocess.run(
        ["quarto", "pandoc", "-f", "html", "-t", "markdown", "--wrap=none"],
        input=html,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def as_include(table: GT) -> str:
    """Build one include file holding both renderings of a table.

    HTML output gets great_tables' own markup, so the fills and striping are
    exactly as generated. The typst and docx outputs get the pandoc grid table,
    which carries the content but not the CSS.

    Blank lines are stripped from the HTML because pandoc's markdown reader
    ends an HTML block at the first one, which would split the table apart.
    """
    html = "\n".join(line for line in table.as_raw_html().splitlines() if line.strip())
    return (
        '::: {.content-visible when-format="html"}\n\n'
        f"{html}\n\n"
        ":::\n\n"
        '::: {.content-hidden when-format="html"}\n\n'
        f"{_to_markdown(html)}\n\n"
        ":::\n"
    )


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, build in TABLES.items():
        target = OUT / f"{name}.md"
        target.write_text(as_include(build()))
        print(f"wrote {target.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
