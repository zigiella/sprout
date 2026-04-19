PYTHON ?= python

.PHONY: e2e e2e-smoke test

e2e:
	$(PYTHON) -m src.cross_node_e2e --help

e2e-smoke:
	$(PYTHON) -m src.cross_node_e2e --model gemma4:e4b --scenario pollen_fresh_weather_review

test:
	$(PYTHON) -m pytest tests
