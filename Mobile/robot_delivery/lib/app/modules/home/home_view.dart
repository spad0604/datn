import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/common/widget/app_bottom_nav_bar.dart';
import 'package:robot_delivery/app/common/widget/custom_icon_button.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';
import 'package:robot_delivery/app/modules/main/controllers/main_controller.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';

import 'home_controller.dart';

part 'widget/quick_actions.dart';
part 'widget/home_header.dart';
part 'widget/current_delivery.dart';
part 'widget/upcoming_orders.dart';

class HomeView extends GetView<HomeController> {
  HomeView({super.key});

  final mainController = Get.find<MainController>();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          HomeHeaderWidget(),
          const SizedBox(height: 20),
          Expanded(
            child: RefreshIndicator(
              onRefresh: mainController.refreshOrders,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    children: [
                      const Padding(
                        padding: EdgeInsets.only(top: 20),
                        child: CurrentDelivery(),
                      ),
                      const SizedBox(height: 20),
                      QuickActions(),
                      const SizedBox(height: 20),
                      UpcomingOrders(onSeeAll: () { mainController.setTabIndex(1); }),
                      const SizedBox(height: 16),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
