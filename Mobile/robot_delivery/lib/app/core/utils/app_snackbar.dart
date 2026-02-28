import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AppSnackbar {
  const AppSnackbar._();

  static void success(String message, {String title = 'Thành công'}) {
    final theme = Get.theme;
    final colors = theme.colorScheme;

    Get.snackbar(
      title,
      message,
      snackPosition: SnackPosition.TOP,
      backgroundColor: colors.primaryContainer,
      colorText: colors.onPrimaryContainer,
      margin: const EdgeInsets.all(12),
      duration: const Duration(seconds: 3),
    );
  }

  static void error(String message, {String title = 'Lỗi'}) {
    final theme = Get.theme;
    final colors = theme.colorScheme;

    Get.snackbar(
      title,
      message,
      snackPosition: SnackPosition.TOP,
      backgroundColor: colors.errorContainer,
      colorText: colors.onErrorContainer,
      margin: const EdgeInsets.all(12),
      duration: const Duration(seconds: 4),
    );
  }
}
