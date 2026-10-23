.PHONY: help install test test-unit test-sec test-ai lint run

help:
	@echo "Protection des Objets Connectes Medicaux (IoMT)"
	@echo "make install    : Installer les dependances"
	@echo "make test       : Lancer tous les tests avec couverture"
	@echo "make test-unit  : Lancer les tests unitaires"
	@echo "make test-sec   : Lancer les tests de securite IoMT"
	@echo "make test-ai    : Lancer les tests de detection d'anomalies IA"
	@echo "make run        : Demarrer l'Edge Gateway API"

install:
	pip install -r requirements/test.txt

test:
	pytest --cov=src --cov-report=term-missing

test-unit:
	pytest tests/unit -v

test-sec:
	pytest tests/security -v

test-ai:
	pytest tests/ai -v

lint:
	ruff check src tests

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
