import 'package:get/get.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/core/storage/secure_token_storage.dart';
import 'package:robot_delivery/app/data/repositories/auth_repository.dart';
import 'package:robot_delivery/app/data/repositories/sample_repository.dart';
import 'package:robot_delivery/app/modules/map/controllers/map_controller.dart';
import 'package:robot_delivery/app/modules/orders/bindings/orders_binding.dart';
import 'package:robot_delivery/app/modules/profile/controllers/profile_controller.dart';

import '../controllers/main_controller.dart';

class MainBinding extends Bindings {
  @override
  void dependencies() {
    if (!Get.isRegistered<MainController>()) {
      Get.put<MainController>(MainController(), permanent: true);
    }

    // Home module dependencies (also used by networking/auth scaffolding).
    if (!Get.isRegistered<SecureTokenStorage>()) {
      Get.lazyPut<SecureTokenStorage>(() => SecureTokenStorage(), fenix: true);
    }
    if (!Get.isRegistered<AuthRepository>()) {
      Get.lazyPut<AuthRepository>(() => AuthRepository(), fenix: true);
    }
    if (!Get.isRegistered<ApiClient>()) {
      Get.lazyPut<ApiClient>(
        () => ApiClient(
          tokenStorage: Get.find<SecureTokenStorage>(),
          authRepository: Get.find<AuthRepository>(),
        ),
        fenix: true,
      );
    }
    if (!Get.isRegistered<SampleRepository>()) {
      Get.lazyPut<SampleRepository>(
        () => SampleRepository(Get.find<ApiClient>()),
        fenix: true,
      );
    }

    // Other tabs.
    Get.lazyPut(OrdersBinding().dependencies);

    if (!Get.isRegistered<MapController>()) {
      Get.lazyPut<MapController>(() => MapController());
    }
    if (!Get.isRegistered<ProfileController>()) {
      Get.put<ProfileController>(ProfileController(), permanent: true);
    }
  }
}
