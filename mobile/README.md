# NOVA HOME Flutter applications

This workspace contains **two independent Flutter applications**, each targeting Android and iOS. Together they deliver four native targets: customer Android, customer iOS, admin Android and admin iOS:

- `apps/customer_app` — customer storefront, catalog, account, cart, checkout, payment hand-off and order history.
- `apps/admin_app` — administrator dashboard, charts, products, offers, orders, customers and payments.
- `packages/nova_core` — shared NOVA HOME theme, Arabic/English direction and strings, API client, secure token storage, OAuth deep-link exchange, models and chart export.

The customer/admin apps intentionally have separate secure token namespaces and separate deep-link schemes (`novahome://auth` and `novahomeadmin://auth`). The API checks admin roles on protected endpoints; the admin UI role check is only an additional usability layer.

## Requirements

- Flutter stable 3.50.0 or newer (Dart 3.14.0 or newer; the package SDK constraints remain compatible with Dart 3.5+)
- Android Studio / Android SDK for Android builds
- Xcode on macOS for iOS builds and signing
- A running NOVA HOME FastAPI + PostgreSQL + Redis stack. Rebuild the API after extracting this release so it includes the mobile session routes:

```bash
docker compose -f docker-compose.dev.yml up -d --build api
```

Flutter is not installed in the code-generation environment used to prepare this source, and network access to the package registry was unavailable. Therefore no claim is made that the apps have already been compiled or run on devices. The commands below are the build and test procedure for a workstation with Flutter installed.

## 1. Generate native Android/iOS runner projects

From this `mobile/` directory:

```bash
chmod +x tool/bootstrap_native.sh
./tool/bootstrap_native.sh all
```

This uses `flutter create` to generate standard Android and iOS runner projects for both apps, then adds the app-specific deep-link URL schemes. Re-run only when you need to regenerate native runner folders; back up any custom native signing or capability changes first.

## 2. API address by device

The API base URL is passed as `--dart-define=API_BASE_URL=...` and must be reachable from the device:

| Target | Example |
|---|---|
| Android emulator | `http://10.0.2.2:8000` |
| iOS simulator | `http://127.0.0.1:8000` |
| Physical device | `http://YOUR_COMPUTER_LAN_IP:8000` |
| Production | `https://api.your-domain.example` |

Bind the FastAPI port to the host and allow LAN access for physical-device testing. Do not expose development HTTP endpoints to the public internet. The generated Android runner permits cleartext HTTP for local development; switch to HTTPS and remove the cleartext allowance before a store release.

## 3. Install packages

```bash
cd packages/nova_core && flutter pub get && cd ../..
cd apps/customer_app && flutter pub get
cd ../admin_app && flutter pub get
```

## 4. Run the customer app

```bash
cd mobile/apps/customer_app
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

On an iOS simulator use `http://127.0.0.1:8000` instead.

## 5. Run the admin app

```bash
cd mobile/apps/admin_app
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Sign in with an existing NOVA HOME administrator account. A customer role is rejected by both the backend's `require_admin` dependency and the mobile session controller. To promote an authorized user from the API container:

```bash
docker compose -f docker-compose.dev.yml exec api \
  python -m app.admin_cli promote YOUR_EMAIL
```

## 6. Tests and static analysis

```bash
cd mobile/packages/nova_core && flutter analyze && flutter test
cd ../../apps/customer_app && flutter analyze && flutter test
cd ../admin_app && flutter analyze && flutter test
```

## 7. Release builds

Android (run on a machine with Android SDK and release signing configured):

```bash
cd mobile/apps/customer_app
flutter build appbundle --release --dart-define=API_BASE_URL=https://api.your-domain.example
cd ../admin_app
flutter build appbundle --release --dart-define=API_BASE_URL=https://api.your-domain.example
```

On macOS with Xcode configured:

```bash
cd mobile/apps/customer_app
flutter build ipa --release --dart-define=API_BASE_URL=https://api.your-domain.example
cd ../admin_app
flutter build ipa --release --dart-define=API_BASE_URL=https://api.your-domain.example
```

Configure App Store / Play Console signing, application identifiers, privacy disclosures, app icons, screenshots, support URLs and store metadata before publishing.

## Features

### Customer

- Email/password registration and login
- Google, Facebook and Apple browser OAuth hand-off using a short-lived one-time exchange code (only shown when server provider config is enabled)
- Arabic/English locale switch with RTL support
- Featured offers from `GET /api/v1/offers/active`
- Live product catalog/categories and product details
- Product view/add-to-cart analytics events
- Local shopping cart, shipping estimate and server-priced order creation
- Kashier hosted payment hand-off and order/payment status history

### Administrator

- Role-protected admin sign-in
- Week/month/year/custom date analytics
- Revenue, orders, new customers, active/low-stock product KPIs
- Interactive sales, customer, payment, best-selling, viewed and added-to-cart charts
- Per-chart CSV and PNG export via the platform share sheet
- Product create/edit/archive and validated image uploads
- Offer create/activate/deactivate/delete and image uploads
- Customer, order and payment ledgers with search and pagination

### Backend mobile-session endpoints

- `POST /api/v1/auth/mobile/login`
- `POST /api/v1/auth/mobile/register`
- `POST /api/v1/auth/mobile/refresh`
- `POST /api/v1/auth/mobile/logout`
- `POST /api/v1/auth/mobile/exchange`
- `GET /api/v1/auth/{provider}/mobile-login?redirect_uri=...&app_type=customer|admin`

Access tokens are short-lived Bearer JWTs. Refresh tokens are rotated and blacklisted in Redis. Social OAuth returns only a random, one-time code through the deep link; the app exchanges the code over HTTPS for tokens. Never place access or refresh tokens in a deep-link query string. Register the server callback URLs with each OAuth provider, use the public HTTPS API origin, and configure the exact `novahome://auth` (customer) and `novahomeadmin://auth` (admin) app redirect URIs. For Apple web OAuth's cross-site form POST, use `COOKIE_SECURE=true` and `COOKIE_SAMESITE=none`. Instagram personal accounts are not offered as a consumer sign-in provider.

## Operational notes

- Kashier checkout remains provider-hosted. The app does not mark an order as paid; only the verified backend webhook does that.
- Admin upload endpoint accepts validated JPEG, PNG and WebP images up to the API-configured limit.
- Product views/cart event analytics are persisted; historical events cannot be reconstructed retroactively.
- The locale switch applies English/Arabic labels included in `nova_core` and switches layout direction; some screen-specific helper copy and admin form labels remain English and should be fully localized before publishing an Arabic-first production app.
- Add API rate limits, privacy disclosures, crash monitoring, push-notification policy, final app icons, app-store metadata, signing and a production HTTPS API before release.
