-- =============================================================================
--  AEGISCORE AI - Script de Inicialización de PostgreSQL 16
--  Base de Datos: aegiscore_erp
--  Microservicios conectados:
--    - ms1-polizas-php (Laravel / DDD) -> Esquema Comercial y Pólizas
--    - ms3-actuarial-springboot (Hexagonal) -> Esquema Actuarial y Liquidaciones
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Configuración de zona horaria por defecto
SET timezone = 'UTC';

-- =============================================================================
-- 1. TABLA: usuario (Sincronizado con Keycloak SSO - CU01)
-- =============================================================================
CREATE TABLE IF NOT EXISTS usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keycloak_sub VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('ADMIN', 'AJUSTADOR', 'PERITO', 'ACTUARIO', 'CLIENTE')),
    telefono VARCHAR(30),
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
CREATE INDEX IF NOT EXISTS idx_usuario_rol ON usuario(rol);

-- =============================================================================
-- 2. TABLA: cliente (Asegurados / Tomadores de Póliza)
-- =============================================================================
CREATE TABLE IF NOT EXISTS cliente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuario(id) ON DELETE SET NULL,
    tipo_documento VARCHAR(20) NOT NULL DEFAULT 'CI' CHECK (tipo_documento IN ('CI', 'NIT', 'PASAPORTE', 'DNI')),
    numero_documento VARCHAR(40) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    telefono VARCHAR(30) NOT NULL,
    direccion TEXT,
    ciudad VARCHAR(80) DEFAULT 'Santa Cruz',
    fecha_nacimiento DATE,
    score_crediticio INT DEFAULT 750 CHECK (score_crediticio BETWEEN 300 AND 950),
    perfil_riesgo VARCHAR(30) DEFAULT 'MODERADO' CHECK (perfil_riesgo IN ('BAJO', 'MODERADO', 'ALTO', 'CRITICO')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cliente_documento ON cliente(numero_documento);
CREATE INDEX IF NOT EXISTS idx_cliente_email ON cliente(email);

-- =============================================================================
-- 3. TABLA: plan_seguro (Catálogo de Planes)
-- =============================================================================
CREATE TABLE IF NOT EXISTS plan_seguro (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('VEHICULAR', 'SALUD', 'VIDA', 'HOGAR')),
    descripcion TEXT,
    prima_base_anual NUMERIC(12, 2) NOT NULL CHECK (prima_base_anual > 0),
    deducible_base_porcentaje NUMERIC(5, 2) DEFAULT 10.00 NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- =============================================================================
-- 4. TABLA: cobertura (Detalle de Coberturas asociadas a Planes)
-- =============================================================================
CREATE TABLE IF NOT EXISTS cobertura (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES plan_seguro(id) ON DELETE CASCADE,
    codigo VARCHAR(40) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    suma_asegurada_max NUMERIC(14, 2) NOT NULL CHECK (suma_asegurada_max > 0),
    deducible_minimo NUMERIC(10, 2) DEFAULT 100.00 NOT NULL,
    deducible_porcentaje NUMERIC(5, 2) DEFAULT 10.00 NOT NULL,
    obligatoria BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_plan_cobertura UNIQUE (plan_id, codigo)
);

CREATE INDEX IF NOT EXISTS idx_cobertura_plan ON cobertura(plan_id);

-- =============================================================================
-- 5. TABLA: poliza (Contrato de Seguro - Aggregate Root en MS1 PHP DDD)
-- =============================================================================
CREATE TABLE IF NOT EXISTS poliza (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_poliza VARCHAR(50) UNIQUE NOT NULL,
    cliente_id UUID NOT NULL REFERENCES cliente(id) ON DELETE RESTRICT,
    plan_id UUID NOT NULL REFERENCES plan_seguro(id) ON DELETE RESTRICT,
    estado VARCHAR(30) NOT NULL DEFAULT 'COTIZADA' CHECK (estado IN ('COTIZADA', 'EMITIDA', 'ACTIVA', 'SUSPENDIDA', 'VENCIDA', 'CANCELADA')),
    fecha_emision DATE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    prima_anual NUMERIC(12, 2) NOT NULL CHECK (prima_anual > 0),
    prima_mensual NUMERIC(12, 2) NOT NULL CHECK (prima_mensual > 0),
    moneda VARCHAR(5) DEFAULT 'USD' NOT NULL,
    -- Techo de cobertura restante (se descuenta en CU09 Paso 2 y se compensa en rollback)
    saldo_cobertura_restante NUMERIC(14, 2) NOT NULL,
    datos_bien_asegurado JSONB NOT NULL, -- placa, vin, marca, modelo, anio, color, valor_comercial
    canal_venta VARCHAR(40) DEFAULT 'WEB_REACT' CHECK (canal_venta IN ('WEB_REACT', 'WHATSAPP_N8N', 'OFICINA_ANGULAR', 'BROKER')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_fechas_poliza CHECK (fecha_fin >= fecha_inicio),
    CONSTRAINT chk_saldo_cobertura CHECK (saldo_cobertura_restante >= 0)
);

CREATE INDEX IF NOT EXISTS idx_poliza_numero ON poliza(numero_poliza);
CREATE INDEX IF NOT EXISTS idx_poliza_cliente ON poliza(cliente_id);
CREATE INDEX IF NOT EXISTS idx_poliza_estado ON poliza(estado);
CREATE INDEX IF NOT EXISTS idx_poliza_bien_gin ON poliza USING gin (datos_bien_asegurado);

-- =============================================================================
-- 6. TABLA: factura_nota_venta (Emisión Fiscal / Comercial - CU05 con n8n)
-- =============================================================================
CREATE TABLE IF NOT EXISTS factura_nota_venta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    poliza_id UUID NOT NULL REFERENCES poliza(id) ON DELETE RESTRICT,
    cliente_id UUID NOT NULL REFERENCES cliente(id) ON DELETE RESTRICT,
    tipo_comprobante VARCHAR(20) NOT NULL DEFAULT 'FACTURA' CHECK (tipo_comprobante IN ('FACTURA', 'NOTA_VENTA')),
    fecha_emision TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    subtotal NUMERIC(12, 2) NOT NULL,
    impuestos NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    total NUMERIC(12, 2) NOT NULL,
    moneda VARCHAR(5) DEFAULT 'USD' NOT NULL,
    estado VARCHAR(20) DEFAULT 'EMITIDA' CHECK (estado IN ('EMITIDA', 'PAGADA', 'ANULADA')),
    url_pdf_almacenado VARCHAR(255),
    hash_digital_sha256 VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_factura_poliza ON factura_nota_venta(poliza_id);
CREATE INDEX IF NOT EXISTS idx_factura_cliente ON factura_nota_venta(cliente_id);

-- =============================================================================
-- 7. TABLA: pago_prima (Cobros QR Idempotentes - CU10 Spring Boot Hexagonal)
-- =============================================================================
CREATE TABLE IF NOT EXISTS pago_prima (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    poliza_id UUID NOT NULL REFERENCES poliza(id) ON DELETE RESTRICT,
    numero_cuota INT NOT NULL,
    monto NUMERIC(12, 2) NOT NULL CHECK (monto > 0),
    moneda VARCHAR(5) DEFAULT 'USD' NOT NULL,
    metodo_pago VARCHAR(30) DEFAULT 'QR_SIMPLE' CHECK (metodo_pago IN ('QR_SIMPLE', 'TARJETA', 'TRANSFERENCIA', 'DEBITO_AUTOMATICO')),
    idempotency_key VARCHAR(64) UNIQUE NOT NULL, -- UUIDv4 validado con DynamoDB
    qr_imagen_payload TEXT,
    codigo_autorizacion_bancaria VARCHAR(80),
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'EXITOSO', 'FALLIDO', 'REEMBOLSADO')),
    fecha_pago TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pago_poliza ON pago_prima(poliza_id);
CREATE INDEX IF NOT EXISTS idx_pago_idempotency ON pago_prima(idempotency_key);

-- =============================================================================
-- 8. TABLA: orden_liquidacion_saga (Orquestador Transversal Saga en MS3 Spring Boot)
--    Interviene en CU09 (MS2 Siniestro -> MS1 Cobertura -> MS3 Pago + Rollback)
-- =============================================================================
CREATE TABLE IF NOT EXISTS orden_liquidacion_saga (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saga_id VARCHAR(64) UNIQUE NOT NULL,
    reclamo_id_mongo VARCHAR(64) NOT NULL, -- Referencia a MongoDB expedientes_siniestros
    poliza_id UUID NOT NULL REFERENCES poliza(id) ON DELETE RESTRICT,
    cliente_id UUID NOT NULL REFERENCES cliente(id) ON DELETE RESTRICT,
    monto_indemnizacion NUMERIC(14, 2) NOT NULL CHECK (monto_indemnizacion > 0),
    deducible_aplicado NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    monto_neto_desembolso NUMERIC(14, 2) NOT NULL,
    estado_saga VARCHAR(40) NOT NULL DEFAULT 'INICIADA' 
        CHECK (estado_saga IN (
            'INICIADA',
            'PASO1_SINIESTRO_BLOQUEADO',
            'PASO2_COBERTURA_DESCONTADA',
            'PASO3_PAGO_EMITIDO',
            'SAGA_COMPLETADA',
            'COMPENSANDO_COBERTURA',
            'COMPENSANDO_SINIESTRO',
            'SAGA_FALLIDA_COMPENSADA',
            'FALLO_IRREVERSIBLE'
        )),
    cuenta_bancaria_destino VARCHAR(60),
    comprobante_transferencia VARCHAR(100),
    motivo_compensacion TEXT,
    fecha_inicio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_finalizacion TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_saga_reclamo ON orden_liquidacion_saga(reclamo_id_mongo);
CREATE INDEX IF NOT EXISTS idx_saga_poliza ON orden_liquidacion_saga(poliza_id);
CREATE INDEX IF NOT EXISTS idx_saga_estado ON orden_liquidacion_saga(estado_saga);

-- =============================================================================
-- 9. TABLA: reserva_tecnica (Control Actuarial de Solvencia - MS3 Spring Boot)
-- =============================================================================
CREATE TABLE IF NOT EXISTS reserva_tecnica (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    periodo VARCHAR(7) NOT NULL UNIQUE, -- YYYY-MM
    saldo_fondo_reserva NUMERIC(18, 2) NOT NULL,
    limite_solvencia_minimo NUMERIC(18, 2) NOT NULL,
    siniestros_liquidados_acumulado NUMERIC(18, 2) DEFAULT 0.00 NOT NULL,
    alertas_liquidez BOOLEAN DEFAULT FALSE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- =============================================================================
-- 10. TABLA HISTÓRICA SINTÉTICA PARA MACHINE LEARNING (CU12: Random Forest)
-- =============================================================================
CREATE TABLE IF NOT EXISTS dataset_historico_ml_polizas (
    id SERIAL PRIMARY KEY,
    mes_registro DATE NOT NULL,
    edad_asegurado INT NOT NULL,
    antiguedad_licencia_anios INT NOT NULL,
    tipo_vehiculo VARCHAR(30) NOT NULL, -- SEDAN, SUV, CAMIONETA, MOTOCICLETA, HATCHBACK
    anio_vehiculo INT NOT NULL,
    valor_comercial_usd NUMERIC(10, 2) NOT NULL,
    historial_siniestros_previos INT NOT NULL,
    perfil_riesgo_score NUMERIC(5, 2) NOT NULL,
    prima_anual_calculada NUMERIC(10, 2) NOT NULL,
    tuvo_siniestro_en_anio INT NOT NULL CHECK (tuvo_siniestro_en_anio IN (0, 1)),
    costo_siniestro_usd NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    tipo_seguro VARCHAR(30) NOT NULL,
    polizas_vendidas_en_mes INT NOT NULL
);

-- =============================================================================
-- POBLADO INICIAL DE PLANES Y COBERTURAS
-- =============================================================================
INSERT INTO plan_seguro (id, codigo, nombre, tipo, descripcion, prima_base_anual, deducible_base_porcentaje, activo)
VALUES
    ('a0000001-0000-0000-0000-000000000001', 'PLAN-AUTO-FULL', 'Todo Riesgo Vehicular Premium', 'VEHICULAR', 'Cobertura completa contra choques, robo total/parcial, vuelcos y auxilio mecánico 24/7.', 720.00, 10.00, TRUE),
    ('a0000001-0000-0000-0000-000000000002', 'PLAN-AUTO-RC', 'Responsabilidad Civil Obligatoria', 'VEHICULAR', 'Cobertura ante daños materiales y corporales a terceros involucrados.', 280.00, 5.00, TRUE),
    ('a0000001-0000-0000-0000-000000000003', 'PLAN-SALUD-TOTAL', 'Salud Integral Familiar', 'SALUD', 'Atención en red hospitalaria privada, cirugías, medicamentos y telemedicina.', 950.00, 15.00, TRUE)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO cobertura (id, plan_id, codigo, nombre, descripcion, suma_asegurada_max, deducible_minimo, deducible_porcentaje, obligatoria)
VALUES
    ('c0000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001', 'COB-DAÑOS-MATERIALES', 'Daños Materiales por Colisión y Vuelco', 'Indemnización o reparación en talleres autorizados.', 25000.00, 150.00, 10.00, TRUE),
    ('c0000001-0000-0000-0000-000000000002', 'a0000001-0000-0000-0000-000000000001', 'COB-ROBO-TOTAL', 'Robo Total del Vehículo', 'Reposición de valor comercial según tabla depreciativa.', 25000.00, 200.00, 10.00, TRUE),
    ('c0000001-0000-0000-0000-000000000003', 'a0000001-0000-0000-0000-000000000001', 'COB-RESP-CIVIL', 'Responsabilidad Civil a Terceros', 'Cobertura frente a demandas o daños a bienes de terceros.', 15000.00, 100.00, 5.00, TRUE),
    ('c0000001-0000-0000-0000-000000000004', 'a0000001-0000-0000-0000-000000000003', 'COB-HOSPITALIZACION', 'Gastos Médicos y Hospitalización', 'Cobertura para internaciones y procedimientos quirúrgicos.', 30000.00, 250.00, 15.00, TRUE)
ON CONFLICT (plan_id, codigo) DO NOTHING;

-- Reserva técnica inicial
INSERT INTO reserva_tecnica (periodo, saldo_fondo_reserva, limite_solvencia_minimo, siniestros_liquidados_acumulado, alertas_liquidez)
VALUES 
    (TO_CHAR(CURRENT_DATE, 'YYYY-MM'), 5000000.00, 1500000.00, 185000.00, FALSE)
ON CONFLICT (periodo) DO NOTHING;

-- Usuario inicial Administrador y Perito
INSERT INTO usuario (id, keycloak_sub, email, nombre_completo, rol, telefono, activo)
VALUES
    ('u0000001-0000-0000-0000-000000000001', 'kc-admin-001', 'admin@aegiscore.com', 'Administrador General AegisCore', 'ADMIN', '+591 70011223', TRUE),
    ('u0000001-0000-0000-0000-000000000002', 'kc-perito-001', 'perito.campo@aegiscore.com', 'Ing. Roberto Paz (Perito)', 'PERITO', '+591 70044556', TRUE),
    ('u0000001-0000-0000-0000-000000000003', 'kc-actuario-001', 'actuario@aegiscore.com', 'Lic. Mariana Vargas (Actuario)', 'ACTUARIO', '+591 70077889', TRUE),
    ('u0000001-0000-0000-0000-000000000004', 'kc-cliente-001', 'carlos.mendoza@gmail.com', 'Carlos Mendoza Roca', 'CLIENTE', '+591 71099887', TRUE)
ON CONFLICT (keycloak_sub) DO NOTHING;

INSERT INTO cliente (id, usuario_id, tipo_documento, numero_documento, nombres, apellidos, email, telefono, direccion, score_crediticio, perfil_riesgo)
VALUES
    ('b0000001-0000-0000-0000-000000000001', 'u0000001-0000-0000-0000-000000000004', 'CI', '6234891-SC', 'Carlos', 'Mendoza Roca', 'carlos.mendoza@gmail.com', '+591 71099887', 'Av. San Martín #450, Equipetrol, Santa Cruz', 820, 'BAJO')
ON CONFLICT (numero_documento) DO NOTHING;

-- Póliza demostrativa para la Saga
INSERT INTO poliza (
    id, numero_poliza, cliente_id, plan_id, estado, fecha_emision, fecha_inicio, fecha_fin, 
    prima_anual, prima_mensual, moneda, saldo_cobertura_restante, datos_bien_asegurado, canal_venta
)
VALUES (
    'd0000001-0000-0000-0000-000000000001',
    'POL-2026-AUT-00892',
    'b0000001-0000-0000-0000-000000000001',
    'a0000001-0000-0000-0000-000000000001',
    'ACTIVA',
    CURRENT_DATE - INTERVAL '60 days',
    CURRENT_DATE - INTERVAL '60 days',
    CURRENT_DATE + INTERVAL '305 days',
    720.00,
    60.00,
    'USD',
    25000.00, -- Techo anual disponible para CU09 Saga
    '{
        "placa": "4028-PLK",
        "marca": "Toyota",
        "modelo": "Hilux 4x4",
        "anio": 2023,
        "color": "Blanco Perlado",
        "vin": "8AJBA3CD701982736",
        "valor_comercial": 34500.00
    }'::jsonb,
    'WEB_REACT'
)
ON CONFLICT (numero_poliza) DO NOTHING;

-- =============================================================================
-- GENERADOR DE DATASET HISTÓRICO SINTÉTICO (12 MESES, 1,200 REGISTROS)
-- Necesario para CU12: Random Forest (Supervisado) y CU13: K-Means (No Supervisado)
-- =============================================================================
DO $$
DECLARE
    i INT;
    mes DATE;
    edad INT;
    antiguedad INT;
    v_tipo VARCHAR(30);
    tipos VARCHAR[] := ARRAY['SEDAN', 'SUV', 'CAMIONETA', 'HATCHBACK', 'MOTOCICLETA'];
    v_anio INT;
    v_valor NUMERIC(10,2);
    v_siniestros_previos INT;
    v_score NUMERIC(5,2);
    v_prima NUMERIC(10,2);
    v_tuvo_siniestro INT;
    v_costo NUMERIC(12,2);
    v_ventas INT;
BEGIN
    -- Evitar duplicación si ya existen datos sintéticos
    IF (SELECT COUNT(*) FROM dataset_historico_ml_polizas) >= 1000 THEN
        RETURN;
    END IF;

    FOR i IN 1..1200 LOOP
        -- Fechas repartidas entre los últimos 12 meses
        mes := CURRENT_DATE - ( (i % 365) || ' days')::INTERVAL;
        edad := 18 + (i * 7 % 55); -- 18 a 72 años
        antiguedad := GREATEST(1, edad - 18 - (i % 5));
        v_tipo := tipos[1 + (i % 5)];
        v_anio := 2010 + (i % 14); -- 2010 a 2024
        
        IF v_tipo = 'CAMIONETA' THEN
            v_valor := 28000 + (i * 23 % 25000);
        ELSIF v_tipo = 'SUV' THEN
            v_valor := 20000 + (i * 17 % 20000);
        ELSIF v_tipo = 'MOTOCICLETA' THEN
            v_valor := 2500 + (i * 11 % 5000);
        ELSE
            v_valor := 12000 + (i * 13 % 15000);
        END IF;

        v_siniestros_previos := (i % 4);
        IF edad < 25 OR v_siniestros_previos > 1 THEN
            v_score := 70.00 + (i % 30); -- Alto riesgo
        ELSE
            v_score := 20.00 + (i % 40); -- Bajo o moderado
        END IF;

        -- Regla de prima con componente estocástico
        v_prima := ROUND( (v_valor * 0.025) + (v_score * 3.5) + (v_siniestros_previos * 75) + 150, 2);

        -- Probabilidad de siniestro correlacionada con edad joven y siniestros previos
        IF (edad < 25 AND v_siniestros_previos >= 1) OR (v_score > 75) THEN
            v_tuvo_siniestro := CASE WHEN (i % 3 = 0) THEN 1 ELSE 0 END;
        ELSE
            v_tuvo_siniestro := CASE WHEN (i % 8 = 0) THEN 1 ELSE 0 END;
        END IF;

        IF v_tuvo_siniestro = 1 THEN
            v_costo := ROUND( 350.00 + ((i * 179) % 4500), 2);
        ELSE
            v_costo := 0.00;
        END IF;

        v_ventas := 85 + (i % 60);

        INSERT INTO dataset_historico_ml_polizas (
            mes_registro, edad_asegurado, antiguedad_licencia_anios, tipo_vehiculo,
            anio_vehiculo, valor_comercial_usd, historial_siniestros_previos,
            perfil_riesgo_score, prima_anual_calculada, tuvo_siniestro_en_anio,
            costo_siniestro_usd, tipo_seguro, polizas_vendidas_en_mes
        ) VALUES (
            mes, edad, antiguedad, v_tipo,
            v_anio, v_valor, v_siniestros_previos,
            v_score, v_prima, v_tuvo_siniestro,
            v_costo, 'VEHICULAR', v_ventas
        );
    END LOOP;
END $$;
