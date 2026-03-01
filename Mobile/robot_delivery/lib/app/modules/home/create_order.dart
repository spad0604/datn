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
          AppTranslationKeys.createNewOrder.tr,
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
                title: AppTranslationKeys.recipientName.tr,
                isRequired: true,
                suffixIcon: Icons.person_outline,
              ),
              const SizedBox(height: 16),
              CustomTextfield(
                hintText: 'e.g. 456 Warehouse Rd, City, Country',
                title: AppTranslationKeys.shippingLocation.tr,
                controller: homeController.shippingLocationController,
                prefixIcon: Icons.location_on_outlined,
                suffixIcon: Icons.map_outlined,
                onSuffixIconPressed: () {
                  homeController.pickShippingLocationFromMap();
                },
                onChanged: homeController.onShippingQueryChanged,
              ),
              Obx(() {
                if (homeController.isSearchingShipping.value) {
                  return const Padding(
                    padding: EdgeInsets.only(top: 12),
                    child: LinearProgressIndicator(
                      color: AppColors.primary,
                      backgroundColor: AppColors.slate200,
                    ),
                  );
                }

                final suggestions = homeController.shippingSuggestions;
                if (suggestions.isEmpty) return const SizedBox.shrink();

                return Container(
                  margin: const EdgeInsets.only(top: 12),
                  decoration: BoxDecoration(
                    color: AppColors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.slate300, width: 1),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: suggestions.length,
                    separatorBuilder: (context, index) =>
                        const Divider(height: 1, color: AppColors.slate200),
                    itemBuilder: (context, index) {
                      final item = suggestions[index];
                      return ListTile(
                        dense: true,
                        title: Text(
                          item.displayName,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: AppColors.slate900,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        trailing: const Icon(
                          Icons.north_west,
                          color: AppColors.slate400,
                          size: 18,
                        ),
                        onTap: () {
                          homeController.selectShippingSuggestion(item);
                          FocusScope.of(context).unfocus();
                        },
                      );
                    },
                  ),
                );
              }),
              const SizedBox(height: 16),
              CustomTextfield(
                controller: homeController.recipientAddressController,
                hintText: 'e.g. 123 Main St, City, Country',
                title: AppTranslationKeys.recipientAddress.tr,
                isRequired: true,
                prefixIcon: Icons.location_on_outlined,
                suffixIcon: Icons.map_outlined,
                onSuffixIconPressed: () {
                  homeController.pickRecipientAddressFromMap();
                },
                onChanged: homeController.onRecipientQueryChanged,
              ),
              Obx(() {
                if (homeController.isSearchingRecipient.value) {
                  return const Padding(
                    padding: EdgeInsets.only(top: 12),
                    child: LinearProgressIndicator(
                      color: AppColors.primary,
                      backgroundColor: AppColors.slate200,
                    ),
                  );
                }

                final suggestions = homeController.recipientSuggestions;
                if (suggestions.isEmpty) return const SizedBox.shrink();

                return Container(
                  margin: const EdgeInsets.only(top: 12),
                  decoration: BoxDecoration(
                    color: AppColors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.slate300, width: 1),
                  ),
                  child: ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: suggestions.length,
                    separatorBuilder: (context, index) =>
                        const Divider(height: 1, color: AppColors.slate200),
                    itemBuilder: (context, index) {
                      final item = suggestions[index];
                      return ListTile(
                        dense: true,
                        title: Text(
                          item.displayName,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: AppColors.slate900,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        trailing: const Icon(
                          Icons.north_west,
                          color: AppColors.slate400,
                          size: 18,
                        ),
                        onTap: () {
                          homeController.selectRecipientSuggestion(item);
                          FocusScope.of(context).unfocus();
                        },
                      );
                    },
                  ),
                );
              }),
              const SizedBox(height: 16),
              CustomTextfield(
                controller: homeController.weightController,
                hintText: '0.0',
                title: AppTranslationKeys.packageWeight.tr,
              ),
              const SizedBox(height: 40),
              CustomButton(
                text: AppTranslationKeys.submitOrder.tr,
                textColor: AppColors.white,
                backgroundColor: AppColors.primary,
                onPressed: () {
                  AppSnackbar.success(AppTranslationKeys.submitOrder.tr);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
