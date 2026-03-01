import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/app_bottom_nav_bar.dart';
import 'package:robot_delivery/app/modules/home/create_order.dart';
import 'package:robot_delivery/app/modules/home/home_binding.dart';
import 'package:robot_delivery/app/modules/notifications/bindings/notifications_binding.dart';
import 'package:robot_delivery/app/modules/notifications/views/notifications_view.dart';

import '../modules/login/bindings/login_binding.dart';
import '../modules/login/views/login_view.dart';
import '../modules/main/bindings/main_binding.dart';
import '../modules/main/views/main_view.dart';

part 'app_routes.dart';

abstract class AppPages {
  const AppPages._();

  static final pages = <GetPage<dynamic>>[
    GetPage(
      name: Routes.HOME,
      page: () => MainView(initialTab: AppNavTab.home),
      binding: MainBinding(),
    ),
    GetPage(
      name: Routes.LOGIN,
      page: () => const LoginView(),
      binding: LoginBinding(),
    ),
    GetPage(
      name: Routes.ORDERS,
      page: () => MainView(initialTab: AppNavTab.orders),
      binding: MainBinding(),
    ),
    GetPage(
      name: Routes.MAP,
      page: () => MainView(initialTab: AppNavTab.map),
      binding: MainBinding(),
    ),
    GetPage(
      name: Routes.PROFILE,
      page: () => MainView(initialTab: AppNavTab.profile),
      binding: MainBinding(),
    ),
    GetPage(
      name: Routes.CREATE_ORDER,
      page: () => CreateNewOrder(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: Routes.NOTIFICATIONS,
      page: () => const NotificationsView(),
      binding: NotificationsBinding(),
    ),
  ];
}
