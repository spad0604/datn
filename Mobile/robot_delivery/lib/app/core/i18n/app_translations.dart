import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'en_us_translation.dart';
import 'vi_vn_translation.dart';

class AppTranslations extends Translations {
  @override
  Map<String, Map<String, String>> get keys {
    final Map<String, Map<String, String>> translations = {};

    // Merge all translations
    translations.addAll(ViVNTranslation().keys);
    translations.addAll(EnUSTranslation().keys);

    return translations;
  }

  static const Locale fallbackLocale = Locale('en', 'US');
  static const Locale defaultLocale = Locale('vi', 'VN');

  static final List<Locale> supportedLocales = [
    const Locale('vi', 'VN'),
    const Locale('en', 'US'),
  ];
}
