# ACL SRW / arXiv Submission Package

## Files
- `main.tex` — LaTeX paper (ACL format, double-blind, ~4 pages)
- `references.bib` — BibTeX bibliography
- `acl.sty` / `acl_natbib.bst` — ACL style files from acl-org/acl-style-files

## Compilation
```bash
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
Or use Overleaf: https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj

## Target Venues
- **arXiv preprint**: category cs.CL or cs.AI. No deadline. Change `[review]{acl}` to `[preprint]{acl}` and add author info.
- **ACL-style SRW**: Keep `[review]{acl}` (double-blind). Next cycle: EMNLP 2026 SRW or AACL-IJCNLP 2026 SRW.
