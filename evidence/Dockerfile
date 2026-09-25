# Evidence OSS (MIT). NOTE: Evidence's main template moved to the commercial "Evidence Studio"
# CLI in 2026. The open-source framework lives on the template's `legacy` branch.
# Pinned to an exact commit + its package-lock.json so the build is reproducible.
FROM node:22-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ARG EVIDENCE_TEMPLATE_SHA=4b13d42e157bf0a5218ba8927912abe3f8f1c248
RUN git init -q . \
 && git remote add origin https://github.com/evidence-dev/template.git \
 && git fetch -q --depth 1 origin ${EVIDENCE_TEMPLATE_SHA} \
 && git checkout -q FETCH_HEAD \
 && rm -rf .git .devcontainer sources/needful_things pages/index.md

RUN npm ci --no-audit --no-fund

COPY sources ./sources
COPY pages ./pages

EXPOSE 3000
# `npm run sources` pulls data from Postgres. It fails harmlessly before the first
# Dagster run; after that, `make evidence-refresh` re-pulls.
CMD ["sh", "-c", "npm run sources || echo '>>> No data yet. Run the Dagster job, then: make evidence-refresh'; npm run dev -- --host 0.0.0.0 --port 3000"]
