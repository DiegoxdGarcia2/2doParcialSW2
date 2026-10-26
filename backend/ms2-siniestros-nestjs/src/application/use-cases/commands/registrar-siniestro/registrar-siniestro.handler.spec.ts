import { RegistrarSiniestroHandler } from './registrar-siniestro.handler';
import { RegistrarSiniestroCommand } from './registrar-siniestro.command';
import { IReclamoRepository } from '../../../../domain/repositories/reclamo.repository.interface';
import { INotificationPort } from '../../../ports/notification.port';
import { ReclamoSiniestro } from '../../../../domain/entities/reclamo-siniestro.entity';

describe('Application: RegistrarSiniestroHandler (CU06)', () => {
  let handler: RegistrarSiniestroHandler;
  let mockReclamoRepository: jest.Mocked<IReclamoRepository>;
  let mockNotificationPort: jest.Mocked<INotificationPort>;

  beforeEach(() => {
    mockReclamoRepository = {
      save: jest.fn().mockResolvedValue(undefined),
      update: jest.fn().mockResolvedValue(undefined),
      findById: jest.fn(),
      findByClienteId: jest.fn(),
      findByPolizaId: jest.fn(),
      findCercanos: jest.fn(),
      generarSiguienteReclamoId: jest.fn().mockResolvedValue('REC-2026-00100'),
    };

    mockNotificationPort = {
      enviarNotificacionPush: jest.fn().mockResolvedValue(true),
      notificarAsignacionPerito: jest.fn().mockResolvedValue(true),
      notificarEstadoSiniestro: jest.fn().mockResolvedValue(true),
    };

    handler = new RegistrarSiniestroHandler(mockReclamoRepository, mockNotificationPort);
  });

  it('debe registrar un siniestro SOS con triaje automático GRAVE y enviar notificación Push', async () => {
    const command = new RegistrarSiniestroCommand(
      'pol-uuid-1234',
      'cli-uuid-5678',
      -16.5050,
      -68.1300,
      'Colisión frontal múltiple',
      'Av. Arce esquina Pinilla',
      1, // 1 herido => debe ser GRAVE
      true,
      true,
      ['http://img.local/evidencia1.jpg'],
    );

    const result = await handler.execute(command);

    expect(result.reclamoId).toBe('REC-2026-00100');
    expect(result.severidad).toBe('GRAVE');
    expect(result.estado).toBe('REPORTADO_SOS');
    expect(mockReclamoRepository.save).toHaveBeenCalledTimes(1);

    const savedReclamo = mockReclamoRepository.save.mock.calls[0][0] as ReclamoSiniestro;
    expect(savedReclamo.ubicacion.latitud).toBe(-16.5050);
    expect(savedReclamo.ubicacion.longitud).toBe(-68.1300);

    expect(mockNotificationPort.notificarEstadoSiniestro).toHaveBeenCalledWith(
      'cli-uuid-5678',
      'REC-2026-00100',
      expect.stringContaining('GRAVE'),
    );
  });
});
