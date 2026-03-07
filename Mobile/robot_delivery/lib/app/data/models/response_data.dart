import 'package:freezed_annotation/freezed_annotation.dart';

part 'response_data.freezed.dart';
part 'response_data.g.dart';

@Freezed(genericArgumentFactories: true)
abstract class ResponseData<T> with _$ResponseData<T> {
  const factory ResponseData({
    String? message,
    T? data
  }) = _ResponseData;

  factory ResponseData.fromJson(Map<String, dynamic> json, T Function(Object? json) fromJsonT) => _$ResponseDataFromJson(json, fromJsonT);
}