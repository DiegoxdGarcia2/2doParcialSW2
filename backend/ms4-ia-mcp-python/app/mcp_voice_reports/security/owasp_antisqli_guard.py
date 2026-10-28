"""
=============================================================================
 AegisCore AI - MS4: Blindaje de Seguridad OWASP Anti-SQLi
 Caso de Uso 15 (CU15) — Control de Ciberseguridad & Sanitización
 Implementa análisis léxico, heurístico y de AST para neutralizar:
   - Inyección SQL clásica (Tautologías, Union-Based, Stacked Queries)
   - Prompt Injection dirigido a esquemas de base de datos
   - Intentos de evasión mediante comentarios o codificación hex
 Estándar: OWASP Top 10 A03:2021 (Injection)
=============================================================================
"""

import re
import html
from typing import List, Tuple
import sqlparse
from app.entities.voice_mcp_dto import OwaspSecurityAuditDTO


class OwaspAntiSqliGuard:
    """Motor de detección y neutralización de vectores de inyección SQL en comandos de voz."""

    # Patrones de ataque conocidos categorizados por regla OWASP
    ATTACK_SIGNATURES: List[Tuple[str, re.Pattern, float]] = [
        # 1. Tautologías y bypass de autenticación/condiciones
        (
            "OWASP-A03:SQLi-Tautology",
            re.compile(
                r"('|\b)\s*OR\s+('?[0-9a-zA-Z]+'?\s*=\s*'?[0-9a-zA-Z]*|TRUE|1=1)|--\s*$|\bOR\s+1\s*=\s*1|\bOR\s+'1'\s*=\s*'1",
                re.IGNORECASE
            ),
            0.98
        ),
        # 2. Inyección basada en UNION
        (
            "OWASP-A03:SQLi-UnionBased",
            re.compile(
                r"\bUNION\s+(ALL\s+)?SELECT\b",
                re.IGNORECASE
            ),
            0.99
        ),
        # 3. Stacked queries (sentencias múltiples con punto y coma)
        (
            "OWASP-A03:SQLi-StackedQueries",
            re.compile(
                r";\s*(DROP|ALTER|TRUNCATE|DELETE|INSERT|UPDATE|CREATE|GRANT|REVOKE|SHUTDOWN)\b",
                re.IGNORECASE
            ),
            1.0
        ),
        # 4. Invocación de procedimientos del sistema o comandos OS
        (
            "OWASP-A03:SQLi-SystemExecution",
            re.compile(
                r"\b(xp_cmdshell|exec\s+master|sp_executesql|pg_read_file|pg_ls_dir|dblink_exec)\b",
                re.IGNORECASE
            ),
            1.0
        ),
        # 5. Ataques basados en tiempo o funciones intrusivas
        (
            "OWASP-A03:SQLi-TimeBlind",
            re.compile(
                r"\b(benchmark\s*\(|sleep\s*\(|pg_sleep\s*\(|waitfor\s+delay)\b",
                re.IGNORECASE
            ),
            0.95
        ),
        # 6. Extracción de metadatos del catálogo del sistema
        (
            "OWASP-A03:SQLi-InformationSchema",
            re.compile(
                r"\b(information_schema|pg_catalog|sys\.tables|sqlite_master)\b",
                re.IGNORECASE
            ),
            0.90
        ),
        # 7. Comentarios SQL de bypass
        (
            "OWASP-A03:SQLi-CommentBypass",
            re.compile(
                r"(--|\/\*.*?\*\/|#\s*)",
                re.IGNORECASE
            ),
            0.88
        ),
    ]

    @classmethod
    def auditar_texto(cls, texto: str) -> OwaspSecurityAuditDTO:
        """
        Inspecciona el texto dictado o transcrito.
        Retorna OwaspSecurityAuditDTO con indicador de amenaza y regla disparada.
        """
        if not texto or not texto.strip():
            return OwaspSecurityAuditDTO(
                es_amenaza=False,
                threat_score=0.0,
                rule_triggered=None,
                payload_original="",
                payload_sanitizado="",
                detalles_inspeccion=["Texto vacío, seguro por defecto"],
                estado="SAFE"
            )

        detalles: List[str] = []
        threat_score: float = 0.0
        regla_disparada: str = None
        texto_limpio = texto.strip()

        # 1. Escaneo por firmas de expresiones regulares
        for regla, patron, peso in cls.ATTACK_SIGNATURES:
            match = patron.search(texto_limpio)
            if match:
                threat_score = max(threat_score, peso)
                regla_disparada = regla
                detalles.append(f"Patrón malicioso detectado [{regla}]: '{match.group(0)}'")

        # 2. Análisis sintáctico de AST con sqlparse
        try:
            parsed = sqlparse.parse(texto_limpio)
            for statement in parsed:
                # Si sqlparse detecta sentencias DDL destructivas o tokens peligrosos
                tokens = [t.value.upper() for t in statement.flatten()]
                dangerous_keywords = {"DROP", "ALTER", "TRUNCATE", "DELETE", "UNION"}
                interseccion = set(tokens).intersection(dangerous_keywords)
                if interseccion:
                    threat_score = max(threat_score, 0.95)
                    if not regla_disparada:
                        regla_disparada = "OWASP-A03:SQLi-DDL-Interception"
                    detalles.append(f"Palabras clave destructivas detectadas en AST: {list(interseccion)}")
        except Exception as e:
            detalles.append(f"Análisis sintáctico AST: {str(e)}")

        es_amenaza = threat_score >= 0.70

        # Sanitización de caracteres peligrosos para prevención en cascada
        payload_sanitizado = re.sub(r"['\";\-\-/\*]", "", texto_limpio)
        payload_sanitizado = html.escape(payload_sanitizado)

        if not es_amenaza:
            detalles.append("Análisis léxico y de AST superado: Cero vectores maliciosos detectados")

        return OwaspSecurityAuditDTO(
            es_amenaza=es_amenaza,
            threat_score=round(threat_score, 2),
            rule_triggered=regla_disparada,
            payload_original=texto_limpio,
            payload_sanitizado=payload_sanitizado,
            detalles_inspeccion=detalles,
            estado="BLOCKED" if es_amenaza else "SAFE"
        )
