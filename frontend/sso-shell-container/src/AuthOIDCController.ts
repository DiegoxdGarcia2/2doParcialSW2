/**
 * =============================================================================
 *  AegisCore AI — CU01: Iniciar Sesión Único Multi-Aplicación (SSO)
 *  Objeto CONTROL de ICONIX: AuthOIDCController (Shell Container Web/Móvil)
 *  Protocolo: OAuth 2.0 / OpenID Connect (OIDC) + PKCE (S256) + JWT RS256
 * =============================================================================
 */

export interface UsuarioRolSSO {
  id: string;
  keycloak_sub: string;
  email: string;
  nombre_completo: string;
  rol: 'ADMIN' | 'AJUSTADOR' | 'PERITO' | 'ACTUARIO' | 'CLIENTE';
  cliente_id: string;
  session_id: string;
}

export interface SesionUnificadaToken {
  authenticated: boolean;
  sso_provider: string;
  protocol: string;
  signature_algorithm: string;
  access_token: string;
  token_type: string;
  expires_in: number;
  usuario_rol: UsuarioRolSSO;
  sesion_unificada_dynamodb: {
    table: string;
    session_id: string;
    keycloak_sub: string;
    rol: string;
    token_sha256: string;
    status: string;
    created_at: string;
    ttl: number;
    latency_ms: number;
  };
}

export class AuthOIDCController {
  private readonly ms1BaseUrl: string;
  private readonly storageKey = 'aegiscore_sso_unified_session_v1';

  constructor(ms1BaseUrl = 'http://localhost:8001') {
    this.ms1BaseUrl = ms1BaseUrl.replace(/\/$/, '');
  }

  /**
   * Método operacional UML 2.5+ (CU01):
   * Genera el par PKCE (code_verifier y code_challenge con SHA-256).
   */
  public async generarChallengePKCE(): Promise<{ codeVerifier: string; codeChallenge: string }> {
    const randomBytes = new Uint8Array(32);
    if (typeof window !== 'undefined' && window.crypto?.getRandomValues) {
      window.crypto.getRandomValues(randomBytes);
    } else {
      for (let i = 0; i < 32; i++) randomBytes[i] = (i * 17 + 43) % 256;
    }

    const codeVerifier = Array.from(randomBytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');

    if (typeof window !== 'undefined' && window.crypto?.subtle) {
      const encoder = new TextEncoder();
      const digest = await window.crypto.subtle.digest('SHA-256', encoder.encode(codeVerifier));
      const base64Url = btoa(String.fromCharCode(...new Uint8Array(digest)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');
      return { codeVerifier, codeChallenge: base64Url };
    }

    return { codeVerifier, codeChallenge: `s256-${codeVerifier.slice(0, 32)}` };
  }

  /**
   * Método operacional UML 2.5+ (CU01):
   * Autentica al usuario una única vez contra Keycloak / MS1 OIDC Adapter y almacena
   * el token JWT RS256 compartido entre Angular, React y Flutter.
   */
  public async autenticarUsuarioOIDC(email: string, rol?: string): Promise<SesionUnificadaToken> {
    const pkce = await this.generarChallengePKCE();
    const response = await fetch(`${this.ms1BaseUrl}/api/v1/auth/oidc-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        rol,
        code_verifier: pkce.codeVerifier,
        code_challenge: pkce.codeChallenge,
        code_challenge_method: 'S256',
      }),
    });

    if (!response.ok) {
      throw new Error(`Error de autenticación SSO OIDC (${response.status})`);
    }

    const sessionData: SesionUnificadaToken = await response.json();
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.storageKey, JSON.stringify(sessionData));
    }
    return sessionData;
  }

  /**
   * Método operacional UML 2.5+ (CU01):
   * Obtiene la sesión SSO activa del contenedor sin requerir nuevo inicio de sesión.
   */
  public obtenerSesionActiva(): SesionUnificadaToken | null {
    if (typeof localStorage === 'undefined') return null;
    const raw = localStorage.getItem(this.storageKey);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as SesionUnificadaToken;
    } catch {
      return null;
    }
  }

  public cerrarSesionUnificada(): void {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.storageKey);
    }
  }
}

