export interface OwaspSecurityAudit {
  es_amenaza: boolean;
  threat_score: number;
  rule_triggered?: string;
  payload_original: string;
  payload_sanitizado: string;
  detalles_inspeccion: string[];
  estado: 'SAFE' | 'BLOCKED';
  timestamp: string;
}

export interface McpToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface McpToolInvocationTrace {
  tool_name: string;
  arguments: Record<string, any>;
  execution_time_ms: number;
  records_processed: number;
  status: 'SUCCESS' | 'ERROR' | 'BLOCKED';
  fuente_datos: string;
}

export interface GeneratedDocument {
  filename: string;
  format: 'xlsx' | 'pdf' | 'docx';
  file_size_bytes: number;
  file_size_kb: number;
  sha256_hash: string;
  download_url: string;
  created_at: string;
}

export interface VoiceMcpResponse {
  transcripcion: string;
  intencion_detectada: string;
  formato_solicitado: string;
  auditoria_seguridad: OwaspSecurityAudit;
  traza_mcp?: McpToolInvocationTrace;
  kpis_resumen: Record<string, any>;
  documento?: GeneratedDocument;
  mensaje: string;
  timestamp: string;
}
