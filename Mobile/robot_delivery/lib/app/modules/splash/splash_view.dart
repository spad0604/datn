import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/storage/secure_token_storage.dart';
import 'package:robot_delivery/app/data/repositories/auth_repository.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';

class SplashView extends StatefulWidget {
  const SplashView({super.key});

  @override
  State<SplashView> createState() => _SplashViewState();
}

class _SplashViewState extends State<SplashView> {
  @override
  void initState() {
    super.initState();
    // Dùng addPostFrameCallback để đảm bảo widget đã build xong trước khi navigate
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkAuth();
    });
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(milliseconds: 1000));

    final tokenStorage = SecureTokenStorage();
    final refreshToken = await tokenStorage.readRefreshToken();

    print('[Splash] refreshToken found: ${refreshToken != null && refreshToken.isNotEmpty}');

    if (refreshToken == null || refreshToken.isEmpty) {
      print('[Splash] No refresh token → go to LOGIN');
      Get.offAllNamed(Routes.LOGIN);
      return;
    }

    // Thử gọi refresh token API
    try {
      print('[Splash] Calling refresh token API...');
      final authRepo = AuthRepository();
      final response = await authRepo.refreshToken(refreshToken: refreshToken);

      print('[Splash] Refresh response: ${response.message}, data: ${response.data}');

      if (response.data != null && response.data!.token.isNotEmpty) {
        await tokenStorage.writeTokens(
          accessToken: response.data!.token,
          refreshToken: response.data!.refreshToken,
        );
        print('[Splash] Token refreshed → go to HOME');
        Get.offAllNamed(Routes.HOME);
      } else {
        print('[Splash] Refresh failed (empty data) → go to LOGIN');
        await tokenStorage.clearTokens();
        Get.offAllNamed(Routes.LOGIN);
      }
    } catch (e) {
      print('[Splash] Refresh error: $e → go to LOGIN');
      await tokenStorage.clearTokens();
      Get.offAllNamed(Routes.LOGIN);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                color: AppColors.primary10,
                borderRadius: BorderRadius.circular(28),
              ),
              child: const Icon(
                Icons.smart_toy_outlined,
                size: 48,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Robot Delivery',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: AppColors.slate900,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Giao hàng thông minh',
              style: TextStyle(fontSize: 14, color: AppColors.slate500),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2),
          ],
        ),
      ),
    );
  }
}
