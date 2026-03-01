import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/app_bottom_nav_bar.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/modules/home/home_view.dart';
import 'package:robot_delivery/app/modules/map/views/map_view.dart';
import 'package:robot_delivery/app/modules/orders/views/orders_view.dart';
import 'package:robot_delivery/app/modules/profile/views/profile_view.dart';

import '../controllers/main_controller.dart';

class MainView extends GetView<MainController> {
  const MainView({super.key, this.initialTab = AppNavTab.home});

  final AppNavTab initialTab;

  @override
  Widget build(BuildContext context) {
    controller.setInitialTab(initialTab);

    return Obx(() {
      return Scaffold(
        backgroundColor: AppColors.slate100,
        body: SafeArea(
          top: false,
          child: IndexedStack(
            index: controller.tabIndex.value,
            children: const [
              HomeView(),
              OrdersView(),
              MapView(),
              ProfileView(),
            ],
          ),
        ),
        bottomNavigationBar: AppBottomNavBar(
          currentIndex: controller.tabIndex.value,
          onChanged: controller.setTabIndex,
        ),
      );
    });
  }
}
