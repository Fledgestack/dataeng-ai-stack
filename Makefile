# Run from WSL/Linux. If `make` is missing: sudo apt install make
SHELL := /bin/bash
DC := docker compose

.PHONY: init up run evidence-refresh status logs kill pause resume down nuke digests

init: ## First-time setup: create .env with a random password
	@test -f .env && echo ".env exists, leaving it alone" || \
	  (sed "s/CHANGE_ME_long_random_string/$$(openssl rand -hex 24)/" .env.example > .env && echo "Created .env")

up: ## Build and start everything
	$(DC) up -d --build
	@echo "Dagster   -> http://localhost:3000"
	@echo "Evidence  -> http://localhost:3001"
	@echo "Metabase  -> http://localhost:3002  (first boot takes ~1 min)"

run: ## Run the full pipeline once, right now (ingest -> transform -> publish)
	$(DC) exec dagster-webserver dagster job execute -m stack.definitions -j full_refresh

evidence-refresh: ## Re-pull data into Evidence after a pipeline run
	$(DC) restart evidence

status:
	$(DC) ps

logs:
	$(DC) logs -f --tail=100

# ---- Kill switches -------------------------------------------------------
kill: ## HARD STOP: kills schedules and any in-flight run. BI stays up.
	$(DC) stop dagster-daemon dagster-webserver
	@echo "Pipeline stopped. Data and dashboards untouched. Restart with: make up"

pause: ## SOFT STOP: containers stay up, every run fails fast at the guard
	sed -i "s/^PIPELINE_ENABLED=.*/PIPELINE_ENABLED=false/" .env
	$(DC) up -d dagster-webserver dagster-daemon
	@echo "PIPELINE_ENABLED=false. Runs will refuse to start."

resume:
	sed -i "s/^PIPELINE_ENABLED=.*/PIPELINE_ENABLED=true/" .env
	$(DC) up -d dagster-webserver dagster-daemon

down: ## Stop everything, keep data
	$(DC) down

nuke: ## Stop everything AND delete all data volumes
	@read -p "Delete ALL data volumes? Type yes: " ans && [ "$$ans" = "yes" ] && $(DC) down -v

# ---- Supply chain ---------------------------------------------------------
digests: ## Print the exact image digests you are running (pin these for true immutability)
	@for img in $$($(DC) config --images | sort -u); do \
	  docker image inspect --format "{{index .RepoDigests 0}}" $$img 2>/dev/null || echo "$$img (local build, no registry digest)"; \
	done
