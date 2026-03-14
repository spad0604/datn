import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/data/models/request/login_request.dart';
import 'package:robot_delivery/app/data/repositories/auth_repository.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';
import 'package:robot_delivery/app/core/storage/secure_token_storage.dart';

enum LoginRole { buyer, seller }

class LoginController extends GetxController {
  final Rx<bool> isShowPassword = false.obs;

  final Rx<LoginRole> role = LoginRole.buyer.obs;

  final TextEditingController usernameController = TextEditingController();

  final TextEditingController passwordController = TextEditingController();

  final AuthRepository authRepository = Get.find<AuthRepository>();
  final SecureTokenStorage _tokenStorage = Get.find<SecureTokenStorage>();

  void setRole(LoginRole value) {
    role.value = value;
  }

  void onSubmitLogin(String username, String password) async {
    EasyLoading.show(status: AppTranslationKeys.loggingIn.tr);

    // Lấy FCM token trước khi gửi request login
    String? fcmToken;
    try {
      fcmToken = await FirebaseMessaging.instance.getToken();
    } catch (_) {
      // Không block login nếu lấy FCM token thất bại
    }

    authRepository
        .login(LoginRequest(
          username: username.trim(),
          password: password.trim(),
          fcmToken: fcmToken,
        ))
        .then((value) {
          EasyLoading.dismiss();
          if (value.data != null) {
            _tokenStorage.writeTokens(
              accessToken: value.data!.token,
              refreshToken: value.data!.refreshToken,
            );
            AppSnackbar.success(AppTranslationKeys.loginSuccess.tr);
            Get.offAllNamed(Routes.HOME);
          } else {
            AppSnackbar.error(AppTranslationKeys.loginError.tr);
          }
        })
        .catchError((e) {
          EasyLoading.dismiss();
          AppSnackbar.error(AppTranslationKeys.loginError.tr);
        });
  }

  @override
  void onClose() {
    usernameController.dispose();
    passwordController.dispose();
    super.onClose();
  }
}
