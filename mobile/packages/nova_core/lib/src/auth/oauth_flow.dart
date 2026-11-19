import 'dart:async';
import 'package:app_links/app_links.dart';
import 'package:flutter/foundation.dart';
import 'package:url_launcher/url_launcher.dart';
import '../api/nova_api_client.dart';
import 'auth_controller.dart';

class NovaOAuthFlow extends ChangeNotifier {
  NovaOAuthFlow({required this.api, required this.auth, required this.appType, required this.scheme}) {
    _subscription = _links.uriLinkStream.listen(_handleUri);
  }
  final NovaApiClient api;
  final AuthController auth;
  final String appType;
  final String scheme;
  final AppLinks _links = AppLinks();
  StreamSubscription<Uri>? _subscription;
  bool busy = false;
  String? error;

  Future<void> checkInitialLink() async {
    final uri = await _links.getInitialLink();
    if (uri != null) await _handleUri(uri);
  }

  Future<void> start(String provider) async {
    if (busy) return;
    busy = true;
    error = null;
    notifyListeners();
    try {
      final redirectUri = '$scheme://auth';
      final uri = Uri.parse('${api.baseUrl}/auth/$provider/mobile-login').replace(queryParameters: {
        'redirect_uri': redirectUri,
        'app_type': appType,
      });
      final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
      if (!launched) throw NovaApiException('Could not open the sign-in provider.');
    } catch (e) {
      error = e.toString();
      notifyListeners();
      rethrow;
    } finally {
      busy = false;
      notifyListeners();
    }
  }

  Future<void> _handleUri(Uri uri) async {
    if (uri.scheme != scheme || uri.host != 'auth') return;
    final code = uri.queryParameters['code'];
    final oauthError = uri.queryParameters['error'];
    if (oauthError != null) {
      error = oauthError.replaceAll('_', ' ');
      notifyListeners();
      return;
    }
    if (code == null || code.isEmpty) return;
    try {
      final ok = await auth.exchangeOAuthCode(code, adminOnly: appType == 'admin');
      error = ok ? null : (auth.error ?? 'Sign-in could not be completed.');
      notifyListeners();
    } catch (e) {
      error = e.toString();
      notifyListeners();
      debugPrint('NOVA OAuth exchange failed: $e');
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
