import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { VoiceMcpResponse, McpToolDefinition } from '../models/voice-mcp.models';

@Injectable({
  providedIn: 'root'
})
export class VoiceMcpService {
  private baseUrl = 'http://127.0.0.1:8000/api/v1/mcp';

  constructor(private http: HttpClient) {}

  /**
   * Envía un comando de voz mediante FormData multipart (audio binario o prompt dictado).
   */
  procesarComandoVoz(
    audioBlob?: Blob,
    promptDictado?: string,
    formato?: string,
    herramienta?: string
  ): Observable<VoiceMcpResponse> {
    const formData = new FormData();
    if (audioBlob) {
      formData.append('audio_file', audioBlob, 'grabacion_microfono.wav');
    }
    if (promptDictado) {
      formData.append('prompt_dictado', promptDictado);
    }
    if (formato) {
      formData.append('formato_preferido', formato);
    }
    if (herramienta) {
      formData.append('herramienta_sugerida', herramienta);
    }

    return this.http.post<VoiceMcpResponse>(`${this.baseUrl}/voice-command`, formData).pipe(
      catchError(err => throwError(() => err))
    );
  }

  /**
   * Envía comando de voz en JSON directo (vía Web Speech API o texto tipado).
   */
  procesarComandoJson(
    promptDictado: string,
    formato?: string,
    herramienta?: string
  ): Observable<VoiceMcpResponse> {
    const body: Record<string, any> = {
      prompt_dictado: promptDictado
    };
    if (formato) {
      body['formato_preferido'] = formato;
    }
    if (herramienta) {
      body['herramienta_sugerida'] = herramienta;
    }
    return this.http.post<VoiceMcpResponse>(`${this.baseUrl}/voice-command/json`, body).pipe(
      catchError(err => throwError(() => err))
    );
  }

  /**
   * Consulta el catálogo oficial de herramientas disponibles en el Servidor MCP.
   */
  obtenerCatalogoTools(): Observable<McpToolDefinition[]> {
    return this.http.get<McpToolDefinition[]>(`${this.baseUrl}/tools`).pipe(
      catchError(err => throwError(() => err))
    );
  }

  /**
   * Retorna la URL directa para descarga del archivo compilado (.xlsx, .pdf, .docx).
   */
  getDownloadUrl(filename: string): string {
    return `${this.baseUrl}/download-report/${filename}`;
  }
}
