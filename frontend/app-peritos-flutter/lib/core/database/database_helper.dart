import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:path/path.dart' as p;

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._internal();
  static Database? _database;

  // Almacenamiento en memoria para modo Web (Chrome)
  final List<Map<String, dynamic>> _webInspecciones = [];
  final List<Map<String, dynamic>> _webPartes = [];
  final List<Map<String, dynamic>> _webSos = [];
  int _nextInspeccionId = 1;
  int _nextSosId = 1;

  DatabaseHelper._internal();

  Future<Database?> get database async {
    if (kIsWeb) return null;
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    // Si corre en Windows / Linux de escritorio o tests, inicializar sqflite_ffi
    if (!kIsWeb && (Platform.isWindows || Platform.isLinux)) {
      sqfliteFfiInit();
      databaseFactory = databaseFactoryFfi;
    }

    final dbPath = await getDatabasesPath();
    final path = p.join(dbPath, 'aegiscore_offline_peritajes.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // 1. Tabla de inspecciones / peritajes técnicos offline (CU07)
    await db.execute('''
      CREATE TABLE inspecciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reclamo_id TEXT NOT NULL,
        perito_id TEXT NOT NULL,
        fecha_inspeccion TEXT NOT NULL,
        monto_estimado_total REAL NOT NULL,
        observaciones TEXT,
        fotos_evidencia TEXT,
        estado_sync TEXT NOT NULL DEFAULT 'PENDIENTE',
        idempotency_key TEXT,
        payload_hash TEXT,
        created_at TEXT NOT NULL
      )
    ''');

    // 2. Tabla de detalle de partes vehiculares evaluadas con IA
    await db.execute('''
      CREATE TABLE partes_inspeccionadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspeccion_id INTEGER NOT NULL,
        parte TEXT NOT NULL,
        severidad TEXT NOT NULL,
        costo_estimado REAL NOT NULL,
        confianza_ia REAL,
        FOREIGN KEY (inspeccion_id) REFERENCES inspecciones (id) ON DELETE CASCADE
      )
    ''');

    // 3. Tabla de reportes SOS locales de emergencia (CU06)
    await db.execute('''
      CREATE TABLE siniestros_sos_locales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poliza_id TEXT NOT NULL,
        cliente_id TEXT NOT NULL,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        direccion TEXT,
        descripcion TEXT NOT NULL,
        severidad TEXT NOT NULL,
        heridos INTEGER DEFAULT 0,
        vehiculo_inmovilizado INTEGER DEFAULT 0,
        airbag_desplegado INTEGER DEFAULT 0,
        estado_sync TEXT NOT NULL DEFAULT 'PENDIENTE',
        idempotency_key TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');
  }

  // Operaciones para Inspecciones (CU07 / CU08)
  Future<int> insertarInspeccion(Map<String, dynamic> inspeccion, List<Map<String, dynamic>> partes) async {
    if (kIsWeb) {
      final id = _nextInspeccionId++;
      final inspCopy = Map<String, dynamic>.from(inspeccion);
      inspCopy['id'] = id;
      _webInspecciones.add(inspCopy);
      for (final parte in partes) {
        final pCopy = Map<String, dynamic>.from(parte);
        pCopy['inspeccion_id'] = id;
        _webPartes.add(pCopy);
      }
      return id;
    }
    final db = (await database)!;
    return await db.transaction((txn) async {
      final inspeccionId = await txn.insert('inspecciones', inspeccion);
      for (final parte in partes) {
        final parteMap = Map<String, dynamic>.from(parte);
        parteMap['inspeccion_id'] = inspeccionId;
        await txn.insert('partes_inspeccionadas', parteMap);
      }
      return inspeccionId;
    });
  }

  Future<List<Map<String, dynamic>>> obtenerInspeccionesPendientes() async {
    if (kIsWeb) {
      return _webInspecciones.where((i) => i['estado_sync'] == 'PENDIENTE').toList();
    }
    final db = (await database)!;
    return await db.query(
      'inspecciones',
      where: 'estado_sync = ?',
      whereArgs: ['PENDIENTE'],
      orderBy: 'created_at ASC',
    );
  }

  Future<List<Map<String, dynamic>>> obtenerPartesDeInspeccion(int inspeccionId) async {
    if (kIsWeb) {
      return _webPartes.where((p) => p['inspeccion_id'] == inspeccionId).toList();
    }
    final db = (await database)!;
    return await db.query(
      'partes_inspeccionadas',
      where: 'inspeccion_id = ?',
      whereArgs: [inspeccionId],
    );
  }

  Future<void> marcarInspeccionSincronizada(int id, String idempotencyKey) async {
    if (kIsWeb) {
      for (final i in _webInspecciones) {
        if (i['id'] == id) {
          i['estado_sync'] = 'SINCRONIZADO';
          i['idempotency_key'] = idempotencyKey;
        }
      }
      return;
    }
    final db = (await database)!;
    await db.update(
      'inspecciones',
      {
        'estado_sync': 'SINCRONIZADO',
        'idempotency_key': idempotencyKey,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Map<String, dynamic>>> obtenerTodasInspecciones() async {
    if (kIsWeb) {
      return List<Map<String, dynamic>>.from(_webInspecciones.reversed);
    }
    final db = (await database)!;
    return await db.query('inspecciones', orderBy: 'created_at DESC');
  }

  // Operaciones para SOS Emergencia (CU06)
  Future<int> insertarSosLocal(Map<String, dynamic> sos) async {
    if (kIsWeb) {
      final id = _nextSosId++;
      final sosCopy = Map<String, dynamic>.from(sos);
      sosCopy['id'] = id;
      _webSos.add(sosCopy);
      return id;
    }
    final db = (await database)!;
    return await db.insert('siniestros_sos_locales', sos);
  }

  Future<List<Map<String, dynamic>>> obtenerSosPendientes() async {
    if (kIsWeb) {
      return _webSos.where((s) => s['estado_sync'] == 'PENDIENTE').toList();
    }
    final db = (await database)!;
    return await db.query(
      'siniestros_sos_locales',
      where: 'estado_sync = ?',
      whereArgs: ['PENDIENTE'],
      orderBy: 'created_at ASC',
    );
  }

  Future<void> marcarSosSincronizado(int id) async {
    if (kIsWeb) {
      for (final s in _webSos) {
        if (s['id'] == id) {
          s['estado_sync'] = 'SINCRONIZADO';
        }
      }
      return;
    }
    final db = (await database)!;
    await db.update(
      'siniestros_sos_locales',
      {'estado_sync': 'SINCRONIZADO'},
      where: 'estado_sync = ?',
      whereArgs: [id],
    );
  }
}
