import 'package:get/get.dart';

enum NotificationFilter { all, alerts, updates, promos }

class NotificationItem {
  final String title;
  final String body;
  final String timeLabel;
  final NotificationFilter category;
  final RxBool isUnread;

  NotificationItem({
    required this.title,
    required this.body,
    required this.timeLabel,
    required this.category,
    bool unread = true,
  }) : isUnread = unread.obs;
}

class NotificationsController extends GetxController {
  final Rx<NotificationFilter> filter = NotificationFilter.all.obs;

  final RxList<NotificationItem> items = <NotificationItem>[].obs;

  @override
  void onInit() {
    super.onInit();

    items.assignAll([
      NotificationItem(
        title: 'Robot Arrival',
        body: 'Stitch-04 has successfully arrived at Loading Bay 3 for pickup.',
        timeLabel: '2m ago',
        category: NotificationFilter.updates,
        unread: true,
      ),
      NotificationItem(
        title: 'System Maintenance',
        body:
            'Scheduled maintenance for tonight at 2:00 AM. Services may be briefly unavailable.',
        timeLabel: '15m ago',
        category: NotificationFilter.alerts,
        unread: true,
      ),
      NotificationItem(
        title: 'Low Battery Alert',
        body:
            'Stitch-09 battery level is critical (15%). Please return to charging station.',
        timeLabel: '2h ago',
        category: NotificationFilter.alerts,
        unread: false,
      ),
      NotificationItem(
        title: 'Delivery Complete',
        body:
            'Order #4492 has been delivered to Zone B. Customer signature received.',
        timeLabel: '5h ago',
        category: NotificationFilter.updates,
        unread: false,
      ),
      NotificationItem(
        title: 'Route Optimization',
        body:
            'New efficient routes have been calculated for the downtown sector.',
        timeLabel: 'Yesterday',
        category: NotificationFilter.updates,
        unread: false,
      ),
      NotificationItem(
        title: 'Team Update',
        body: 'Sarah mentioned you in "Dispatch Logs - Week 42".',
        timeLabel: 'Yesterday',
        category: NotificationFilter.promos,
        unread: false,
      ),
    ]);
  }

  List<NotificationItem> get filteredItems {
    final selected = filter.value;
    if (selected == NotificationFilter.all) return items;
    return items.where((e) => e.category == selected).toList();
  }

  void markAllRead() {
    for (final item in items) {
      item.isUnread.value = false;
    }
  }
}
