# Control Centre - one command to regenerate everything.
#
#   make            extract -> bootstrap -> build
#   make check      validate everything waiting in intake/drop/
#   make ingest     validate + merge everything in intake/drop/, then rebuild
#   make measure    re-measure the workspace only
#   make serve      serve the site on :8080

PY ?= python3

.PHONY: all measure bootstrap build check test ingest serve clean

# `all` runs the selftest first. A red selftest means a validation rule is
# either too loose or too strict, and nothing downstream can be trusted.
all: test measure bootstrap build

test:
	$(PY) tools/selftest.py

measure:
	$(PY) tools/extract_state.py

bootstrap:
	$(PY) tools/bootstrap.py

build:
	$(PY) tools/build.py

check:
	$(PY) tools/validate.py --all

ingest:
	$(PY) tools/ingest.py --all
	$(PY) tools/bootstrap.py
	$(PY) tools/build.py

serve: all
	$(PY) -m http.server 8080 --bind 0.0.0.0

clean:
	rm -rf tools/__pycache__
