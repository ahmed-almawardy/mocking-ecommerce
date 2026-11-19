# NOVA HOME Admin Dashboard Release

## Entry points

- Admin sign-in: `http://localhost:3000/admin/login`
- Dashboard: `http://localhost:3000/admin`
- Backend OpenAPI (development): `http://localhost:8000/docs`

The admin app uses NOVA HOME's storefront palette: red, charcoal, white and neutral greys. It is a separate workspace from the customer storefront.

## Admin access

1. Register the owner account through the storefront.
2. Start the development stack so Alembic applies the migrations.
3. Promote the registered account from the API container:

   ```bash
   docker compose -f docker-compose.dev.yml exec api \
     python -m app.admin_cli promote owner@example.com
   ```

4. Sign in at `/admin/login`.
5. Seed the sample catalog and four bilingual offer records if this is a new development database:

   ```bash
   docker compose -f docker-compose.dev.yml exec api python -m app.seed
   ```

Only `admin` and `super_admin` roles can access admin endpoints. Do not grant roles through customer-submitted registration fields.

## Dashboard features

- Week-to-date, month-to-date, year-to-date and custom date reporting.
- Date boundaries follow `Africa/Cairo`, independently of the browser's configured timezone.
- KPIs: paid revenue, orders, paid orders, pending payments, new/total customers, active products and low-stock products.
- Interactive sales, customer registration, payment-state, best-selling, most-viewed and most-added-to-cart charts.
- Every chart downloads as CSV or PNG; the overview also downloads as a CSV report.
- Recent order overview.
- Product creation, editing, archiving, pricing, stock and image management.
- Offer creation, bilingual content, image upload, scheduling, activation, ordering and deletion.
- Searchable/paginated customers, orders and payment ledger.
- Searchable/paginated catalog and payment records; customer and payment CSV exports.

## Analytics data notes

- Revenue and paid order values come from persisted orders whose payment state was confirmed by the verified Kashier webhook.
- Payment-state statistics prefer the `payment_transactions` ledger and fall back to order payment fields for older orders created before the ledger migration.
- Customer registration metrics come from customer-role accounts; administrator accounts are excluded.
- Product views and add-to-cart quantities are collected by `POST /api/v1/analytics/events`. These metrics accumulate after this release is deployed; earlier browsing events are not reconstructed.
- Best-selling products are calculated from paid order items, not cart events.
- The dashboard does not invent chart numbers. Empty periods display an empty-state message.

## Product and offer media

Admin image upload accepts JPEG, PNG or WebP up to 10 MB. The API checks image file signatures, saves a random filename under `MEDIA_DIR`, and returns a same-origin `/media/...` URL.

- Development: persisted in `backend/media`.
- Production: persisted in the `media_prod` Docker volume.

Back up the media volume alongside PostgreSQL. The bundled generic product renders are original NOVA HOME sample imagery, not manufacturer-authorized photographs. Replace them with licensed manufacturer/distributor assets before launch.

## Upgrade safely

Back up `.env` and PostgreSQL first. Preserve the existing Compose volumes. Rebuild and recreate the development services without deleting volumes:

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Do **not** use `docker compose down -v` for an upgrade. The API startup command applies `alembic upgrade head`.

## Verification status for this packaged release

Executed in the build workspace:

- Backend unit tests: **22 passed**.
- Backend integration/startup tests: **14 skipped** because this workspace does not have the Redis/Authlib runtime dependencies and dedicated PostgreSQL `TEST_DATABASE_URL` needed by those tests.
- Python compilation: passed.
- Alembic revision graph and offline SQL generation through `0002_admin_analytics`: passed.
- Frontend TypeScript syntax transpilation: passed for 50 TypeScript files and Vue `<script setup>` blocks.
- JSON and Docker/GitHub Actions YAML parsing: passed.

Not executed in this workspace:

- Docker image build or Compose startup (Docker CLI is unavailable here).
- Full Nuxt production build, `vue-tsc`, Vitest or Playwright browser tests (frontend dependencies are not installed in this workspace).

The GitHub Actions workflow installs backend/frontend dependencies, provisions PostgreSQL 17, applies Alembic migrations, and runs backend, unit, typecheck/build and Playwright jobs. A successful local syntax check is not presented as a substitute for those complete runtime checks.
