import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_map/flutter_map.dart' hide MapController;
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

import '../controllers/map_controller.dart';

class MapView extends GetView<MapController> {
  const MapView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      body: SafeArea(
        top: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 40, 16, 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    AppTranslationKeys.mapTitle.tr,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      color: AppColors.slate900,
                    ),
                  ),
                  IconButton(
                    onPressed: controller.recenter,
                    icon: const Icon(Icons.my_location, color: AppColors.primary),
                    tooltip: 'Recenter',
                  ),
                ],
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: Obx(() {
                    final markersList = controller.markersData.map((data) {
                      return Marker(
                        point: data.position,
                        width: 44,
                        height: 44,
                        child: Tooltip(
                          message: 'Order ${data.order.orderId}',
                          child: Container(
                            decoration: BoxDecoration(
                              color: AppColors.white,
                              borderRadius: BorderRadius.circular(9999),
                              border: Border.all(color: AppColors.slate200, width: 1),
                            ),
                            child: Icon(
                              data.type == MarkerType.pickup
                                  ? Icons.store_mall_directory_outlined
                                  : Icons.flag_outlined,
                              color: data.type == MarkerType.pickup
                                  ? AppColors.teal
                                  : AppColors.success,
                              size: 22,
                            ),
                          ),
                        ),
                      );
                    }).toList();

                    return FlutterMap(
                      mapController: controller.mapController,
                      options: MapOptions(
                        initialCenter: controller.defaultCenter,
                        initialZoom: 13,
                        onMapReady: () {
                          if (markersList.isNotEmpty) {
                            controller.recenter();
                          }
                        },
                      ),
                      children: [
                        TileLayer(
                          urlTemplate:
                              'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                          userAgentPackageName: 'robot_delivery',
                        ),
                        MarkerLayer(
                          markers: markersList,
                        ),
                      ],
                    );
                  }),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
