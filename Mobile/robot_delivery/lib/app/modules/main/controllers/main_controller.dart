import 'package:get/get.dart';
import 'package:robot_delivery/app/common/widget/app_bottom_nav_bar.dart';

class MainController extends GetxController {
  final RxInt tabIndex = 0.obs;

  bool _didSetInitialTab = false;

  void setInitialTab(AppNavTab tab) {
    if (_didSetInitialTab) return;
    _didSetInitialTab = true;
    tabIndex.value = AppNavTab.values.indexOf(tab);
  }

  void setTabIndex(int index) {
    if (index < 0 || index >= AppNavTab.values.length) return;
    tabIndex.value = index;
  }

  AppNavTab get currentTab => AppNavTab.values[tabIndex.value];
}
