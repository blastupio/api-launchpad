include .env
export


dev:
	uvicorn main:socket_app --host 0.0.0.0 --port 80 --reload

up:
	docker compose up --build