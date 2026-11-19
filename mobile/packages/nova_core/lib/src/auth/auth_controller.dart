import 'package:flutter/foundation.dart';
import '../api/nova_api_client.dart';
import '../models/nova_models.dart';

class AuthController extends ChangeNotifier {
  AuthController(this.api);
  final NovaApiClient api;
  NovaUser? user;
  bool isLoading = false;
  bool isReady = false;
  String? error;
  bool get isSignedIn => user != null;
  bool get isAdmin => user != null && {'admin', 'super_admin'}.contains(user!.role);

  Future<void> restore() async {
    isLoading = true;
    notifyListeners();
    try {
      if (await api.hasSession) {
        final data = await api.get('/auth/me');
        user = NovaUser.fromJson(Map<String, dynamic>.from(data as Map));
      }
    } catch (_) {
      user = null;
      await api.clearTokens();
    } finally {
      isLoading = false;
      isReady = true;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password, {required bool adminOnly}) async {
    return _runAuth(() => api.post('/auth/mobile/login', data: {'email': email.trim(), 'password': password}), adminOnly: adminOnly);
  }

  Future<bool> register({required String name, required String email, required String phone, required String password, bool whatsappOptIn = false}) async {
    return _runAuth(() => api.post('/auth/mobile/register', data: {
      'name': name.trim(), 'email': email.trim(), 'phone': phone.trim(), 'password': password,
      'whatsapp_opt_in': whatsappOptIn,
    }), adminOnly: false);
  }

  Future<bool> exchangeOAuthCode(String code, {required bool adminOnly}) async {
    return _runAuth(() => api.post('/auth/mobile/exchange', data: {'code': code}), adminOnly: adminOnly);
  }

  Future<bool> _runAuth(Future<dynamic> Function() action, {required bool adminOnly}) async {
    isLoading = true;
    error = null;
    notifyListeners();
    try {
      final raw = await action();
      final data = Map<String, dynamic>.from(raw as Map);
      await api.saveTokens(data);
      final nextUser = NovaUser.fromJson(Map<String, dynamic>.from(data['user'] as Map));
      if (adminOnly && !{'admin', 'super_admin'}.contains(nextUser.role)) {
        await api.clearTokens();
        throw NovaApiException('This account does not have administrator access.');
      }
      user = nextUser;
      isReady = true;
      return true;
    } catch (e) {
      error = e.toString();
      return false;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refreshProfile() async {
    final raw = await api.get('/auth/me');
    user = NovaUser.fromJson(Map<String, dynamic>.from(raw as Map));
    notifyListeners();
  }

  Future<void> logout() async {
    try {
      await api.post('/auth/mobile/logout', data: {
        'access_token': await api.accessToken,
        'refresh_token': await api.refreshToken,
      });
    } catch (_) {
      // Local credentials are still removed if the network is unavailable.
    }
    await api.clearTokens();
    user = null;
    error = null;
    notifyListeners();
  }

  void clearError() { error = null; notifyListeners(); }
}
