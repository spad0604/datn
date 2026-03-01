import 'package:flutter/widgets.dart';
import 'package:get/get.dart';

class ProfileController extends GetxController {
  final Rx<bool> isUpdatingProfile = false.obs;

  final TextEditingController nameController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();
  final TextEditingController addressController = TextEditingController();

  @override
  void onInit() {
    super.onInit();
    nameController.text = 'John Doe';
    phoneController.text = '+1 234 567 890';
    addressController.text = '123 Main Street, City, Country';
  }

  Future<void> updateProfileButtonPressed() async {
    if (isUpdatingProfile.value == false) 
    {
      isUpdatingProfile.value = true;
    }
    else
    {
      try {
        // Simulate API call delay
        await Future.delayed(const Duration(seconds: 2));
        isUpdatingProfile.value = false;
      } catch (e) {
        isUpdatingProfile.value = false;
      }
    }
  }

  @override
  void onClose() {
    nameController.dispose();
    phoneController.dispose();
    addressController.dispose();
    super.onClose();
  }
}
