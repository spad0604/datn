import 'package:get/get.dart';

import '../../core/network/api_client.dart';
import '../../core/storage/secure_token_storage.dart';
import '../../data/repositories/auth_repository.dart';
import '../../data/repositories/geocoding_repository.dart';
import '../../data/repositories/order_repository.dart';
import '../../data/repositories/user_repository.dart';
import 'home_controller.dart';

class HomeBinding extends Bindings {
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
    Get.lazyPut<GeocodingRepository>(() => GeocodingRepository(), fenix: true);
    Get.lazyPut<OrderRepository>(() => OrderRepository(Get.find<ApiClient>()), fenix: true);
    Get.lazyPut<UserRepository>(() => UserRepository(Get.find<ApiClient>()), fenix: true);
    Get.lazyPut<HomeController>(() => HomeController());
  }
}
