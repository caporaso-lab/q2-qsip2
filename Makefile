.PHONY: all lint test install dev clean distclean

PYTHON ?= python

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

REPO = jeffkimbrel/qSIP2
HASH = fee266bb14836f7a6c45ef9ef11d451999936a3a
install: all
	pip install .
	conda install --yes r-devtools r-svglite r-gt rpy2 -c r
	Rscript -e 'install.packages("S7", repos="https://cloud.r-project.org")'
	Rscript -e 'devtools::install_github("$(REPO)", ref="$(HASH)")'

dev: all
	pip install -e .

clean: distclean

distclean: ;
