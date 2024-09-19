.PHONY: all lint test install dev clean distclean

PYTHON ?= python

all: ;

lint:
	q2lint
	flake8

test: all
	py.test

install: all
	pip install .
	conda install --yes r-devtools r-svglite r-gt rpy2 -c r
	Rscript -e 'install.packages("S7", repos="https://cloud.r-project.org")'
	# TODO: don't just install HEAD
	Rscript -e 'devtools::install_github("jeffkimbrel/qSIP2")'

dev: all
	pip install -e .

clean: distclean

distclean: ;
