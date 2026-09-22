# Continuidad — Cierre M2-T3.7 Revisión, activación y ciclo de vida RAT

**Fecha:** 2026-09-22
**Rama:** `feature/m2-t3-7-rat-review-activation`
**Base:** `e0c10aa feat: complete RAT international transfers workflow`

## Estado

M2-T3.7 — Revisión, activación y ciclo de vida del RAT queda funcionalmente completado y validado.

La ficha RAT dispone ahora de un flujo explícito de revisión y activación, alineado con los 10 requisitos de preparación y con validación equivalente en backend.

## Fuente única de preparación

Se creó:

`frontend/lib/rat-readiness.ts`

Centraliza la evaluación de los 10 requisitos usados tanto por:

- `TreatmentProgress`
- `TreatmentReviewActivationSection`

Esto evita divergencias entre el indicador 9/10–10/10 y la disponibilidad de la acción de activación.

La preparación no representa porcentaje de cumplimiento legal.

## Revisión y activación

Se agregó:

`frontend/components/rat/TreatmentReviewActivationSection.tsx`

Comportamiento:

- RAT borrador incompleto:
  - muestra requisitos pendientes;
  - botón `Activar actividad` deshabilitado.
- RAT borrador 10/10:
  - informa que está preparado;
  - permite activar.
- RAT activo:
  - informa que forma parte del inventario activo;
  - permite volver a preparación;
  - permite archivar.
- RAT archivado:
  - permite reactivar solo si cumple nuevamente los requisitos de preparación.

El backend continúa siendo la autoridad final y revalida los requisitos antes de una transición a `activo`.

## Revalidación automática de registros activos

Se incorporó una regla de consistencia:

Si una actividad está `activo` y una modificación deja pendiente alguno de sus requisitos mínimos, el RAT vuelve automáticamente a:

`borrador` / `Registro en preparación`

Ejemplo validado:

- RAT activo 10/10;
- transferencia internacional existente cambia a `adequacy_status = pendiente`;
- al guardar:
  - estado pasa automáticamente a preparación;
  - progreso baja a 9/10;
  - requisito de transferencias queda pendiente;
  - activación queda deshabilitada.

También fue validado el caso de declaración general de transferencias en `pendiente`.

## Ciclo de vida y timestamps

Se incorporaron tres timestamps específicos:

- `activated_at`
  - fecha de la activación más reciente;
- `archived_at`
  - fecha en que la actividad fue archivada;
- `status_changed_at`
  - fecha del último cambio de estado, cualquiera sea la transición.

La `start_date` existente mantiene su significado original:

fecha real de inicio de la actividad de tratamiento en la organización.

No se reutiliza para fechas internas de CumpleIA.

## Actualización del RAT

Se corrigió el comportamiento de `updated_at`.

Antes, `Treatment.updated_at` tenía únicamente `server_default=func.now()` y podía conservar la fecha de creación aunque el registro se modificara.

Ahora `updated_at` y `updated_by` se actualizan cuando cambia:

- información general;
- finalidades;
- categorías de datos;
- titulares;
- fuentes;
- sistemas asociados;
- proveedores asociados;
- transferencias internacionales;
- estado del RAT.

Las operaciones sobre catálogos independientes de sistemas/proveedores no se consideran por sí solas una edición del RAT padre.

## Inventario RAT

`RatWorkspace` ahora diferencia claramente:

- `Creado`
- `Estado`
- `Último cambio de estado`
- `Última actualización`

Esto evita confundir las fechas internas del ciclo de vida con la fecha real de inicio de la actividad de tratamiento.

Los registros históricos anteriores a la incorporación de estos timestamps pueden presentar `—` hasta que experimenten una nueva transición real. No se inventan fechas históricas.

## Migraciones

Se agregaron dos migraciones Alembic:

### `267224e9b9e6`

`treatment lifecycle timestamps`

Agrega:

- `activated_at`
- `archived_at`

### `48fe0b9c21e4`

`treatment status changed timestamp`

Agrega:

- `status_changed_at`

Cadena final:

`f4a5b6c7d8e9 -> 267224e9b9e6 -> 48fe0b9c21e4`

Base local validada en:

`48fe0b9c21e4 (head)`

## Pruebas funcionales realizadas

Se validó manualmente:

1. Preparación 10/10 -> Activar -> Activo.
2. Activo -> Volver a preparación.
3. Activo -> requisito general pendiente -> Preparación 9/10.
4. Activo + transferencia individual con `adequacy_status = pendiente`
   -> Preparación 9/10.
5. Requisito resuelto nuevamente -> 10/10 y posibilidad de activar.
6. Inventario refleja correctamente:
   - estado;
   - creación;
   - último cambio de estado;
   - última actualización.

## Pruebas automáticas y calidad

Resultados finales:

- suite backend completa:
  `167 passed in 13.65s`
- pruebas focalizadas RAT:
  PASS
- Ruff backend:
  PASS
- TypeScript:
  PASS
- Prettier:
  PASS
- `git diff --check`:
  PASS

## Archivos principales

Backend:

- `backend/app/api/rat.py`
- `backend/app/db/models.py`
- `backend/app/schemas/rat.py`
- `backend/app/services/rat.py`
- `backend/tests/test_treatment_activation.py`
- `backend/alembic/versions/267224e9b9e6_treatment_lifecycle_timestamps.py`
- `backend/alembic/versions/48fe0b9c21e4_treatment_status_changed_timestamp.py`

Frontend:

- `frontend/components/rat/RatWorkspace.tsx`
- `frontend/components/rat/TreatmentGeneralForm.tsx`
- `frontend/components/rat/TreatmentProgress.tsx`
- `frontend/components/rat/TreatmentReviewActivationSection.tsx`
- `frontend/lib/rat-readiness.ts`
- `frontend/lib/api/client.ts`

## Próximo paso

Con M2-T3.7 cerrado, continuar con el cierre integral de M2-T3:

- UX/errores/empty states pendientes;
- validaciones finales frontend/E2E;
- documentación final de M2;
- preparación de la etapa siguiente del producto.
