import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'home_controller.dart';

class HomeView extends GetView<HomeController> {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Robot Delivery'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Obx(() {
              if (controller.isLoading.value) {
                return const Center(child: CircularProgressIndicator());
              }

              final data = controller.todo.value;
              if (data == null || data.isEmpty) {
                return const Text('Chưa có dữ liệu.');
              }

              return Text(
                data.toString(),
                style: Theme.of(context).textTheme.bodyMedium,
              );
            }),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: controller.fetchTodo,
              child: const Text('Call API (Dio)'),
            ),
          ],
        ),
      ),
    );
  }
}
