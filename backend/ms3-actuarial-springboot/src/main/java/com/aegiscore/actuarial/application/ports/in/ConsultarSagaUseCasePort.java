package com.aegiscore.actuarial.application.ports.in;

import com.aegiscore.actuarial.application.dto.LiquidacionSagaResponseDTO;

public interface ConsultarSagaUseCasePort {
    LiquidacionSagaResponseDTO consultarPorSagaId(String sagaId);
}
