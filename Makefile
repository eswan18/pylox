test:
	python -m unittest tests/test_scripts.py

lint:
	python -m flake8 src

typecheck:
	python -m mypy src
