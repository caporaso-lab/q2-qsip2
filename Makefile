.PHONY: all lint test install dev clean distclean

PYTHON ?= python

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

REPO = jeffkimbrel/qSIP2
HASH = b867c96aa7b72b72f47942f11dbcd18319cae8bc
install: all
	pip install .
	Rscript -e 'devtools::install_github("$(REPO)", ref="$(HASH)")'

dev: all
	pip install -e .

clean: distclean

distclean: ;
