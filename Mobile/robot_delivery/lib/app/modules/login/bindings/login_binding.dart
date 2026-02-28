import 'package:get/get.dart';
import 'package:robot_delivery/app/core/network/api_client.dart';
import 'package:robot_delivery/app/core/storage/secure_token_storage.dart';
import 'package:robot_delivery/app/data/repositories/auth_repository.dart';
import 'package:robot_delivery/app/data/repositories/sample_repository.dart';
import 'package:robot_delivery/app/modules/home/home_controller.dart';

import '../controllers/login_controller.dart';

class LoginBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<SecureTokenStorage>(() => SecureTokenStorage(), fenix: true);
    Get.lazyPut<AuthRepository>(() => AuthRepository(), fenix: true);
    Get.lazyPut<ApiClient>(
      () => ApiClient(
        tokenStorage: Get.find<SecureTokenStorage>(),
        authRepository: Get.find<AuthRepository>(),
      ),
      fenix: true,
    );
    Get.lazyPut<SampleRepository>(() => SampleRepository(Get.find<ApiClient>()), fenix: true);
    Get.lazyPut<HomeController>(() => HomeController(Get.find<SampleRepository>()));
    Get.lazyPut<LoginController>(
      () => LoginController(),
    );
  }
}
