import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

import '../controllers/notifications_controller.dart';

class NotificationsView extends GetView<NotificationsController> {
  const NotificationsView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        backgroundColor: AppColors.slate100,
        centerTitle: true,
        title: Text(
          AppTranslationKeys.notifications.tr,
          style: const TextStyle(
            color: AppColors.slate900,
            fontWeight: FontWeight.w600,
            fontSize: 18,
          ),
        ),
        actions: [
          TextButton(
            onPressed: controller.markAllRead,
            child: Text(
              AppTranslationKeys.markAllRead.tr,
              style: const TextStyle(
                color: AppColors.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Obx(() {
              return SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _FilterChip(
                      label: AppTranslationKeys.all.tr,
                      selected:
                          controller.filter.value == NotificationFilter.all,
                      onSelected: (_) =>
                          controller.filter.value = NotificationFilter.all,
                    ),
                    const SizedBox(width: 8),
                    _FilterChip(
                      label: AppTranslationKeys.alerts.tr,
                      selected:
                          controller.filter.value == NotificationFilter.alerts,
                      onSelected: (_) =>
                          controller.filter.value = NotificationFilter.alerts,
                    ),
                    const SizedBox(width: 8),
                    _FilterChip(
                      label: AppTranslationKeys.updates.tr,
                      selected:
                          controller.filter.value == NotificationFilter.updates,
                      onSelected: (_) =>
                          controller.filter.value = NotificationFilter.updates,
                    ),
                    const SizedBox(width: 8),
                    _FilterChip(
                      label: AppTranslationKeys.promos.tr,
                      selected:
                          controller.filter.value == NotificationFilter.promos,
                      onSelected: (_) =>
                          controller.filter.value = NotificationFilter.promos,
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 12),
            Expanded(
              child: Obx(() {
                final items = controller.filteredItems;
                final newItems = items.where((e) => e.isUnread.value).toList();
                final earlierItems = items
                    .where((e) => !e.isUnread.value)
                    .toList();

                return ListView(
                  children: [
                    if (newItems.isNotEmpty) ...[
                      _SectionHeader(title: AppTranslationKeys.newLabel.tr),
                      const SizedBox(height: 8),
                      ...newItems.map((e) => _NotificationTile(item: e)),
                      const SizedBox(height: 16),
                    ],
                    if (earlierItems.isNotEmpty) ...[
                      _SectionHeader(title: AppTranslationKeys.earlierLabel.tr),
                      const SizedBox(height: 8),
                      ...earlierItems.map((e) => _NotificationTile(item: e)),
                    ],
                    if (newItems.isEmpty && earlierItems.isEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 24),
                        child: Center(
                          child: Text(
                            AppTranslationKeys.noNotifications.tr,
                            style: const TextStyle(
                              color: AppColors.slate500,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                  ],
                );
              }),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;

  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: const TextStyle(
        color: AppColors.slate600,
        fontWeight: FontWeight.w700,
        fontSize: 12,
        letterSpacing: 0.6,
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool selected;
  final ValueChanged<bool> onSelected;

  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return CustomButton(
      text: label,
      textColor: selected ? AppColors.primary : AppColors.slate600,
      backgroundColor:
          selected ? AppColors.primary.withAlpha(26) : AppColors.white,
      borderColor: selected ? AppColors.primary : AppColors.slate200,
      onPressed: () => onSelected(true),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      borderRadius: BorderRadius.circular(9999),
      fontSize: 13,
      fontWeight: FontWeight.w600,
    );
  }
}

class _NotificationTile extends StatelessWidget {
  final NotificationItem item;

  const _NotificationTile({required this.item});

  IconData get _icon {
    switch (item.category) {
      case NotificationFilter.alerts:
        return Icons.warning_amber_rounded;
      case NotificationFilter.updates:
        return Icons.notifications_active_outlined;
      case NotificationFilter.promos:
        return Icons.local_offer_outlined;
      case NotificationFilter.all:
        return Icons.notifications_none;
    }
  }

  Color get _iconBg {
    switch (item.category) {
      case NotificationFilter.alerts:
        return AppColors.orangeSoftAlt;
      case NotificationFilter.updates:
        return AppColors.indigoSoft;
      case NotificationFilter.promos:
        return AppColors.purpleSoftAlt;
      case NotificationFilter.all:
        return AppColors.slate100;
    }
  }

  Color get _iconColor {
    switch (item.category) {
      case NotificationFilter.alerts:
        return AppColors.warning;
      case NotificationFilter.updates:
        return AppColors.info;
      case NotificationFilter.promos:
        return AppColors.purple;
      case NotificationFilter.all:
        return AppColors.slate600;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.slate100, width: 1),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: _iconBg,
            borderRadius: BorderRadius.circular(9999),
          ),
          child: Icon(_icon, color: _iconColor, size: 22),
        ),
        title: Text(
          item.title,
          style: const TextStyle(
            color: AppColors.slate900,
            fontWeight: FontWeight.w700,
            fontSize: 14,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Text(
            item.body,
            style: const TextStyle(
              color: AppColors.slate600,
              fontWeight: FontWeight.w500,
              fontSize: 13,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),
        trailing: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              item.timeLabel,
              style: const TextStyle(
                color: AppColors.slate400,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 10),
            Obx(() {
              return Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: item.isUnread.value
                      ? AppColors.primary
                      : AppColors.white,
                  borderRadius: BorderRadius.circular(9999),
                  border: Border.all(color: AppColors.slate200, width: 1),
                ),
              );
            }),
          ],
        ),
        onTap: () {
          item.isUnread.value = false;
        },
      ),
    );
  }
}
