import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../data/models/auth_tokens.dart';

class SecureTokenStorage {
  SecureTokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
            );

  final FlutterSecureStorage _storage;

  static const _kAccessTokenKey = 'access_token';
  static const _kRefreshTokenKey = 'refresh_token';

  Future<String?> readAccessToken() => _storage.read(key: _kAccessTokenKey);

  Future<String?> readRefreshToken() => _storage.read(key: _kRefreshTokenKey);

  Future<void> writeAccessToken(String token) =>
      _storage.write(key: _kAccessTokenKey, value: token);

  Future<void> writeRefreshToken(String token) =>
      _storage.write(key: _kRefreshTokenKey, value: token);

  Future<void> writeTokens({required String accessToken, String? refreshToken}) async {
    await writeAccessToken(accessToken);
    if (refreshToken != null && refreshToken.isNotEmpty) {
      await writeRefreshToken(refreshToken);
    }
  }

  Future<void> writeAuthTokens(AuthTokens tokens) =>
      writeTokens(accessToken: tokens.accessToken, refreshToken: tokens.refreshToken);

  Future<void> clearTokens() async {
    await _storage.delete(key: _kAccessTokenKey);
    await _storage.delete(key: _kRefreshTokenKey);
  }
}
