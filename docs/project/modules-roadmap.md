# Módulos y roadmap

## Módulo 1 - Autodiagnóstico

**Estado: funcional en el snapshot.**

### Construido

- Tarea 0: catálogo/configuración.
- Tarea 1: persistencia/RLS de diagnóstico y brechas.
- Tarea 2: scoring determinista.
- Tarea 3: API.
- Tarea 4: informe con IA y guardarraíles.
- Tarea 5: exportación HTML.
- Tarea 6: frontend.

### Mejoras pendientes más claras

- mostrar N/A por sección;
- contenido más accionable por hallazgo;
- nota DPD/autodesignación;
- fundamento legal específico por hallazgo;
- cierre formal/firma/confidencialidad;
- re-evaluaciones e histórico;
- endpoint para `reference_documents`;
- testing de frontend como decisión transversal.

### Consistencia documental verificada (2026-09-15)

`docs/backlog.md` ya declara Tareas 0-6 completadas para el MVP y marca Tareas 4-6 como realizadas. El conflicto de estados anteriormente señalado queda resuelto.

## Módulo 2 - Inventario / RAT

**Estado: no implementado como módulo funcional.**

Hay scaffolding en los modelos (`Treatment`, `System`, `Vendor`), que requiere rediseño/ampliación según el [diseño conceptual del RAT](modulo2-rat-diseno.md).

- [x] **M2-T0 — Descubrimiento y diseño conceptual: DONE (2026-09-15).** Cierre conceptual, matriz canónica resumida, decisiones, fronteras M2/M3/M5 y modelo objetivo registrados.
- [x] **M2-T1 — Persistencia RAT: DONE (2026-09-15).** Migración `0010`, modelo SQLAlchemy normalizado, relaciones N:M, transferencias internacionales, auditoría, FK compuestas tenant-aware, RLS y tests de aislamiento/integridad implementados. Validación: 7 tests RAT y 136 tests backend PASS.
- [x] **M2-T2 — Servicio/API RAT: DONE (2026-09-15).** Contratos Pydantic normalizados, service layer, API REST, permisos `view_content`/`edit_content`, gate server-side de suscripción para M2+, aislamiento tenant-aware y tests HTTP end-to-end implementados. Validación: 26 tests específicos M2-T2 y 162 tests backend PASS.
- [ ] **M2-T3 — Siguiente paso:** frontend del RAT e integración funcional end-to-end sobre la API estabilizada.

M2 dispone ya de persistencia técnica, pero todavía no constituye un módulo funcional para el usuario: faltan servicio/API, reglas de aplicación y UI.

## Módulo 3 - Bases de licitud

**Estado: no implementado como módulo funcional.**

Existe `LegalBase` en el modelo inicial. Falta definir flujo, reglas, endpoints y UI.

## Módulo 4 - Generación de documentos

**Estado: no implementado.**

Existe `Document` como scaffolding. Word/PDF y workflow formal borrador/aprobado siguen siendo arquitectura futura.

## Módulo 5 - Carpeta de evidencia

**Estado: no implementado.**

Existe `EvidenceEvent` como scaffolding. No se observa todavía storage WORM/Object Lock, cadena de evidencia operacional, exportación del expediente ni anexo de respuestas.

## Monetización

La infraestructura de `Subscription` y permisos existe, pero todavía no hay pasarela de pago ni gate de módulos por suscripción.

Decisión de producto documentada:

- Módulo 1 permanece freemium.
- Al iniciar una función de Módulo 2+, crear una dependencia server-side tipo `require_active_subscription` y proteger el módulo completo.
