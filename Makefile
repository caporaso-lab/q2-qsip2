.PHONY: all lint test install dev clean distclean

PYTHON ?= python

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

REPO = jeffkimbrel/qSIP2
HASH = af7e19757ae73c837507bbd672054bb9fdee74d5
install: all
	pip install .
	Rscript -e 'remotes::install_github("$(REPO)", ref="$(HASH)", auth_token = NULL)'

dev: all
	pip install -e .

clean: distclean

distclean: ;
