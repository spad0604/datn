import 'package:flutter/material.dart';
import 'package:get/get.dart';

/// Language controller to manage language switching
class LanguageController extends GetxController {
  final currentLocale = Get.locale.obs;

  void changeLanguage(String languageCode, String countryCode) {
    final locale = Locale(languageCode, countryCode);
    Get.updateLocale(locale);
    currentLocale.value = locale;
  }

  void switchToVietnamese() => changeLanguage('vi', 'VN');

  void switchToEnglish() => changeLanguage('en', 'US');

  bool get isVietnamese => currentLocale.value?.languageCode == 'vi';

  bool get isEnglish => currentLocale.value?.languageCode == 'en';
}
