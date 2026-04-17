PYTHON ?= python

.PHONY: check-examples generate-examples test-schemas

check-examples:
	$(PYTHON) schemas/examples/generate_examples.py --check

generate-examples:
	$(PYTHON) schemas/examples/generate_examples.py

test-schemas:
	$(PYTHON) -m pytest schemas/tests
