import 'package:get/get.dart';

import 'app_translation_keys.dart';

class ViVNTranslation extends Translations {
  @override
  Map<String, Map<String, String>> get keys => {
    'vi_VN': {
      // Common
      AppTranslationKeys.appName: 'Robot Delivery',
      AppTranslationKeys.ok: 'Đồng ý',
      AppTranslationKeys.cancel: 'Hủy',
      AppTranslationKeys.save: 'Lưu',
      AppTranslationKeys.delete: 'Xóa',
      AppTranslationKeys.edit: 'Sửa',
      AppTranslationKeys.search: 'Tìm kiếm',
      AppTranslationKeys.loading: 'Đang tải...',
      AppTranslationKeys.error: 'Lỗi',
      AppTranslationKeys.success: 'Thành công',
      AppTranslationKeys.retry: 'Thử lại',
      AppTranslationKeys.close: 'Đóng',
      AppTranslationKeys.back: 'Quay lại',
      AppTranslationKeys.next: 'Tiếp tục',
      AppTranslationKeys.confirm: 'Xác nhận',
      AppTranslationKeys.yes: 'Có',
      AppTranslationKeys.no: 'Không',

      AppTranslationKeys.dontHaveAccount: "Bạn chưa có tài khoản?",
      AppTranslationKeys.createAccount: 'Tạo tài khoản',
      AppTranslationKeys.orContinueWith: 'HOẶC TIẾP TỤC VỚI',
      AppTranslationKeys.quickActions: 'Hành động nhanh',
      AppTranslationKeys.pending: 'Đang chờ',

      // History
      AppTranslationKeys.deliveryHistory: 'Lịch sử giao hàng',
      AppTranslationKeys.all: 'Tất cả',
      AppTranslationKeys.deliveredStatus: 'Đã giao',
      AppTranslationKeys.cancelledStatus: 'Đã hủy',
      AppTranslationKeys.thisWeek: 'TUẦN NÀY',
      AppTranslationKeys.lastWeek: 'TUẦN TRƯỚC',
      AppTranslationKeys.sender: 'Người gửi:',

      // Roles
      AppTranslationKeys.buyer: 'Người mua',
      AppTranslationKeys.seller: 'Người bán',

      // Auth
      AppTranslationKeys.login: 'Đăng nhập',
      AppTranslationKeys.logout: 'Đăng xuất',
      AppTranslationKeys.register: 'Đăng ký',
      AppTranslationKeys.forgotPassword: 'Quên mật khẩu?',
      AppTranslationKeys.email: 'Email',
      AppTranslationKeys.password: 'Mật khẩu',
      AppTranslationKeys.confirmPassword: 'Xác nhận mật khẩu',
      AppTranslationKeys.emailHint: 'Nhập email của bạn',
      AppTranslationKeys.passwordHint: 'Nhập mật khẩu',
      AppTranslationKeys.loginSuccess: 'Đăng nhập thành công',
      AppTranslationKeys.loginError: 'Đăng nhập thất bại. Vui lòng thử lại.',

      // Validation
      AppTranslationKeys.emailRequired: 'Vui lòng nhập email',
      AppTranslationKeys.emailInvalid: 'Email không hợp lệ',
      AppTranslationKeys.passwordRequired: 'Vui lòng nhập mật khẩu',
      AppTranslationKeys.passwordTooShort: 'Mật khẩu phải có ít nhất 6 ký tự',
      AppTranslationKeys.passwordMismatch: 'Mật khẩu không khớp',

      // Network
      AppTranslationKeys.connectionError: 'Lỗi kết nối. Vui lòng thử lại.',
      AppTranslationKeys.connectionTimeout:
          'Kết nối bị timeout. Vui lòng thử lại.',
      AppTranslationKeys.serverError: 'Lỗi máy chủ. Vui lòng thử lại sau.',
      AppTranslationKeys.noInternet: 'Không có kết nối internet',

      // Home
      AppTranslationKeys.home: 'Trang chủ',
      AppTranslationKeys.homeTitle: 'Robot Delivery',
      AppTranslationKeys.upcomingOrders: 'Đơn hàng sắp tới',
      AppTranslationKeys.seeAll: 'Xem tất cả',
      AppTranslationKeys.currentDelivery: 'Đơn hàng hiện tại',
      AppTranslationKeys.arrivingSoon: 'Sắp tới nơi',
      AppTranslationKeys.currentDeliveryHeadline: 'Robot còn khoảng 5 phút',
      // Quick Actions
      AppTranslationKeys.newOrder: 'Tạo đơn mới',
      AppTranslationKeys.address: 'Địa chỉ',
      AppTranslationKeys.history: 'Lịch sử',
      AppTranslationKeys.support: 'Hỗ trợ',

      // Profile
      AppTranslationKeys.profileView: 'Hồ sơ',
      AppTranslationKeys.userOrShopName: 'Tên người dùng hoặc cửa hàng',
      AppTranslationKeys.phoneNumber: 'Số điện thoại',
      AppTranslationKeys.addressField: 'Địa chỉ',
      AppTranslationKeys.updateProfile: 'Cập nhật hồ sơ',

      // Notifications
      AppTranslationKeys.notifications: 'Thông báo',
      AppTranslationKeys.markAllRead: 'Đánh dấu đã đọc',
      AppTranslationKeys.alerts: 'Cảnh báo',
      AppTranslationKeys.updates: 'Cập nhật',
      AppTranslationKeys.promos: 'Ưu đãi',
      AppTranslationKeys.newLabel: 'MỚI',
      AppTranslationKeys.earlierLabel: 'TRƯỚC ĐÓ',
      AppTranslationKeys.noNotifications: 'Chưa có thông báo',

      // Map
      AppTranslationKeys.mapTitle: 'Bản đồ',
      AppTranslationKeys.robot: 'Robot',
      AppTranslationKeys.pickup: 'Điểm lấy',
      AppTranslationKeys.dropoff: 'Điểm giao',
      AppTranslationKeys.currentDeliveryDescription:
          'Đơn hàng của bạn đang rẽ vào đường Main St.',
      AppTranslationKeys.trackLive: 'Theo dõi trực tiếp',
      AppTranslationKeys.trackingId: 'Mã theo dõi:',

      // Order status
      AppTranslationKeys.moving: 'Đang di chuyển',
      AppTranslationKeys.inTransit: 'Đang vận chuyển',
      AppTranslationKeys.scheduled: 'Đã lên lịch',

      AppTranslationKeys.recipientName: 'Tên người nhận',
      AppTranslationKeys.recipientAddress: 'Địa chỉ người nhận',
      AppTranslationKeys.packageWeight: 'Trọng lượng',
      AppTranslationKeys.createNewOrder: 'Tạo đơn hàng mới',
      AppTranslationKeys.shippingLocation: 'Vị trí giao hàng',
      AppTranslationKeys.submitOrder: 'Gửi đơn hàng',
    },
  };
}
