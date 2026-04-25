PYTHON ?= python

.PHONY: analyze-benchmarks benchmark check-images check-prompts generate-images generate-prompts test

generate-images:
	$(PYTHON) -m bench.render_synthetic_images

check-images:
	$(PYTHON) -m bench.render_synthetic_images --check

analyze-benchmarks:
	$(PYTHON) -m bench.analyze_reports --write-default-output

generate-prompts:
	$(PYTHON) -m bench.render_synthetic_images
	$(PYTHON) -m bench.build_prompt_set

check-prompts:
	$(PYTHON) -m bench.render_synthetic_images --check
	$(PYTHON) -m bench.build_prompt_set --check

benchmark:
	$(PYTHON) -m bench.run_ollama_benchmark --help

test:
	$(PYTHON) -m pytest tests
