package com.aegiscore.actuarial.application.ports.in;

import com.aegiscore.actuarial.application.dto.IniciarLiquidacionCommand;
import com.aegiscore.actuarial.application.dto.LiquidacionSagaResponseDTO;

public interface IniciarLiquidacionSagaUseCasePort {
    LiquidacionSagaResponseDTO iniciarLiquidacion(IniciarLiquidacionCommand command);
}
