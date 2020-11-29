include Make.rules

format:
	$(ACTIVATE) isort .
	$(ACTIVATE) black .

develop:
	virtualenv --clear .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.dev.txt
	$(PIP) install --editable .

test:
	$(ACTIVATE) tox

shell:
	$(ACTIVATE) /bin/bash

.PHONY: format test shell
