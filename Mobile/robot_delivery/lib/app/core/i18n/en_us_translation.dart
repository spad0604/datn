import 'package:get/get.dart';

import 'app_translation_keys.dart';

class EnUSTranslation extends Translations {
  @override
  Map<String, Map<String, String>> get keys => {
    'en_US': {
      // Common
      AppTranslationKeys.appName: 'Robot Delivery',
      AppTranslationKeys.ok: 'OK',
      AppTranslationKeys.cancel: 'Cancel',
      AppTranslationKeys.save: 'Save',
      AppTranslationKeys.delete: 'Delete',
      AppTranslationKeys.edit: 'Edit',
      AppTranslationKeys.search: 'Search',
      AppTranslationKeys.loading: 'Loading...',
      AppTranslationKeys.error: 'Error',
      AppTranslationKeys.success: 'Success',
      AppTranslationKeys.retry: 'Retry',
      AppTranslationKeys.close: 'Close',
      AppTranslationKeys.back: 'Back',
      AppTranslationKeys.next: 'Next',
      AppTranslationKeys.confirm: 'Confirm',
      AppTranslationKeys.yes: 'Yes',
      AppTranslationKeys.no: 'No',
      AppTranslationKeys.dontHaveAccount: "Don't have an account?",
      AppTranslationKeys.createAccount: 'Create account',
      AppTranslationKeys.orContinueWith: 'OR CONTINUE WITH',
      AppTranslationKeys.quickActions: 'Quick Actions',
      AppTranslationKeys.pending: 'Pending',

      // History
      AppTranslationKeys.deliveryHistory: 'Delivery History',
      AppTranslationKeys.all: 'All',
      AppTranslationKeys.deliveredStatus: 'Delivered',
      AppTranslationKeys.cancelledStatus: 'Cancelled',
      AppTranslationKeys.thisWeek: 'THIS WEEK',
      AppTranslationKeys.lastWeek: 'LAST WEEK',
      AppTranslationKeys.sender: 'Sender:',

      // Roles
      AppTranslationKeys.buyer: 'Buyer',
      AppTranslationKeys.seller: 'Seller',

      // Auth
      AppTranslationKeys.login: 'Login',
      AppTranslationKeys.logout: 'Logout',
      AppTranslationKeys.register: 'Register',
      AppTranslationKeys.forgotPassword: 'Forgot password?',
      AppTranslationKeys.email: 'Email',
      AppTranslationKeys.password: 'Password',
      AppTranslationKeys.confirmPassword: 'Confirm password',
      AppTranslationKeys.emailHint: 'Enter your email',
      AppTranslationKeys.passwordHint: 'Enter password',
      AppTranslationKeys.loginSuccess: 'Login successful',
      AppTranslationKeys.loginError: 'Login failed. Please try again.',

      // Validation
      AppTranslationKeys.emailRequired: 'Please enter email',
      AppTranslationKeys.emailInvalid: 'Invalid email',
      AppTranslationKeys.passwordRequired: 'Please enter password',
      AppTranslationKeys.passwordTooShort:
          'Password must be at least 6 characters',
      AppTranslationKeys.passwordMismatch: 'Passwords do not match',

      // Network
      AppTranslationKeys.connectionError: 'Connection error. Please try again.',
      AppTranslationKeys.connectionTimeout:
          'Connection timeout. Please try again.',
      AppTranslationKeys.serverError: 'Server error. Please try again later.',
      AppTranslationKeys.noInternet: 'No internet connection',

      // Home
      AppTranslationKeys.home: 'Home',
      AppTranslationKeys.homeTitle: 'Robot Delivery',
      AppTranslationKeys.upcomingOrders: 'Upcoming Orders',
      AppTranslationKeys.seeAll: 'See All',
      AppTranslationKeys.currentDelivery: 'Current Delivery',
      AppTranslationKeys.arrivingSoon: 'Arriving Soon',
      AppTranslationKeys.currentDeliveryHeadline: 'Robot is 5 mins away',
      // Quick Actions
      AppTranslationKeys.newOrder: 'New Order',
      AppTranslationKeys.address: 'Address',
      AppTranslationKeys.history: 'History',
      AppTranslationKeys.support: 'Support',

      // Profile
      AppTranslationKeys.profileView: 'Profile',
      AppTranslationKeys.userOrShopName: 'User or shop name',
      AppTranslationKeys.phoneNumber: 'Phone number',
      AppTranslationKeys.addressField: 'Address',
      AppTranslationKeys.updateProfile: 'Update Profile',

      // Notifications
      AppTranslationKeys.notifications: 'Notifications',
      AppTranslationKeys.markAllRead: 'Mark all read',
      AppTranslationKeys.alerts: 'Alerts',
      AppTranslationKeys.updates: 'Updates',
      AppTranslationKeys.promos: 'Promos',
      AppTranslationKeys.newLabel: 'NEW',
      AppTranslationKeys.earlierLabel: 'EARLIER',
      AppTranslationKeys.noNotifications: 'No notifications',

      // Map
      AppTranslationKeys.mapTitle: 'Map',
      AppTranslationKeys.robot: 'Robot',
      AppTranslationKeys.pickup: 'Pickup',
      AppTranslationKeys.dropoff: 'Dropoff',
      AppTranslationKeys.currentDeliveryDescription:
          'Your package is turning onto Main St.',
      AppTranslationKeys.trackLive: 'Track Live',
      AppTranslationKeys.trackingId: 'Tracking ID:',

      // Order status
      AppTranslationKeys.moving: 'Moving',
      AppTranslationKeys.inTransit: 'In Transit',
      AppTranslationKeys.scheduled: 'Scheduled',

      AppTranslationKeys.recipientName: 'Recipient Name',
      AppTranslationKeys.recipientAddress: 'Recipient Address',
      AppTranslationKeys.packageWeight: 'Package Weight',
      AppTranslationKeys.createNewOrder: 'Create New Order',
      AppTranslationKeys.shippingLocation: 'Shipping Location',
      AppTranslationKeys.submitOrder: 'Submit Order',
    },
  };
}
