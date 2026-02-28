import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../theme/app_colors.dart';

class AppSnackbar {
  const AppSnackbar._();

  static Future<void> success(
    String message, {
    String title = 'Thành công',
    Duration duration = const Duration(seconds: 3),
  }) {
    return _showPopup(
      title: title,
      message: message,
      backgroundColor: AppColors.success,
      icon: Icons.check_circle_outline,
      duration: duration,
    );
  }

  static Future<void> error(
    String message, {
    String title = 'Lỗi',
    Duration duration = const Duration(seconds: 4),
  }) {
    return _showPopup(
      title: title,
      message: message,
      backgroundColor: AppColors.errorAlt,
      icon: Icons.error_outline,
      duration: duration,
    );
  }

  static Future<void> _showPopup({
    required String title,
    required String message,
    required Color backgroundColor,
    required IconData icon,
    required Duration duration,
  }) async {
    // Close previous popup if any.
    if (Get.isDialogOpen == true) {
      Get.back<void>();
    }

    final context = Get.overlayContext;
    if (context == null) return;

    // Show a non-dimming popup.
    Get.dialog<void>(
      _PopupToast(
        title: title,
        message: message,
        backgroundColor: backgroundColor,
        icon: icon,
      ),
      barrierDismissible: true,
      barrierColor: Colors.transparent,
      useSafeArea: true,
    );

    await Future<void>.delayed(duration);
    if (Get.isDialogOpen == true) {
      Get.back<void>();
    }
  }
}

class _PopupToast extends StatelessWidget {
  const _PopupToast({
    required this.title,
    required this.message,
    required this.backgroundColor,
    required this.icon,
  });

  final String title;
  final String message;
  final Color backgroundColor;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Material(
      type: MaterialType.transparency,
      child: SafeArea(
        child: Align(
          alignment: Alignment.topCenter,
          child: Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            constraints: const BoxConstraints(maxWidth: 520),
            decoration: BoxDecoration(
              color: backgroundColor,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(icon, color: AppColors.white),
                const SizedBox(width: 10),
                Flexible(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: AppColors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        message,
                        style: const TextStyle(color: AppColors.white),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
