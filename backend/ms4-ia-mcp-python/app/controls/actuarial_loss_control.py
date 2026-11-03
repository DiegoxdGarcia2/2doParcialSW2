"""
=============================================================================
 AegisCore AI - MS4: [CONTROL] Orquestador de Siniestralidad y Riesgo Demográfico 360°
 Metodología ICONIX - Clase de Control Orquestadora
 Consultas 100% SQL Puras sobre dataset_historico_ml_polizas en PostgreSQL Neon
 Cero Mockups, Cero Diccionarios en Memoria: Toda métrica proviene de PostgreSQL.
=============================================================================
"""

import datetime
from typing import Dict, List, Tuple, Any
from app.db.connections import get_postgres_connection
from app.entities.actuarial_loss_dto import (
    ActuarialLossFilterInputDTO,
    ActuarialLossSummaryDTO,
    VehicleLossMetricDTO,
    AgeCohortMetricDTO,
    MonthlyTrendMetricDTO,
    ActuarialFilterOptionsDTO
)


class ActuarialLossAnalysisControl:
    """
    Clase de Control ICONIX que ejecuta consultas analíticas parametrizadas
    sobre la persistencia relacional PostgreSQL Neon (dataset_historico_ml_polizas).
    """

    def obtener_opciones_filtros(self) -> ActuarialFilterOptionsDTO:
        """Retorna las opciones reales disponibles para los selectores de filtros 360°."""
        return ActuarialFilterOptionsDTO(
            tipos_vehiculo=[
                {"id": "TODOS", "label": "Todos los Vehículos (Consolidado)"},
                {"id": "SUV", "label": "SUV / Crossover Familiar"},
                {"id": "CAMIONETA", "label": "Camioneta / Pick-up Comercial"},
                {"id": "HATCHBACK", "label": "Hatchback Compacto Urbano"},
                {"id": "MOTOCICLETA", "label": "Motocicleta / Entrega Ligera"},
                {"id": "SEDAN", "label": "Sedán Ejecutivo y Particular"}
            ],
            rangos_edad=[
                {"id": "TODOS", "label": "Todas las Edades (18 a 72 años)"},
                {"id": "18-25", "label": "Jóvenes (18 a 25 años)"},
                {"id": "26-35", "label": "Adultos Jóvenes (26 a 35 años)"},
                {"id": "36-50", "label": "Adultos Intermedios (36 a 50 años)"},
                {"id": "51-65", "label": "Adultos Mayores (51 a 65 años)"},
                {"id": "65+", "label": "Senior (Más de 65 años)"}
            ],
            antiguedades_licencia=[
                {"id": "TODOS", "label": "Toda Experiencia de Licencia"},
                {"id": "NOVATO", "label": "Novato (0 a 2 años de licencia)"},
                {"id": "INTERMEDIO", "label": "Intermedio (3 a 7 años de licencia)"},
                {"id": "EXPERTO", "label": "Experto (8 o más años de licencia)"}
            ],
            antiguedades_vehiculo=[
                {"id": "TODOS", "label": "Todos los Modelos (2010 a 2023)"},
                {"id": "2020_2023", "label": "Modelos Recientes (2020 - 2023)"},
                {"id": "2015_2019", "label": "Modelos Intermedios (2015 - 2019)"},
                {"id": "2010_2014", "label": "Modelos Antiguos (2010 - 2014)"}
            ]
        )

    def _construir_clausula_where(self, filtros: ActuarialLossFilterInputDTO) -> Tuple[str, Dict[str, Any]]:
        """Construye la cláusula WHERE SQL parametrizada de manera segura."""
        condiciones = []
        params: Dict[str, Any] = {}

        if filtros.tipo_vehiculo != "TODOS":
            condiciones.append("tipo_vehiculo = %(tipo_vehiculo)s")
            params["tipo_vehiculo"] = filtros.tipo_vehiculo

        if filtros.rango_edad != "TODOS":
            if filtros.rango_edad == "18-25":
                condiciones.append("edad_asegurado BETWEEN 18 AND 25")
            elif filtros.rango_edad == "26-35":
                condiciones.append("edad_asegurado BETWEEN 26 AND 35")
            elif filtros.rango_edad == "36-50":
                condiciones.append("edad_asegurado BETWEEN 36 AND 50")
            elif filtros.rango_edad == "51-65":
                condiciones.append("edad_asegurado BETWEEN 51 AND 65")
            elif filtros.rango_edad == "65+":
                condiciones.append("edad_asegurado >= 66")

        if filtros.antiguedad_licencia != "TODOS":
            if filtros.antiguedad_licencia == "NOVATO":
                condiciones.append("antiguedad_licencia_anios BETWEEN 0 AND 2")
            elif filtros.antiguedad_licencia == "INTERMEDIO":
                condiciones.append("antiguedad_licencia_anios BETWEEN 3 AND 7")
            elif filtros.antiguedad_licencia == "EXPERTO":
                condiciones.append("antiguedad_licencia_anios >= 8")

        if filtros.antiguedad_vehiculo != "TODOS":
            if filtros.antiguedad_vehiculo == "2020_2023":
                condiciones.append("anio_vehiculo BETWEEN 2020 AND 2023")
            elif filtros.antiguedad_vehiculo == "2015_2019":
                condiciones.append("anio_vehiculo BETWEEN 2015 AND 2019")
            elif filtros.antiguedad_vehiculo == "2010_2014":
                condiciones.append("anio_vehiculo BETWEEN 2010 AND 2014")

        where_str = "WHERE " + " AND ".join(condiciones) if condiciones else ""
        return where_str, params

    def analizar_siniestralidad_actuarial_360(
        self,
        filtros: ActuarialLossFilterInputDTO
    ) -> ActuarialLossSummaryDTO:
        """
        Ejecuta agregaciones SQL puras en Neon PostgreSQL sobre los 1,200 registros.
        """
        conn = get_postgres_connection()
        cur = conn.cursor()
        where_clause, params = self._construir_clausula_where(filtros)

        # 1. Consulta SQL para Top 5 Bento KPIs
        query_kpis = f"""
            SELECT 
                COUNT(*) as total_polizas,
                COALESCE(SUM(tuvo_siniestro_en_anio), 0) as total_siniestros,
                COALESCE(AVG(prima_anual_calculada), 0) as prima_media,
                COALESCE(SUM(prima_anual_calculada), 0) as primas_totales,
                COALESCE(SUM(CASE WHEN tuvo_siniestro_en_anio = 1 THEN costo_siniestro_usd ELSE 0 END), 0) as costo_total_siniestros,
                COALESCE(AVG(CASE WHEN tuvo_siniestro_en_anio = 1 THEN costo_siniestro_usd ELSE NULL END), 0) as severidad_media,
                COALESCE(AVG(perfil_riesgo_score), 0) as score_medio_riesgo
            FROM dataset_historico_ml_polizas
            {where_clause};
        """
        cur.execute(query_kpis, params)
        kpi_row = cur.fetchone()

        total_polizas = int(kpi_row[0] or 0)
        total_siniestros = int(kpi_row[1] or 0)
        prima_media = float(kpi_row[2] or 0.0)
        primas_totales = float(kpi_row[3] or 0.0)
        costo_total_siniestros = float(kpi_row[4] or 0.0)
        severidad_media = float(kpi_row[5] or 0.0)
        score_medio_riesgo = float(kpi_row[6] or 0.0)

        frecuencia_pct = round((total_siniestros / max(1, total_polizas)) * 100.0, 2)
        loss_ratio_pct = round((costo_total_siniestros / max(1.0, primas_totales)) * 100.0, 2)

        if loss_ratio_pct <= 65.0:
            salud_label = "SUPERÁVIT TÉCNICO (Margen Actuarial Sano)"
        elif loss_ratio_pct <= 80.0:
            salud_label = "EQUILIBRADO (Monitoreo de Frecuencia)"
        else:
            salud_label = "DÉFICIT TÉCNICO (Ajustar Primas o Deducibles)"

        # 2. Consulta SQL para la Matriz de Vehículos
        query_vehiculos = f"""
            SELECT 
                tipo_vehiculo,
                COUNT(*) as total_polizas,
                COALESCE(SUM(tuvo_siniestro_en_anio), 0) as total_siniestros,
                COALESCE(AVG(prima_anual_calculada), 0) as prima_media,
                COALESCE(SUM(prima_anual_calculada), 0) as primas_totales,
                COALESCE(SUM(CASE WHEN tuvo_siniestro_en_anio = 1 THEN costo_siniestro_usd ELSE 0 END), 0) as costo_total_siniestros,
                COALESCE(AVG(CASE WHEN tuvo_siniestro_en_anio = 1 THEN costo_siniestro_usd ELSE NULL END), 0) as severidad_media
            FROM dataset_historico_ml_polizas
            {where_clause}
            GROUP BY tipo_vehiculo
            ORDER BY total_polizas DESC, tipo_vehiculo ASC;
        """
        cur.execute(query_vehiculos, params)
        vehiculo_rows = cur.fetchall()

        desglose_vehiculos: List[VehicleLossMetricDTO] = []
        for r in vehiculo_rows:
            v_tipo = str(r[0])
            v_tot = int(r[1] or 0)
            v_sin = int(r[2] or 0)
            v_prima_med = round(float(r[3] or 0.0), 2)
            v_prima_tot = round(float(r[4] or 0.0), 2)
            v_costo_tot = round(float(r[5] or 0.0), 2)
            v_sev_med = round(float(r[6] or 0.0), 2)

            v_frec_pct = round((v_sin / max(1, v_tot)) * 100.0, 1)
            v_loss_ratio = round((v_costo_tot / max(1.0, v_prima_tot)) * 100.0, 1)

            if v_loss_ratio <= 60.0:
                v_semaforo = "SUPERÁVIT TÉCNICO"
            elif v_loss_ratio <= 75.0:
                v_semaforo = "EQUILIBRADO"
            else:
                v_semaforo = "ALTO RIESGO"

            desglose_vehiculos.append(
                VehicleLossMetricDTO(
                    tipo_vehiculo=v_tipo,
                    total_polizas=v_tot,
                    siniestros_count=v_sin,
                    frecuencia_siniestralidad_pct=v_frec_pct,
                    costo_medio_usd=v_sev_med,
                    prima_media_usd=v_prima_med,
                    total_costo_siniestros_usd=v_costo_tot,
                    total_primas_usd=v_prima_tot,
                    loss_ratio_pct=v_loss_ratio,
                    semaforo_tecnico=v_semaforo
                )
            )

        # 3. Consulta SQL para Gráfico 1: Cohortes de Edad (Siniestralidad vs Severidad)
        query_edad = f"""
            SELECT 
                CASE 
                    WHEN edad_asegurado BETWEEN 18 AND 25 THEN '18-25'
                    WHEN edad_asegurado BETWEEN 26 AND 35 THEN '26-35'
                    WHEN edad_asegurado BETWEEN 36 AND 50 THEN '36-50'
                    WHEN edad_asegurado BETWEEN 51 AND 65 THEN '51-65'
                    ELSE '65+'
                END as rango_edad,
                COUNT(*) as total_conductores,
                COALESCE(SUM(tuvo_siniestro_en_anio), 0) as total_siniestros,
                COALESCE(AVG(CASE WHEN tuvo_siniestro_en_anio = 1 THEN costo_siniestro_usd ELSE NULL END), 0) as costo_medio_usd
            FROM dataset_historico_ml_polizas
            {where_clause}
            GROUP BY 1
            ORDER BY MIN(edad_asegurado) ASC;
        """
        cur.execute(query_edad, params)
        edad_rows = cur.fetchall()

        cohortes_edad: List[AgeCohortMetricDTO] = []
        for r in edad_rows:
            e_rango = str(r[0])
            e_tot = int(r[1] or 0)
            e_sin = int(r[2] or 0)
            e_costo = round(float(r[3] or 0.0), 2)
            e_frec = round((e_sin / max(1, e_tot)) * 100.0, 1)

            cohortes_edad.append(
                AgeCohortMetricDTO(
                    rango_edad=e_rango,
                    total_conductores=e_tot,
                    total_siniestros=e_sin,
                    frecuencia_pct=e_frec,
                    costo_medio_usd=e_costo
                )
            )

        # 4. Consulta SQL para Gráfico 2: Evolución Mensual Cronológica (12 Meses en la BD)
        query_mensual = f"""
            SELECT 
                TO_CHAR(mes_registro, 'YYYY-MM') as mes,
                COUNT(*) as polizas_activas,
                COALESCE(SUM(tuvo_siniestro_en_anio), 0) as siniestros_mes,
                COALESCE(SUM(CASE WHEN tuvo_siniestro_en_anio = 1 THEN costo_siniestro_usd ELSE 0 END), 0) as costo_total_mes_usd
            FROM dataset_historico_ml_polizas
            {where_clause}
            GROUP BY 1
            ORDER BY 1 ASC;
        """
        cur.execute(query_mensual, params)
        mensual_rows = cur.fetchall()

        tendencia_mensual: List[MonthlyTrendMetricDTO] = []
        for r in mensual_rows:
            m_mes = str(r[0])
            m_pol = int(r[1] or 0)
            m_sin = int(r[2] or 0)
            m_costo = round(float(r[3] or 0.0), 2)
            m_tasa = round((m_sin / max(1, m_pol)) * 100.0, 1)

            tendencia_mensual.append(
                MonthlyTrendMetricDTO(
                    mes=m_mes,
                    polizas_activas=m_pol,
                    siniestros_mes=m_sin,
                    costo_total_mes_usd=m_costo,
                    tasa_incurrencia_pct=m_tasa
                )
            )

        cur.close()
        conn.close()

        return ActuarialLossSummaryDTO(
            frecuencia_siniestralidad_pct=frecuencia_pct,
            severidad_media_usd=round(severidad_media, 2),
            loss_ratio_tecnico_pct=loss_ratio_pct,
            prima_media_anual_usd=round(prima_media, 2),
            score_medio_riesgo=round(score_medio_riesgo, 1),
            total_polizas=total_polizas,
            total_siniestros=total_siniestros,
            costo_total_siniestros_usd=round(costo_total_siniestros, 2),
            primas_totales_usd=round(primas_totales, 2),
            salud_cartera_label=salud_label,
            desglose_por_vehiculo=desglose_vehiculos,
            cohortes_edad=cohortes_edad,
            tendencia_mensual=tendencia_mensual,
            filtros_aplicados=filtros,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )


# Instancia Singleton de Control ICONIX
actuarial_loss_control = ActuarialLossAnalysisControl()

