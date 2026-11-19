.PHONY: dev down logs migrate seed test test-backend test-frontend test-e2e lint prod prod-down

dev:
	cp -n .env.development.example .env || true
	docker compose -f docker-compose.dev.yml up --build

down:
	docker compose -f docker-compose.dev.yml down

logs:
	docker compose -f docker-compose.dev.yml logs -f --tail=100

migrate:
	docker compose -f docker-compose.dev.yml exec api alembic upgrade head

seed:
	docker compose -f docker-compose.dev.yml exec api python -m app.seed

test: test-backend test-frontend

test-backend:
	cd backend && python -m pytest -q

test-frontend:
	cd frontend && npm run test:unit

test-e2e:
	cd frontend && npm run test:e2e

prod:
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.prod.yml down
