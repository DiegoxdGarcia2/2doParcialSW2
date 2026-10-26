package com.aegiscore.actuarial.application.ports.in;

import com.aegiscore.actuarial.application.dto.ConfirmarPagoQRCommand;
import com.aegiscore.actuarial.application.dto.GenerarCobroQRCommand;
import com.aegiscore.actuarial.application.dto.PagoQRResponseDTO;

public interface CobroPrimaQRUseCasePort {
    PagoQRResponseDTO generarOrdenCobroQR(GenerarCobroQRCommand command, String idempotencyKey);
    PagoQRResponseDTO confirmarPagoQR(ConfirmarPagoQRCommand command, String idempotencyKey);
}
