import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class NovaApiException implements Exception {
  NovaApiException(this.message, {this.statusCode});
  final String message;
  final int? statusCode;
  @override
  String toString() => message;
}

class NovaApiClient {
  NovaApiClient({required String baseUrl, required this.storageNamespace})
      : baseUrl = _normaliseBaseUrl(baseUrl),
        _storage = const FlutterSecureStorage() {
    dio = Dio(BaseOptions(
      baseUrl: this.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 25),
      sendTimeout: const Duration(seconds: 25),
      headers: const {'Accept': 'application/json'},
    ));
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await accessToken;
        if (token != null && token.isNotEmpty) options.headers['Authorization'] = 'Bearer $token';
        handler.next(options);
      },
      onError: (error, handler) async {
        final request = error.requestOptions;
        final isAuthCall = request.path.contains('/auth/mobile/');
        if (error.response?.statusCode == 401 && !isAuthCall && request.extra['novaRetried'] != true) {
          try {
            await _refreshSession();
            final token = await accessToken;
            final options = request.copyWith(
              headers: {...request.headers, 'Authorization': 'Bearer $token'},
              extra: {...request.extra, 'novaRetried': true},
            );
            handler.resolve(await dio.fetch<dynamic>(options));
            return;
          } catch (_) {
            await clearTokens();
          }
        }
        handler.next(error);
      },
    ));
  }

  final String baseUrl;
  final String storageNamespace;
  final FlutterSecureStorage _storage;
  late final Dio dio;
  Future<void>? _refreshing;

  static String _normaliseBaseUrl(String value) {
    final trimmed = value.trim().replaceAll(RegExp(r'/+$'), '');
    if (trimmed.isEmpty) return 'http://10.0.2.2:8000/api/v1';
    return trimmed.endsWith('/api/v1') ? trimmed : '$trimmed/api/v1';
  }

  String get apiOrigin {
    final uri = Uri.parse(baseUrl);
    return '${uri.scheme}://${uri.authority}';
  }

  String resolveUrl(String path) {
    if (path.startsWith('https://') || path.startsWith('http://')) return path;
    final clean = path.startsWith('/') ? path : '/$path';
    return '$apiOrigin$clean';
  }

  String _key(String suffix) => '$storageNamespace.$suffix';
  Future<String?> get accessToken => _storage.read(key: _key('access'));
  Future<String?> get refreshToken => _storage.read(key: _key('refresh'));

  Future<bool> get hasSession async => (await accessToken)?.isNotEmpty == true || (await refreshToken)?.isNotEmpty == true;

  Future<void> saveTokens(Map<String, dynamic> json) async {
    final access = json['access_token'] as String?;
    final refresh = json['refresh_token'] as String?;
    if (access == null || refresh == null || access.isEmpty || refresh.isEmpty) {
      throw NovaApiException('The server returned an incomplete sign-in session.');
    }
    await _storage.write(key: _key('access'), value: access);
    await _storage.write(key: _key('refresh'), value: refresh);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _key('access'));
    await _storage.delete(key: _key('refresh'));
  }

  Future<void> _refreshSession() {
    final running = _refreshing;
    if (running != null) return running;
    final refreshFuture = _performRefresh();
    _refreshing = refreshFuture;
    return refreshFuture.whenComplete(() {
      if (identical(_refreshing, refreshFuture)) _refreshing = null;
    });
  }

  Future<void> _performRefresh() async {
    final refresh = await refreshToken;
    if (refresh == null || refresh.isEmpty) {
      throw NovaApiException('Your session has expired. Please sign in again.');
    }
    final bare = Dio(BaseOptions(baseUrl: baseUrl, headers: const {'Accept': 'application/json'}));
    final response = await bare.post<Map<String, dynamic>>(
      '/auth/mobile/refresh',
      data: {'refresh_token': refresh},
    );
    await saveTokens(response.data ?? <String, dynamic>{});
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async => _guard(() async => (await dio.get<dynamic>(path, queryParameters: query)).data);
  Future<dynamic> post(String path, {Object? data, Map<String, dynamic>? query}) async => _guard(() async => (await dio.post<dynamic>(path, data: data, queryParameters: query)).data);
  Future<dynamic> patch(String path, {Object? data}) async => _guard(() async => (await dio.patch<dynamic>(path, data: data)).data);
  Future<void> delete(String path) async => _guard(() async { await dio.delete<dynamic>(path); });

  Future<Map<String, dynamic>> uploadMedia(File file) async {
    final name = file.path.split(Platform.pathSeparator).last;
    final form = FormData.fromMap({'file': await MultipartFile.fromFile(file.path, filename: name)});
    final result = await _guard(() async => (await dio.post<dynamic>('/admin/media', data: form)).data);
    return Map<String, dynamic>.from(result as Map);
  }

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DioException catch (e) {
      final data = e.response?.data;
      final message = data is Map && data['detail'] != null
          ? '${data['detail']}'
          : e.type == DioExceptionType.connectionTimeout || e.type == DioExceptionType.connectionError
              ? 'Cannot connect to NOVA HOME. Check your API address and network.'
              : e.message ?? 'The request could not be completed.';
      throw NovaApiException(message, statusCode: e.response?.statusCode);
    }
  }
}
