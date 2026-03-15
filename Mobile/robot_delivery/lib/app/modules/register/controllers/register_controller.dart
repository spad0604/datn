import 'package:flutter/material.dart';
import 'package:flutter_easyloading/flutter_easyloading.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';
import 'package:robot_delivery/app/data/models/request/register_request.dart';
import 'package:robot_delivery/app/data/repositories/auth_repository.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';

class RegisterController extends GetxController {
  final AuthRepository _authRepository = Get.find<AuthRepository>();

  final TextEditingController usernameController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController confirmPasswordController = TextEditingController();
  final TextEditingController firstNameController = TextEditingController();
  final TextEditingController lastNameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();
  final TextEditingController addressController = TextEditingController();

  final RxBool isShowPassword = false.obs;
  final RxBool isShowConfirmPassword = false.obs;

  void toggleShowPassword() => isShowPassword.toggle();
  void toggleShowConfirmPassword() => isShowConfirmPassword.toggle();

  Future<void> register() async {
    if (!_validate()) return;

    EasyLoading.show(status: AppTranslationKeys.loading.tr);

    final request = RegisterRequest(
      username: usernameController.text.trim(),
      password: passwordController.text.trim(),
      firstName: firstNameController.text.trim(),
      lastName: lastNameController.text.trim(),
      email: emailController.text.trim(),
      phoneNumber: phoneController.text.trim(),
      address: addressController.text.trim(),
    );

    try {
      final response = await _authRepository.register(request);
      EasyLoading.dismiss();

      if (response.data != null) {
        AppSnackbar.success(AppTranslationKeys.success.tr);
        Get.offAllNamed(Routes.LOGIN);
      } else {
        AppSnackbar.error(response.message ?? AppTranslationKeys.error.tr);
      }
    } catch (e) {
      EasyLoading.dismiss();
      AppSnackbar.error(e.toString());
    }
  }

  bool _validate() {
    if (usernameController.text.isEmpty ||
        passwordController.text.isEmpty ||
        firstNameController.text.isEmpty ||
        lastNameController.text.isEmpty ||
        emailController.text.isEmpty ||
        phoneController.text.isEmpty ||
        addressController.text.isEmpty) {
      AppSnackbar.error(AppTranslationKeys.emailRequired.tr); // Using emailRequired as generic missing field for now
      return false;
    }

    if (passwordController.text != confirmPasswordController.text) {
      AppSnackbar.error(AppTranslationKeys.passwordMismatch.tr);
      return false;
    }

    if (passwordController.text.length < 6) {
      AppSnackbar.error(AppTranslationKeys.passwordTooShort.tr);
      return false;
    }

    if (!GetUtils.isEmail(emailController.text)) {
      AppSnackbar.error(AppTranslationKeys.emailInvalid.tr);
      return false;
    }

    return true;
  }

  @override
  void onClose() {
    usernameController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
    firstNameController.dispose();
    lastNameController.dispose();
    emailController.dispose();
    phoneController.dispose();
    addressController.dispose();
    super.onClose();
  }
}
