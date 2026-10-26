export class UbicacionGeoVO {
  constructor(
    public readonly latitud: number,
    public readonly longitud: number,
    public readonly direccion?: string,
  ) {
    this.validarCoordenadas(latitud, longitud);
  }

  private validarCoordenadas(lat: number, lng: number): void {
    if (lat < -90 || lat > 90) {
      throw new Error(`Latitud inválida: ${lat}. Debe estar entre -90 y 90.`);
    }
    if (lng < -180 || lng > 180) {
      throw new Error(`Longitud inválida: ${lng}. Debe estar entre -180 y 180.`);
    }
  }

  /**
   * Genera el formato estándar GeoJSON Point para indexación geoespacial 2dsphere en MongoDB
   */
  toGeoJSON(): { type: 'Point'; coordinates: [number, number] } {
    return {
      type: 'Point',
      coordinates: [this.longitud, this.latitud], // [lng, lat] según estándar GeoJSON
    };
  }

  static fromGeoJSON(geo: { type: string; coordinates: [number, number] }, direccion?: string): UbicacionGeoVO {
    return new UbicacionGeoVO(geo.coordinates[1], geo.coordinates[0], direccion);
  }
}
