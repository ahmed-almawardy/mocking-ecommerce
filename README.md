# NOVA HOME — full-stack appliance storefront

A fresh, red-and-white Egyptian appliance-shopping storefront inspired by the broad shopping patterns of the Fresh Egypt website. This is a separate brand and implementation: it does not use Fresh trademarks, copied website text, or Fresh-owned product photographs. The first pass uses custom CSS/SVG appliance artwork and sample product records that you can replace with licensed product photography and real catalog data.

## Storefront navigation, offers and translations

- The category navigation uses a hover/focus mega-menu with grouped, multi-column links. On touch-sized screens each category also has a dedicated expand button because mobile browsers do not have hover.
- The homepage places a four-slide `FeaturedOffersCarousel` directly after the category navigation. It advances left every five seconds, pauses while hovered/focused or when reduced motion is requested, and supports previous/next arrows plus four centered pagination dots.
- Offer artwork lives in `frontend/public/images/offers/`; the slide definitions and wraparound behavior are in `frontend/app/composables/offerCarouselCore.ts`. Replace these neutral NOVA HOME assets with campaign images that you own or are licensed to use.
- Localized routes are `/en` and `/ar`. Translation files are discovered from `frontend/app/locales/*.json`; each catalog declares `languageName` and `direction` (`ltr` or `rtl`). Add further locales by following [`docs/LOCALIZATION.md`](docs/LOCALIZATION.md). Missing keys fall back to English, and the frontend unit tests check that the English and Arabic catalogs remain in sync.

## Included

- **Frontend:** Nuxt 4, Vue 3, TypeScript, responsive storefront, hover mega-menu, four-slide offer carousel, `/en` + `/ar` and extensible JSON translations, product/category listing, product detail, cart, account screens, registration/login, checkout and payment-return state.
- **Backend:** FastAPI, Pydantic v2, pydantic-settings, async SQLAlchemy 2, PostgreSQL, Alembic, Redis.
- **Identity:** email/password registration with normalized phone numbers, Google/Facebook/Apple OAuth entry points, one customer record with multiple linked provider identities, access/refresh JWT cookies, Redis-backed token revocation, explicit provider-link flow for authenticated customers.
- **Commerce:** database-backed products, Redis-cached catalog/category/product reads, server-priced orders, delivery details, Kashier hosted checkout session, signed webhook validation, order-status transition, stock adjustment after payment confirmation, PDF receipts.
- **Messaging:** WhatsApp Cloud API integration hooks for opt-in welcome templates and an approved receipt template with a PDF document header.
- **Operations:** separate development and production Compose files, Dockerfiles, health endpoint, GitHub Actions CI and SSH deployment workflows.

## Quick start — development

Requirements: Docker Engine + Docker Compose v2, Git.

```bash
cp .env.development.example .env
# Edit .env and set a long random SECRET_KEY before sharing this environment.
make dev
```

In another terminal, seed the starter catalog:

```bash
docker compose -f docker-compose.dev.yml exec api python -m app.seed
```

Open:

- Storefront: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

The development compose stack runs PostgreSQL, Redis, FastAPI and Nuxt. The API container applies Alembic migrations before starting. `make down` stops the stack but keeps named development volumes.

## Environment configuration

Start from `.env.example` or `.env.development.example`. Keep real secrets only in local `.env` or your deployment secret manager. Never commit `.env`.

### Core

- `SECRET_KEY`: unique random value; at least 48 characters in production.
- `DATABASE_URL`: async PostgreSQL URL (`postgresql+asyncpg://...`).
- `REDIS_URL`: Redis connection string.
- `CORS_ORIGINS`: comma-separated exact browser origins.
- `COOKIE_SECURE=true` and HTTPS are required in production. The production Compose topology serves `/api/*` and `/health` through the same domain as the Nuxt storefront.

### OAuth callback URLs

The API exposes `GET /api/v1/auth/providers` to show which providers are configured and the exact callback URL the backend will send. The frontend disables unconfigured buttons and explains why. The callback URL is built from `API_PUBLIC_URL`, not from a reverse-proxy `Host` header.

For local development with the Compose ports exposed, use:

- Google: `http://localhost:8000/api/v1/auth/google/callback`
- Facebook: `http://localhost:8000/api/v1/auth/facebook/callback`

For production, use the public HTTPS origin (the same host that proxies `/api/*` to FastAPI), for example `https://store.example.com/api/v1/auth/google/callback`. Set `API_PUBLIC_URL=https://store.example.com` and register the exact same URL in each provider console. Scheme, hostname, path and trailing slash must match exactly.

**Google:** create a Web application OAuth client, add the callback under Authorized redirect URIs, configure the OAuth consent screen, and set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. Request only `openid email profile`. Google requires the callback URI to exactly match an authorized redirect URI.

**Facebook:** add the Facebook Login product to a Meta app, enable Web OAuth, add the callback to Valid OAuth Redirect URIs, request the `email` and `public_profile` permissions, and set `FACEBOOK_CLIENT_ID` and `FACEBOOK_CLIENT_SECRET`. The current Graph API version defaults to `v26.0` and can be changed using `FACEBOOK_GRAPH_VERSION`. Facebook does not return the OIDC `email_verified` claim in the `/me` profile, so a matching email is not silently merged with an existing password account; the customer must sign in first and explicitly link Facebook.

**Apple:** create a Services ID, associate the website domain with an enabled primary App ID, add the exact return URL, generate a valid Apple client-secret JWT, and set `APPLE_CLIENT_ID` and `APPLE_CLIENT_SECRET`. The generated secret expires and must be rotated. Apple uses `response_mode=form_post`; the site must use HTTPS and `COOKIE_SECURE=true` so the signed OAuth-state cookie is sent on Apple's cross-site POST. The API reports Apple as unavailable when this requirement is not met.

**Account matching rule:** Google/Apple accounts with a provider-verified email may be attached to the existing customer with that same email. The backend refuses to merge an unverified email claim. A logged-in customer can explicitly link another configured identity through `/api/v1/auth/{provider}/link`. Provider identities are unique by `(provider, subject)`; a provider account cannot be linked to two customers.

**Instagram limitation:** there is no supported general-purpose Instagram personal-account OAuth sign-up for an ordinary shopping customer. Meta's current Instagram APIs are for professional Business/Creator accounts, not personal shopper accounts. Instagram Basic Display (the older consumer-profile API) was discontinued. For this reason, NOVA HOME does not show a misleading “Sign up with Instagram” button. A separate “Connect Instagram Business” feature can be implemented for the store owner's professional account, but it must not be used as consumer customer authentication.

### OAuth troubleshooting

1. Copy the environment template to the project-root `.env`, then enter real provider credentials. The example files intentionally contain empty values; blank credentials cannot perform a real OAuth login.
2. Start the API and inspect `curl http://localhost:8000/api/v1/auth/providers`. Each provider reports `configured`, `available`, a safe explanation, and the exact callback URI. This endpoint never returns a client secret.
3. Copy each callback URI from that endpoint into the matching provider dashboard exactly. In production, set `API_PUBLIC_URL` to the public HTTPS origin and register the HTTPS callback through the same host. Do not set it to the internal Docker hostname `api`.
4. After changing `.env`, recreate the API container so Docker supplies the updated environment and Python re-registers the OAuth clients: `docker compose -f docker-compose.dev.yml up -d --build --force-recreate api`. A normal browser refresh or `docker compose restart api` does not replace environment variables captured when the container was created.
5. Google: check OAuth consent-screen publishing/test-user status and Authorized redirect URIs. Facebook: check Facebook Login > Settings > Valid OAuth Redirect URIs, app mode/roles, and the `email` permission. Apple: use a Services ID, verified HTTPS domain/return URL, valid signing key/client-secret JWT, HTTPS and `COOKIE_SECURE=true`.
6. If the provider is marked available but the callback still fails, inspect `docker compose -f docker-compose.dev.yml logs --tail=200 api`. The backend now logs the underlying callback exception while returning a generic message to the browser. Never paste client secrets, Apple private keys, or access tokens into support messages.

### Kashier

Create a Kashier developer/sandbox account and set `KASHIER_ENV=test`, `KASHIER_API_KEY`, `KASHIER_SECRET_KEY`, and `KASHIER_MERCHANT_ID`. The API creates a one-time hosted payment session and sends a `serverWebhook` URL. Configure/allow the public webhook URL:

`https://store.example.com/api/v1/webhooks/kashier`

The webhook validates the `x-kashier-signature` header using the Payment API Key and reads `data.status`. **A redirect to the storefront does not mark an order paid.** Switch `KASHIER_ENV=live` only after Kashier enables the live merchant profile and you have completed their go-live checklist. Test mode does not move real money.

### WhatsApp Cloud API

Set `WHATSAPP_ENABLED=true`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, and the Graph API version. Create and approve templates matching the configured names:

- `WHATSAPP_WELCOME_TEMPLATE` — one body text variable for the customer's name.
- `WHATSAPP_RECEIPT_TEMPLATE` — document header and two body text variables (order number and total).

Customers must explicitly opt in using the registration checkbox. The implementation uses template messages because proactive business-initiated notifications require approved templates and valid opt-in under WhatsApp's platform rules. The PDF is uploaded to WhatsApp media first, then referenced by media ID in the template. Receipt delivery is idempotency-guarded, and it is not marked as sent while WhatsApp is disabled. Configure the template structure and language in Meta to match the variables used by the code.

## Production deployment

1. Provision a Linux host with Docker Engine/Compose v2, a domain and an HTTPS-terminating reverse proxy/load balancer. This stack's included Nginx file is an HTTP reverse-proxy example; terminate TLS at a managed load balancer/CDN or adapt Nginx with your real certificates before public launch.
2. Clone the repository to the server and create `.env` from `.env.production.example`.
3. Set unique high-entropy `SECRET_KEY`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, real provider credentials, production hostnames, `CORS_ORIGINS`, and `COOKIE_SECURE=true`.
4. Confirm the public HTTPS frontend/API origins and OAuth callback URLs.
5. Run `docker compose -f docker-compose.prod.yml up -d --build`.
6. Confirm migrations and health: `docker compose -f docker-compose.prod.yml exec api alembic current` and `curl https://store.example.com/health`.
7. Seed the catalog once if this is a new empty database: `docker compose -f docker-compose.prod.yml exec api python -m app.seed`.

Production containers use restart policies, a private database/Redis network, persistent volumes and a non-root API process. Before a real launch, configure backups, log aggregation, monitoring, TLS, firewall policy, admin/catalog operations, transactional email, rate limiting, CSRF/origin controls, email/phone verification and a tested restore procedure. Review cookie domain/path and same-site policy if frontend/API use different registrable domains.

## GitHub Actions

- `ci.yml` provisions PostgreSQL 17, runs Alembic and backend unit/API/database integration tests, then runs frontend unit tests, type checking, a Nuxt production build, and Playwright browser UI/end-to-end tests on PRs and pushes to `main`/`develop`.
- `deploy-dev.yml` deploys `develop` to a dev host over SSH.
- `deploy-prod.yml` deploys `main` to a GitHub `production` environment (enable required reviewers on that environment if approval is desired).

Add these repository/environment secrets:

- Dev: `DEV_HOST`, `DEV_USER`, `DEV_SSH_KEY`, `DEV_PORT` (optional), `DEV_DEPLOY_PATH`.
- Production: `PROD_HOST`, `PROD_USER`, `PROD_SSH_KEY`, `PROD_PORT` (optional), `PROD_DEPLOY_PATH`.

The remote deployment directory must already contain the repository clone and its own protected `.env`. GitHub Actions never transfers local secrets to the host.

## API outline

- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout`; `GET /api/v1/auth/me`
- `GET /api/v1/auth/{google|facebook|apple}/login`
- `GET /api/v1/auth/{google|facebook|apple}/link` (requires an authenticated session)
- `GET /api/v1/products`, `/categories`, `/{slug}`
- `POST /api/v1/orders` (authenticated; server calculates prices and delivery)
- `GET /api/v1/orders`, `GET /api/v1/orders/{order_number}` (owner only), `GET /api/v1/orders/{order_number}/receipt.pdf` (owner-only receipt download)
- `POST /api/v1/webhooks/kashier` (provider signature required)

## Testing locally

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt ruff
pytest -q
ruff check app tests
python -m compileall -q app alembic tests
```

Frontend checks:

```bash
cd frontend
npm install
npm run test:unit
npm run typecheck
npm run build
npx playwright install chromium
npm run test:e2e
```

## Important implementation notes

- The sample catalog uses original, generic appliance product renders stored under `frontend/public/images/products/`. They are not manufacturer-authorized brand photos. Replace them with licensed manufacturer/distributor media before commercial launch.
- The seed catalog is fictional demo content and demo prices, not current Fresh prices or real inventory.
- The current checkout flow creates an order, asks Kashier for a hosted session and trusts only verified provider webhook data for the paid state. Catalog cache entries expire automatically (60–300 seconds); product create/update/archive operations also invalidate matching catalog cache entries. The TTL remains a fallback if Redis is unavailable. Successful payment webhooks are checked against order amount/currency; duplicate cart lines are aggregated and per-product quantity is capped. The account area includes order history, payment retry for eligible orders, and authenticated receipt download. For production-grade stock reservation, add expiring inventory reservations and a reconciliation worker to handle abandoned sessions and late webhook delivery.
- Before opening to real shoppers, finish payment-session retry/reconciliation, customer email verification, password reset, tax/invoice rules, delivery zones, inventory reservations and a production media backup/retention policy.
- Social OAuth requires registered app credentials, approved scopes, valid redirect URLs, domain verification and (where applicable) provider app review. Apple requires a valid time-limited client-secret JWT.


## Automated test strategy

The repository separates the test layers so a green unit-test run is not mistaken for a verified deployment:

- **Backend unit tests:** `cd backend && python -m pytest tests/unit -q`
- **Backend API integration tests:** `cd backend && python -m pytest tests/integration -q`
- **Frontend unit tests:** `cd frontend && npm install && npm run test:unit`
- **Browser UI and end-to-end tests:** `cd frontend && npx playwright install chromium && npm run test:e2e`
- **Frontend production checks:** `cd frontend && npm run typecheck && npm run build`

The real-PostgreSQL integration tests use `TEST_DATABASE_URL`. **It must point to a dedicated database whose name ends in `_test`**: the fixture deliberately truncates test tables and refuses database names that do not end in `_test`. Never point it at development or production data. GitHub Actions provisions PostgreSQL 17 with a dedicated `nova_home_test` database, runs `alembic upgrade head`, and then tests registration and checkout persistence. Without `TEST_DATABASE_URL`, those tests are skipped intentionally rather than pretending a fake session is a database integration test. Kashier network calls are mocked during tests; no live payment is initiated. Playwright tests run against the Nuxt development server with the sample catalog fallback, so they do not require provider credentials.

### Rebuilding after backend dependency changes

Docker caches the Python dependency layer. After editing `backend/requirements.txt`, rebuild the API image before restarting it:

```bash
docker compose -f docker-compose.dev.yml build --no-cache api
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml logs -f api
```

The `itsdangerous` dependency is required by Starlette `SessionMiddleware`, which Authlib uses for signed OAuth state/session handling. Do not remove that middleware to work around a missing dependency.

For local real-PostgreSQL integration tests, create a separate database first (never use `nova_home`):

```bash
docker compose -f docker-compose.dev.yml exec db createdb -U nova nova_home_test
docker compose -f docker-compose.dev.yml exec \
  -e TEST_DATABASE_URL=postgresql+asyncpg://nova:nova_dev_password@db:5432/nova_home_test \
  api pytest tests/integration -q
```

Replace the example password with the value configured in your `.env`.

## Administrator dashboard

The administration workspace is available at `http://localhost:3000/admin` and is separate from the public storefront. Access is restricted to users whose database `role` is `admin` or `super_admin`; ordinary customers cannot read admin APIs.

### First-time administrator setup

1. Register a normal customer account through the storefront.
2. Apply the current Alembic migrations (the development API command runs `alembic upgrade head` at startup).
3. Promote that existing account from inside the API container:

   ```bash
   docker compose -f docker-compose.dev.yml exec api \
     python -m app.admin_cli promote your-admin-email@example.com
   ```

4. Open `http://localhost:3000/admin/login` and sign in with that account.
5. Seed the initial catalog and four offer banners if the local store has not been seeded yet:

   ```bash
   docker compose -f docker-compose.dev.yml exec api python -m app.seed
   ```

The CLI is intentionally not exposed as an HTTP endpoint. Never grant administrator privileges through customer registration fields.

### Dashboard data and analytics

The dashboard supports Week, Month, Year and custom date ranges. It reports paid revenue, order totals and payment states, customer registrations, active/low-stock products, best-selling products, most viewed products, most added-to-cart products and recent orders. Every dashboard chart (sales, customer registrations, payment status, best-selling products, most-viewed products and most-added-to-cart products) is interactive and can be downloaded as CSV or PNG. The full overview can also be exported as a CSV report.

`POST /api/v1/analytics/events` records `view` and `add_to_cart` events for real catalog product UUIDs. Product view and cart analytics therefore begin accumulating after this tracking update is deployed; old browsing behavior cannot be reconstructed retroactively. Paid sales and payment status come from persisted orders and verified Kashier callbacks, not generated demo chart values.

The dashboard includes product create/update/archive, offer create/update/activate/deactivate/delete, customer lookup, order listing and payment ledger views. Offer campaigns support separate English and Arabic headings and subtitles, start/end schedules, display order and a local image URL. The public carousel consumes the four highest-priority active offers.

Product and offer images can use local storefront paths such as `/images/products/refrigerator.webp` and `/images/offers/offer-1.webp`, approved HTTPS media URLs, or images uploaded directly from the admin forms. Admin uploads accept JPEG, PNG and WebP files up to 10 MB, validate file signatures, and save them under `MEDIA_DIR` (default `/app/media`). Development persists files in `backend/media`; production persists them in the `media_prod` Docker volume. Back up this volume alongside PostgreSQL. The bundled sample images are original generic NOVA HOME appliance photography, not manufacturer-authorized brand photography; replace them with licensed manufacturer/distributor product images before commercial launch.

## Flutter mobile applications

The `mobile/` workspace contains separate NOVA HOME customer and administrator Flutter apps. Each targets Android and iOS. See [`mobile/README.md`](mobile/README.md) for native runner generation, API configuration, testing, CI, and release-build instructions.
