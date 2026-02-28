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
  const MainView({
    super.key,
    this.initialTab = AppNavTab.home,
  });

  final AppNavTab initialTab;

  String _titleForTab(AppNavTab tab) {
    return switch (tab) {
      AppNavTab.home => 'Home',
      AppNavTab.orders => 'Orders',
      AppNavTab.map => 'Map',
      AppNavTab.profile => 'Profile',
    };
  }

  @override
  Widget build(BuildContext context) {
    controller.setInitialTab(initialTab);

    return Obx(
      () {
        final current = controller.currentTab;
        return Scaffold(
          appBar: AppBar(
            title: Text(
              _titleForTab(current),
              style: const TextStyle(
                color: AppColors.slate900,
                fontWeight: FontWeight.w700,
              ),
            ),
            centerTitle: true,
            backgroundColor: Colors.transparent,
            elevation: 0,
          ),
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
      },
    );
  }
}
