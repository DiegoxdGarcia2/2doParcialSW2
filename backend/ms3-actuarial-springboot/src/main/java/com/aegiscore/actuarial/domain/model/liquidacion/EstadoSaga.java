package com.aegiscore.actuarial.domain.model.liquidacion;

/**
 * Estados del ciclo de vida de la transacción distribuida Saga (CU09).
 * Trazabilidad con contracts/saga-events.schema.json y PostgreSQL orden_liquidacion_saga.
 */
public enum EstadoSaga {
    INICIADA,
    PASO1_SINIESTRO_BLOQUEADO,
    PASO2_COBERTURA_DESCONTADA,
    PASO3_PAGO_EMITIDO,
    SAGA_COMPLETADA,
    COMPENSANDO_COBERTURA,
    COMPENSANDO_SINIESTRO,
    SAGA_FALLIDA_COMPENSADA,
    FALLO_IRREVERSIBLE
}
