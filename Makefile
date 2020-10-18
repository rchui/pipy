include Make.rules

fmt:
	isort .
	black .

develop:
	virtualenv --clear .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.dev.txt
	$(PIP) install --editable .

test:
	@tox

shell:
	$(ACTIVATE) /bin/zsh

.PHONY: fmt test shell
