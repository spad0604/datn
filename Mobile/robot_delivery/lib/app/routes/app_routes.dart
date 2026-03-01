// ignore_for_file: constant_identifier_names

part of 'app_pages.dart';

abstract class Routes {
  Routes._();

  static const HOME = _Paths.HOME;
  static const LOGIN = _Paths.LOGIN;
  static const ORDERS = _Paths.ORDERS;
  static const MAP = _Paths.MAP;
  static const PROFILE = _Paths.PROFILE;
  static const CREATE_ORDER = _Paths.CREATE_ORDER;
  static const NOTIFICATIONS = _Paths.NOTIFICATIONS;
}

abstract class _Paths {
  _Paths._();

  static const HOME = '/';
  static const LOGIN = '/login';
  static const ORDERS = '/orders';
  static const MAP = '/map';
  static const PROFILE = '/profile';
  static const CREATE_ORDER = '/create-order';
  static const NOTIFICATIONS = '/notifications';
}
