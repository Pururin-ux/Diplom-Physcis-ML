# Thesis Scaffold

This folder contains a compilable LaTeX scaffold for the BGU physics diploma.
It is not the final thesis text. The chapter files contain structure, equations,
figure placeholders, and TODO notes that must be completed and checked manually.

## Build

Preferred build:

```bash
latexmk -xelatex thesis.tex
```

If `biblatex`/`biber` requires a separate pass:

```bash
biber thesis
latexmk -xelatex thesis.tex
```

Or use:

```bash
make pdf
```

Clean generated files:

```bash
make clean
```

## Required Tools

The scaffold is intended for XeLaTeX with `latexmk`, `biblatex`, and `biber`.
On Linux, a typical installation command is:

```bash
sudo apt-get update
sudo apt-get install -y texlive-xetex texlive-lang-cyrillic texlive-science texlive-latex-extra latexmk biber
```

If `sudo` is unavailable, install the equivalent packages through the local
system package manager or compile on a machine with a full TeX distribution.

## Manual Work Still Required

- Fill title-page personal and supervisor information.
- Verify department-specific formatting rules.
- Write and proofread the Belarusian, Russian, and English abstracts.
- Replace TODO blocks with final thesis text.
- Verify all bibliography metadata and DOIs.
- Decide whether to copy final figures into `thesis/figures/` or reference
  generated report figures from `../reports/assets/`.
- Re-check every scientific claim against the final notebooks and reports.
