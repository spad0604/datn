import 'package:get/get.dart';

import '../../core/utils/app_snackbar.dart';
import '../../data/repositories/sample_repository.dart';

class HomeController extends GetxController {
  HomeController(this._repository);

  final SampleRepository _repository;

  final isLoading = false.obs;
  final todo = Rxn<Map<String, dynamic>>();

  Future<void> fetchTodo() async {
    isLoading.value = true;
    try {
      final result = await _repository.fetchTodo();
      todo.value = result;
      AppSnackbar.success('Đã tải dữ liệu thành công');
    } catch (e) {
      AppSnackbar.error(e.toString());
    } finally {
      isLoading.value = false;
    }
  }
}
