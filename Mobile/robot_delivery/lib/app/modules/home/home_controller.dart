import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:latlong2/latlong.dart';
import 'package:robot_delivery/app/data/models/nominatim_model.dart';
import 'package:robot_delivery/app/data/repositories/geocoding_repository.dart';
import 'package:robot_delivery/app/modules/home/location_picker_map.dart';

class HomeController extends GetxController {
  HomeController({GeocodingRepository? geocodingRepository})
    : _geocodingRepository =
          geocodingRepository ?? Get.find<GeocodingRepository>();

  final GeocodingRepository _geocodingRepository;

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

  Worker? _shippingDebounceWorker;
  Worker? _recipientDebounceWorker;

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

  @override
  void onClose() {
    _shippingDebounceWorker?.dispose();
    _recipientDebounceWorker?.dispose();
    recipientNameController.dispose();
    shippingLocationController.dispose();
    recipientAddressController.dispose();
    weightController.dispose();
    super.onClose();
  }
}
