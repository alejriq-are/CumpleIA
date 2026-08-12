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

### Conflicto documental

`docs/backlog.md` conserva líneas antiguas que dicen que Tareas 4-6 siguen pendientes, aunque secciones posteriores del mismo archivo y el código muestran que ya fueron implementadas. Debe limpiarse.

## Módulo 2 - Inventario / RAT

**Estado: no implementado como módulo funcional.**

Hay scaffolding en los modelos (`Treatment`, `System`, `Vendor`). La instrucción más reciente recomienda comenzar con una **Tarea 0 de descubrimiento**: comparar la estructura objetivo del RAT con la guía CCS y la Ley 21.719 antes de crear endpoints o migraciones nuevas.

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
