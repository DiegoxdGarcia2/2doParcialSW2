import { ReclamoSiniestro } from './reclamo-siniestro.entity';
import { UbicacionGeoVO } from '../value-objects/ubicacion-geo.vo';
import { SeveridadVO } from '../value-objects/severidad.vo';
import { EstadoReclamoVO } from '../value-objects/estado-reclamo.vo';
import { PeritajeDetalle } from './peritaje-detalle.entity';
import { TransicionEstadoInvalidaException } from '../exceptions/domain.exceptions';

describe('Domain: ReclamoSiniestro Aggregate Root & Value Objects', () => {
  it('debe crear un reclamo con estado REPORTADO_SOS y coordenadas válidas', () => {
    const ubicacion = new UbicacionGeoVO(-16.5000, -68.1500, 'Av. 6 de Agosto, La Paz');
    const severidad = SeveridadVO.calcularTriaje({
      heridos: 0,
      vehiculoInmovilizado: true,
      airbagDesplegado: false,
    });

    const reclamo = new ReclamoSiniestro(
      'REC-2026-0001',
      'pol-123',
      'cli-456',
      new Date(),
      ubicacion,
      'Choque por alcance',
      severidad,
      new EstadoReclamoVO('REPORTADO_SOS'),
    );

    expect(reclamo.reclamoId).toBe('REC-2026-0001');
    expect(reclamo.estado.valor).toBe('REPORTADO_SOS');
    expect(reclamo.severidad.nivel).toBe('MODERADO');
    expect(reclamo.ubicacion.toGeoJSON()).toEqual({
      type: 'Point',
      coordinates: [-68.1500, -16.5000],
    });
  });

  it('debe calcular severidad GRAVE cuando hay heridos o airbags activados', () => {
    const severidadGrave = SeveridadVO.calcularTriaje({
      heridos: 2,
      vehiculoInmovilizado: true,
      airbagDesplegado: true,
    });
    expect(severidadGrave.nivel).toBe('GRAVE');
    expect(severidadGrave.esGrave()).toBe(true);
  });

  it('debe permitir asignar perito y registrar peritaje técnico', () => {
    const ubicacion = new UbicacionGeoVO(-16.5000, -68.1500);
    const reclamo = new ReclamoSiniestro(
      'REC-2026-0002',
      'pol-123',
      'cli-456',
      new Date(),
      ubicacion,
      'Impacto frontal',
      new SeveridadVO('LEVE'),
      new EstadoReclamoVO('REPORTADO_SOS'),
    );

    // Asignar perito
    reclamo.asignarPerito('PERITO-007');
    expect(reclamo.estado.valor).toBe('PERITAJE_ASIGNADO');
    expect(reclamo.peritoAsignadoId).toBe('PERITO-007');

    // Registrar peritaje técnico con partes clasificadas por IA
    const peritaje = new PeritajeDetalle(
      'PERITO-007',
      new Date(),
      [
        { parte: 'parachoques', severidad: 'MODERADO', costoEstimado: 1200, confianzaIa: 0.94 },
        { parte: 'faroles', severidad: 'GRAVE', costoEstimado: 850, confianzaIa: 0.89 },
      ],
      2050.0,
      ['http://s3.aegiscore.local/evidencias/foto1.jpg'],
      'Daños en frontal y ópticas',
      true,
    );

    reclamo.registrarPeritaje(peritaje);
    expect(reclamo.estado.valor).toBe('PERITAJE_COMPLETADO');
    expect(reclamo.peritaje?.montoEstimadoTotal).toBe(2050.0);
  });

  it('debe fallar si se intenta marcar en liquidación un reclamo sin peritaje completado', () => {
    const ubicacion = new UbicacionGeoVO(-16.5000, -68.1500);
    const reclamo = new ReclamoSiniestro(
      'REC-2026-0003',
      'pol-123',
      'cli-456',
      new Date(),
      ubicacion,
      'Daño menor',
      new SeveridadVO('LEVE'),
      new EstadoReclamoVO('REPORTADO_SOS'),
    );

    expect(() => reclamo.marcarEnLiquidacion()).toThrow(TransicionEstadoInvalidaException);
  });

  it('debe permitir marcar en liquidación (Saga CU09) y revertir compensatoriamente en caso de fallo', () => {
    const ubicacion = new UbicacionGeoVO(-16.5000, -68.1500);
    const reclamo = new ReclamoSiniestro(
      'REC-2026-0004',
      'pol-123',
      'cli-456',
      new Date(),
      ubicacion,
      'Colisión',
      new SeveridadVO('MODERADO'),
      new EstadoReclamoVO('PERITAJE_ASIGNADO'),
    );

    const peritaje = new PeritajeDetalle(
      'PERITO-001',
      new Date(),
      [{ parte: 'capo', severidad: 'LEVE', costoEstimado: 500 }],
      500.0,
      ['foto1.png'],
      'Abolladura menor',
    );
    reclamo.registrarPeritaje(peritaje);
    expect(reclamo.estado.valor).toBe('PERITAJE_COMPLETADO');

    // Paso 1 Saga: Bloquear en liquidación
    reclamo.marcarEnLiquidacion('Inicio de Saga CU09');
    expect(reclamo.estado.valor).toBe('EN_PROCESO_LIQUIDACION');

    // Rollback compensatorio Saga
    reclamo.revertirEstado('Fallo en reserva técnica de MS3');
    expect(reclamo.estado.valor).toBe('PERITAJE_COMPLETADO');
  });
});
