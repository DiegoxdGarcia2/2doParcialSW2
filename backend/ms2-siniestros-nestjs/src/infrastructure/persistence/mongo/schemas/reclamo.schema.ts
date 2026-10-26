import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type ReclamoDocument = ReclamoMongoEntity & Document;

@Schema({ _id: false })
export class GeoJSONPoint {
  @Prop({ type: String, enum: ['Point'], default: 'Point' })
  type: string;

  @Prop({ type: [Number], required: true }) // [longitud, latitud]
  coordinates: number[];

  @Prop({ type: String, required: false })
  direccion?: string;
}

@Schema({ _id: false })
export class ParteDanadaMongo {
  @Prop({ type: String, required: true })
  parte: string;

  @Prop({ type: String, required: true })
  severidad: string;

  @Prop({ type: Number, required: true })
  costo_estimado: number;

  @Prop({ type: Number, required: false })
  confianza_ia?: number;
}

@Schema({ _id: false })
export class PeritajeMongo {
  @Prop({ type: String, required: true })
  perito_id: string;

  @Prop({ type: Date, required: true })
  fecha_inspeccion: Date;

  @Prop({ type: [ParteDanadaMongo], default: [] })
  partes_danadas: ParteDanadaMongo[];

  @Prop({ type: Number, required: true })
  monto_estimado_total: number;

  @Prop({ type: [String], default: [] })
  fotos_evidencia: string[];

  @Prop({ type: String, required: false })
  observaciones: string;

  @Prop({ type: Boolean, default: false })
  sincronizado_offline: boolean;

  @Prop({ type: String, required: false })
  hash_integridad_offline?: string;
}

@Schema({ _id: false })
export class HistorialEstadoMongo {
  @Prop({ type: String, required: true })
  estado: string;

  @Prop({ type: Date, default: Date.now })
  fecha: Date;

  @Prop({ type: String, required: false })
  motivo?: string;

  @Prop({ type: String, required: false })
  autor_id?: string;
}

@Schema({ collection: 'expedientes_siniestros', timestamps: true })
export class ReclamoMongoEntity {
  @Prop({ type: String, required: true, unique: true, index: true })
  reclamo_id: string;

  @Prop({ type: String, required: true, index: true })
  poliza_id: string;

  @Prop({ type: String, required: true, index: true })
  cliente_id: string;

  @Prop({ type: Date, default: Date.now })
  fecha_siniestro: Date;

  @Prop({ type: GeoJSONPoint, required: true })
  ubicacion_geo: GeoJSONPoint;

  @Prop({ type: String, required: true })
  descripcion: string;

  @Prop({ type: String, required: true })
  severidad: string;

  @Prop({ type: String, required: true, index: true })
  estado: string;

  @Prop({ type: [String], default: [] })
  fotos_preliminares: string[];

  @Prop({ type: String, required: false })
  perito_asignado_id?: string;

  @Prop({ type: PeritajeMongo, required: false })
  peritaje?: PeritajeMongo;

  @Prop({ type: [HistorialEstadoMongo], default: [] })
  historial_estados: HistorialEstadoMongo[];

  @Prop({ type: Number, required: false })
  monto_indemnizacion_aprobado?: number;
}

export const ReclamoMongoSchema = SchemaFactory.createForClass(ReclamoMongoEntity);

// Índice geoespacial 2dsphere obligatorio para búsquedas por proximidad (CU06 / CU07)
ReclamoMongoSchema.index({ ubicacion_geo: '2dsphere' });
