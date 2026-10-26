import {
  IsString,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsBoolean,
  IsArray,
  ValidateNested,
  Min,
} from 'class-validator';
import { Type } from 'class-transformer';

export class DanoParteVehiculoDto {
  @IsString()
  @IsNotEmpty()
  parte: string; // 'parachoques' | 'capo' | 'puertas' | 'faroles'

  @IsString()
  @IsNotEmpty()
  severidad: 'LEVE' | 'MODERADO' | 'GRAVE';

  @IsNumber()
  @Min(0)
  costoEstimado: number;

  @IsNumber()
  @IsOptional()
  confianzaIa?: number;
}

export class SincronizarPeritajeDto {
  @IsString()
  @IsNotEmpty()
  reclamoId: string;

  @IsString()
  @IsNotEmpty()
  peritoId: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => DanoParteVehiculoDto)
  partesDanadas: DanoParteVehiculoDto[];

  @IsNumber()
  @Min(0)
  montoEstimadoTotal: number;

  @IsArray()
  @IsNotEmpty()
  fotosEvidencia: string[];

  @IsString()
  @IsOptional()
  observaciones?: string;

  @IsBoolean()
  @IsOptional()
  sincronizadoOffline?: boolean = false;

  @IsString()
  @IsOptional()
  hashIntegridadOffline?: string;
}
