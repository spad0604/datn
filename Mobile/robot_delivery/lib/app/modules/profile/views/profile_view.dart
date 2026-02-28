import 'package:flutter/material.dart';

import 'package:get/get.dart';

import '../controllers/profile_controller.dart';

class ProfileView extends GetView<ProfileController> {
  const ProfileView({super.key});
  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text(
        'Profile page (placeholder)',
        style: TextStyle(fontSize: 20),
      ),
    );
  }
}
