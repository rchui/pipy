include Make.rules

format:
	$(ACTIVATE) isort .
	$(ACTIVATE) black .

env:
	virtualenv --clear .venv
	$(PIP) install --upgrade pip
	$(PIP) install --use-feature=2020-resolver --requirement requirements.dev.txt
	$(PIP) install --use-feature=2020-resolver --editable .

test:
	$(ACTIVATE) tox

shell:
	$(ACTIVATE) /bin/bash

.PHONY: format test shell
