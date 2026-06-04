.PHONY: backend frontend test docker-up docker-down k8s-dry-run mcp

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest
	cd frontend && npm test

docker-up:
	docker compose up --build

docker-down:
	docker compose down

k8s-dry-run:
	kubectl kustomize infra/k8s

mcp:
	cd backend && python -m app.mcp_server.server
