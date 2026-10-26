export class ReclamoNotFoundException extends Error {
  constructor(reclamoId: string) {
    super(`El reclamo de siniestro con ID '${reclamoId}' no fue encontrado.`);
    this.name = 'ReclamoNotFoundException';
  }
}

export class TransicionEstadoInvalidaException extends Error {
  constructor(estadoActual: string, nuevoEstado: string, motivo?: string) {
    super(
      `Transición de estado inválida de '${estadoActual}' hacia '${nuevoEstado}'. ${
        motivo ? `Motivo: ${motivo}` : ''
      }`,
    );
    this.name = 'TransicionEstadoInvalidaException';
  }
}

export class PeritajeInvalidoException extends Error {
  constructor(mensaje: string) {
    super(`Peritaje inválido: ${mensaje}`);
    this.name = 'PeritajeInvalidoException';
  }
}
