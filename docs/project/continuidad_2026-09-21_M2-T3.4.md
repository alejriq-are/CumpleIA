# Cierre M2-T3.4 — Sistemas utilizados

Fecha: 21 septiembre 2026

## Estado

M2-T3.4 quedó implementado y validado funcionalmente.

Punto de partida:

- rama: `feature/m2-t3-4-rat-systems`
- commit base: `1fcc694`
- progreso RAT previo: 7/10

## Implementación

Se creó:

- `frontend/components/rat/TreatmentSystemsSection.tsx`

Se amplió:

- `frontend/lib/api/client.ts`
- `frontend/components/rat/TreatmentGeneralForm.tsx`

### Cliente API

Se incorporaron:

- `SystemCreate`
- `SystemUpdate`
- `SystemOut`
- tipado de `TreatmentDetailOut.systems`
- `systems_declaration` en `TreatmentCreate/Update`
- `api.rat.listSystems(...)`
- `api.rat.createSystem(...)`
- `api.rat.updateSystem(...)`
- `api.rat.deleteSystem(...)`
- `api.rat.replaceSystems(...)`

También se ajustó `apiFetch()` para soportar respuestas HTTP `204 No Content`.

## UX implementada

La sección permite declarar:

- Sí usa sistemas
- No usa sistemas
- Pendiente de revisión

Cuando la declaración es `si`:

- se muestran los sistemas reutilizables de la organización;
- se puede seleccionar uno o más;
- se puede crear un sistema nuevo desde la misma ficha;
- el sistema creado queda disponible en el catálogo de la organización.

Cuando la declaración es `no`:

- se guardan cero asociaciones de sistemas.

Cuando la declaración es `pendiente`:

- el requisito no se considera resuelto.

La activación continúa usando la semántica backend canónica:

- `si` y `no` satisfacen el requisito;
- `pendiente` y `null` no lo satisfacen.

## Validación

Se ejecutó:

`npm run type-check`

Resultado: PASS.

Prueba funcional sobre la actividad `Gestión de clientes`:

- carga del catálogo: PASS
- declaración de sistemas: PASS
- asociación/guardado: PASS
- actualización de la ficha: PASS
- actualización inmediata del progreso: PASS

Resultado:

`7/10 -> 8/10`

## Siguiente paso

M2-T3.5 / siguiente bloque funcional:

**Proveedores / terceros -> potencial 9/10**

Después:

- transferencias internacionales -> potencial 10/10;
- revisión y activación.
