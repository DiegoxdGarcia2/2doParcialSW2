import { SincronizarPeritajeHandler } from './sincronizar-peritaje.handler';
import { SincronizarPeritajeCommand } from './sincronizar-peritaje.command';
import { IReclamoRepository } from '../../../../domain/repositories/reclamo.repository.interface';
import { INotificationPort } from '../../../ports/notification.port';
import { IEventPublisherPort } from '../../../ports/event-publisher.port';
import { ReclamoSiniestro } from '../../../../domain/entities/reclamo-siniestro.entity';
import { UbicacionGeoVO } from '../../../../domain/value-objects/ubicacion-geo.vo';
import { SeveridadVO } from '../../../../domain/value-objects/severidad.vo';
import { EstadoReclamoVO } from '../../../../domain/value-objects/estado-reclamo.vo';

describe('Application: SincronizarPeritajeHandler (CU07 / CU08)', () => {
  let handler: SincronizarPeritajeHandler;
  let mockReclamoRepository: jest.Mocked<IReclamoRepository>;
  let mockNotificationPort: jest.Mocked<INotificationPort>;
  let mockEventPublisherPort: jest.Mocked<IEventPublisherPort>;

  beforeEach(() => {
    mockReclamoRepository = {
      save: jest.fn(),
      update: jest.fn().mockResolvedValue(undefined),
      findById: jest.fn(),
      findByClienteId: jest.fn(),
      findByPolizaId: jest.fn(),
      findCercanos: jest.fn(),
      generarSiguienteReclamoId: jest.fn(),
    };

    mockNotificationPort = {
      enviarNotificacionPush: jest.fn().mockResolvedValue(true),
      notificarAsignacionPerito: jest.fn().mockResolvedValue(true),
      notificarEstadoSiniestro: jest.fn().mockResolvedValue(true),
    };

    mockEventPublisherPort = {
      publicarEvento: jest.fn().mockResolvedValue(undefined),
    };

    handler = new SincronizarPeritajeHandler(
      mockReclamoRepository,
      mockNotificationPort,
      mockEventPublisherPort,
    );
  });

  it('debe registrar el peritaje offline, actualizar estado a PERITAJE_COMPLETADO y emitir evento a Kafka', async () => {
    const reclamoExistente = new ReclamoSiniestro(
      'REC-2026-00050',
      'pol-uuid-1',
      'cli-uuid-1',
      new Date(),
      new UbicacionGeoVO(-16.5000, -68.1500),
      'Impacto en lateral izquierdo',
      new SeveridadVO('MODERADO'),
      new EstadoReclamoVO('REPORTADO_SOS'),
    );

    mockReclamoRepository.findById.mockResolvedValue(reclamoExistente);

    const command = new SincronizarPeritajeCommand(
      'REC-2026-00050',
      'PERITO-EXP-44',
      [
        { parte: 'puertas', severidad: 'GRAVE', costoEstimado: 2400, confianzaIa: 0.96 },
        { parte: 'parachoques', severidad: 'LEVE', costoEstimado: 600, confianzaIa: 0.88 },
      ],
      3000.0,
      ['http://s3.local/img/puerta.jpg'],
      'Daño severo en puerta delantera izquierda',
      true, // Sincronizado offline desde SQLite móvil
      'sha256-hash-mobile-sqlite-1234',
    );

    const result = await handler.execute(command);

    expect(result.reclamoId).toBe('REC-2026-00050');
    expect(result.estado).toBe('PERITAJE_COMPLETADO');
    expect(result.montoEstimadoTotal).toBe(3000.0);
    expect(mockReclamoRepository.update).toHaveBeenCalledTimes(1);
    expect(mockEventPublisherPort.publicarEvento).toHaveBeenCalledWith(
      'aegiscore.saga.events',
      expect.objectContaining({
        event_type: 'PeritajeCompletadoEvent',
      }),
    );
  });
});
