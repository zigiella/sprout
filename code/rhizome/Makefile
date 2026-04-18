PYTHON ?= python

.PHONY: benchmark check-prompts generate-prompts test

generate-prompts:
	$(PYTHON) -m bench.build_prompt_set

check-prompts:
	$(PYTHON) -m bench.build_prompt_set --check

benchmark:
	$(PYTHON) -m bench.run_ollama_benchmark --help

test:
	$(PYTHON) -m pytest tests
