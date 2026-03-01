import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

enum ItemEnum {
  delivered,
  cancelled,
  arriving;

  String get name {
    switch (this) {
      case ItemEnum.delivered:
        return AppTranslationKeys.deliveredStatus.tr;
      case ItemEnum.cancelled:
        return AppTranslationKeys.cancelledStatus.tr;
      case ItemEnum.arriving:
        return AppTranslationKeys.pending.tr;
    }
  }
}

IconData getItemIcon(ItemEnum item) {
  switch (item) {
    case ItemEnum.delivered:
      return Icons.check_circle_outline;
    case ItemEnum.cancelled:
      return Icons.cancel_outlined;
    case ItemEnum.arriving:
      return Icons.local_shipping_outlined;
  }
}

String getItemStatus(ItemEnum item) {
  switch (item) {
    case ItemEnum.delivered:
      return AppTranslationKeys.deliveredStatus.tr;
    case ItemEnum.cancelled:
      return AppTranslationKeys.cancelledStatus.tr;
    case ItemEnum.arriving:
      return AppTranslationKeys.pending.tr;
  }
}

Color getItemColor(ItemEnum item) {
  switch (item) {
    case ItemEnum.delivered:
      return AppColors.primary;
    case ItemEnum.cancelled:
      return AppColors.error;
    case ItemEnum.arriving:
      return AppColors.warning;
  }
}

Widget getItemStatusWidget(ItemEnum item)
{
  return Column(
    mainAxisAlignment: MainAxisAlignment.start,
    mainAxisSize: MainAxisSize.min,
    crossAxisAlignment: CrossAxisAlignment.end,
    children: [
      Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: getItemColor(item),
        ),
        padding: const EdgeInsets.all(8),
        child: Icon(
          getItemIcon(item),
          color: Colors.white,
          size: 16,
        ),
      ),
      Text(
        getItemStatus(item),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w400,
          color: getItemColor(item),
        ),
      )
    ],
  ) ;
}