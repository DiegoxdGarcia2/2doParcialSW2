class NotificationModel {
  final int id;
  final String titulo;
  final String mensaje;
  final String tipo; // 'sos', 'peritaje', 'qr', 'alerta', 'info'
  final String origen; // 'sistema', 'perito', 'cliente'
  final bool leida;
  final String creado;
  final Map<String, dynamic>? metadata;

  NotificationModel({
    required this.id,
    required this.titulo,
    required this.mensaje,
    required this.tipo,
    required this.origen,
    required this.leida,
    required this.creado,
    this.metadata,
  });

  String get timeFormatted {
    try {
      final dt = DateTime.parse(creado);
      final hour = dt.hour.toString().padLeft(2, '0');
      final minute = dt.minute.toString().padLeft(2, '0');
      return '$hour:$minute';
    } catch (_) {
      return '';
    }
  }

  NotificationModel copyWith({bool? leida}) {
    return NotificationModel(
      id: id,
      titulo: titulo,
      mensaje: mensaje,
      tipo: tipo,
      origen: origen,
      leida: leida ?? this.leida,
      creado: creado,
      metadata: metadata,
    );
  }

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] is int ? json['id'] : int.tryParse(json['id'].toString()) ?? DateTime.now().millisecondsSinceEpoch,
      titulo: json['titulo'] ?? '',
      mensaje: json['mensaje'] ?? '',
      tipo: json['tipo'] ?? 'info',
      origen: json['origen'] ?? 'sistema',
      leida: json['leida'] ?? false,
      creado: json['creado'] ?? DateTime.now().toIso8601String(),
      metadata: json['metadata'] is Map<String, dynamic> ? json['metadata'] : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'titulo': titulo,
    'mensaje': mensaje,
    'tipo': tipo,
    'origen': origen,
    'leida': leida,
    'creado': creado,
    'metadata': metadata,
  };
}

