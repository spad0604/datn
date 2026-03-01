import 'package:robot_delivery/app/core/network/external_api_client.dart';
import 'package:robot_delivery/app/data/models/nominatim_model.dart';

class GeocodingRepository {
  static const String _baseUrl = 'https://nominatim.openstreetmap.org/search';
  static const String _reverseUrl =
      'https://nominatim.openstreetmap.org/reverse';

  // Nominatim requires a valid User-Agent identifying your app.
  static const Map<String, String> _defaultHeaders = {
    'User-Agent': 'robot_delivery/1.0 (mobile-app)',
    'Accept': 'application/json',
    'Accept-Language': 'vi',
  };

  Future<List<NominatimModel>> searchAddress(String query) async {
    final trimmed = query.trim();
    if (trimmed.isEmpty) return [];

    final formattedQuery = trimmed.replaceAll(' ', '+');

    final url =
        '$_baseUrl?q=$formattedQuery&format=json&limit=5&addressdetails=1&countrycodes=vn';

    try {
      final data = await ExternalApiClient.get(url, headers: _defaultHeaders);
      if (data is! List) return [];

      return data
          .whereType<Map<String, dynamic>>()
          .map(NominatimModel.fromJson)
          .toList();
    } catch (e) {
      return [];
    }
  }

  Future<String?> reverseGeocode({
    required double lat,
    required double lon,
  }) async {
    final url = '$_reverseUrl?lat=$lat&lon=$lon&format=json&addressdetails=1';

    try {
      final data = await ExternalApiClient.get(url, headers: _defaultHeaders);
      if (data is Map<String, dynamic>) {
        return data['display_name'] as String?;
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
