import { describe, it, expect } from 'vitest';
import { ValidadorNitidezLocalWebControl } from './ValidadorNitidezLocalWebControl';
import { AuthOIDCService, PERFILES_SSO_DEMO } from '../auth/AuthOIDCService';
import { ApolloFederationClient } from '../graphql/ApolloFederationClient';

describe('Perfil A — Pruebas Unitarias MF2 React PWA (CU01, CU02, CU04, CU10)', () => {
  const validador = new ValidadorNitidezLocalWebControl();

  it('CU04: ValidadorNitidezLocalWebControl.validarNitidez() aprueba documento nítido HD (score >= 0.65)', () => {
    const tensor = validador.generarTensorSimulado('NITIDA_HD', 96, 64);
    const resultado = validador.validarNitidez(tensor.pixels, tensor.width, tensor.height, {
      tipoDoc: 'RUAT Vehicular',
      placa: '5892-TXR'
    });

    expect(resultado.esValidoTfJs).toBe(true);
    expect(resultado.nitidezScore).toBeGreaterThanOrEqual(0.65);
    expect(resultado.varianzaLaplaciana).toBeGreaterThan(200);
    expect(resultado.tokenValidacionNitidezLocal).toContain('TFJS-ONNX-LOCAL-OK');
  });

  it('CU04: ValidadorNitidezLocalWebControl.validarNitidez() rechaza documento borroso (score < 0.65)', () => {
    const tensor = validador.generarTensorSimulado('BORROSA_DESENFOCADA', 96, 64);
    const resultado = validador.validarNitidez(tensor.pixels, tensor.width, tensor.height);

    expect(resultado.esValidoTfJs).toBe(false);
    expect(resultado.nitidezScore).toBeLessThan(0.65);
    expect(resultado.tokenValidacionNitidezLocal).toContain('BLURRY_REJECTED');
  });

  it('CU01: AuthOIDCService.obtenerSesionInicial() genera sesión OIDC + PKCE S256 y JWT RS256', () => {
    const authService = new AuthOIDCService();
    const sesion = authService.obtenerSesionInicial();

    expect(sesion.email).toBe(PERFILES_SSO_DEMO[0].email);
    expect(sesion.pkce_challenge).toContain('pkce-s256');
    expect(sesion.access_token.split('.').length).toBe(3);

    const claims = authService.decodificarPayloadJWT(sesion.access_token);
    expect(claims.pkce_challenge_method).toBe('S256');
  });

  it('CU04 & CU10: ApolloFederationClient.generarUUIDv4() genera llaves válidas para Idempotency-Key', () => {
    const uuid = ApolloFederationClient.generarUUIDv4();
    expect(uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
  });
});
