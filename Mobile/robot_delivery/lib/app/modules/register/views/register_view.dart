import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/common/widget/custom_icon_button.dart';
import 'package:robot_delivery/app/common/widget/custom_textfield.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

import '../controllers/register_controller.dart';

class RegisterView extends GetView<RegisterController> {
  const RegisterView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.slate900),
          onPressed: () => Get.back(),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: CustomIconButton(
                  backGroundColor: AppColors.primary.withValues(alpha: 0.1),
                  icon: Icons.person_add_outlined,
                  iconColor: AppColors.primary,
                  onPressed: () {},
                ),
              ),
              const SizedBox(height: 24),
              Center(
                child: Text(
                  AppTranslationKeys.register.tr,
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: AppColors.slate900,
                  ),
                ),
              ),
              const SizedBox(height: 32),
              
              Row(
                children: [
                  Expanded(
                    child: CustomTextfield(
                      controller: controller.firstNameController,
                      title: AppTranslationKeys.firstName.tr,
                      hintText: 'John',
                    ),

                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: CustomTextfield(
                      controller: controller.lastNameController,
                      title: AppTranslationKeys.lastName.tr,
                      hintText: 'Doe',
                    ),

                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              CustomTextfield(
                controller: controller.usernameController,
                prefixIcon: Icons.account_circle_outlined,
                title: AppTranslationKeys.username.tr,
                hintText: 'johndoe123',
              ),

              const SizedBox(height: 16),
              
              CustomTextfield(
                controller: controller.emailController,
                prefixIcon: Icons.email_outlined,
                title: AppTranslationKeys.email.tr,
                hintText: AppTranslationKeys.emailHint.tr,
              ),
              const SizedBox(height: 16),
              
              CustomTextfield(
                controller: controller.phoneController,
                prefixIcon: Icons.phone_outlined,
                title: AppTranslationKeys.phoneNumber.tr,
                hintText: '0123456789',
              ),
              const SizedBox(height: 16),
              
              CustomTextfield(
                controller: controller.addressController,
                prefixIcon: Icons.location_on_outlined,
                title: AppTranslationKeys.addressField.tr,
                hintText: '123 Main St, New York',
              ),
              const SizedBox(height: 16),
              
              Obx(() => CustomTextfield(
                controller: controller.passwordController,
                prefixIcon: Icons.lock_outline,
                suffixIcon: controller.isShowPassword.value
                    ? Icons.visibility_off_outlined
                    : Icons.visibility_outlined,
                title: AppTranslationKeys.password.tr,
                hintText: AppTranslationKeys.passwordHint.tr,
                isPassword: !controller.isShowPassword.value,
                onSuffixIconPressed: controller.toggleShowPassword,
              )),
              const SizedBox(height: 16),
              
              Obx(() => CustomTextfield(
                controller: controller.confirmPasswordController,
                prefixIcon: Icons.lock_outline,
                suffixIcon: controller.isShowConfirmPassword.value
                    ? Icons.visibility_off_outlined
                    : Icons.visibility_outlined,
                title: AppTranslationKeys.confirmPassword.tr,
                hintText: AppTranslationKeys.reEnterPassword.tr,

                isPassword: !controller.isShowConfirmPassword.value,
                onSuffixIconPressed: controller.toggleShowConfirmPassword,
              )),
              
              const SizedBox(height: 32),
              CustomButton(
                text: AppTranslationKeys.register.tr,
                backgroundColor: AppColors.primary,
                textColor: AppColors.white,
                onPressed: controller.register,
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
