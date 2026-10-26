package com.aegiscore.actuarial.application.ports.in;

import com.aegiscore.actuarial.application.dto.SagaEventDTO;

public interface ProcesarPasoSagaUseCasePort {
    void procesarRespuestaPaso1SiniestroBloqueado(SagaEventDTO event);
    void procesarRespuestaPaso2CoberturaDescontada(SagaEventDTO event);
    void procesarFalloYCompensar(String sagaId, String motivoFallo);
}
