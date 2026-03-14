part of '../home_view.dart';

class CurrentDelivery extends StatelessWidget {
  const CurrentDelivery({super.key});

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      final mainController = Get.find<MainController>();

      final activeReceived = mainController.myReceivedOrders
          .where((o) => o.status == 'DELIVERING' || o.status == 'PENDING' || o.status == 'WAIT_ROBOT')
          .toList();
      final activeSent = mainController.myOrders
          .where((o) => o.status == 'DELIVERING' || o.status == 'PENDING' || o.status == 'WAIT_ROBOT')
          .toList();

      final activeOrder = activeReceived.isNotEmpty
          ? activeReceived.first
          : activeSent.isNotEmpty
              ? activeSent.first
              : null;

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            AppTranslationKeys.currentDelivery.tr,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          if (activeOrder == null) _buildEmpty() else _buildCard(context, activeOrder),
        ],
      );
    });
  }

  Widget _buildEmpty() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.slate50,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.slate200, width: 1),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.inbox_outlined, size: 40, color: AppColors.slate300),
          const SizedBox(height: 10),
          Text(
            AppTranslationKeys.noOrders.tr,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppColors.slate400),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildCard(BuildContext context, OrderResponse order) {
    final startLatLng = LatLng(order.startLat, order.startLng);
    final endLatLng = LatLng(order.deliveryLat, order.deliveryLng);
    final center = LatLng(
      (order.startLat + order.deliveryLat) / 2,
      (order.startLng + order.deliveryLng) / 2,
    );

    return GestureDetector(
      onTap: () => Get.toNamed('/order-details', arguments: order),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.primary10,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.primary20, width: 1),
        ),
        child: Column(
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.access_time, size: 14, color: AppColors.primary),
                          const SizedBox(width: 6),
                          Text(
                            _statusLabel(order.status),
                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.primary),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Order #${order.orderId}',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.slate900),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Từ ${order.senderName} → ${order.recipient.fullName}',
                        style: const TextStyle(fontSize: 13, color: AppColors.slate600),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  width: 42,
                  height: 42,
                  decoration: const BoxDecoration(color: AppColors.white, shape: BoxShape.circle),
                  child: const Icon(Icons.smart_toy_outlined, color: AppColors.primary, size: 22),
                ),
              ],
            ),
            const SizedBox(height: 14),
            // 🗺️ Embedded mini-map
            ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: SizedBox(
                height: 160,
                width: double.infinity,
                child: Stack(
                  children: [
                    FlutterMap(
                      options: MapOptions(
                        initialCenter: center,
                        initialZoom: 13.5,
                        interactionOptions: const InteractionOptions(flags: InteractiveFlag.none),
                      ),
                      children: [
                        TileLayer(
                          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                          userAgentPackageName: 'com.example.robot_delivery',
                        ),
                        PolylineLayer(
                          polylines: [
                            Polyline(
                              points: [startLatLng, endLatLng],
                              color: AppColors.primary,
                              strokeWidth: 3.5,
                            ),
                          ],
                        ),
                        MarkerLayer(
                          markers: [
                            Marker(
                              point: startLatLng,
                              width: 28,
                              height: 28,
                              child: const Icon(Icons.person_pin_circle, color: Colors.orange, size: 28),
                            ),
                            Marker(
                              point: endLatLng,
                              width: 28,
                              height: 28,
                              child: const Icon(Icons.location_on, color: Colors.green, size: 28),
                            ),
                          ],
                        ),
                      ],
                    ),
                    // Tap overlay → go to details
                    Positioned(
                      right: 10,
                      bottom: 10,
                      child: GestureDetector(
                        onTap: () => Get.toNamed('/order-details', arguments: order),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: AppColors.white,
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(color: AppColors.slate200, width: 1),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.bar_chart, size: 14, color: AppColors.slate900),
                              const SizedBox(width: 6),
                              Text(
                                AppTranslationKeys.trackLive.tr,
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.slate900),
                              ),
                            ],
                          ),
                        ),
                      ),
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

  String _statusLabel(String status) {
    switch (status.toUpperCase()) {
      case 'WAIT_ROBOT': return 'Đang chờ robot...';
      case 'PENDING': return 'Robot đang đến lấy hàng';
      case 'DELIVERING': return 'Đang giao hàng';
      default: return status;
    }
  }
}
