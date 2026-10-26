import { ReclamoSiniestro } from '../entities/reclamo-siniestro.entity';

export const RECLAMO_REPOSITORY_TOKEN = 'IReclamoRepository';

export interface IReclamoRepository {
  save(reclamo: ReclamoSiniestro): Promise<void>;
  update(reclamo: ReclamoSiniestro): Promise<void>;
  findById(reclamoId: string): Promise<ReclamoSiniestro | null>;
  findByClienteId(clienteId: string): Promise<ReclamoSiniestro[]>;
  findByPolizaId(polizaId: string): Promise<ReclamoSiniestro[]>;
  findCercanos(lat: number, lng: number, radioKm: number): Promise<ReclamoSiniestro[]>;
  generarSiguienteReclamoId(): Promise<string>;
}
