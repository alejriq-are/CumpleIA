# Módulo 2 - Inventario / RAT: diseño conceptual

**Tarea:** M2-T0 — Descubrimiento y diseño conceptual del RAT.
**Estado:** DONE — cierre conceptual.
**Fecha de registro:** 2026-09-15.
**Siguiente paso:** M2-T1 — diseño técnico del modelo de datos y plan de migraciones.

## Cierre y alcance

Se registra el cierre conceptual aprobado en la conversación
[Estrategia LLM local y nube](chatgpt-conversation://6a8f5468-fe5c-83e9-985a-d3929d0a3dfb).
La referencia a «M1-T0» de esa conversación corresponde a **M2-T0**, Tarea 0
del Módulo 2 — Inventario / Registro de Actividades de Tratamiento (RAT).

El objetivo cerrado es contrastar el scaffolding existente con la Ley 21.719,
la guía CCS, el RAT de Gobierno Digital de Chile y las plantillas de Seifti,
y fijar el alcance del inventario antes de modificar base de datos o API.
El RAT chileno orienta el núcleo regulatorio y la experiencia mínima para PYME;
la plantilla española aporta profundidad funcional, sin ser fuente jurídica
chilena ni un esquema que deba copiarse.

Este registro sintetiza las decisiones visibles en la referencia de conversación
aportada; no reproduce la matriz original íntegra ni una nueva revisión jurídica.
Las referencias a fuentes describen el contraste aprobado en esa conversación;
no se atribuyen citas textuales ni localizadores de archivos no disponibles aquí.

**M2-T0 DONE no significa Módulo 2 implementado.** El cierre entrega alcance,
matriz resumida, decisiones, fronteras y modelo conceptual. Quedan fuera de esta
tarea migraciones, modelos nuevos, endpoints, servicios, UI y flujos funcionales
de M3/M5. El esquema físico y la estrategia de transición se concretan en M2-T1.

## Matriz canónica resumida

Clasificación de fundamento:

- **A — exigencia legal directa:** obligación identificada en la Ley 21.719.
- **B — soporte necesario/relevante:** ayuda a cumplir o demostrar una obligación.
- **C — recomendación práctica CCS / referencia chilena.**
- **D — decisión de producto CumpleIA:** estructura, trazabilidad o facilidad de uso.

La obligatoriedad de un campo en CumpleIA es una decisión de producto; no implica
que la ley imponga ese campo o un formato RAT particular. Las filas A/C siguientes
recogen la clasificación visible del cierre; las filas D consolidan las restantes
decisiones de diseño sin extender su atribución normativa.

| Elemento | Clasificación | Fundamento / referencia | Decisión CumpleIA |
|---|---|---|---|
| Nombre de la actividad | C + D | RAT de Gobierno Digital: actividad de tratamiento | Obligatorio; nombre comprensible de la actividad. |
| Descripción del tratamiento | B + D | Delimitación del alcance; referencia funcional Seifti | Obligatoria y breve, separada del nombre. |
| Área / departamento responsable | C + D | Organización operativa del registro; referencia funcional Seifti | Recomendado; lista o texto guiado para PYME. |
| Rol de la organización | B + C | RAT chileno distingue responsable o encargado | Obligatorio por tratamiento; separado del rol de terceros. |
| Finalidades | A | Art. 14 ter, según el contraste registrado; guía CCS | Obligatorias; admitir múltiples finalidades. |
| Categorías de datos personales | A | Art. 14 ter y RAT chileno, según el contraste registrado | Obligatorias mediante catálogo chileno estructurado. |
| Identificación de datos sensibles | D | Decisión canónica del cierre | Derivar de las categorías seleccionadas; `has_sensitive` no es fuente primaria. |
| Categorías de titulares | D | Decisión canónica del cierre | Admitir múltiples categorías por actividad. |
| Sistemas utilizados | D | Decisión canónica del cierre | Relación N:M entre actividad y sistemas. |
| Terceros y su rol | D | Decisión canónica del cierre | Relación N:M; encargado/cesionario se define en la relación con la actividad. |
| Encargo de tratamiento | D | Decisión canónica del cierre | Registrar objeto, duración, finalidad, datos, titulares, contrato y subencargados. |
| Transferencias internacionales | D | Decisión canónica del cierre | Entidad explícita con país, receptor, mecanismo y garantías. |
| Base de legitimidad | D | Frontera canónica M2/M3 | Mostrar la base y su estado; determinación, justificación y aprobación en M3. |
| Consentimiento y LIA | D | Frontera canónica M2/M3 | Evaluaciones propias de M3; no columnas de `Treatment`. |
| Referencias documentales y trazabilidad | D | Frontera de producto M2/M5 | M2 mantiene contexto y referencias; M5 concentra el expediente probatorio. |

Los atributos existentes que el extracto no desarrolla, como conservación
(`retention`), deben revisarse expresamente en M2-T1. Su ausencia en esta matriz
resumida no autoriza eliminarlos ni permite inferir una clasificación legal.

## Decisiones de diseño

1. Conservar `Treatment`, `System` y `Vendor` como punto de partida, con
   rediseño/ampliación. Su existencia actual no acredita funcionalidad del RAT.
2. `Treatment` representa una actividad de tratamiento. Un sistema puede apoyar
   varias actividades y una actividad puede utilizar varios sistemas.
3. Separar las finalidades, categorías de datos y categorías de titulares para
   admitir multiplicidad. Las categorías de datos usan un catálogo chileno
   estructurado; el texto libre no será la única fuente de clasificación.
4. Derivar sensibilidad desde las categorías seleccionadas. Diseñar la transición
   de `has_sensitive` sin convertir el booleano antiguo en una segunda verdad.
5. Registrar el rol de la organización como responsable o encargado en cada
   actividad. No confundirlo con `Membership.role` ni con el rol de un tercero.
6. Rediseñar `Vendor.role` / `ThirdPartyRole`: encargado/cesionario pertenece a la
   relación tratamiento-tercero. La dimensión internacional es independiente.
7. Representar el encargo con su alcance y referencia contractual, incluyendo
   subencargados. `has_dpa` por sí solo no describe ese alcance.
8. Modelar cada transferencia internacional explícitamente. `is_international`
   no sustituye país, receptor, mecanismo y garantías.
9. Mantener aislamiento por organización, auditoría y validación de relaciones
   entre entidades del mismo tenant, de acuerdo con los ADR y la arquitectura.
   M2-T1 debe especificar RLS y restricciones antes de implementar migraciones.

## Frontera M2 / M3 / M5

| Módulo | Responsabilidad | Relación con el RAT |
|---|---|---|
| M2 — Inventario / RAT | Describir actividades, finalidades, datos, titulares, sistemas, terceros, encargos y transferencias | Mantiene el contexto factual y muestra referencias a decisiones y documentos. |
| M3 — Bases de licitud | Determinar, justificar y aprobar la base de legitimidad; gestionar evaluaciones de consentimiento y LIA (interés legítimo) | Recibe el contexto de M2 y devuelve resultados/estado vinculados; no duplicar su lógica en `Treatment`. |
| M5 — Carpeta de evidencia | Consolidar bitácora, versiones y soportes probatorios del expediente, con la inmutabilidad prevista para ese módulo | Consume referencias y eventos de M2/M3; la auditoría operativa de M2 no equivale a un expediente inmutable implementado. |

M2 debe poder reflejar que la evaluación de M3 está pendiente, sin presentar una
base como aprobada. La creación de documentos pertenece al Módulo 4; su referencia
en el RAT no implica implementar generación documental en M2.

## Modelo conceptual objetivo

Los nombres siguientes expresan responsabilidades y cardinalidades; no fijan aún
nombres de tablas, columnas ni contratos API.

| Relación / entidad | Cardinalidad y contenido |
|---|---|
| Organización → actividad (`Treatment`) | 1:N; actividad con nombre, descripción, área y rol de la organización. |
| Actividad → finalidades | Una actividad admite múltiples finalidades. |
| Actividad ↔ categoría de datos | N:M con catálogo estructurado; sensibilidad derivada del catálogo. |
| Actividad ↔ categoría de titulares | N:M; múltiples categorías por actividad. |
| Actividad ↔ sistema (`System`) | N:M mediante asociación explícita. |
| Actividad ↔ tercero (`Vendor`) | N:M mediante asociación que contiene el rol del tercero en esa actividad. |
| Relación con encargado → alcance del encargo | Objeto, duración, finalidad, datos/titulares involucrados, contrato y subencargados. |
| Actividad → transferencia internacional | 1:N; cada transferencia identifica receptor, país, mecanismo y garantías. |
| Actividad → evaluaciones M3 | Referencias a base, justificación, aprobación y evaluaciones; detalle de cardinalidad en M2-T1/M3. |
| Actividad / relaciones → referencias de evidencia M5 | Vinculación trazable con soportes y eventos; contrato técnico pendiente. |

El modelo actual conserva `purpose` como texto, categorías como arrays y banderas
de sensibilidad/internacionalidad. No representa todavía las asociaciones N:M
ni las transferencias explícitas del objetivo. `LegalBase` ya existe como
scaffolding de M3; su rediseño debe respetar la frontera definida arriba.

## Criterios de cierre y continuidad

- [x] Alcance conceptual del RAT registrado y separado de implementación.
- [x] Matriz resumida con distinción entre fundamento y decisión de producto.
- [x] Rediseño de entidades, multiplicidades y banderas identificado.
- [x] Fronteras M2/M3/M5 y modelo conceptual documentados.
- [x] Roadmap, checkpoint y riesgos documentales sincronizados.
- [x] **M2-T1 — Persistencia RAT: DONE (2026-09-15).** El diseño conceptual
  se tradujo a persistencia normalizada, relaciones tenant-aware, auditoría,
  RLS y estrategia de transición compatible con el scaffolding existente.
  La migración `0010_modulo2_rat_persistencia.py` fue validada con
  upgrade → downgrade → re-upgrade y quedó en `e3f4a5b6c7d8 (head)`.

## Implementación técnica M2-T1 — 2026-09-15

M2-T1 materializa la persistencia del RAT sin implementar todavía endpoints,
servicios de negocio ni frontend.

Cambios principales:

- `Treatment` permanece como raíz de la actividad de tratamiento y se amplía
  con descripción, rol de la organización, área, flujo, revisión, estado,
  conservación y decisiones automatizadas.
- Se conservan temporalmente los campos legacy (`purpose`, arrays de categorías
  y titulares, `has_sensitive`, `retention`, `is_international`) para una
  transición compatible; dejan de ser el modelo objetivo.
- Se incorporan `treatment_purposes`, `treatment_data_categories`,
  `treatment_data_subjects` y `treatment_data_sources`.
- Se implementan relaciones N:M explícitas `treatment_systems` y
  `treatment_vendors`.
- `international_transfers` representa transferencias internacionales como
  entidad propia, separada del rol contractual de un tercero.
- `System` y `Vendor` reciben auditoría completa; el rol de `Vendor` y sus
  banderas legacy se preservan sólo por compatibilidad transitoria.
- Las entidades raíz utilizan `UNIQUE(id, organization_id)` y las relaciones
  usan claves foráneas compuestas para impedir vínculos entre objetos de tenants
  distintos incluso cuando un usuario pertenece a ambas organizaciones.
- Las tablas nuevas usan el patrón RLS existente basado en `auth_org_ids()`.
- `LegalBase` conserva su semántica de M3; M2-T1 sólo refuerza la coherencia
  tenant-aware del vínculo con `Treatment`.

Validación ejecutada:

- migración `0010`: upgrade PASS;
- downgrade `0010 → 0009`: PASS;
- re-upgrade `0009 → 0010`: PASS;
- metadata SQLAlchemy: PASS;
- tests específicos RAT/RLS/integridad: **7 passed**;
- suite backend completa: **136 passed**;
- `ruff`: PASS;
- `black --check`: PASS;
- `git diff --check`: PASS.

M2-T1 no convierte todavía M2 en un módulo funcional para el usuario. La
persistencia queda preparada para la siguiente tarea de servicio/API y para el
gate de suscripción definido para M2+.

Seguimiento: [roadmap](modules-roadmap.md), [estado](status.md) y
[riesgos y asuntos abiertos](risks-open-items.md).
