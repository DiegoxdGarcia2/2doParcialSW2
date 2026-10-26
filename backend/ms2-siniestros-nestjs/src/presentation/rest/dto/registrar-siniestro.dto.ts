import {
  IsString,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsBoolean,
  IsArray,
  Min,
  Max,
} from 'class-validator';

export class RegistrarSiniestroDto {
  @IsString()
  @IsNotEmpty()
  polizaId: string;

  @IsString()
  @IsNotEmpty()
  clienteId: string;

  @IsNumber()
  @Min(-90)
  @Max(90)
  latitud: number;

  @IsNumber()
  @Min(-180)
  @Max(180)
  longitud: number;

  @IsString()
  @IsNotEmpty()
  descripcion: string;

  @IsString()
  @IsOptional()
  direccion?: string;

  @IsNumber()
  @IsOptional()
  @Min(0)
  heridos?: number = 0;

  @IsBoolean()
  @IsOptional()
  vehiculoInmovilizado?: boolean = false;

  @IsBoolean()
  @IsOptional()
  airbagDesplegado?: boolean = false;

  @IsArray()
  @IsOptional()
  fotosPreliminares?: string[] = [];
}
