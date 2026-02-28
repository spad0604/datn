import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';

import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/common/widget/custom_icon_button.dart';
import 'package:robot_delivery/app/common/widget/custom_textfield.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

import '../controllers/login_controller.dart';

class LoginView extends GetView<LoginController> {
  const LoginView({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 40),
                Center(
                  child: CustomIconButton(
                    backGroundColor: AppColors.primary.withValues(alpha: 0.1),
                    icon: Icons.fire_truck,
                    iconColor: AppColors.primary,
                    onPressed: () {},
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Robot Express',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: AppColors.slate900,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Robot delivery logistics management system',
                  style: TextStyle(fontSize: 14, color: AppColors.slate500),
                ),
                const SizedBox(height: 24),
                Obx(
                  () => _RolePicker(
                    value: controller.role.value,
                    onChanged: controller.setRole,
                  ),
                ),
                const SizedBox(height: 24),
                CustomTextfield(
                  controller: controller.usernameController,
                  prefixIcon: Icons.email_outlined,
                  hintText: AppTranslationKeys.emailHint.tr,
                  title: 'Email',
                ),
                const SizedBox(height: 16),
                Obx(
                  () => CustomTextfield(
                    controller: controller.passwordController,
                    prefixIcon: Icons.lock_outline,
                    suffixIcon: !controller.isShowPassword.value == true
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                    hintText: AppTranslationKeys.passwordHint.tr,
                    title: AppTranslationKeys.password.tr,
                    isPassword: !controller.isShowPassword.value,
                    onSuffixIconPressed: () {
                      controller.isShowPassword.value =
                          !controller.isShowPassword.value;
                    },
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () {},
                      child: Text(
                        AppTranslationKeys.forgotPassword.tr,
                        style: TextStyle(
                          color: AppColors.primary,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                CustomButton(
                  text: AppTranslationKeys.login.tr,
                  textColor: AppColors.white,
                  backgroundColor: AppColors.primary,
                  onPressed: () {
                    controller.onSubmitLogin(
                      controller.usernameController.text,
                      controller.passwordController.text,
                    );
                  },
                ),
                const SizedBox(height: 20),
                RichText(
                  text: TextSpan(
                    children: [
                      TextSpan(
                        text: '${AppTranslationKeys.dontHaveAccount.tr} ',
                        style: TextStyle(
                          color: AppColors.slate500,
                          fontSize: 14,
                        ),
                      ),
                      TextSpan(
                        text: AppTranslationKeys.createAccount.tr,
                        style: TextStyle(
                          color: AppColors.primary,
                          fontWeight: FontWeight.w500,
                          fontSize: 14,
                        ),
                        recognizer: TapGestureRecognizer()..onTap = () {},
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  AppTranslationKeys.orContinueWith.tr,
                  style: TextStyle(color: AppColors.slate400, fontSize: 14),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CustomIconButton(
                      backGroundColor: AppColors.primary.withValues(alpha: 0.1),
                      icon: Icons.g_mobiledata_outlined,
                      iconColor: AppColors.primary,
                      onPressed: () {},
                    ),
                    const SizedBox(width: 16),
                    CustomIconButton(
                      backGroundColor: AppColors.primary.withValues(alpha: 0.1),
                      icon: Icons.facebook_outlined,
                      iconColor: AppColors.primary,
                      onPressed: () {},
                    ),
                    const SizedBox(width: 16),
                    CustomIconButton(
                      backGroundColor: AppColors.primary.withValues(alpha: 0.1),
                      icon: Icons.apple_outlined,
                      iconColor: AppColors.primary,
                      onPressed: () {},
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RolePicker extends StatelessWidget {
  const _RolePicker({
    required this.value,
    required this.onChanged,
  });

  final LoginRole value;
  final ValueChanged<LoginRole> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: AppColors.slate200,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Stack(
        children: [
          AnimatedAlign(
            alignment: value == LoginRole.buyer
                ? Alignment.centerLeft
                : Alignment.centerRight,
            duration: const Duration(milliseconds: 220),
            curve: Curves.easeOutCubic,
            child: FractionallySizedBox(
              widthFactor: 0.5,
              heightFactor: 1,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 220),
                curve: Curves.easeOutCubic,
                decoration: BoxDecoration(
                  color: AppColors.white,
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            ),
          ),
          Row(
            children: [
              Expanded(
                child: _RoleItem(
                  text: AppTranslationKeys.buyer.tr,
                  selected: value == LoginRole.buyer,
                  onTap: () => onChanged(LoginRole.buyer),
                ),
              ),
              Expanded(
                child: _RoleItem(
                  text: AppTranslationKeys.seller.tr,
                  selected: value == LoginRole.seller,
                  onTap: () => onChanged(LoginRole.seller),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RoleItem extends StatelessWidget {
  const _RoleItem({
    required this.text,
    required this.selected,
    required this.onTap,
  });

  final String text;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(999),
        onTap: onTap,
        child: Center(
          child: AnimatedDefaultTextStyle(
            duration: const Duration(milliseconds: 180),
            curve: Curves.easeOut,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: !selected ? AppColors.slate700 : AppColors.primary,
            ),
            child: Text(text),
          ),
        ),
      ),
    );
  }
}
