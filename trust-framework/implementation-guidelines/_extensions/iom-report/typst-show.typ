// ===========================================================================
// IOM report template  ·  typst-show.typ
//
// This is a Pandoc template, not plain Typst. The placeholders below are
// substituted by Pandoc with values from the document's YAML header before
// Typst ever sees the file. It emits a single show rule that pipes the whole
// document body into iom-report() as the `doc` argument.
//
// Each conditional block below corresponds to a key you can set in YAML.
//
// CAUTION: Pandoc parses this entire file as a template, comments included.
// A literal dollar sign anywhere -- even inside a comment -- is read as
// template syntax and will fail the render. Write $$ if you need one.
// ===========================================================================

#show: doc => iom-report(
$if(title)$
  title: [$title$],
$endif$
$if(subtitle)$
  subtitle: [$subtitle$],
$endif$
$if(by-author)$
  authors: (
$for(by-author)$
    ( name: [$it.name.literal$] ),
$endfor$
  ),
$endif$
$if(date)$
  date: [$date$],
$endif$
$if(keywords)$
  keywords: ($for(keywords)$"$it$",$endfor$),
$endif$
$if(lang)$
  lang: "$lang$",
$endif$
$if(region)$
  region: "$region$",
$endif$
$if(fontsize)$
  fontsize: $fontsize$,
$endif$
$if(section-numbering)$
  sectionnumbering: "$section-numbering$",
$endif$
$if(toc)$
  toc: $toc$,
$endif$
$if(toc-title)$
  toc_title: [$toc-title$],
$endif$
$if(toc-depth)$
  toc_depth: $toc-depth$,
$endif$

  // ---- IOM-specific keys -------------------------------------------------
  // These are arbitrary YAML keys; Pandoc makes any top-level key available
  // to the template, which is how you extend the metadata surface.
  //
  // CAUTION: avoid keys Quarto already reserves for the typst format --
  // logo, margin, papersize, columns, keywords, toc. Quarto rewrites those
  // into its own structures before the template sees them, so a plain path
  // in `logo` arrives as an object, not a string. Hence `cover-logo-left`
  // and `cover-logo-right` here.
$if(running-title)$
  running-title: [$running-title$],
$endif$
$if(cover-image)$
  cover-image: "$cover-image$",
$endif$
$if(cover-logo-left)$
  logo-left: "$cover-logo-left$",
$endif$
$if(cover-logo-right)$
  logo-right: "$cover-logo-right$",
$endif$
$if(cover-logo-height)$
  logo-height: $cover-logo-height$,
$endif$
$if(publisher-address)$
  publisher-address: [$publisher-address$],
$endif$
$if(donor)$
  donor: [$donor$],
$endif$
$if(required-citation)$
  required-citation: [$required-citation$],
$endif$
$if(cover-photo)$
  cover-photo: [$cover-photo$],
$endif$
$if(isbn-pdf)$
  isbn-pdf: [$isbn-pdf$],
$endif$
$if(isbn-print)$
  isbn-print: [$isbn-print$],
$endif$
$if(issn)$
  issn: [$issn$],
$endif$
$if(copyright-year)$
  copyright-year: [$copyright-year$],
$endif$
$if(pub-reference)$
  pub-reference: [$pub-reference$],
$endif$
$if(unedited)$
  unedited: true,
$endif$
$if(unapproved)$
  unapproved: true,
$endif$
$if(unendorsed)$
  unendorsed: true,
$endif$
$if(confidential)$
  confidential: true,
$endif$
  doc,
)
