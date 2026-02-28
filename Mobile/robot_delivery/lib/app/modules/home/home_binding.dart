import 'package:get/get.dart';

import '../../core/network/api_client.dart';
import '../../data/repositories/sample_repository.dart';
import 'home_controller.dart';

class HomeBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<ApiClient>(() => ApiClient(), fenix: true);
    Get.lazyPut<SampleRepository>(() => SampleRepository(Get.find()), fenix: true);
    Get.lazyPut<HomeController>(() => HomeController(Get.find()));
  }
}
