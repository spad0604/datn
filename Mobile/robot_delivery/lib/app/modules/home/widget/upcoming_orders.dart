part of '../home_view.dart';

class UpcomingOrders extends StatelessWidget {
  UpcomingOrders({
    super.key,
    this.orders,
    this.onSeeAll,
    this.onOrderTap,
  });

  final List<UpcomingOrderItem>? orders;
  final void Function()? onSeeAll;
  final void Function(UpcomingOrderItem order)? onOrderTap;


  final mainController = Get.find<MainController>();

  @override
  Widget build(BuildContext context) {

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              AppTranslationKeys.upcomingOrders.tr,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            TextButton(
              onPressed: onSeeAll,
              child: Text(
                AppTranslationKeys.seeAll.tr,
                style: const TextStyle(color: AppColors.primary),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Obx(() {
          final items = mainController.myReceivedOrders;
          if (items.isEmpty) {
            return Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 16),
              decoration: BoxDecoration(
                color: AppColors.slate50,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.slate200, width: 1),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.local_shipping_outlined, size: 38, color: AppColors.slate300),
                  const SizedBox(height: 10),
                  Text(
                    AppTranslationKeys.noOrders.tr,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: AppColors.slate400,
                    ),
                  ),
                ],
              ),
            );
          }
          return ListView.separated(
            itemCount: items.length,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final order = items[index];
              return UpcomingOrderCard.fromOrder(
                order,
                onTap: () => Get.toNamed('/order-details', arguments: order),
              );
            },
          );
        }),
      ],
    );
  }
}

enum UpcomingOrderStatus { moving, inTransit, scheduled }

class UpcomingOrderItem {
  const UpcomingOrderItem({
    required this.icon,
    required this.title,
    required this.trackingId,
    required this.status,
  });

  final IconData icon;
  final String title;
  final String? trackingId;
  final UpcomingOrderStatus status;
}

class UpcomingOrderCard extends StatelessWidget {
  const UpcomingOrderCard({super.key, required this.order, this.onTap});

  final UpcomingOrderItem order;
  final VoidCallback? onTap;

  // Named constructor to create card directly from OrderResponse
  factory UpcomingOrderCard.fromOrder(
    OrderResponse orderResponse, {
    VoidCallback? onTap,
  }) {
    return UpcomingOrderCard(
      order: UpcomingOrderItem(
        icon: Icons.local_shipping,
        title: orderResponse.senderName,
        trackingId: orderResponse.orderId,
        status: _mapOrderStatus(orderResponse.status),
      ),
      onTap: onTap,
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        decoration: BoxDecoration(
          color: AppColors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: AppColors.slate100, width: 1),
          boxShadow: const [
            BoxShadow(
              color: AppColors.black05,
              blurRadius: 12,
              offset: Offset(0, 6),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: AppColors.slate50,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.slate100, width: 1),
              ),
              child: Icon(order.icon, color: AppColors.slate400, size: 22),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    order.title,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: AppColors.slate900,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${AppTranslationKeys.trackingId.tr} ${order.trackingId ?? AppTranslationKeys.pending.tr}',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: AppColors.slate500,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            OrderStatusChip(status: order.status),
            const SizedBox(width: 10),
            const Icon(Icons.chevron_right, color: AppColors.slate300),
          ],
        ),
      ),
    );
  }
}

UpcomingOrderStatus _mapOrderStatus(String status) {
  switch (status.toUpperCase()) {
    case 'WAIT_ROBOT':
      return UpcomingOrderStatus.scheduled;
    case 'PENDING':
      return UpcomingOrderStatus.moving;
    case 'DELIVERING':
      return UpcomingOrderStatus.inTransit;
    case 'DELIVERED':
      return UpcomingOrderStatus.scheduled;
    default:
      return UpcomingOrderStatus.scheduled;
  }
}

class OrderStatusChip extends StatelessWidget {
  const OrderStatusChip({super.key, required this.status});

  final UpcomingOrderStatus status;

  @override
  Widget build(BuildContext context) {
    final (bg, fg, label) = switch (status) {
      UpcomingOrderStatus.moving => (
        AppColors.primary10,
        AppColors.primary,
        AppTranslationKeys.moving.tr,
      ),
      UpcomingOrderStatus.inTransit => (
        AppColors.indigoSoft,
        AppColors.info,
        AppTranslationKeys.inTransit.tr,
      ),
      UpcomingOrderStatus.scheduled => (
        AppColors.slate100,
        AppColors.slate600,
        AppTranslationKeys.scheduled.tr,
      ),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: fg),
      ),
    );
  }
}
