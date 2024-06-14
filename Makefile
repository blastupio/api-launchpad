makemigrations:
	PYTHONPATH=. alembic revision -m "${m}" --autogenerate

migrate:
	PYTHONPATH=. alembic upgrade head

downgrade:
	PYTHONPATH=. alembic downgrade head-1

dev:
	uvicorn main:app --host 0.0.0.0 --port 80 --reload

up:
	docker compose up -d --build
