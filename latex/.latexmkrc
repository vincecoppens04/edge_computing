# =====================================================
# latexmk configuration for BibTeX (no biber)
# =====================================================

# Keep all auxiliary/output files in _build
$aux_dir = '_build';
$out_dir = '_build';

# Use BibTeX instead of biber
$bibtex_use = 1;

# LaTeX build commands
$pdflatex = 'pdflatex -interaction=nonstopmode -file-line-error %O %S';
$pdf_previewer = 'open';

# Clean-up extensions
@generated_exts = qw(aux bbl blg fdb_latexmk fls log out synctex.gz toc lof lot);

# No biber dependencies
# (old biber lines removed entirely)