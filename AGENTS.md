# Repository Guidelines

## Project Structure & Module Organization
Source code is grouped by platform: `web/` (Vite + React), `mobile/` (React Native CLI), and `backend/` (FastAPI) with cross-cutting helpers in `shared/`. The backend follows Clean Architecture—domain rules in `app/domain`, orchestration in `app/application`, gateways in `app/infrastructure`, and API adapters in `app/presentation`. Tests live in each platform’s `tests` or `src/__tests__/` folders, while automation artefacts stay in `n8n/`, `supabase/`, `scripts/`, and human-readable docs under `docs/`.

## Build, Test, and Development Commands
`make start` builds and boots the full stack with Docker; `make stop`, `make restart`, and `make logs-*` manage running services. For local-only iterations run `npm run dev` inside `web/`, `npm run ios|android` or `npm run start` inside `mobile/`, and `uvicorn main:app --reload` inside `backend/`. Lint and unit suites run via `npm run lint` or `npm run test` on the JavaScript apps, and `pytest` or `make test` (containerised) for the API.

## Coding Style & Naming Conventions
Respect the TypeScript ESLint rules in `web/`; prefer functional components, PascalCase for components, camelCase utilities, and Tailwind utility classes for styling. Mobile code inherits the React Native ESLint/Prettier bundle—keep two-space indentation, avoid default exports for screens, and colocate styles next to the component. Python modules remain PEP 8 compliant with 4-space indentation, snake_case identifiers, and exhaustive type hints; align FastAPI schemas with their DTOs in `app/presentation`.

## Testing Guidelines
`backend/pytest.ini` enforces `test_*.py` discovery, marker discipline, and an 80% coverage floor—run `pytest` locally and ensure HTML/XML reports stay updated when touching pipelines. Web tests reside in `web/src/__tests__/` and run through `npm run test` (Vitest) or `npm run test:ui` for exploratory sessions; name files `*.test.tsx`. Mobile uses Jest with Testing Library; `npm run test` targets `*.test.ts(x)` under `mobile/src/__tests__/`, and Detox scenarios belong under `mobile/e2e` when added.

## Commit & Pull Request Guidelines
History uses Conventional Commits (`feat(testing): ...`), so keep the `<type>(scope): imperative summary` pattern for traceability. PRs should link issues, summarise platform impacts, attach screenshots or command output for verification, and flag configuration changes (environment files, Supabase migrations) so reviewers can reproduce the setup. Request reviewers from each affected platform whenever work spans web, mobile, and backend.

## Environment & Security Notes
Copy `env.template` to `.env` (and service-specific variants) before running any command, storing API keys locally or in your secret manager. Never commit live credentials, rotate leaked tokens immediately, and document required variables in PR descriptions when new configuration is introduced.
