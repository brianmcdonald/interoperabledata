// ===========================================================================
// IOM report template  ·  page.typ
//
// Quarto emits this partial at the top level, BEFORE the show rule in
// typst-show.typ, so these rules apply to the whole document. Functions
// defined in typst-template.typ are already in scope here, because
// template.typ includes that partial first.
//
// Requires Quarto >= 1.8, which is when page.typ became overridable.
// On earlier versions, move this `set page` call inside iom-report().
// ===========================================================================

#set page(
  // A4 is the standard size for reports, manuals, studies and journals
  // (Layout Manual, "Size of publication", p. 7). For the book format
  // (17 x 24 cm) use: width: 17cm, height: 24cm.
$if(papersize)$
  paper: "$papersize$",
$else$
  paper: "a4",
$endif$

  // "Inside margins must be wider than the other sides", at least 2.54 cm
  // inside and 1.27 cm elsewhere (Layout Manual, "Margins and columns", p. 11).
  // Typst's `inside`/`outside` keys are binding-aware, so verso and recto
  // pages mirror automatically.
$if(margin)$
  margin: ($for(margin/pairs)$$margin.key$: $margin.value$,$endfor$),
$else$
  margin: (inside: 2.54cm, outside: 2cm, top: 2cm, bottom: 2.2cm),
$endif$
  binding: left,

$if(columns)$
  columns: $columns$,
$endif$

  // Arabic page numbers throughout (no roman front matter). To restore the
  // Layout Manual convention, use "i" here and call #iom-mainmatter() at the
  // start of Chapter 1 (Layout Manual, "Pagination", p. 9).
  numbering: "1",
  footer: iom-footer(running-title: [$if(running-title)$$running-title$$else$$title$$endif$]),
  footer-descent: 0.8cm,
)
