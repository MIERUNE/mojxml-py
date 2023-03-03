.PHONY: help init run test

init: ## 初期化
	poetry install
	pre-commit install

run: ## 実行
	poetry run time python3 -m mojxml testdata/15222-1107-1553.xml

test: ## テスト
	poetry run pytest -v --cov --cov-report xml --cov-report html --cov-report term