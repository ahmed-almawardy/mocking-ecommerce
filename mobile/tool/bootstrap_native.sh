#!/usr/bin/env bash
set -euo pipefail

MOBILE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-all}"

create_app_platforms() {
  local app_name="$1" app_dir="$2" org="$3" project="$4" scheme="$5" display_name="$6"
  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  echo "Generating Android and iOS runners for ${app_name}..."
  flutter create --no-pub --platforms=android,ios --org "$org" --project-name "$project" "$tmp/$project"
  rm -rf "$app_dir/android" "$app_dir/ios"
  cp -a "$tmp/$project/android" "$app_dir/android"
  cp -a "$tmp/$project/ios" "$app_dir/ios"

  python3 - "$app_dir" "$scheme" "$display_name" <<'PY'
import pathlib, sys, xml.etree.ElementTree as ET, re, plistlib
app_dir = pathlib.Path(sys.argv[1])
scheme, display_name = sys.argv[2], sys.argv[3]
manifest = app_dir / 'android/app/src/main/AndroidManifest.xml'
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
tree = ET.parse(manifest); root = tree.getroot()
android = '{http://schemas.android.com/apk/res/android}'
permission_names = {node.get(android + 'name') for node in root.findall('uses-permission')}
if 'android.permission.INTERNET' not in permission_names:
    root.insert(0, ET.Element('uses-permission', {android + 'name': 'android.permission.INTERNET'}))
application = root.find('application')
application.set(android + 'label', display_name)
application.set(android + 'usesCleartextTraffic', 'true')  # Development only. Use HTTPS in release builds.
activity = next((a for a in application.findall('activity') if a.get(android + 'name', '').endswith('MainActivity')), None)
if activity is None: raise SystemExit('Could not locate MainActivity in AndroidManifest.xml')
intent = ET.SubElement(activity, 'intent-filter')
ET.SubElement(intent, 'action', {android + 'name': 'android.intent.action.VIEW'})
ET.SubElement(intent, 'category', {android + 'name': 'android.intent.category.DEFAULT'})
ET.SubElement(intent, 'category', {android + 'name': 'android.intent.category.BROWSABLE'})
ET.SubElement(intent, 'data', {android + 'scheme': scheme, android + 'host': 'auth'})
tree.write(manifest, encoding='utf-8', xml_declaration=True)

plist_path = app_dir / 'ios/Runner/Info.plist'
with plist_path.open('rb') as f: info = plistlib.load(f)
info['CFBundleDisplayName'] = display_name
info['CFBundleURLTypes'] = [{'CFBundleTypeRole': 'Editor', 'CFBundleURLName': scheme, 'CFBundleURLSchemes': [scheme]}]
info['NSLocalNetworkUsageDescription'] = 'NOVA HOME connects to your configured development API on your local network.'
info['NSPhotoLibraryUsageDescription'] = 'Choose product and offer photos to upload them to the NOVA HOME store.'
info['NSAppTransportSecurity'] = {'NSAllowsLocalNetworking': True}
with plist_path.open('wb') as f: plistlib.dump(info, f)

# Set bundle IDs to stable, App-Store-safe values without underscores.
pbx = app_dir / 'ios/Runner.xcodeproj/project.pbxproj'
if pbx.exists():
    text = pbx.read_text()
    bundle_id = 'com.novahome.customer.customerapp' if scheme == 'novahome' else 'com.novahome.admin.adminapp'
    text = re.sub(r'PRODUCT_BUNDLE_IDENTIFIER = [^;]+;', f'PRODUCT_BUNDLE_IDENTIFIER = {bundle_id};', text)
    pbx.write_text(text)
PY
  rm -rf "$tmp"
  trap - RETURN
}

case "$TARGET" in
  customer)
    create_app_platforms customer_app "$MOBILE_ROOT/apps/customer_app" com.novahome.customer customerapp novahome "NOVA HOME"
    ;;
  admin)
    create_app_platforms admin_app "$MOBILE_ROOT/apps/admin_app" com.novahome.admin adminapp novahomeadmin "NOVA HOME Admin"
    ;;
  all)
    create_app_platforms customer_app "$MOBILE_ROOT/apps/customer_app" com.novahome.customer customerapp novahome "NOVA HOME"
    create_app_platforms admin_app "$MOBILE_ROOT/apps/admin_app" com.novahome.admin adminapp novahomeadmin "NOVA HOME Admin"
    ;;
  *) echo "Usage: $0 [customer|admin|all]" >&2; exit 2 ;;
esac

echo "Native Android/iOS runner projects generated. These are development scaffolds; review signing, app IDs, HTTPS and store assets before release."
