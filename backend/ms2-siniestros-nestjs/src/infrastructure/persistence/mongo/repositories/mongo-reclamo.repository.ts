import { Injectable, Logger } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { IReclamoRepository } from '../../../../domain/repositories/reclamo.repository.interface';
import { ReclamoSiniestro, EntradaHistorialEstado } from '../../../../domain/entities/reclamo-siniestro.entity';
import { ReclamoDocument, ReclamoMongoEntity } from '../schemas/reclamo.schema';
import { UbicacionGeoVO } from '../../../../domain/value-objects/ubicacion-geo.vo';
import { SeveridadVO, NivelSeveridad } from '../../../../domain/value-objects/severidad.vo';
import { EstadoReclamoVO, TipoEstadoReclamo } from '../../../../domain/value-objects/estado-reclamo.vo';
import { PeritajeDetalle, DanoParteVehiculo } from '../../../../domain/entities/peritaje-detalle.entity';

@Injectable()
export class MongoReclamoRepository implements IReclamoRepository {
  private readonly logger = new Logger(MongoReclamoRepository.name);

  constructor(
    @InjectModel(ReclamoMongoEntity.name)
    private readonly reclamoModel: Model<ReclamoDocument>,
  ) {}

  async save(reclamo: ReclamoSiniestro): Promise<void> {
    const rawData = this.toRaw(reclamo);
    await this.reclamoModel.create(rawData);
    this.logger.log(`Documento de siniestro guardado en MongoDB con ID: ${reclamo.reclamoId}`);
  }

  async update(reclamo: ReclamoSiniestro): Promise<void> {
    const rawData = this.toRaw(reclamo);
    await this.reclamoModel.updateOne({ reclamo_id: reclamo.reclamoId }, { $set: rawData });
    this.logger.log(`Documento de siniestro ${reclamo.reclamoId} actualizado en MongoDB`);
  }

  async findById(reclamoId: string): Promise<ReclamoSiniestro | null> {
    const doc = await this.reclamoModel.findOne({ reclamo_id: reclamoId }).exec();
    if (!doc) return null;
    return this.toDomain(doc);
  }

  async findByClienteId(clienteId: string): Promise<ReclamoSiniestro[]> {
    const docs = await this.reclamoModel.find({ cliente_id: clienteId }).sort({ fecha_siniestro: -1 }).exec();
    return docs.map((d) => this.toDomain(d));
  }

  async findByPolizaId(polizaId: string): Promise<ReclamoSiniestro[]> {
    const docs = await this.reclamoModel.find({ poliza_id: polizaId }).exec();
    return docs.map((d) => this.toDomain(d));
  }

  /**
   * Búsqueda geoespacial mediante operador $near y el índice 2dsphere
   */
  async findCercanos(lat: number, lng: number, radioKm: number): Promise<ReclamoSiniestro[]> {
    const maxMeters = radioKm * 1000;
    const docs = await this.reclamoModel.find({
      ubicacion_geo: {
        $near: {
          $geometry: {
            type: 'Point',
            coordinates: [lng, lat], // [longitud, latitud]
          },
          $maxDistance: maxMeters,
        },
      },
    }).exec();

    return docs.map((d) => this.toDomain(d));
  }

  async generarSiguienteReclamoId(): Promise<string> {
    const anio = new Date().getFullYear();
    const count = await this.reclamoModel.countDocuments();
    const correlativo = String(count + 1).padStart(5, '0');
    return `REC-${anio}-${correlativo}`;
  }

  private toDomain(doc: ReclamoDocument): ReclamoSiniestro {
    const ubicacion = new UbicacionGeoVO(
      doc.ubicacion_geo.coordinates[1], // lat
      doc.ubicacion_geo.coordinates[0], // lng
      doc.ubicacion_geo.direccion,
    );

    const severidad = new SeveridadVO(doc.severidad as NivelSeveridad);
    const estado = new EstadoReclamoVO(doc.estado as TipoEstadoReclamo);

    let peritaje: PeritajeDetalle | undefined;
    if (doc.peritaje) {
      peritaje = new PeritajeDetalle(
        doc.peritaje.perito_id,
        doc.peritaje.fecha_inspeccion,
        doc.peritaje.partes_danadas.map((p) => ({
          parte: p.parte,
          severidad: p.severidad as any,
          costoEstimado: p.costo_estimado,
          confianzaIa: p.confianza_ia,
        })),
        doc.peritaje.monto_estimado_total,
        doc.peritaje.fotos_evidencia,
        doc.peritaje.observaciones || '',
        doc.peritaje.sincronizado_offline,
        doc.peritaje.hash_integridad_offline,
      );
    }

    const historial: EntradaHistorialEstado[] = (doc.historial_estados || []).map((h) => ({
      estado: h.estado as TipoEstadoReclamo,
      fecha: h.fecha,
      motivo: h.motivo,
      autorId: h.autor_id,
    }));

    return new ReclamoSiniestro(
      doc.reclamo_id,
      doc.poliza_id,
      doc.cliente_id,
      doc.fecha_siniestro,
      ubicacion,
      doc.descripcion,
      severidad,
      estado,
      doc.fotos_preliminares,
      doc.perito_asignado_id,
      peritaje,
      historial,
      doc.monto_indemnizacion_aprobado,
    );
  }

  private toRaw(reclamo: ReclamoSiniestro): any {
    return {
      reclamo_id: reclamo.reclamoId,
      poliza_id: reclamo.polizaId,
      cliente_id: reclamo.clienteId,
      fecha_siniestro: reclamo.fechaSiniestro,
      ubicacion_geo: {
        type: 'Point',
        coordinates: [reclamo.ubicacion.longitud, reclamo.ubicacion.latitud],
        direccion: reclamo.ubicacion.direccion,
      },
      descripcion: reclamo.descripcion,
      severidad: reclamo.severidad.nivel,
      estado: reclamo.estado.valor,
      fotos_preliminares: reclamo.fotosPreliminares,
      perito_asignado_id: reclamo.peritoAsignadoId,
      peritaje: reclamo.peritaje
        ? {
            perito_id: reclamo.peritaje.peritoId,
            fecha_inspeccion: reclamo.peritaje.fechaInspeccion,
            partes_danadas: reclamo.peritaje.partesDanadas.map((p) => ({
              parte: p.parte,
              severidad: p.severidad,
              costo_estimado: p.costoEstimado,
              confianza_ia: p.confianzaIa,
            })),
            monto_estimado_total: reclamo.peritaje.montoEstimadoTotal,
            fotos_evidencia: reclamo.peritaje.fotosEvidencia,
            observaciones: reclamo.peritaje.observaciones,
            sincronizado_offline: reclamo.peritaje.sincronizadoOffline,
            hash_integridad_offline: reclamo.peritaje.hashIntegridadOffline,
          }
        : undefined,
      historial_estados: reclamo.historialEstados.map((h) => ({
        estado: h.estado,
        fecha: h.fecha,
        motivo: h.motivo,
        autor_id: h.autorId,
      })),
      monto_indemnizacion_aprobado: reclamo.montoIndemnizacionAprobado,
    };
  }
}
