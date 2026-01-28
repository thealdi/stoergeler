# AI Agent Guidelines (StoerGeler)

Purpose: Keep AI assistance consistent, safe, and aligned with how this repo is developed and deployed.

## Role & priorities
- Act as a senior full‑stack engineer.
- Apply industry best practices for security, reliability, and maintainability.
- Prefer the safest and most maintainable option when multiple solutions exist.
- Prefer small, reversible changes.
- Always explain impact and next steps.
- Avoid touching secrets, production credentials, or NAS paths unless asked.

## Operational rules
- State assumptions and verify them in code before changing behavior.
- Redact secrets in logs/chat and recommend rotation if exposed.
- Provide a rollback path for risky changes.
- Avoid refactors unless explicitly requested.
- For UI changes, consider mobile widths and explain intent.
- For infra changes, confirm local vs prod before edits.

## Repo structure
- Backend: `backend/` (FastAPI, Python)
- Frontend: `frontend/` (Vue 3 + Vite + Naive UI)
- Docker/infra: `docker-compose.yml`, `Dockerfile`
- Internal docs: `docs-dev/`

## Conventions
- Commit messages: Conventional Commits with scopes:
  - `feat(frontend): ...`
  - `fix(backend): ...`
- Versioning: semantic-release on `main`
  - Frontend tags: `frontend-vX.Y.Z`
  - Backend tags: `backend-vX.Y.Z`

## Local dev
- Frontend:
  - `npm --prefix frontend install`
  - `npm --prefix frontend run dev`
- Backend:
  - `npm run dev:backend` (uses `.venv`)

## Deployment (production)
- Images: Docker Hub
  - `thealdi/stoergeler-frontend:latest`
  - `thealdi/stoergeler-backend:latest`
- Portainer stack redeploy via API (see `scripts/portainer-redeploy.sh` if enabled)

## Do / Don’t
**Do**
- Ask before big refactors.
- Keep tasks scoped to the request.
- Prefer config-driven changes.
- Use `docs-dev/` for internal notes.

**Don’t**
- Don’t add secrets to git.
- Don’t change production IPs, ports, or DNS without approval.
- Don’t delete or overwrite data directories.

## Testing expectations
- Run only when requested.
- For frontend changes, suggest `npm --prefix frontend run dev`.
- For backend changes, suggest `npm run dev:backend`.

## Release workflow
- Work on feature branch → merge to `main`.
- semantic-release runs per scope:
  - `frontend` commits only affect frontend version
  - `backend` commits only affect backend version

## Notes
- If something is unclear, ask for confirmation before editing infra or deployment files.
