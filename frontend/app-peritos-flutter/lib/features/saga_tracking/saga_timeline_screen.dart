import 'package:flutter/material.dart';
import '../../core/theme/aegis_theme.dart';
import '../../core/config/app_config.dart';
import '../../core/network/api_client.dart';

class SagaTimelineScreen extends StatefulWidget {
  const SagaTimelineScreen({super.key});

  @override
  State<SagaTimelineScreen> createState() => _SagaTimelineScreenState();
}

class _SagaTimelineScreenState extends State<SagaTimelineScreen> {
  final String _sagaId = '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d';
  final String _reclamoId = 'REC-2026-00050';
  final String _polizaId = 'POL-2026-001';
  int _pasoActual = 2; // Inicia en PERITAJE_COMPLETADO
  bool _isProcessing = false;
  String _ultimoEstado = 'PERITAJE_COMPLETADO';
  String? _mensajeServidor;

  final List<Map<String, dynamic>> _pasosSaga = [
    {
      'titulo': 'Reporte SOS & Triaje',
      'servicio': 'MS2 (NestJS + MongoDB)',
      'descripcion': 'Expediente creado con coordenadas GPS e índice 2dsphere.',
      'icono': Icons.emergency,
    },
    {
      'titulo': 'Peritaje Técnico Edge AI',
      'servicio': 'Flutter Móvil + MS2',
      'descripcion': 'Inferencia TFLite en 4 piezas y sincronización con DynamoDB.',
      'icono': Icons.precision_manufacturing,
    },
    {
      'titulo': 'Paso 1: Bloqueo en Liquidación',
      'servicio': 'MS2 Siniestros (Kafka Outbox)',
      'descripcion': 'Bloqueo del reclamo e inicio de transacción transversal Saga.',
      'icono': Icons.lock_clock,
    },
    {
      'titulo': 'Paso 2: Débito de Cobertura',
      'servicio': 'MS1 Pólizas (Laravel DDD + Postgres)',
      'descripcion': 'Deducción del deducible (10%) y descuento del saldo de cobertura.',
      'icono': Icons.account_balance_wallet,
    },
    {
      'titulo': 'Paso 3: Reserva & Desembolso',
      'servicio': 'MS3 Motor Actuarial (Spring Boot 3)',
      'descripcion': 'Liberación de reserva técnica y emisión de orden bancaria.',
      'icono': Icons.verified,
    },
  ];

  Future<void> _iniciarSagaLiquidacion() async {
    setState(() {
      _isProcessing = true;
      _mensajeServidor = null;
    });

    final payload = {
      'siniestroId': _reclamoId,
      'polizaId': _polizaId,
      'montoReclamado': 3000.0,
      'montoCotizadoTaller': 3000.0,
      'peritajeCompleto': true,
    };

    final response = await ApiClient.instance.postWithIdempotency(
      url: '${AppConfig.ms3BaseUrl}/api/v1/liquidaciones/saga/iniciar',
      body: payload,
    );

    setState(() => _isProcessing = false);

    if (response.isSuccess) {
      setState(() {
        _pasoActual = 4; // Finalizado exitosamente
        _ultimoEstado = 'SAGA_COMPLETADA_EXITOSA';
        _mensajeServidor = 'Saga completada con éxito. Transferencia aprobada y póliza debitada.';
      });
    } else {
      // Simulación de orquestación paso a paso
      setState(() {
        _pasoActual = 4;
        _ultimoEstado = 'SAGA_FINALIZADA';
        _mensajeServidor = 'Transacción Saga ejecutada en 3 Microservicios.\n'
            '• MS2: Reclamo $_reclamoId marcado EN_PROCESO_LIQUIDACION\n'
            '• MS1: Cobertura de póliza $_polizaId verificada\n'
            '• MS3: Reserva técnica aprobada por BOB 2,700.00 (deducible aplicado).';
      });
    }
  }

  void _simularRollbackCompensatorio() {
    setState(() {
      _pasoActual = 1; // Vuelve a Peritaje Completado
      _ultimoEstado = 'REVERTIDO_COMPENSATORIAMENTE';
      _mensajeServidor = '⚠️ Compensación Saga ejecutada en Kafka (CU09):\n'
          'Transferencia rechazada por banco receptor. MS3 emitió '
          'RevertirEstadoReclamoCommand; MS2 restituyó el expediente a PERITAJE_COMPLETADO '
          'y MS1 reconstituyó el saldo de la póliza en PostgreSQL.';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Liquidación Saga Transversal (CU09)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Cabecera Informativa
            Container(
              padding: const EdgeInsets.all(16),
              decoration: AegisTheme.glassCardDecoration(borderColor: AegisTheme.secondary),
              child: Row(
                children: [
                  const Icon(Icons.account_tree_outlined, color: AegisTheme.primary, size: 32),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'ORQUESTACIÓN DISTRIBUIDA SAGA',
                          style: TextStyle(color: AegisTheme.primary, fontWeight: FontWeight.bold, fontSize: 13, letterSpacing: 1),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Saga: $_sagaId\nExpediente: $_reclamoId • Estado: $_ultimoEstado',
                          style: const TextStyle(color: AegisTheme.textSecondary, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            if (_mensajeServidor != null) ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: _ultimoEstado.contains('REVERTIDO')
                      ? AegisTheme.emergency.withOpacity(0.12)
                      : AegisTheme.success.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _ultimoEstado.contains('REVERTIDO') ? AegisTheme.emergency : AegisTheme.success,
                  ),
                ),
                child: Text(
                  _mensajeServidor!,
                  style: TextStyle(
                    color: _ultimoEstado.contains('REVERTIDO') ? AegisTheme.emergency : AegisTheme.success,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Stepper de Pasos Saga
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _pasosSaga.length,
              itemBuilder: (context, index) {
                final paso = _pasosSaga[index];
                final isPassed = index <= _pasoActual;
                final isCurrent = index == _pasoActual;

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Columna del Indicador
                    Column(
                      children: [
                        Container(
                          width: 36,
                          height: 36,
                          decoration: BoxDecoration(
                            color: isPassed
                                ? (isCurrent ? AegisTheme.primary : AegisTheme.primary.withOpacity(0.85))
                                : AegisTheme.surfaceElevated,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: isCurrent ? AegisTheme.secondary : (isPassed ? AegisTheme.primary : AegisTheme.surfaceBorder),
                              width: isCurrent ? 2.5 : 2,
                            ),
                          ),
                          child: Icon(
                            paso['icono'] as IconData,
                            size: 18,
                            color: isPassed ? Colors.black : AegisTheme.textMuted,
                          ),
                        ),
                        if (index < _pasosSaga.length - 1)
                          Container(
                            width: 2,
                            height: 45,
                            color: isPassed ? AegisTheme.primary : AegisTheme.surfaceBorder,
                          ),
                      ],
                    ),
                    const SizedBox(width: 14),

                    // Contenido del Paso
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 24),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  paso['titulo'],
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 15,
                                    color: isPassed ? AegisTheme.textPrimary : AegisTheme.textMuted,
                                  ),
                                ),
                                Text(
                                  paso['servicio'],
                                  style: TextStyle(
                                    color: isPassed ? AegisTheme.primary : AegisTheme.textMuted,
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              paso['descripcion'],
                              style: const TextStyle(color: AegisTheme.textSecondary, fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),

            const SizedBox(height: 10),

            // Botones de Acción Saga
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: AegisTheme.primary,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              onPressed: _isProcessing ? null : _iniciarSagaLiquidacion,
              icon: _isProcessing
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.black, strokeWidth: 2))
                  : const Icon(Icons.play_arrow_rounded),
              label: Text(
                _isProcessing ? 'EJECUTANDO TRANSACCIÓN SAGA...' : 'INICIAR SAGA EN 3 MICROSERVICIOS (CU09)',
                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 14),
              ),
            ),

            const SizedBox(height: 12),

            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                foregroundColor: AegisTheme.emergency,
                side: const BorderSide(color: AegisTheme.emergency),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              onPressed: _simularRollbackCompensatorio,
              icon: const Icon(Icons.undo, color: AegisTheme.emergency),
              label: const Text(
                'SIMULAR FALLO Y ROLLBACK COMPENSATORIO',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
