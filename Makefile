.PHONY: backend-test frontend-lint frontend-build docker-build docker-up docker-down docker-logs

backend-test:
	cd backend && .venv/bin/python -m pytest -m "not integration"

frontend-lint:
	cd frontend && npm run lint

frontend-build:
	cd frontend && npm run build

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

test: backend-test frontend-lint frontend-build