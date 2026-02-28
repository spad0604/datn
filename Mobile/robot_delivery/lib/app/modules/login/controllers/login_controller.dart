import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';

enum LoginRole { buyer, seller }

class LoginController extends GetxController {
  final Rx<bool> isShowPassword = false.obs;

  final Rx<LoginRole> role = LoginRole.buyer.obs;

  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  void setRole(LoginRole value) {
    role.value = value;
  }

  void onSubmitLogin(String username, String password) {
    if (username == 'admin' && password == 'password') {
      Get.offAllNamed(Routes.HOME);
      Future.microtask(() {
        AppSnackbar.success(AppTranslationKeys.loginSuccess.tr);
      });
      return;
    }

    AppSnackbar.error(AppTranslationKeys.loginError.tr);
  }

  @override
  void onClose() {
    usernameController.dispose();
    passwordController.dispose();
    super.onClose();
  }
}
