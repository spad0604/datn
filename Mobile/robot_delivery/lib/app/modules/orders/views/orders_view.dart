import 'package:flutter/material.dart';

import 'package:get/get.dart';
import 'package:robot_delivery/app/common/enum/item_enum.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

import '../controllers/orders_controller.dart';

enum DeliveryHistoryFilter {
  all,
  delivered,
  pending,
  cancelled,
}

class DeliveryHistoryItem {
  const DeliveryHistoryItem({
    required this.title,
    required this.sender,
    required this.dateTimeText,
    required this.status,
    required this.leadingIcon,
    required this.leadingBg,
    required this.leadingFg,
    this.showMapPreview = false,
  });

  final String title;
  final String sender;
  final String dateTimeText;
  final ItemEnum status;

  final IconData leadingIcon;
  final Color leadingBg;
  final Color leadingFg;
  final bool showMapPreview;
}

class OrdersView extends GetView<OrdersController> {
  const OrdersView({super.key});
  @override
  Widget build(BuildContext context) {
    final Rx<DeliveryHistoryFilter> filter = DeliveryHistoryFilter.all.obs;

    final thisWeek = <DeliveryHistoryItem>[
      DeliveryHistoryItem(
        title: 'Stitch Fix Order #4922',
        sender: 'Stitch Fix Inc.',
        dateTimeText: 'Oct 24, 2023 • 2:30 PM',
        status: ItemEnum.delivered,
        leadingIcon: Icons.local_shipping_outlined,
        leadingBg: AppColors.primary10,
        leadingFg: AppColors.primary,
        showMapPreview: true,
      ),
      DeliveryHistoryItem(
        title: 'Nike Air Max',
        sender: 'Nike Store',
        dateTimeText: 'Oct 22, 2023 • 10:15 AM',
        status: ItemEnum.delivered,
        leadingIcon: Icons.inventory_2_outlined,
        leadingBg: AppColors.orangeSoft,
        leadingFg: AppColors.warning,
      ),
    ];

    final lastWeek = <DeliveryHistoryItem>[
      DeliveryHistoryItem(
        title: 'Threadless Tees',
        sender: 'Threadless',
        dateTimeText: 'Oct 18, 2023 • 4:45 PM',
        status: ItemEnum.delivered,
        leadingIcon: Icons.receipt_long_outlined,
        leadingBg: AppColors.purpleSoft,
        leadingFg: AppColors.purple,
      ),
      DeliveryHistoryItem(
        title: 'Books Bundle',
        sender: 'Amazon',
        dateTimeText: 'Oct 15, 2023 • 9:00 AM',
        status: ItemEnum.cancelled,
        leadingIcon: Icons.cancel_outlined,
        leadingBg: AppColors.redSoft,
        leadingFg: AppColors.error,
      ),
    ];

    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        backgroundColor: AppColors.white,
        elevation: 0,
        centerTitle: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            bottomLeft: Radius.circular(24),
            bottomRight: Radius.circular(24),
          ),
        ),
        title: Text(
          AppTranslationKeys.deliveryHistory.tr,
          style: const TextStyle(
            color: AppColors.slate900,
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        actions: [
          IconButton(
            onPressed: () {},
            icon: const Icon(Icons.tune, color: AppColors.slate900),
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
            child: Obx(() {
              Widget buildFilterChip({
                required DeliveryHistoryFilter value,
                required String label,
              }) {
                final isSelected = filter.value == value;
                return CustomButton(
                  text: label,
                  textColor: isSelected ? AppColors.white : AppColors.slate900,
                  backgroundColor: isSelected ? AppColors.primary : AppColors.white,
                  borderColor: isSelected ? null : AppColors.slate200,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  borderRadius: BorderRadius.circular(999),
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  onPressed: () => filter.value = value,
                );
              }

              return SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    buildFilterChip(
                      value: DeliveryHistoryFilter.all,
                      label: AppTranslationKeys.all.tr,
                    ),
                    const SizedBox(width: 10),
                    buildFilterChip(
                      value: DeliveryHistoryFilter.delivered,
                      label: AppTranslationKeys.deliveredStatus.tr,
                    ),
                    const SizedBox(width: 10),
                    buildFilterChip(
                      value: DeliveryHistoryFilter.pending,
                      label: AppTranslationKeys.pending.tr,
                    ),
                    const SizedBox(width: 10),
                    buildFilterChip(
                      value: DeliveryHistoryFilter.cancelled,
                      label: AppTranslationKeys.cancelledStatus.tr,
                    ),
                  ],
                ),
              );
            }),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
              child: Obx(() {
                bool matchesFilter(DeliveryHistoryItem item) {
                  return switch (filter.value) {
                    DeliveryHistoryFilter.all => true,
                    DeliveryHistoryFilter.delivered => item.status == ItemEnum.delivered,
                    DeliveryHistoryFilter.cancelled => item.status == ItemEnum.cancelled,
                    DeliveryHistoryFilter.pending => item.status == ItemEnum.arriving,
                  };
                }

                final filteredThisWeek = thisWeek.where(matchesFilter).toList();
                final filteredLastWeek = lastWeek.where(matchesFilter).toList();

                Widget sectionTitle(String text) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(
                      text,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: AppColors.slate500,
                        letterSpacing: 1.2,
                      ),
                    ),
                  );
                }

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    sectionTitle(AppTranslationKeys.thisWeek.tr),
                    ...filteredThisWeek.map((e) => Padding(
                          padding: const EdgeInsets.only(bottom: 14),
                          child: DeliveryHistoryCard(item: e),
                        )),
                    const SizedBox(height: 8),
                    sectionTitle(AppTranslationKeys.lastWeek.tr),
                    ...filteredLastWeek.map((e) => Padding(
                          padding: const EdgeInsets.only(bottom: 14),
                          child: DeliveryHistoryCard(item: e),
                        )),
                  ],
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}

class DeliveryHistoryCard extends StatelessWidget {
  const DeliveryHistoryCard({super.key, required this.item});

  final DeliveryHistoryItem item;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.slate100, width: 1),
        boxShadow: const [
          BoxShadow(
            color: AppColors.black05,
            blurRadius: 14,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: item.leadingBg,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(item.leadingIcon, color: item.leadingFg, size: 22),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.title,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w800,
                          color: AppColors.slate900,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${AppTranslationKeys.sender.tr} ${item.sender}',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: AppColors.slate600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        item.dateTimeText,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: AppColors.slate400,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                getItemStatusWidget(item.status),
              ],
            ),
            if (item.showMapPreview) ...[
              const SizedBox(height: 12),
              Container(
                height: 96,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: AppColors.grayF6,
                  borderRadius: BorderRadius.circular(18),
                ),
                child: const Center(
                  child: Icon(
                    Icons.map_outlined,
                    color: AppColors.slate300,
                    size: 30,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
