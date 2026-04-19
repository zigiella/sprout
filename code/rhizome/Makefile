PYTHON ?= python

.PHONY: benchmark check-prompts generate-prompts test test-firmware demo-firmware

generate-prompts:
	$(PYTHON) -m bench.build_prompt_set

check-prompts:
	$(PYTHON) -m bench.build_prompt_set --check

benchmark:
	$(PYTHON) -m bench.run_ollama_benchmark --help

test:
	$(PYTHON) -m pytest tests

test-firmware:
	$(PYTHON) -m pytest tests/firmware

demo-firmware:
	$(PYTHON) -m tests.firmware.mock_esp32 --scenario low_tank_block
