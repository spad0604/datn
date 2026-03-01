import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/common/widget/custom_textfield.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';
import 'package:robot_delivery/app/modules/home/home_controller.dart';

class CreateNewOrder extends StatelessWidget {
  CreateNewOrder({super.key});

  final homeController = Get.find<HomeController>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        backgroundColor: AppColors.slate100,
        centerTitle: true,
        title: Text(
          'Create New Order',
          style: TextStyle(
            color: AppColors.slate900,
            fontWeight: FontWeight.w600,
            fontSize: 18,
          ),
        ),
      ),
      body: Container(
        padding: const EdgeInsets.all(24.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const Text(
                'Fill in the details below to schedule a pickup',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: AppColors.slate900,
                ),
              ),
              const SizedBox(height: 24),
              CustomTextfield(
                controller: homeController.recipientNameController,
                hintText: 'e.g. Jan Doe',
                title: 'Recipient Name',
                isRequired: true,
              ),
              const SizedBox(height: 16),
              CustomTextfield(
                controller: homeController.recipientAddressController,
                hintText: 'e.g. 123 Main St, City, Country',
                title: 'Recipient Address',
                isRequired: true,
              ),
              const SizedBox(height: 16),
              CustomTextfield(
                controller: homeController.weightController,
                hintText: '0.0',
                title: 'Package Weight',
              ),
              const SizedBox(height: 40),
              CustomButton(
                text: 'Summon Robot',
                textColor: AppColors.white,
                backgroundColor: AppColors.primary,
                onPressed: () {
                  AppSnackbar.success(AppTranslationKeys.loginSuccess.tr);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
