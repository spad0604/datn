import 'package:flutter/material.dart';

import 'package:get/get.dart';
import 'package:intl/intl.dart';
import 'package:robot_delivery/app/common/enum/item_enum.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';

import '../controllers/orders_controller.dart';

part 'delivery_history_card.dart';

enum DeliveryHistoryFilter { all, delivered, pending, cancelled }

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

  static DeliveryHistoryItem fromOrder(OrderResponse order) {
    final status = _mapStatus(order.status);
    return DeliveryHistoryItem(
      title: 'Order #${order.orderId}',
      sender: order.senderName,
      dateTimeText: DateFormat('MMM d, yyyy • h:mm a').format(order.createdAt.toLocal()),
      status: status,
      leadingIcon: _leadingIcon(status),
      leadingBg: _leadingBg(status),
      leadingFg: _leadingFg(status),
    );
  }

  static ItemEnum _mapStatus(String s) {
    switch (s.toUpperCase()) {
      case 'DELIVERED':
        return ItemEnum.delivered;
      case 'WAIT_ROBOT':
      case 'PENDING':
      case 'DELIVERING':
        return ItemEnum.arriving;
      default:
        return ItemEnum.arriving;
    }
  }

  static IconData _leadingIcon(ItemEnum status) {
    switch (status) {
      case ItemEnum.delivered:
        return Icons.check_circle_outline;
      case ItemEnum.cancelled:
        return Icons.cancel_outlined;
      case ItemEnum.arriving:
        return Icons.local_shipping_outlined;
    }
  }

  static Color _leadingBg(ItemEnum status) {
    switch (status) {
      case ItemEnum.delivered:
        return AppColors.primary10;
      case ItemEnum.cancelled:
        return AppColors.redSoft;
      case ItemEnum.arriving:
        return AppColors.orangeSoft;
    }
  }

  static Color _leadingFg(ItemEnum status) {
    switch (status) {
      case ItemEnum.delivered:
        return AppColors.primary;
      case ItemEnum.cancelled:
        return AppColors.error;
      case ItemEnum.arriving:
        return AppColors.warning;
    }
  }
}

class OrdersView extends GetView<OrdersController> {
  const OrdersView({super.key});

  @override
  Widget build(BuildContext context) {
    final Rx<DeliveryHistoryFilter> filter = DeliveryHistoryFilter.all.obs;

    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        shadowColor: AppColors.slate100,
        backgroundColor: AppColors.white,
        elevation: 4,
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
      ),
      body: Column(
        children: [
          // Filter chips
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
                    buildFilterChip(value: DeliveryHistoryFilter.all, label: AppTranslationKeys.all.tr),
                    const SizedBox(width: 10),
                    buildFilterChip(value: DeliveryHistoryFilter.delivered, label: AppTranslationKeys.deliveredStatus.tr),
                    const SizedBox(width: 10),
                    buildFilterChip(value: DeliveryHistoryFilter.pending, label: AppTranslationKeys.pending.tr),
                    const SizedBox(width: 10),
                    buildFilterChip(value: DeliveryHistoryFilter.cancelled, label: AppTranslationKeys.cancelledStatus.tr),
                  ],
                ),
              );
            }),
          ),

          // Order list
          Expanded(
            child: Obx(() {
              final allOrders = controller.myOrders;

              bool matchesFilter(OrderResponse order) {
                final mapped = DeliveryHistoryItem._mapStatus(order.status);
                return switch (filter.value) {
                  DeliveryHistoryFilter.all => true,
                  DeliveryHistoryFilter.delivered => mapped == ItemEnum.delivered,
                  DeliveryHistoryFilter.cancelled => mapped == ItemEnum.cancelled,
                  DeliveryHistoryFilter.pending => mapped == ItemEnum.arriving,
                };
              }

              final filtered = allOrders.where(matchesFilter).toList();

              if (filtered.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.inbox_outlined, size: 72, color: AppColors.slate300),
                      const SizedBox(height: 16),
                      Text(
                        AppTranslationKeys.noOrders.tr,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: AppColors.slate400,
                        ),
                      ),
                    ],
                  ),
                );
              }

              return RefreshIndicator(
                onRefresh: controller.refresh,
                child: ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final order = filtered[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 14),
                      child: GestureDetector(
                        onTap: () => Get.toNamed(
                          '/order-details',
                          arguments: order,
                        ),
                        child: DeliveryHistoryCard(
                          item: DeliveryHistoryItem.fromOrder(order),
                        ),
                      ),
                    );
                  },
                ),
              );
            }),
          ),
        ],
      ),
    );
  }
}