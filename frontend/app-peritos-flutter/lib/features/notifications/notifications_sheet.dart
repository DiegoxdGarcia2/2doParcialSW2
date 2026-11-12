import 'package:flutter/material.dart';
import '../../core/services/push_notification_service.dart';
import '../../core/theme/aegis_theme.dart';
import 'notification_model.dart';

class NotificationsSheet extends StatefulWidget {
  const NotificationsSheet({super.key});

  static void show(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const NotificationsSheet(),
    );
  }

  @override
  State<NotificationsSheet> createState() => _NotificationsSheetState();
}

class _NotificationsSheetState extends State<NotificationsSheet> {
  bool _isLoadingAction = false;

  @override
  Widget build(BuildContext context) {
    final pushService = PushNotificationService();

    return Container(
      height: MediaQuery.of(context).size.height * 0.80,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Barra de agarre
          Container(
            margin: const EdgeInsets.only(top: 12, bottom: 8),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Cabecera Principal
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AegisTheme.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.notifications_active, color: AegisTheme.primary, size: 22),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Centro de Notificaciones Push',
                          style: TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0B1C30),
                          ),
                        ),
                        ValueListenableBuilder<int>(
                          valueListenable: pushService.unreadCountNotifier,
                          builder: (context, count, _) {
                            return Text(
                              count > 0 ? '$count alertas sin leer' : 'Bandeja al día',
                              style: TextStyle(
                                fontSize: 13,
                                color: count > 0 ? Colors.orange.shade800 : Colors.grey.shade600,
                                fontWeight: count > 0 ? FontWeight.w600 : FontWeight.normal,
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ],
                ),
                PopupMenuButton<String>(
                  icon: const Icon(Icons.more_vert, color: Colors.grey),
                  onSelected: (value) async {
                    if (value == 'read_all') {
                      pushService.markAllAsRead();
                    } else if (value == 'clear') {
                      pushService.clearAll();
                    } else if (value == 'sync_cloud') {
                      setState(() => _isLoadingAction = true);
                      await pushService.sincronizarNotificacionesCloud(esPrimeraCarga: false);
                      setState(() => _isLoadingAction = false);
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Alertas sincronizadas con LangGraph Cloud.')),
                        );
                      }
                    } else if (value == 'disparar_langgraph') {
                      setState(() => _isLoadingAction = true);
                      final ok = await pushService.dispararCicloLangGraphDesdeMovil();
                      setState(() => _isLoadingAction = false);
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(ok
                                ? 'Ciclo LangGraph CU14 ejecutado con éxito en MS4.'
                                : 'Error al conectar con MS4.'),
                          ),
                        );
                      }
                    } else if (value == 'inyectar_siniestro') {
                      setState(() => _isLoadingAction = true);
                      final ok = await pushService.inyectarSiniestroPruebaDesdeMovil();
                      setState(() => _isLoadingAction = false);
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(ok
                                ? 'Siniestro inyectado en MongoDB. Auto-remediación disparada.'
                                : 'Error al inyectar siniestro.'),
                          ),
                        );
                      }
                    } else if (value == 'test_sos') {
                      pushService.showEmergencyAlert(
                        title: 'Simulación Choque en Av. Cristo Redentor',
                        body: 'Sensor detectó desaceleración violenta > 28 m/s². Despacho pericial solicitado.',
                      );
                    }
                  },
                  itemBuilder: (context) => [
                    const PopupMenuItem(
                      value: 'sync_cloud',
                      child: Row(
                        children: [
                          Icon(Icons.sync, size: 18, color: Colors.blue),
                          SizedBox(width: 8),
                          Text('Sincronizar Alertas Cloud Ahora'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'disparar_langgraph',
                      child: Row(
                        children: [
                          Icon(Icons.bolt, size: 18, color: Colors.amber),
                          SizedBox(width: 8),
                          Text('Disparar Ciclo LangGraph (CU14)'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'inyectar_siniestro',
                      child: Row(
                        children: [
                          Icon(Icons.add_alert, size: 18, color: Colors.redAccent),
                          SizedBox(width: 8),
                          Text('Inyectar Siniestro Prueba Cloud'),
                        ],
                      ),
                    ),
                    const PopupMenuDivider(),
                    const PopupMenuItem(
                      value: 'test_sos',
                      child: Row(
                        children: [
                          Icon(Icons.notification_important, size: 18, color: Colors.orange),
                          SizedBox(width: 8),
                          Text('Probar Alerta SOS Local'),
                        ],
                      ),
                    ),
                    const PopupMenuItem(
                      value: 'read_all',
                      child: Text('Marcar todas leídas'),
                    ),
                    const PopupMenuItem(
                      value: 'clear',
                      child: Text('Limpiar bandeja'),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Banner de Estado Cloud en Vivo
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFE2E8F0)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Colors.green,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'Canal LangGraph Cloud 24/7 (MS4)',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                  ],
                ),
                _isLoadingAction
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : InkWell(
                        onTap: () async {
                          setState(() => _isLoadingAction = true);
                          await pushService.sincronizarNotificacionesCloud(esPrimeraCarga: false);
                          setState(() => _isLoadingAction = false);
                        },
                        child: const Row(
                          children: [
                            Icon(Icons.refresh, size: 15, color: AegisTheme.primary),
                            SizedBox(width: 4),
                            Text(
                              'Actualizar',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: AegisTheme.primary,
                              ),
                            ),
                          ],
                        ),
                      ),
              ],
            ),
          ),

          const Divider(height: 1),

          // Lista de notificaciones
          Expanded(
            child: ValueListenableBuilder<List<NotificationModel>>(
              valueListenable: pushService.notificationsNotifier,
              builder: (context, notifs, _) {
                if (notifs.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.notifications_off_outlined, size: 48, color: Colors.grey.shade400),
                        const SizedBox(height: 12),
                        Text(
                          'No hay notificaciones registradas',
                          style: TextStyle(fontSize: 15, color: Colors.grey.shade600),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton.icon(
                          onPressed: () {
                            pushService.showEmergencyAlert(
                              title: 'Alerta Pericial Simulada',
                              body: 'Notificación push en tiempo real conectada al canal de alta prioridad.',
                            );
                          },
                          icon: const Icon(Icons.send, size: 16),
                          label: const Text('Generar Notificación de Prueba'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AegisTheme.primary,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  itemCount: notifs.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final item = notifs[index];
                    return _buildNotificationCard(context, item, pushService);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationCard(
    BuildContext context,
    NotificationModel item,
    PushNotificationService service,
  ) {
    Color badgeColor;
    IconData iconData;

    switch (item.tipo) {
      case 'sos':
        badgeColor = Colors.red.shade600;
        iconData = Icons.warning_amber_rounded;
        break;
      case 'peritaje':
        badgeColor = AegisTheme.primary;
        iconData = Icons.document_scanner;
        break;
      case 'qr':
        badgeColor = Colors.purple.shade600;
        iconData = Icons.qr_code_2;
        break;
      default:
        badgeColor = Colors.blue.shade600;
        iconData = Icons.info_outline;
    }

    final bool esOrigenCloud = item.origen == 'langgraph_cloud';

    return InkWell(
      onTap: () => service.markAsRead(item.id),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: item.leida ? Colors.grey.shade50 : badgeColor.withValues(alpha: 0.06),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: item.leida ? Colors.grey.shade200 : badgeColor.withValues(alpha: 0.3),
            width: item.leida ? 1 : 1.5,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: badgeColor.withValues(alpha: 0.12),
                shape: BoxShape.circle,
              ),
              child: Icon(iconData, color: badgeColor, size: 20),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          item.titulo,
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: item.leida ? FontWeight.w600 : FontWeight.bold,
                            color: const Color(0xFF0B1C30),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(
                        item.timeFormatted,
                        style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                      ),
                    ],
                  ),
                  const SizedBox(height: 3),
                  if (esOrigenCloud)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1.5),
                        decoration: BoxDecoration(
                          color: const Color(0xFF005C55).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'LANGGRAPH CLOUD (CU14)',
                          style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF005C55),
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    ),
                  Text(
                    item.mensaje,
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey.shade700,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
