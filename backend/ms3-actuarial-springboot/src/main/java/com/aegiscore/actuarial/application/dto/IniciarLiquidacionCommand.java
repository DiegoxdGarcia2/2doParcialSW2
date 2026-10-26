package com.aegiscore.actuarial.application.dto;

import java.math.BigDecimal;
import java.util.UUID;

public class IniciarLiquidacionCommand {

    private String reclamoIdMongo;
    private UUID polizaId;
    private UUID clienteId;
    private BigDecimal montoIndemnizacion;
    private String cuentaBancariaDestino;
    private boolean simularFalloReserva; // Para demostrar el Rollback compensatorio ante el docente

    public IniciarLiquidacionCommand() {
    }

    public IniciarLiquidacionCommand(String reclamoIdMongo, UUID polizaId, UUID clienteId, BigDecimal montoIndemnizacion, String cuentaBancariaDestino) {
        this.reclamoIdMongo = reclamoIdMongo;
        this.polizaId = polizaId;
        this.clienteId = clienteId;
        this.montoIndemnizacion = montoIndemnizacion;
        this.cuentaBancariaDestino = cuentaBancariaDestino;
    }

    public String getReclamoIdMongo() {
        return reclamoIdMongo;
    }

    public void setReclamoIdMongo(String reclamoIdMongo) {
        this.reclamoIdMongo = reclamoIdMongo;
    }

    public UUID getPolizaId() {
        return polizaId;
    }

    public void setPolizaId(UUID polizaId) {
        this.polizaId = polizaId;
    }

    public UUID getClienteId() {
        return clienteId;
    }

    public void setClienteId(UUID clienteId) {
        this.clienteId = clienteId;
    }

    public BigDecimal getMontoIndemnizacion() {
        return montoIndemnizacion;
    }

    public void setMontoIndemnizacion(BigDecimal montoIndemnizacion) {
        this.montoIndemnizacion = montoIndemnizacion;
    }

    public String getCuentaBancariaDestino() {
        return cuentaBancariaDestino;
    }

    public void setCuentaBancariaDestino(String cuentaBancariaDestino) {
        this.cuentaBancariaDestino = cuentaBancariaDestino;
    }

    public boolean isSimularFalloReserva() {
        return simularFalloReserva;
    }

    public void setSimularFalloReserva(boolean simularFalloReserva) {
        this.simularFalloReserva = simularFalloReserva;
    }
}
