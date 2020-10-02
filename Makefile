fmt:
	isort .
	black .

test:
	@tox

shell:
	$(ACTIVATE) $(MAKESHELL)

.PHONY: fmt test shell
