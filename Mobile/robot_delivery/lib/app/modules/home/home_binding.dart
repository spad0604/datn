import 'package:get/get.dart';

import '../../core/network/api_client.dart';
import '../../core/storage/secure_token_storage.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/repositories/sample_repository.dart';
import 'home_controller.dart';

class HomeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<SecureTokenStorage>(() => SecureTokenStorage(), fenix: true);
    Get.lazyPut<AuthRepository>(() => AuthRepository(), fenix: true);
    Get.lazyPut<ApiClient>(
      () => ApiClient(
        tokenStorage: Get.find(),
        authRepository: Get.find(),
      ),
      fenix: true,
    );
    Get.lazyPut<SampleRepository>(() => SampleRepository(Get.find()), fenix: true);
    Get.lazyPut<HomeController>(() => HomeController(Get.find()));
  }
}
