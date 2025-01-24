.PHONY: help init run test

init: ## 初期化
	uv sync

run: ## 実行
	uv run time python3 -m mojxml testdata/15222-1107-1553.xml

test: ## テスト
	uv run pytest -v --cov --cov-report xml --cov-report html --cov-report term
