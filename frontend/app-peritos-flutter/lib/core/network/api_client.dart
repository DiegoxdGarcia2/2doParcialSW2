import 'dart:convert';
import 'package:http/http.dart' as http;
import '../idempotency/idempotency_service.dart';

class ApiResponse {
  final bool isSuccess;
  final int statusCode;
  final dynamic data;
  final String? errorMessage;
  final bool isCacheHit;

  ApiResponse({
    required this.isSuccess,
    required this.statusCode,
    this.data,
    this.errorMessage,
    this.isCacheHit = false,
  });
}

class ApiClient {
  static final ApiClient instance = ApiClient._internal();
  final http.Client _client = http.Client();

  ApiClient._internal();

  /// Petición POST con protocolo de Idempotencia estricto (UUIDv4 + SHA-256)
  Future<ApiResponse> postWithIdempotency({
    required String url,
    required Map<String, dynamic> body,
    String? customIdempotencyKey,
  }) async {
    final idempotencyKey = customIdempotencyKey ?? IdempotencyService.generateIdempotencyKey();
    final headers = IdempotencyService.buildHeaders(idempotencyKey: idempotencyKey);
    final jsonBody = jsonEncode(body);

    try {
      final response = await _client
          .post(
            Uri.parse(url),
            headers: headers,
            body: jsonBody,
          )
          .timeout(const Duration(seconds: 5));

      final isCache = response.headers['x-cache-lookup'] == 'HIT_IDEMPOTENCY_DYNAMODB';
      dynamic responseData;
      try {
        responseData = jsonDecode(response.body);
      } catch (_) {
        responseData = response.body;
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return ApiResponse(
          isSuccess: true,
          statusCode: response.statusCode,
          data: responseData,
          isCacheHit: isCache,
        );
      } else {
        return ApiResponse(
          isSuccess: false,
          statusCode: response.statusCode,
          errorMessage: responseData is Map ? (responseData['message'] ?? responseData['error']) : 'Error del servidor',
          data: responseData,
        );
      }
    } catch (e) {
      // Error de red / Sin conexión
      return ApiResponse(
        isSuccess: false,
        statusCode: 0,
        errorMessage: 'Sin conexión con el servidor ($e). Operación en cola offline.',
      );
    }
  }

  /// Petición GET estándar
  Future<ApiResponse> get(String url) async {
    try {
      final response = await _client.get(
        Uri.parse(url),
        headers: {'Accept': 'application/json'},
      ).timeout(const Duration(seconds: 4));

      dynamic responseData;
      try {
        responseData = jsonDecode(response.body);
      } catch (_) {
        responseData = response.body;
      }

      return ApiResponse(
        isSuccess: response.statusCode >= 200 && response.statusCode < 300,
        statusCode: response.statusCode,
        data: responseData,
        errorMessage: response.statusCode >= 400 ? 'Error ${response.statusCode}' : null,
      );
    } catch (e) {
      return ApiResponse(
        isSuccess: false,
        statusCode: 0,
        errorMessage: 'Servicio no disponible: $e',
      );
    }
  }
}
