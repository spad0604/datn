// [
//     {
//         "place_id": 227539163,
//         "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
//         "osm_type": "way",
//         "osm_id": 1049553920,
//         "lat": "20.9765347",
//         "lon": "105.8124970",
//         "class": "amenity",
//         "type": "courthouse",
//         "place_rank": 30,
//         "importance": 7.283054856179167e-05,
//         "addresstype": "amenity",
//         "name": "Tòa án nhân dân Thành phố Hà Nội",
//         "display_name": "Tòa án nhân dân Thành phố Hà Nội, Ave 2, The Manor Central Park, Phường Định Công, Hà Nội, 10135, Việt Nam",
//         "address": {
//             "amenity": "Tòa án nhân dân Thành phố Hà Nội",
//             "road": "Ave 2",
//             "residential": "The Manor Central Park",
//             "city_district": "Phường Định Công",
//             "city": "Hà Nội",
//             "ISO3166-2-lvl4": "VN-HN",
//             "postcode": "10135",
//             "country": "Việt Nam",
//             "country_code": "vn"
//         },
//         "boundingbox": [
//             "20.9761806",
//             "20.9772854",
//             "105.8118932",
//             "105.8130544"
//         ]
//     }
// ]


class NominatimModel {
  final int placeId;
  final String licence;
  final String osmType;
  final int osmId;
  final double lat;
  final double lon;
  final String classType;
  final String type;
  final int placeRank;
  final double importance;
  final String addresstype;
  final String name;
  final String displayName;
  final Address? address;
  final List<String>? boundingBox;

  NominatimModel({
    required this.placeId,
    required this.licence,
    required this.osmType,
    required this.osmId,
    required this.lat,
    required this.lon,
    required this.classType,
    required this.type,
    required this.placeRank,
    required this.importance,
    required this.addresstype,
    required this.name,
    required this.displayName,
    required this.address,
    required this.boundingBox,
  });

  factory NominatimModel.fromJson(Map<String, dynamic> json) {
    return NominatimModel(
      placeId: json['place_id'] ?? 0,
      licence: json['licence'] ?? '',
      osmType: json['osm_type'] ?? '',
      osmId: json['osm_id'] ?? 0,
      lat: double.tryParse(json['lat'] ?? '') ?? 0.0,
      lon: double.tryParse(json['lon'] ?? '') ?? 0.0,
      classType: json['class'] ?? '',
      type: json['type'] ?? '',
      placeRank: json['place_rank'] ?? 0,
      importance: (json['importance'] is double)
          ? json['importance']
          : (json['importance'] is num)
              ? (json['importance'] as num).toDouble()
              : double.tryParse(json['importance']?.toString() ?? '') ?? 0.0,
      addresstype: json['addresstype'] ?? '',
      name: json['name'] ?? '',
      displayName: json['display_name'] ?? '',
      address: json['address'] != null ? Address.fromJson(json['address']) : null,
      boundingBox: json['boundingbox'] != null
          ? List<String>.from(json['boundingbox'])
          : null,
    );
  }
}


class Address {
  final String? amenity;
  final String? road;
  final String? residential;
  final String? cityDistrict;
  final String? city;
  final String? iso3166Lvl4;
  final String? postcode;
  final String? country;
  final String? countryCode;

  Address({
    this.amenity,
    this.road,
    this.residential,
    this.cityDistrict,
    this.city,
    this.iso3166Lvl4,
    this.postcode,
    this.country,
    this.countryCode,
  });

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      amenity: json['amenity'],
      road: json['road'],
      residential: json['residential'],
      cityDistrict: json['city_district'],
      city: json['city'],
      iso3166Lvl4: json['ISO3166-2-lvl4'],
      postcode: json['postcode'],
      country: json['country'],
      countryCode: json['country_code'],
    );
  }
}