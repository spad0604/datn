import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/data/models/nominatim_model.dart';
import 'package:robot_delivery/app/data/repositories/geocoding_repository.dart';
import 'package:robot_delivery/app/modules/home/location_picker_map.dart';
import 'package:robot_delivery/app/core/utils/app_snackbar.dart';

import 'package:robot_delivery/app/data/repositories/user_repository.dart';
import 'package:robot_delivery/app/data/repositories/order_repository.dart';
import 'package:robot_delivery/app/data/models/request/create_order_request.dart';

class HomeController extends GetxController {
  HomeController({
    GeocodingRepository? geocodingRepository,
    UserRepository? userRepository,
    OrderRepository? orderRepository,
  }) : _geocodingRepository =
           geocodingRepository ?? Get.find<GeocodingRepository>(),
       _userRepository = userRepository ?? Get.find<UserRepository>(),
       _orderRepository = orderRepository ?? Get.find<OrderRepository>();

  final GeocodingRepository _geocodingRepository;
  final UserRepository _userRepository;
  final OrderRepository _orderRepository;

  final RxBool isCreatingOrder = false.obs;

  final TextEditingController recipientPhoneController =
      TextEditingController();

  final TextEditingController recipientNameController = TextEditingController();

  final TextEditingController shippingLocationController =
      TextEditingController();

  final TextEditingController recipientAddressController =
      TextEditingController();

  final TextEditingController weightController = TextEditingController();

  final RxString _shippingQuery = ''.obs;
  final RxList<NominatimModel> shippingSuggestions = <NominatimModel>[].obs;
  final RxBool isSearchingShipping = false.obs;

  final RxnDouble shippingLat = RxnDouble();
  final RxnDouble shippingLon = RxnDouble();

  final RxString _recipientQuery = ''.obs;
  final RxList<NominatimModel> recipientSuggestions = <NominatimModel>[].obs;
  final RxBool isSearchingRecipient = false.obs;

  final RxnDouble recipientLat = RxnDouble();
  final RxnDouble recipientLon = RxnDouble();

  final RxBool isSearchingUser = false.obs;
  final RxString userSearchError = ''.obs;
  final RxBool isGettingCurrentLocation = false.obs;

  Worker? _shippingDebounceWorker;
  Worker? _recipientDebounceWorker;
  Worker? _phoneDebounceWorker;

  @override
  void onInit() {
    super.onInit();

    _shippingDebounceWorker = debounce<String>(_shippingQuery, (query) async {
      final trimmed = query.trim();
      if (trimmed.isEmpty) {
        shippingSuggestions.clear();
        return;
      }

      isSearchingShipping.value = true;
      try {
        final results = await _geocodingRepository.searchAddress(trimmed);
        shippingSuggestions.assignAll(results);
      } finally {
        isSearchingShipping.value = false;
      }
    }, time: const Duration(seconds: 1));

    _recipientDebounceWorker = debounce<String>(_recipientQuery, (query) async {
      final trimmed = query.trim();
      if (trimmed.isEmpty) {
        recipientSuggestions.clear();
        return;
      }

      isSearchingRecipient.value = true;
      try {
        final results = await _geocodingRepository.searchAddress(trimmed);
        recipientSuggestions.assignAll(results);
      } finally {
        isSearchingRecipient.value = false;
      }
    }, time: const Duration(seconds: 1));

    _phoneDebounceWorker = debounce<String>(
      recipientPhoneController.text.obs,
      (phone) =>
          {}, // Changed to use explicit button for phone search to avoid spamming
    );
  }

  Future<void> searchUserByPhone() async {
    final phone = recipientPhoneController.text.trim();
    if (phone.isEmpty) return;

    isSearchingUser.value = true;
    userSearchError.value = '';

    try {
      final response = await _userRepository.searchUserByPhone(phone);
      if (response.data != null) {
        final name =
            response.data!.fullName ?? response.data!.username ?? 'Unknown';
        recipientNameController.text = name;
        AppSnackbar.success('Tìm thấy người dùng: $name');
      } else {
        userSearchError.value = 'Không tìm thấy người dùng';
        AppSnackbar.error('Không tìm thấy người dùng với số điện thoại này');
      }
    } catch (e) {
      userSearchError.value = 'Lỗi tìm kiếm';
    } finally {
      isSearchingUser.value = false;
    }
  }

  Future<void> submitOrder() async {
    if (recipientNameController.text.isEmpty ||
        recipientPhoneController.text.isEmpty ||
        shippingLat.value == null ||
        recipientLat.value == null) {
      AppSnackbar.error(
        'Vui lòng điền đầy đủ thông tin bắt buộc và chọn vị trí trên bản đồ',
      );
      return;
    }

    isCreatingOrder.value = true;
    try {
      final request = CreateOrderRequest(
        recipientPhone: recipientPhoneController.text.trim(),
        startLat: shippingLat.value!.toString(),
        startLng: shippingLon.value!.toString(),
        deliveryLat: recipientLat.value!.toString(),
        deliveryLng: recipientLon.value!.toString(),
      );

      final response = await _orderRepository.createOrder(request);

      if (response.data != null) {
        AppSnackbar.success('Tạo đơn hàng thành công!, tự động thoát trong 2s');
        Future.delayed(const Duration(seconds: 2), () {
          Get.back();
          Get.back();
        });
      } else {
        AppSnackbar.error(response.message ?? 'Lỗi tạo đơn hàng');
      }
    } catch (e) {
      AppSnackbar.error('Đã xảy ra lỗi không mong muốn');
    } finally {
      isCreatingOrder.value = false;
    }
  }

  void onShippingQueryChanged(String value) {
    // If user edits text manually, clear chosen coordinates until they pick again.
    shippingLat.value = null;
    shippingLon.value = null;
    _shippingQuery.value = value;
  }

  void onRecipientQueryChanged(String value) {
    recipientLat.value = null;
    recipientLon.value = null;
    _recipientQuery.value = value;
  }

  void selectShippingSuggestion(NominatimModel suggestion) {
    shippingLocationController.text = suggestion.displayName;
    shippingLat.value = suggestion.lat;
    shippingLon.value = suggestion.lon;
    shippingSuggestions.clear();
    _shippingQuery.value = suggestion.displayName;
  }

  void selectRecipientSuggestion(NominatimModel suggestion) {
    recipientAddressController.text = suggestion.displayName;
    recipientLat.value = suggestion.lat;
    recipientLon.value = suggestion.lon;
    recipientSuggestions.clear();
    _recipientQuery.value = suggestion.displayName;
  }

  Future<void> pickShippingLocationFromMap() async {
    final initial = (shippingLat.value != null && shippingLon.value != null)
        ? LatLng(shippingLat.value!, shippingLon.value!)
        : const LatLng(21.027763, 105.834160); // Hanoi default

    final picked = await Get.to<LatLng>(
      () => LocationPickerMapPage(initialCenter: initial),
    );

    if (picked == null) return;

    shippingLat.value = picked.latitude;
    shippingLon.value = picked.longitude;
    shippingSuggestions.clear();

    final address = await _geocodingRepository.reverseGeocode(
      lat: picked.latitude,
      lon: picked.longitude,
    );
    shippingLocationController.text =
        address ?? '${picked.latitude}, ${picked.longitude}';
    _shippingQuery.value = shippingLocationController.text;
  }

  Future<void> pickRecipientAddressFromMap() async {
    final initial = (recipientLat.value != null && recipientLon.value != null)
        ? LatLng(recipientLat.value!, recipientLon.value!)
        : const LatLng(21.027763, 105.834160); // Hanoi default

    final picked = await Get.to<LatLng>(
      () => LocationPickerMapPage(initialCenter: initial),
    );

    if (picked == null) return;

    recipientLat.value = picked.latitude;
    recipientLon.value = picked.longitude;
    recipientSuggestions.clear();

    final address = await _geocodingRepository.reverseGeocode(
      lat: picked.latitude,
      lon: picked.longitude,
    );
    recipientAddressController.text =
        address ?? '${picked.latitude}, ${picked.longitude}';
    _recipientQuery.value = recipientAddressController.text;
  }

  Future<void> getCurrentLocationForDelivery() async {
    await _doGetCurrentLocation(
      onSuccess: (position, address) {
        recipientLat.value = position.latitude;
        recipientLon.value = position.longitude;
        recipientSuggestions.clear();
        recipientAddressController.text = address;
        _recipientQuery.value = address;
      },
    );
  }

  Future<void> getCurrentLocationForShipping() async {
    await _doGetCurrentLocation(
      onSuccess: (position, address) {
        shippingLat.value = position.latitude;
        shippingLon.value = position.longitude;
        shippingSuggestions.clear();
        shippingLocationController.text = address;
        _shippingQuery.value = address;
      },
    );
  }

  Future<void> _doGetCurrentLocation({
    required Function(Position position, String address) onSuccess,
  }) async {
    isGettingCurrentLocation.value = true;
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          AppSnackbar.error('Vui lòng cấp quyền truy cập vị trí');
          return;
        }
      }
      if (permission == LocationPermission.deniedForever) {
        AppSnackbar.error(
          'Quyền truy cập vị trí bị từ chối vĩnh viễn. Vui lòng bật trong Cài đặt.',
        );
        return;
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );

      final address =
          await _geocodingRepository.reverseGeocode(
            lat: position.latitude,
            lon: position.longitude,
          ) ??
          '${position.latitude.toStringAsFixed(5)}, ${position.longitude.toStringAsFixed(5)}';

      onSuccess(position, address);
      AppSnackbar.success('Đã lấy vị trí hiện tại!');
    } catch (e) {
      AppSnackbar.error('Không thể lấy vị trí: $e');
    } finally {
      isGettingCurrentLocation.value = false;
    }
  }

  @override
  void onClose() {
    _shippingDebounceWorker?.dispose();
    _recipientDebounceWorker?.dispose();
    _phoneDebounceWorker?.dispose();
    recipientPhoneController.dispose();
    recipientNameController.dispose();
    shippingLocationController.dispose();
    recipientAddressController.dispose();
    weightController.dispose();
    super.onClose();
  }
}
