import 'package:flutter/widgets.dart';
import 'package:get/get.dart';
import 'package:robot_delivery/app/core/storage/secure_token_storage.dart';
import 'package:robot_delivery/app/data/repositories/user_repository.dart';
import 'package:robot_delivery/app/routes/app_pages.dart';

class ProfileController extends GetxController {
  ProfileController({UserRepository? userRepository, SecureTokenStorage? tokenStorage})
    : _userRepository = userRepository ?? Get.find<UserRepository>(),
      _tokenStorage = tokenStorage ?? Get.find<SecureTokenStorage>();

  final UserRepository _userRepository;
  final SecureTokenStorage _tokenStorage;

  final Rx<bool> isUpdatingProfile = false.obs;

  final TextEditingController nameController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();
  final TextEditingController addressController = TextEditingController();

  @override
  void onInit() {
    super.onInit();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    final response = await _userRepository.getMyInfo();
    if (response.data != null) {
      final user = response.data!;
      nameController.text = user.fullName;
      phoneController.text = user.phoneNumber ?? '';
      addressController.text = user.address ?? '';
    }
  }

  Future<void> updateProfileButtonPressed() async {
    if (isUpdatingProfile.value == false) {
      isUpdatingProfile.value = true;
    } else {
      try {
        // Simulate API call delay
        await Future.delayed(const Duration(seconds: 2));
        isUpdatingProfile.value = false;
      } catch (e) {
        isUpdatingProfile.value = false;
      }
    }
  }

  Future<void> logout() async {
    await _tokenStorage.clearTokens();
    Get.deleteAll(force: true);
    Get.offAllNamed(Routes.LOGIN);
  }

  @override
  void onClose() {
    nameController.dispose();
    phoneController.dispose();
    addressController.dispose();
    super.onClose();
  }
}
