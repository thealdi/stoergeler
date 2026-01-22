# StoerGeler Frontend Migration (Vue + Vite + TypeScript)

This is a step-by-step checklist you can follow to migrate the current static
frontend to Vue + Vite + TypeScript. No code changes are applied yet.

## 0) Prep
- [x] New frontend location: `frontend-vue/`.
- [x] Keep old `frontend/` for rollback during migration.
- [x] Backend base path stays `/api`.

## 1) Create the new frontend project
- [x] Initialize a Vue + Vite + TypeScript app in `frontend-vue/`.
- [x] Verify `npm run dev` starts and renders the default Vue page.
- [x] Add a Vite dev proxy so `/api` points to `http://localhost:8000`.
- [x] Add a basic `src/styles/base.css` and wire it in `main.ts`.

## 2) Port the API layer
- [x] Create `src/config.ts` to resolve backend base URL (port logic + override).
- [x] Create `src/api/client.ts` with a `request()` helper (error handling).
- [x] Add API functions:
  - [x] `fetchOutages()`
  - [x] `fetchDeviceLog(limit?: number)`
  - [x] `fetchConnectionStatus()`
- [x] Define TypeScript types for outages, logs, status.

## 3) Add state management
- [x] Decide between Composition API state or Pinia (recommended: Composition API).
- [x] Create a `useStoergelerState()` composable:
  - [x] `outages`, `logs`, `selectedEventId`
  - [x] `setSelectedEvent`, `resetSelection`
- [x] Add pagination composables for outages/logs.

## 4) Build core components
- [x] `App.vue` layout (header, controls, sections).
- [x] `StatusBar.vue` for status message and connection check.
- [x] `CalendarView.vue` for FullCalendar integration.
- [x] `OutageTable.vue` (table + pagination).
- [x] `DeviceLogTable.vue` (table + pagination).
- [x] `Pagination.vue` reusable prev/next component.

## 5) Port the calendar logic
- [x] Install FullCalendar for Vue and configure in `CalendarView.vue`.
- [x] Port event rendering logic (planned vs offline coloring).
- [x] Implement event click -> filter logs in state.
- [x] Add highlight selection behavior.

## 6) Port UI behavior and formatting
- [x] Move format helpers to `src/utils/format.ts`:
  - [x] `formatDate()`
  - [x] `formatDuration()`
  - [x] `formatRangeLabel()`
- [x] Port "filter reset" flow and status updates.
- [x] Ensure log filtering matches current behavior.

## 7) Bring over styles
- [x] Copy `frontend/styles.css` into `src/styles/base.css`.
- [x] Adjust class names if needed for Vue components.
- [ ] Verify layout on mobile and desktop.

## 8) Verify parity with existing frontend
- [ ] Calendar renders outages.
- [ ] Click outage filters logs correctly.
- [ ] Pagination works for outages and logs.
- [ ] Status messages show for refresh + connection check.
- [ ] Empty states render as expected.

## 9) Update deployment
- [ ] Add build script for Vite in Docker/Compose or CI.
- [ ] Update Nginx to serve `frontend-vue/dist` instead of `frontend/`.
- [ ] Update README with new dev and build commands.

## 10) Cleanup (optional)
- [ ] Remove old `frontend/` once the new UI is stable.
- [ ] Remove old static deployment instructions.
