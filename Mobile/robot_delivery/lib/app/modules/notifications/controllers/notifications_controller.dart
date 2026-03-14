import 'package:get/get.dart';
import 'package:robot_delivery/app/data/models/response/notification_response.dart';
import 'package:robot_delivery/app/data/repositories/notification_repository.dart';

enum NotificationFilter { all, alerts, updates, promos }

class NotificationItem {
  final NotificationResponse data;
  final String title;
  final String body;
  final String timeLabel;
  final NotificationFilter category;
  final RxBool isUnread;

  NotificationItem({
    required this.data,
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
  final RxBool isLoading = false.obs;

  final NotificationRepository repository = Get.find<NotificationRepository>();

  @override
  void onInit() {
    super.onInit();
    fetchNotifications();
  }

  Future<void> fetchNotifications() async {
    isLoading.value = true;
    final res = await repository.getMyNotifications();
    isLoading.value = false;

    if (res.data != null) {
      final parsedItems = res.data!.map((n) {
        return NotificationItem(
          data: n,
          title: n.title,
          body: n.body,
          timeLabel: _formatTime(n.createdAt),
          category: _mapTypeToFilter(n.type),
          unread: !n.isRead,
        );
      }).toList();
      items.assignAll(parsedItems);
    }
  }

  String _formatTime(String createdAtString) {
    try {
      final dt = DateTime.parse(createdAtString).toLocal();
      final difference = DateTime.now().difference(dt);
      if (difference.inMinutes < 60) {
        final m = difference.inMinutes < 1 ? 1 : difference.inMinutes;
        return '${m}m ago';
      } else if (difference.inHours < 24) {
        return '${difference.inHours}h ago';
      } else if (difference.inDays == 1) {
        return 'Yesterday';
      } else {
        return '${dt.day}/${dt.month} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
      }
    } catch (_) {
      return '';
    }
  }

  NotificationFilter _mapTypeToFilter(String type) {
    final t = type.toUpperCase();
    if (t.contains('ALERT') || t.contains('APPROACHING') || t.contains('CANCELLED')) {
      return NotificationFilter.alerts;
    } else if (t.contains('PROMO')) {
      return NotificationFilter.promos;
    }
    return NotificationFilter.updates;
  }

  List<NotificationItem> get filteredItems {
    final selected = filter.value;
    if (selected == NotificationFilter.all) return items;
    return items.where((e) => e.category == selected).toList();
  }

  Future<void> markAllRead() async {
    for (final item in items) {
      if (item.isUnread.value) {
        item.isUnread.value = false;
        await repository.markAsRead(item.data.id);
      }
    }
  }

  Future<void> markAsRead(NotificationItem item) async {
    if (item.isUnread.value) {
      item.isUnread.value = false;
      await repository.markAsRead(item.data.id);
    }
  }
}
