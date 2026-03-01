import 'package:flutter/material.dart';
import 'dart:math' as math;

import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/common/widget/custom_textfield.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/modules/profile/views/profile_image.dart';

import '../controllers/profile_controller.dart';

class ProfileView extends GetView<ProfileController> {
  const ProfileView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        backgroundColor: AppColors.slate100,
        title: Text(
          AppTranslationKeys.profileView.tr,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            bottomLeft: Radius.circular(24),
            bottomRight: Radius.circular(24),
          ),
        ),
        shadowColor: AppColors.slate100,
        elevation: 1,
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minHeight: math.max(0, constraints.maxHeight - 32),
              ),
              child: IntrinsicHeight(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Obx(
                      () => Column(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          const SizedBox(height: 24),
                          ProfileImage(),
                          const SizedBox(height: 16),
                          CustomTextfield(
                            suffixIcon: controller.isUpdatingProfile.value
                                ? null
                                : Icons.edit_outlined,
                            hintText: AppTranslationKeys.userOrShopName.tr,
                            title: AppTranslationKeys.userOrShopName.tr,
                            isRequired: false,
                            readOnly: controller.isUpdatingProfile.value,
                            controller: controller.nameController,
                          ),
                          const SizedBox(height: 16),
                          CustomTextfield(
                            suffixIcon: controller.isUpdatingProfile.value
                                ? null
                                : Icons.edit_outlined,
                            hintText: AppTranslationKeys.phoneNumber.tr,
                            title: AppTranslationKeys.phoneNumber.tr,
                            isRequired: false,
                            readOnly: controller.isUpdatingProfile.value,
                            controller: controller.phoneController,
                          ),
                          const SizedBox(height: 16),
                          CustomTextfield(
                            suffixIcon: controller.isUpdatingProfile.value
                                ? null
                                : Icons.edit_outlined,
                            hintText: AppTranslationKeys.addressField.tr,
                            title: AppTranslationKeys.addressField.tr,
                            isRequired: false,
                            readOnly: controller.isUpdatingProfile.value,
                            controller: controller.addressController,
                          ),
                        ],
                      ),
                    ),
                    Column(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        CustomButton(
                          text: AppTranslationKeys.updateProfile.tr,
                          textColor: AppColors.white,
                          backgroundColor: AppColors.primary,
                          onPressed: () {
                            controller.updateProfileButtonPressed();
                          },
                        ),
                        const SizedBox(height: 16),
                        CustomButton(
                          text: AppTranslationKeys.logout.tr,
                          textColor: AppColors.white,
                          backgroundColor: AppColors.error,
                          onPressed: () {},
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
