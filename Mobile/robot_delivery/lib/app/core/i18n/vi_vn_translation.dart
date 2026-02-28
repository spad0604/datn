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
          AppTranslationKeys.connectionTimeout: 'Kết nối bị timeout. Vui lòng thử lại.',
          AppTranslationKeys.serverError: 'Lỗi máy chủ. Vui lòng thử lại sau.',
          AppTranslationKeys.noInternet: 'Không có kết nối internet',

          // Home
          AppTranslationKeys.home: 'Trang chủ',
          AppTranslationKeys.homeTitle: 'Robot Delivery',
        },
      };
}
