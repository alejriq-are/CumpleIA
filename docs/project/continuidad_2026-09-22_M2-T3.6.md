# Continuidad — Cierre M2-T3.6 Transferencias internacionales

**Fecha:** 2026-09-22  
**Rama:** `feature/m2-t3-6-rat-transfers`  
**Base:** `dbb0965 docs: record pause before RAT transfers`

## Estado

M2-T3.6 — Transferencias internacionales queda funcionalmente completado y validado.

El flujo RAT alcanza el décimo requisito de preparación cuando la declaración y la evaluación de las transferencias internacionales están resueltas.

## Funcionalidad implementada

### Frontend

Se agregó la sección `TreatmentInternationalTransfersSection` a la ficha RAT.

Permite:

- declarar:
  - Sí existen transferencias internacionales
  - No existen
  - Pendiente de revisión
- registrar una o más transferencias;
- seleccionar como destinatario una organización/proveedor ya registrado;
- ingresar manualmente un destinatario;
- registrar país de destino;
- registrar estado de adecuación:
  - `adecuado`
  - `no_adecuado`
  - `pendiente`
  - `no_determinado`
- registrar mecanismo aplicable;
- registrar garantías o medidas;
- registrar referencia de evidencia;
- crear, modificar y eliminar transferencias mediante la API existente.

Se agregó ayuda contextual al estado de adecuación.

En particular, `no_adecuado` se explica expresamente como un estado que no implica por sí solo incumplimiento. La interfaz solicita documentar mecanismo, garantías y evidencia.

También se aclara que el estado de adecuación se refiere al país de destino y no a la seguridad, calidad o reputación del proveedor.

## Regla de preparación RAT

El requisito 10 quedó definido de la siguiente forma:

- declaración `no` → requisito resuelto;
- declaración `pendiente` o nula → requisito no resuelto;
- declaración `si` sin transferencias registradas → requisito no resuelto;
- declaración `si` con al menos una transferencia `pendiente` → requisito no resuelto;
- declaración `si` con todas las transferencias en `adecuado`, `no_adecuado` o `no_determinado` → requisito resuelto.

Validación funcional de interfaz:

- `Sí + pendiente` → 9/10;
- `Sí + adecuado` → 10/10;
- `Sí + no_adecuado` → 10/10;
- `Sí + no_determinado` → 10/10;
- `No existen` → 10/10.

El indicador continúa representando preparación del registro para activación y no porcentaje de cumplimiento legal.

## Backend

`_validate_activation()` fue alineado con la regla de progreso del frontend.

La activación se rechaza cuando:

- se declara que existen transferencias pero no hay ninguna registrada;
- existe al menos una transferencia con `adequacy_status = pendiente`.

Los estados `adecuado`, `no_adecuado` y `no_determinado` se consideran estados evaluados para efectos de preparación/activación.

## Pruebas

Se agregó cobertura específica en:

`backend/tests/test_treatment_activation.py`

Casos verificados:

- `si` sin transferencias → bloquea activación;
- transferencia `pendiente` → bloquea activación;
- `adecuado` → permite activación;
- `no_adecuado` → permite activación;
- `no_determinado` → permite activación;
- declaración `no` conserva el comportamiento previo.

Resultados:

- prueba específica: `1 passed`;
- archivo de activación: `4 passed`;
- suite backend completa: `167 passed in 14.54s`;
- frontend TypeScript: PASS;
- Prettier: PASS;
- `git diff --check`: PASS.

## Archivos principales modificados

- `backend/app/services/rat.py`
- `backend/tests/test_treatment_activation.py`
- `frontend/components/rat/TreatmentGeneralForm.tsx`
- `frontend/components/rat/TreatmentProgress.tsx`
- `frontend/components/rat/TreatmentInternationalTransfersSection.tsx`
- `frontend/lib/api/client.ts`

## Próximo paso

Con M2-T3.6 cerrado, continuar con la siguiente etapa del flujo RAT, incluyendo revisión/activación y los ajustes de UX/errores/empty states pendientes antes del cierre integral de M2-T3.
