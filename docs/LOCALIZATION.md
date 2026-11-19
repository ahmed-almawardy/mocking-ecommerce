# Adding storefront translations

NOVA HOME uses JSON message catalogs and locale-prefixed Nuxt routes. The locale file name is the URL prefix:

- `frontend/app/locales/en.json` → `/en`
- `frontend/app/locales/ar.json` → `/ar`
- `frontend/app/locales/fr.json` → `/fr` (after creating the file and rebuilding)

## Add a language

1. Copy `frontend/app/locales/en.json` to `frontend/app/locales/<locale>.json`.
2. Set `languageName` to the language's self-name (for example, `Français`).
3. Set `direction` to `ltr` or `rtl`. Direction is read from the locale catalog; it is not inferred from the locale code.
4. Translate the message values while preserving every JSON key and every interpolation placeholder such as `{name}`, `{number}`, `{amount}`, `{count}`, and `{category}`.
5. Run the frontend unit tests and Nuxt type check, then rebuild the frontend. The new JSON file is discovered automatically by `import.meta.glob`; no route table or TypeScript switch statement needs editing.

Example metadata:

```json
{
  "languageName": "Français",
  "direction": "ltr"
}
```

Keep the rest of the keys from `en.json`. Missing messages fall back to English at runtime, but production translations should be complete. The locale unit test verifies English and Arabic key parity. Add parity coverage for any new locale before shipping it.

## How the locale routing works

The `[locale]` route segment serves the same pages beneath `/en` and `/ar`. The global locale middleware redirects an unprefixed path to the default English prefix. The header lists every discovered locale and switches the current page while preserving its remaining path. The app writes the selected language and text direction to the document's `lang` and `dir` attributes, and the root storefront shell applies the RTL layout adjustments.
