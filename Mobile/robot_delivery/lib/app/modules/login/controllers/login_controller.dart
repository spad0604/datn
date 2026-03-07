import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/data/models/request/login_request.dart';
import 'package:robot_delivery/app/data/repositories/auth_repository.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';

enum LoginRole { buyer, seller }

class LoginController extends GetxController {
  final Rx<bool> isShowPassword = false.obs;

  final Rx<LoginRole> role = LoginRole.buyer.obs;

  final TextEditingController usernameController = TextEditingController();

  final TextEditingController passwordController = TextEditingController();

  final AuthRepository authRepository = Get.find<AuthRepository>();

  void setRole(LoginRole value) {
    role.value = value;
  }

  void onSubmitLogin(String username, String password) {
    try {
      authRepository
          .login(LoginRequest(username: username, password: password))
          .then((value) {
            if (value != null) {
              AppSnackbar.success(AppTranslationKeys.loginSuccess.tr);
              Get.offAllNamed(Routes.HOME);
            } else {
              AppSnackbar.error(AppTranslationKeys.loginError.tr);
            }
          });
    } catch (e) {
      AppSnackbar.error(AppTranslationKeys.loginError.tr);
    }
  }

  @override
  void onClose() {
    usernameController.dispose();
    passwordController.dispose();
    super.onClose();
  }
}
