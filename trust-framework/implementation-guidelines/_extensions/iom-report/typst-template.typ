// ===========================================================================
// IOM report template  ·  typst-template.typ
// Encodes the IOM Publications Layout Manual (March 2026) and the
// typographic parts of the IOM House Style Manual (August 2024).
//
// This partial replaces Quarto's default `typst-template.typ`. Its only job
// is to DEFINE the function that wraps the whole document; `typst-show.typ`
// is what actually calls it with metadata from the YAML header.
// ===========================================================================

// --- Corporate colours -----------------------------------------------------
// Layout Manual, "Corporate colours" (p. 6)
#let iom-blue    = rgb("#0033A0") // PANTONE 286C — official dark blue
#let iom-un-blue = rgb("#418FDE") // PANTONE 279C — light blue / UN blue
#let iom-yellow  = rgb("#FFB81C") // PANTONE 1235C
#let iom-mint    = rgb("#5CB8B2") // PANTONE 7472C
#let iom-orange  = rgb("#FF671F") // PANTONE 165C
#let iom-red     = rgb("#D22630") // PANTONE 1795C

// --- Typeface --------------------------------------------------------------
// Gill Sans Nova is the primary typeface; Calibri is the sanctioned
// substitute when it is unavailable (Layout Manual, p. 15–16).
// Typst falls through this list in order.
#let iom-font = ("Gill Sans Nova", "Calibri", "Carlito")

// NOTE ON LEADING
// The Layout Manual specifies leading as baseline-to-baseline (e.g. 11/13 pt).
// Typst's `leading` is the GAP between lines, not baseline-to-baseline, so the
// values below are approximations. Check a printed proof and adjust.

// --- Small reusable pieces -------------------------------------------------

// Page number in the blue box used on IOM page runners.
#let iom-page-number() = box(
  fill: iom-blue,
  inset: (x: 7pt, y: 4pt),
  text(fill: white, size: 9pt, weight: "semibold")[
    #context counter(page).display(here().page-numbering())
  ],
)

// Page runner / footer.
// Verso (left) pages carry the chapter or section title; recto (right) pages
// carry the publication title (Layout Manual, "Page runner", p. 9).
#let iom-footer(running-title: none) = context {
  let runner = text.with(size: 7pt, fill: luma(45%), tracking: 0.5pt)
  let previous = query(selector(heading.where(level: 1)).before(here()))
  let section = if previous.len() > 0 { upper(previous.last().body) } else { none }

  if calc.odd(here().page()) {
    grid(
      columns: (1fr, auto), column-gutter: 8pt, align: horizon,
      align(right, runner(upper(running-title))),
      iom-page-number(),
    )
  } else {
    grid(
      columns: (auto, 1fr), column-gutter: 8pt, align: horizon,
      iom-page-number(),
      align(left, runner(section)),
    )
  }
}

// Part / main section divider: white all-caps on an IOM-blue band.
// Gill Sans Nova Light, 20/22 pt, centred, white over IOM blue.
#let iom-part(title) = {
  pagebreak(weak: true)
  block(
    width: 100%,
    fill: iom-blue,
    inset: (x: 12pt, y: 8pt),
    above: 0pt,
    below: 1.5em,
    text(font: iom-font, weight: 300, size: 20pt, fill: white, upper(title)),
  )
}

// Source: / Note: lines beneath figures, tables and maps.
// Gill Sans Nova Book Italic, 8/9.6 pt. The label is italic; the text after
// the colon is not (Layout Manual, p. 16).
#let iom-source(body) = block(above: 0.6em, below: 1em)[
  #text(size: 8pt)[#emph[Source:] #h(0.3em) #body]
]
#let iom-note(body) = block(above: 0.3em, below: 1em)[
  #text(size: 8pt)[#emph[Note:] #h(0.3em) #body]
]

// The standard map disclaimer (Layout Manual, p. 19). Required under every
// map in an official IOM document.
#let iom-map-disclaimer(organization: "International Organization for Migration") = iom-note[
  This map is for illustration purposes only. The boundaries and names shown
  and the designations used on this map do not imply official endorsement or
  acceptance by the #organization.
]

// Standard disclaimer / imprint page (Layout Manual, p. 13).
#let iom-imprint(
  publisher-address: none,
  donor: none,
  required-citation: none,
  cover-photo: none,
  isbn-pdf: none,
  isbn-print: none,
  issn: none,
  copyright-year: none,
  pub-reference: none,
  unedited: false,
  unapproved: false,
  unendorsed: false,
  confidential: false,
) = {
  set text(size: 8.5pt)
  set par(justify: true, leading: 0.5em)
  let rule = line(length: 30%, stroke: 0.5pt + black)

  [
    The opinions expressed in this publication are those of the authors and do
    not necessarily reflect the views of the International Organization for
    Migration (IOM). The designations employed and the presentation of material
    throughout the publication do not imply expression of any opinion whatsoever
    on the part of IOM concerning the legal status of any country, territory,
    city or area, or of its authorities, or concerning its frontiers or
    boundaries.

    IOM is committed to the principle that humane and orderly migration benefits
    migrants and society. As an intergovernmental organization, IOM acts with its
    partners in the international community to: assist in meeting the operational
    challenges of migration; advance understanding of migration issues; encourage
    social and economic development through migration; and uphold the human
    dignity and well-being of migrants.
  ]

  v(0.5em); rule; v(0.5em)

  if donor != none [
    This publication was made possible through support provided by #donor.
    The opinions expressed herein are those of the author and do not necessarily
    reflect the views of #donor.

  ]

  if publisher-address != none {
    grid(
      columns: (auto, 1fr), column-gutter: 1em,
      [Publisher:], publisher-address,
    )
    v(0.5em)
  }

  if unedited [This publication was issued without formal editing by IOM. This publication was issued without IOM Publications Unit (PUB) approval for adherence to IOM’s brand and style standards. This publication was issued without IOM Research Unit (RES) endorsement.\ ]
  if unapproved [
    This publication was issued without IOM Publications Unit (PUB) approval for
    adherence to IOM's brand and style standards.\
  ]
  if unendorsed [
    This publication was issued without IOM Research Unit (RES) endorsement.\
  ]

  if cover-photo != none {
    v(0.5em)
    grid(columns: (auto, 1fr), column-gutter: 1em, [Cover photo:], cover-photo)
  }
  if required-citation != none {
    v(0.5em)
    grid(columns: (auto, 1fr), column-gutter: 1em, [Required citation:], required-citation)
  }

  v(0.5em); rule; v(0.5em)

  if isbn-pdf != none [ISBN #isbn-pdf (PDF)\ ]
  if isbn-print != none [ISBN #isbn-print (print)\ ]
  if issn != none [ISSN #issn\ ]

  if copyright-year != none [
    #v(0.5em)
    #text(weight: "bold")[© IOM #copyright-year]
  ]

  // CC BY-NC-ND 3.0 IGO badge, shipped alongside this partial. Partials are
  // concatenated into the .typ next to the input, so the path is relative to
  // the document, not to this file — it assumes the standard layout with
  // `_extensions/` beside the .qmd.
  // Suppressed when `confidential: true` is set in the YAML header, for
  // documents distributed under restricted terms rather than CC licensing.
  if not confidential {
    block(above: 0.6em, below: 0.2em)[
      #link("https://creativecommons.org/licenses/by-nc-nd/3.0/igo/")[
        #image(
          "_extensions/iom-report/cc-by-nc-nd-3.0-igo.svg",
          width: 2.5cm,
          alt: "CC BY-NC-ND 3.0 IGO",
        )
      ]
    ]

    [
      #v(0.5em)
      Some rights reserved. This work is made available under the Creative Commons
      Attribution-NonCommercial-NoDerivs 3.0 IGO License (CC BY-NC-ND 3.0 IGO).

      This publication should not be used, published or redistributed for purposes
      primarily intended for or directed towards commercial advantage or monetary
      compensation, with the exception of educational purposes, e.g. to be included
      in textbooks.

      Permissions: Requests for commercial use or further rights and licensing
      should be submitted to publications\@iom.int.
    ]
  }

  if pub-reference != none {
    place(bottom, text(size: 6.5pt, fill: luma(40%), pub-reference))
  }
}

// Switch from roman front-matter numbering to arabic body numbering.
// Call `#iom-mainmatter()` in a raw typst block at the start of Chapter 1
// (Layout Manual, "Pagination", p. 9).
#let iom-mainmatter() = {
  pagebreak(weak: true, to: "odd")
  counter(page).update(1)
  set page(numbering: "1")
  []
}

// ===========================================================================
// The document wrapper. `typst-show.typ` calls this with YAML metadata.
// ===========================================================================
#let iom-report(
  title: none,
  subtitle: none,
  authors: none,
  date: none,
  running-title: none,
  keywords: (),
  lang: "en",
  region: "GB",
  fontsize: 11pt,
  cover-image: none,
  cover-colour: iom-blue,
  logo-left: none,
  logo-right: none,
  logo-height: 0.9cm,
  publisher-address: none,
  donor: none,
  required-citation: none,
  cover-photo: none,
  isbn-pdf: none,
  isbn-print: none,
  issn: none,
  copyright-year: none,
  pub-reference: none,
  unedited: false,
  unapproved: false,
  unendorsed: false,
  confidential: false,
  sectionnumbering: none,
  toc: false,
  toc_title: "CONTENTS",
  toc_depth: 3,
  toc_indent: 1.2em,
  doc,
) = {
  set document(title: title, keywords: keywords)

  // --- Body text: Gill Sans Nova Book, 11/13-14 pt, justified, no hyphens --
  set text(
    font: iom-font,
    size: fontsize,
    lang: lang,
    region: region,
    hyphenate: false,        // "Don't use hyphenation" (Layout Manual, p. 17)
    fill: black,
  )
  set par(justify: true, leading: 0.55em, spacing: 1.5em)

  // --- Headings ----------------------------------------------------------
  // Markdown level -> Layout Manual level:
  //   #      -> CHAPTER          17/20 pt semibold, centred, all caps, blue
  //   ##     -> HEADING 1        12 pt, left, all caps, blue
  //   ###    -> Heading 2        12 pt, left, sentence case, blue
  //   ####   -> Subheading 3     12 pt, left, black
  //   #####  -> Subheading 4     12 pt italic, left, black
  // MAIN SECTION HEADING is a part divider: use #iom-part[...] instead.
  set heading(numbering: sectionnumbering)
  show heading: set block(sticky: true)   // never orphan a heading
  show heading: set text(font: iom-font, hyphenate: false)

  // Heading number, or nothing when numbering is off or the heading is
  // {.unnumbered}. Uses the location form; counter.display is deprecated.
  let heading-number(it) = if it.numbering != none {
    numbering(it.numbering, ..counter(heading).at(it.location()))
    h(0.6em)
  }

  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    block(width: 100%, above: 0pt, below: 2em)[
      #set align(center)
      #set par(leading: 0.3em)
      #text(size: 17pt, weight: "semibold", fill: iom-blue)[
        #heading-number(it)#upper(it.body)
      ]
    ]
  }
  show heading.where(level: 2): it => block(above: 1.6em, below: 0.9em)[
    #text(size: 12pt, weight: "regular", fill: iom-blue)[
      #heading-number(it)#upper(it.body)
    ]
  ]
  show heading.where(level: 3): it => block(above: 1.4em, below: 0.9em)[
    #text(size: 12pt, weight: "regular", fill: iom-blue)[
      #heading-number(it)#it.body
    ]
  ]
  show heading.where(level: 4): it => block(above: 1.2em, below: 0.9em)[
    #text(size: 12pt, weight: "regular", fill: black)[
      #heading-number(it)#it.body
    ]
  ]
  show heading.where(level: 5): it => block(above: 1.2em, below: 0pt)[
    #text(size: 12pt, style: "italic", fill: black)[
      #heading-number(it)#it.body
    ]
  ]

  // --- Links -------------------------------------------------------------
  // "Make URL / hyperlink in colour and clickable" (Layout Manual, p. 17)
  show link: set text(fill: iom-un-blue)

  // --- Footnotes: 7/8.4 pt ------------------------------------------------
  show footnote.entry: set text(size: 7pt)
  set footnote.entry(separator: line(length: 30%, stroke: 0.5pt + luma(60%)))

  // --- Figures and tables -------------------------------------------------
  // Caption above, bold, no terminal full stop, full stop between the number
  // and the title: "Figure 1. Title" (House Style Manual, p. 46).
  set figure.caption(separator: [. ], position: top)
  show figure.caption: it => block(width: 100%)[
    #set align(center)
    #text(size: 11pt, weight: "bold", fill: iom-blue)[#it]
  ]

  // Table header: bold, centred, white on IOM blue. No vertical rules.
  set table(
    inset: 6pt,
    stroke: (x, y) => (
      top: if y == 0 { none } else { 0.5pt + luma(75%) },
      bottom: 0.5pt + luma(75%),
    ),
    fill: (x, y) => if y == 0 { iom-blue },
  )
  show table.cell.where(y: 0): set text(fill: white, weight: "bold")
  show table.cell.where(y: 0): set align(center)

  // --- Cover page ---------------------------------------------------------
  if title != none {
    set page(
      header: none,
      footer: none,
      numbering: none,
      margin: 0cm,
      fill: if cover-image == none { cover-colour } else { none },
    )
    if cover-image != none {
      place(top + left, image(cover-image, width: 100%, height: 100%, fit: "cover"))
    }
    block(width: 100%, height: 100%)[
      #set text(fill: white)
      #place(top + left, dx: 2.54cm, dy: 6cm)[
        #block(width: 13cm)[
          #set par(leading: 0.4em, justify: false)
          #text(size: 26pt, weight: "semibold", upper(title))
          #if subtitle != none [
            #v(0.6em)
            #text(size: 14pt, weight: "regular", style: "italic", subtitle)
          ]
        ]
      ]
      // Logos sit at least 1.27 cm from the bottom edge (Layout Manual,
      // "Logo placement", p. 5). A single logo is centred at the manual's
      // 3.97 cm width; a pair (IOM left, donor/partner right) is aligned to
      // the text margin and sized to a common height, so logos of differing
      // aspect ratios still balance optically.
      #if logo-left != none and logo-right != none {
        place(bottom + left, dx: 2.54cm, dy: -1.6cm, image(logo-left, height: logo-height))
        place(bottom + right, dx: -2.54cm, dy: -1.6cm, image(logo-right, height: logo-height))
      } else if logo-left != none {
        place(bottom + center, dy: -1.6cm, image(logo-left, width: 3.97cm))
      } else if logo-right != none {
        place(bottom + center, dy: -1.6cm, image(logo-right, height: logo-height))
      }
    ]
    pagebreak(weak: true)
  }

  // --- Inside front cover: disclaimer / imprint ---------------------------
  set page(numbering: "1", footer: iom-footer(running-title: running-title))
  counter(page).update(1)

  iom-imprint(
    publisher-address: publisher-address,
    donor: donor,
    required-citation: required-citation,
    cover-photo: cover-photo,
    isbn-pdf: isbn-pdf,
    isbn-print: isbn-print,
    issn: issn,
    copyright-year: copyright-year,
    pub-reference: pub-reference,
    unedited: unedited,
    unapproved: unapproved,
    unendorsed: unendorsed,
    confidential: confidential,
  )

  // --- Title page ---------------------------------------------------------
  pagebreak(weak: true)
  block(width: 100%, above: 4cm)[
    #set align(left)
    #set par(leading: 0.4em, justify: false)
    #text(size: 26pt, weight: "bold", fill: black, title)
    #if subtitle != none [
      #v(0.4em)
      #line(length: 40%, stroke: 1pt + black)
      #v(0.4em)
      #text(size: 15pt, weight: "regular", subtitle)
    ]
    #if authors != none and authors != () [
      #v(3em)
      #set text(size: 9pt)
      #for a in authors [#a.name \ ]
    ]
    #if date != none [ #v(1em) #text(size: 10pt, date) ]
  ]

  // --- Contents -----------------------------------------------------------
  if toc {
    pagebreak(weak: true)
    block(width: 100%, fill: iom-blue, inset: (x: 12pt, y: 8pt), below: 1.5em)[
      #text(font: iom-font, weight: 300, size: 20pt, fill: white, toc_title)
    ]
    show outline.entry.where(level: 1): set text(weight: "bold", fill: iom-blue)
    outline(title: none, depth: toc_depth, indent: toc_indent)
  }

  doc
}
