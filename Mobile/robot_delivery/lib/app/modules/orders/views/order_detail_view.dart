import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/common/widget/custom_button.dart';
import 'package:robot_delivery/app/core/i18n/app_translation_keys.dart';
import 'package:robot_delivery/app/core/theme/app_colors.dart';
import 'package:robot_delivery/app/data/models/response/order_response.dart';

import '../controllers/order_detail_controller.dart';

class OrderDetailView extends GetView<OrderDetailController> {
  const OrderDetailView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          AppTranslationKeys.orderDetails.tr,
          style: const TextStyle(
            fontWeight: FontWeight.w700,
            fontSize: 16,
            color: AppColors.slate900,
          ),
        ),
        centerTitle: true,
        backgroundColor: AppColors.white,
        elevation: 4,
        shadowColor: AppColors.slate100,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.only(
            bottomLeft: Radius.circular(24),
            bottomRight: Radius.circular(24),
          ),
        ),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(
            child: CircularProgressIndicator(color: AppColors.primary),
          );
        }

        final order = controller.currentOrder.value;
        if (order == null) {
          return Center(child: Text(AppTranslationKeys.noOrders.tr));
        }

        return Column(
          children: [
            Expanded(flex: 5, child: _buildMap(order)),
            Expanded(flex: 4, child: _buildOrderInfoSheet(context, order)),
          ],
        );
      }),
    );
  }

  Widget _buildMap(OrderResponse order) {
    final startLatLng = LatLng(order.startLat, order.startLng);
    final endLatLng = LatLng(order.deliveryLat, order.deliveryLng);

    return FlutterMap(
      options: MapOptions(initialCenter: startLatLng, initialZoom: 14.0),
      children: [
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.example.robot_delivery',
        ),
        PolylineLayer(
          polylines: [
            Polyline(
              points: controller.routePoints.isNotEmpty
                  ? controller.routePoints
                  : [startLatLng, endLatLng],
              color: AppColors.primary,
              strokeWidth: 5.0,
            ),
          ],
        ),
        MarkerLayer(
          markers: [
            Marker(
              point: startLatLng,
              width: 40,
              height: 40,
              child: const Icon(
                Icons.person_pin_circle,
                color: Colors.orange,
                size: 40,
              ),
            ),
            Marker(
              point: endLatLng,
              width: 40,
              height: 40,
              child: const Icon(
                Icons.location_on,
                color: Colors.green,
                size: 40,
              ),
            ),
            if (controller.robotLocation.value != null)
              Marker(
                point: controller.robotLocation.value!,
                width: 44,
                height: 44,
                child: Container(
                  decoration: const BoxDecoration(
                    color: AppColors.white,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 4,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Icon(
                      Icons.smart_toy,
                      color: AppColors.primary,
                      size: 28,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildOrderInfoSheet(BuildContext context, OrderResponse order) {
    return Container(
      decoration: const BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, -4),
          ),
        ],
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    '${AppTranslationKeys.order.tr} #${order.orderId}',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: AppColors.slate900,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.primary10,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _displayStatus(order.status),
                    style: const TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),

              ],
            ),
            const SizedBox(height: 24),
            _buildInfoRow(Icons.person, AppTranslationKeys.sender.tr, order.senderName),
            const SizedBox(height: 12),
            _buildInfoRow(
              Icons.location_on_outlined,
              AppTranslationKeys.senderLocationLabel.tr,
              order.senderAddress ?? '${order.startLat}, ${order.startLng}',
            ),
            const SizedBox(height: 12),
            _buildInfoRow(
              Icons.person_pin,
              AppTranslationKeys.recipientName.tr,
              order.recipient.fullName,
            ),
            const SizedBox(height: 12),
            _buildInfoRow(
              Icons.local_shipping_outlined,
              AppTranslationKeys.deliveryAddressLabel.tr,
              order.deliveryAddress ?? '${order.deliveryLat}, ${order.deliveryLng}',
            ),
            const SizedBox(height: 12),
            _buildInfoRow(Icons.phone, AppTranslationKeys.recipientPhoneLabel.tr, order.recipientPhone),
            const SizedBox(height: 12),
            _buildInfoRow(Icons.pin, AppTranslationKeys.pinCode.tr, order.pinCode),

            const SizedBox(height: 32),
            if (controller.isSender &&
                (order.status == 'PENDING' ||
                    order.status == 'WAIT_ROBOT')) ...[
              CustomButton(
                text: AppTranslationKeys.confirmSenderButton.tr,
                backgroundColor: AppColors.primary,
                textColor: AppColors.white,
                onPressed: controller.confirmSender,
              ),
              const SizedBox(height: 16),
              CustomButton(
                text: AppTranslationKeys.deleteOrderButton.tr,
                textColor: AppColors.white,
                backgroundColor: AppColors.error,
                onPressed: controller.deleteOrder,
              ),
            ],
            if (!controller.isSender && order.status == 'DELIVERING')
              CustomButton(
                text: AppTranslationKeys.confirmReceiverButton.tr,
                backgroundColor: AppColors.primary,
                textColor: AppColors.white,
                onPressed: controller.confirmReceiver,
              ),
          ],
        ),
      ),
    );
  }

  String _displayStatus(String status) {
    switch (status.toUpperCase()) {
      case 'WAIT_ROBOT': return AppTranslationKeys.waitingForRobot.tr;
      case 'PENDING': return AppTranslationKeys.robotComingToPickup.tr;
      case 'DELIVERING': return AppTranslationKeys.deliveringStatus.tr;
      case 'DELIVERED': return AppTranslationKeys.deliveredStatus.tr;
      case 'CANCELLED': return AppTranslationKeys.cancelledStatus.tr;
      default: return status;
    }
  }


  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, color: AppColors.slate400, size: 24),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(fontSize: 12, color: AppColors.slate500),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: AppColors.slate900,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

