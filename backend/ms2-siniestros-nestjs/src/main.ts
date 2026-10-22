import express, { Request, Response } from 'express';

const app = express();
const PORT = process.env.PORT || 8002;

app.use(express.json());

app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'UP',
    service: 'ms2-siniestros-nestjs',
    pattern: 'Clean Architecture + CQRS',
    runtime: 'Node.js / TypeScript',
    timestamp: new Date().toISOString(),
  });
});

app.get('/api/siniestros/demo', (_req: Request, res: Response) => {
  res.json({
    reclamo_id: 'REC-2026-00492',
    estado: 'PERITAJE_COMPLETADO',
    poliza_id: 'd0000001-0000-0000-0000-000000000001',
    monto_indemnizacion_aprobado: 2500.0,
  });
});

app.listen(PORT, () => {
  console.log(`[ms2-siniestros-nestjs] Corriendo en puerto ${PORT} bajo Clean Architecture + CQRS`);
});
