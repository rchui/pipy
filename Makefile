fmt:
	isort .
	black .

develop:
	virtualenv --clear .venv
	. .venv/bin/activate && python -m pip install --editable .
	. .venv/bin/activate && python -m pip install -r requirements.dev.txt

test:
	@tox

shell:
	$(ACTIVATE) $(MAKESHELL)

.PHONY: fmt test shell
