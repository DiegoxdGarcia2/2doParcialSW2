<?php
declare(strict_types=1);

namespace AegisCore\Polizas\Application\Services;

use AegisCore\Polizas\Application\DTOs\EmitirPolizaInputDTO;

/**
 * Objeto CONTROL de ICONIX (CU05: Contratar / Renovar Póliza por WhatsApp y Emitir Factura PDF).
 * Recibe los pedidos provenientes del flujo automatizado en n8n (WhatsApp Business API -> ERP PHP),
 * registra la orden/suscripción de póliza y dispara la facturación automática.
 */
class RecepcionPedidoService
{
    public function __construct(
        private readonly EmisionPolizaGraphQLController $emisionPolizaController,
        private readonly FacturacionService $facturacionService
    ) {
    }

    /**
     * Método operacional UML 2.5+ (CU05):
     * Procesa un pedido o renovación de póliza capturado por el bot de WhatsApp en n8n
     * y retorna la póliza emitida junto con su Factura / Nota de Venta en PDF firmada con SHA-256.
     */
    public function procesarPedidoPolizaWhatsApp(array $payloadWhatsApp): array
    {
        $documento = (string)($payloadWhatsApp['numero_documento'] ?? $payloadWhatsApp['documento'] ?? '6234891-SC');
        $placa = (string)($payloadWhatsApp['placa'] ?? '4028-PLK');
        $planCodigo = (string)($payloadWhatsApp['plan_codigo'] ?? $payloadWhatsApp['planId'] ?? 'PLAN-AUTO-FULL');
        $telefono = (string)($payloadWhatsApp['telefono'] ?? '+591 71099887');
        $tipoComprobante = strtoupper((string)($payloadWhatsApp['tipo_comprobante'] ?? 'FACTURA'));

        $inputDto = new EmitirPolizaInputDTO(
            clienteId: (string)($payloadWhatsApp['cliente_id'] ?? $documento),
            planId: $planCodigo,
            datosBien: [
                'placa' => $placa,
                'vin' => (string)($payloadWhatsApp['vin'] ?? '8AJBA3CD701982736'),
                'marca' => (string)($payloadWhatsApp['marca'] ?? 'Toyota'),
                'modelo' => (string)($payloadWhatsApp['modelo'] ?? 'Hilux 4x4'),
                'anio' => (int)($payloadWhatsApp['anio'] ?? 2024),
                'color' => (string)($payloadWhatsApp['color'] ?? 'Blanco Perlado'),
                'valorComercial' => (float)($payloadWhatsApp['valor_comercial'] ?? 34500.00),
            ],
            fechaInicio: gmdate('Y-m-d\TH:i:s\Z'),
            mesesVigencia: (int)($payloadWhatsApp['meses_vigencia'] ?? 12),
            canalVenta: 'WHATSAPP_N8N',
            tokenValidacionNitidezLocal: 'N8N-WHATSAPP-VERIFIED',
            documento: $documento,
            placa: $placa
        );

        $polizaEmitida = $this->emisionPolizaController->insertarPoliza($inputDto);
        $pdfResultado = $this->facturacionService->generarFacturaNotaVentaPDF(
            (string)$polizaEmitida['id'],
            $tipoComprobante
        );

        return [
            'status' => 'SUCCESS',
            'canal' => 'WHATSAPP_N8N',
            'telefono_notificado' => $telefono,
            'poliza' => $polizaEmitida,
            'factura' => $pdfResultado['factura'],
            'url_pdf' => $pdfResultado['url_pdf'],
            'hash_digital_sha256' => $pdfResultado['hash_digital_sha256'],
            'mensaje_whatsapp' => sprintf(
                'Estimado asegurado (%s), su póliza %s para el vehículo placa %s fue emitida exitosamente. Factura %s adjunta en PDF.',
                $polizaEmitida['cliente']['nombreCompleto'] ?? 'Cliente AegisCore',
                $polizaEmitida['numeroPoliza'],
                $placa,
                $pdfResultado['factura']['numeroFactura']
            ),
        ];
    }
}

