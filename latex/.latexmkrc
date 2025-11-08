$out_dir = '_build';
$aux_dir = '_build';
$pdflatex = 'pdflatex -interaction=nonstopmode -file-line-error %O %S';
$bibtex   = 'biber %O %B';
$pdf_previewer = 'open';
@generated_exts = qw(aux bbl bcf blg fdb_latexmk fls log out run.xml synctex.gz toc lof lot);