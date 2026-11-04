# 📱 App Móvil Flutter: Peritaje en Terreno, Offline SQLite & Edge AI TFLite

## 📌 Contexto
- **Directorio:** `frontend/app-peritos-flutter/`
- **Framework:** Flutter 3.x / Dart (Android, iOS)
- **Diseño Visual:** Tema Corporativo Formal / Executive Precision (`AegisTheme`).
- **Hardware:** Cámara con guía visual, GPS de alta precisión y escáner/generador de códigos QR.
- **Persistencia Local:** SQLite (`sqflite`) vía `DatabaseHelper`.
- **IA Local On-Device:** TensorFlow Lite (`damage_classifier.tflite`).

---

## 🏛️ Módulos y Pantallas Principales
1. **Home Dashboard (`home_dashboard_screen.dart`):**
   - Tarjetas de acceso a los 5 módulos del Perfil B.
   - Indicador de estado de conexión y cola pendiente de sincronización.
2. **CU06 — SOS Emergency (`sos_emergency_screen.dart`):**
   - Disparo de alarma inmediata con geolocalización satelital precisa y fotos de choque.
3. **CU07 — Inspección Pericial Offline (`peritaje_capture_screen.dart`):**
   - Inferencia con modelo TFLite para parachoques, capó, faroles y puertas.
   - Guardado local 100% offline en `aegiscore_offline_peritajes.db`.
4. **CU08 — Cola de Sincronización Idempotente (`sync_queue_screen.dart`):**
   - Gestión de pestañas "En Cola SQLite" vs "Sincronizados en Nube".
   - Generación de `Idempotency-Key` UUIDv4 y hash SHA-256.
   - Selector en caliente de IP de red (`127.0.0.1` USB reverse, Wi-Fi LAN, Emulador).
5. **CU09 — Saga Timeline (`saga_timeline_screen.dart`):**
   - Seguimiento visual del ciclo de vida distribuido en 3 microservicios.
   - Simulación de compensación semántica (rollback en Kafka).
6. **CU10 — Pagos QR (`qr_payment_screen.dart`):**
   - Renderizado de código QR EMV/BCB y confirmación idempotente contra MS3 Spring Boot.

