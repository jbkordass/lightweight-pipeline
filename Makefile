.PHONY: all clean-pyc clean-so clean-build clean-ctags clean-cache clean-e clean inplace test ruff-check ruff-format pep build-doc dist-build

all: clean inplace pep test build-doc dist-build

clean-pyc:
	find . -name "*.pyc" | xargs rm -f

clean-so:
	find . -name "*.so" | xargs rm -f
	find . -name "*.pyd" | xargs rm -f

clean-build:
	rm -rf _build

clean-ctags:
	rm -f tags

clean-cache:
	find . -name "__pycache__" | xargs rm -rf

clean-e:
	find . -name "*-e" | xargs rm -rf

clean: clean-build clean-pyc clean-so clean-ctags clean-cache clean-e

inplace:
	@python -m pip install -e ".[dev]"

test:
	@echo "Running tests"
	@python -m pytest . \
		--verbose \
	--ignore examples

ruff-format:
	@echo "Running ruff format"
	@ruff format lw_pipeline/
	@ruff format examples/ --exclude="*/doc/*,examples/trivial/*"

ruff-check:
	@echo "Running ruff check"
	@ruff check lw_pipeline/
	@ruff check examples/ --exclude="*/doc/*,examples/trivial/*"

pep: ruff-check ruff-format

build-doc:
	@echo "Building documentation"
	make -C doc/ clean
	make -C doc/ html
	cd doc/ && make view
