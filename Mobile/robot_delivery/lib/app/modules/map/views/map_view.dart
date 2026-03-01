import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_map/flutter_map.dart' hide MapController;
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

import '../controllers/map_controller.dart';

class MapView extends GetView<MapController> {
  const MapView({super.key});
  @override
  Widget build(BuildContext context) {
    final robot = controller.robot;
    final pickup = controller.pickup;
    final dropoff = controller.dropoff;

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
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: FlutterMap(
                    mapController: controller.mapController,
                    options: MapOptions(
                      initialCenter: controller.initialCenter,
                      initialZoom: 15,
                    ),
                    children: [
                      TileLayer(
                        urlTemplate:
                            'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                        userAgentPackageName: 'robot_delivery',
                      ),
                      PolylineLayer(
                        polylines: [
                          Polyline(
                            points: controller.routePoints,
                            strokeWidth: 4,
                            color: AppColors.primary70,
                          ),
                        ],
                      ),
                      MarkerLayer(
                        markers: [
                          _marker(
                            point: pickup,
                            icon: Icons.store_mall_directory_outlined,
                            color: AppColors.teal,
                          ),
                          _marker(
                            point: robot,
                            icon: Icons.smart_toy_outlined,
                            color: AppColors.primary,
                          ),
                          _marker(
                            point: dropoff,
                            icon: Icons.flag_outlined,
                            color: AppColors.success,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: AppColors.slate100, width: 1),
                  boxShadow: const [
                    BoxShadow(
                      color: AppColors.black05,
                      blurRadius: 10,
                      offset: Offset(0, 6),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(
                          Icons.smart_toy_outlined,
                          color: AppColors.primary,
                          size: 18,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          AppTranslationKeys.robot.tr,
                          style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            color: AppColors.slate900,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '${robot.latitude.toStringAsFixed(5)}, ${robot.longitude.toStringAsFixed(5)}',
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            color: AppColors.slate500,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    _row(
                      icon: Icons.store_mall_directory_outlined,
                      iconColor: AppColors.teal,
                      title: AppTranslationKeys.pickup.tr,
                      value:
                          '${pickup.latitude.toStringAsFixed(5)}, ${pickup.longitude.toStringAsFixed(5)}',
                    ),
                    const SizedBox(height: 8),
                    _row(
                      icon: Icons.flag_outlined,
                      iconColor: AppColors.success,
                      title: AppTranslationKeys.dropoff.tr,
                      value:
                          '${dropoff.latitude.toStringAsFixed(5)}, ${dropoff.longitude.toStringAsFixed(5)}',
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Marker _marker({
    required LatLng point,
    required IconData icon,
    required Color color,
  }) {
    return Marker(
      point: point,
      width: 44,
      height: 44,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(9999),
          border: Border.all(color: AppColors.slate200, width: 1),
        ),
        child: Icon(icon, color: color, size: 22),
      ),
    );
  }

  Widget _row({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
  }) {
    return Row(
      children: [
        Icon(icon, color: iconColor, size: 18),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w700,
            color: AppColors.slate900,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            color: AppColors.slate500,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
