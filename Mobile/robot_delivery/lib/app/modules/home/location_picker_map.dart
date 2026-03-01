import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';

class LocationPickerMapPage extends StatefulWidget {
  final LatLng initialCenter;
  final double initialZoom;

  const LocationPickerMapPage({
    super.key,
    required this.initialCenter,
    this.initialZoom = 15,
  });

  @override
  State<LocationPickerMapPage> createState() => _LocationPickerMapPageState();
}

class _LocationPickerMapPageState extends State<LocationPickerMapPage> {
  LatLng? _picked;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.slate100,
      appBar: AppBar(
        backgroundColor: AppColors.slate100,
        centerTitle: true,
        title: const Text(
          'Chọn vị trí',
          style: TextStyle(
            color: AppColors.slate900,
            fontWeight: FontWeight.w600,
            fontSize: 18,
          ),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                child: FlutterMap(
                  options: MapOptions(
                    initialCenter: widget.initialCenter,
                    initialZoom: widget.initialZoom,
                    onTap: (tapPosition, point) {
                      setState(() {
                        _picked = point;
                      });
                    },
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'robot_delivery',
                    ),
                    MarkerLayer(
                      markers: [
                        if (_picked != null)
                          Marker(
                            point: _picked!,
                            width: 42,
                            height: 42,
                            child: const Icon(
                              Icons.location_on,
                              color: AppColors.primary,
                              size: 42,
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.slate300, width: 1),
                  ),
                  child: Text(
                    _picked == null
                        ? 'Chạm trên bản đồ để chọn toạ độ'
                        : 'Đã chọn: ${_picked!.latitude.toStringAsFixed(6)}, ${_picked!.longitude.toStringAsFixed(6)}',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: AppColors.slate900,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                CustomButton(
                  text: 'Dùng vị trí này',
                  textColor: AppColors.white,
                  backgroundColor: AppColors.primary,
                  onPressed: () {
                    if (_picked == null) return;
                    Get.back(result: _picked);
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
