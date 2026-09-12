MAIN = tz_shortcuter
LATEX = pdflatex
BIBTEX = bibtex
FLAGS = -interaction=nonstopmode -halt-on-error

SOURCES = $(wildcard *.tex)
STY_FILES = tz_style.sty

.PHONY: all clean

all: $(MAIN).pdf

$(MAIN).pdf: $(SOURCES) $(STY_FILES)
	$(LATEX) $(FLAGS) $(MAIN).tex
	$(LATEX) $(FLAGS) $(MAIN).tex

clean:
	rm -f *.aux *.log *.out *.toc *.pdf *.bbl *.blg *.run.xml *.bcf *.fdb_latexmk *.fls *.synctex.gz
