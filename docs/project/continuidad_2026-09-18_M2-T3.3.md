# Continuidad M2-T3.3 — 18 septiembre 2026

## Estado de la jornada

M2-T3.3 quedó parcialmente implementado.

La ficha RAT mantiene la arquitectura incremental existente, sin realizar todavía
una refactorización mayor a un workspace general.

## Implementado y validado

### 1. Finalidades

Se creó:

- `frontend/components/rat/TreatmentPurposesSection.tsx`

Se amplió el cliente API con:

- `TreatmentPurposeIn`
- `TreatmentPurposeOut`
- `api.rat.replacePurposes(...)`

`TreatmentDetailOut.purposes` dejó de utilizar `unknown[]`.

La sección permite:

- agregar múltiples finalidades;
- definir una finalidad principal;
- eliminar finalidades;
- guardar explícitamente mediante PUT;
- actualizar el estado local de `TreatmentGeneralForm`.

Prueba funcional realizada con la actividad `Gestión de clientes`.

Resultado:

- guardado: PASS
- actualización inmediata del progreso: PASS
- progreso: 3/10 -> 4/10

### 2. Categorías de datos personales

Se creó el catálogo:

- `frontend/lib/rat/dataCategories.ts`

El catálogo inicial está basado en la fuente CCS del repositorio y distingue
categorías generales y categorías sensibles.

Se creó:

- `frontend/components/rat/TreatmentDataCategoriesSection.tsx`

Se amplió el cliente API con:

- `TreatmentDataCategoryIn`
- `TreatmentDataCategoryOut`
- `api.rat.replaceDataCategories(...)`

`TreatmentDetailOut.data_categories` dejó de utilizar `unknown[]`.

La sensibilidad se deriva de la categoría seleccionada y no se captura como una
segunda fuente independiente.

Prueba funcional realizada con la actividad `Gestión de clientes`.

Resultado:

- selección múltiple: PASS
- guardado: PASS
- persistencia: PASS
- actualización inmediata del progreso: PASS
- progreso: 4/10 -> 5/10

### 3. Validación técnica

Durante la implementación se ejecutó repetidamente:

`npm run type-check`

Resultado final: PASS.

## Estado actual del progreso RAT probado

La actividad de prueba `Gestión de clientes` tiene actualmente 5 de los 10
requisitos de activación satisfechos.

Los cinco requisitos actualmente satisfechos son:

1. nombre;
2. rol de la organización;
3. al menos una finalidad;
4. al menos una categoría de datos;
5. regla de conservación.

La barra muestra correctamente `5/10`.

## Próximo paso

Retomar M2-T3.3 con **Titulares de los datos**.

La próxima sección debe permitir registrar una o más categorías de titulares
mediante `TreatmentDataSubject`.

Al guardar al menos un titular, el progreso esperado será:

`5/10 -> 6/10`

Antes de implementar la UI debe revisarse el repositorio para definir las
categorías guiadas de titulares y no inventar un catálogo sin respaldo.

Después continuar con:

- Fuentes de datos -> potencial 7/10
- Declaración y sistemas -> potencial 8/10
- Declaración y proveedores/terceros -> potencial 9/10
- Transferencias internacionales -> potencial 10/10
- Revisión y activación del tratamiento

## Archivos modificados o creados durante M2-T3.3 parcial

- `frontend/lib/api/client.ts`
- `frontend/lib/rat/dataCategories.ts`
- `frontend/components/rat/TreatmentPurposesSection.tsx`
- `frontend/components/rat/TreatmentDataCategoriesSection.tsx`
- `frontend/components/rat/TreatmentGeneralForm.tsx`

## Nota de entorno

Durante la jornada también se corrigió el comportamiento de Ctrl+C en la
terminal integrada de VS Code.

Configuración final:

- Ctrl+C: copiar en terminal.
- Ctrl+Shift+C: enviar interrupción (^C).

Esto quedó resuelto antes de continuar M2-T3.3.

## Cierre M2-T3.3 — 21 septiembre 2026

Se retomó la implementación y se completaron las dos secciones pendientes de M2-T3.3.

### 4. Titulares de los datos

Se creó:

- `frontend/lib/rat/dataSubjects.ts`
- `frontend/components/rat/TreatmentDataSubjectsSection.tsx`

Se amplió el cliente API con:

- `TreatmentDataSubjectIn`
- `TreatmentDataSubjectOut`
- `api.rat.replaceDataSubjects(...)`

`TreatmentDetailOut.data_subjects` dejó de utilizar `unknown[]`.

La sección permite:

- seleccionar categorías guiadas de titulares;
- agregar categorías personalizadas;
- indicar inclusión de niños;
- indicar inclusión de adolescentes;
- marcar grupos vulnerables;
- registrar notas;
- guardar explícitamente mediante PUT.

Prueba funcional con `Gestión de clientes`:

- guardado: PASS
- persistencia: PASS
- actualización inmediata del progreso: PASS
- progreso: 5/10 -> 6/10

### 5. Fuentes de datos

Se creó:

- `frontend/components/rat/TreatmentDataSourcesSection.tsx`

Se amplió el cliente API con:

- `DataSourceType`
- `TreatmentDataSourceIn`
- `TreatmentDataSourceOut`
- `api.rat.replaceDataSources(...)`

`TreatmentDetailOut.data_sources` dejó de utilizar `unknown[]`.

La sección admite múltiples fuentes de los tipos:

- titular;
- tercero;
- fuente pública;
- recogida automática;
- otro.

`is_public_source` se deriva en frontend cuando `source_type` es
`fuente_publica`, manteniendo sin cambios el contrato backend actual.

Prueba funcional con `Gestión de clientes`:

- guardado: PASS
- persistencia: PASS
- actualización inmediata del progreso: PASS
- progreso: 6/10 -> 7/10

## Resultado funcional de M2-T3.3

M2-T3.3 — finalidades, categorías de datos, titulares y fuentes queda
funcionalmente completado.

Progreso RAT validado con la actividad `Gestión de clientes`:

`3/10 -> 4/10 -> 5/10 -> 6/10 -> 7/10`

Las siete condiciones actualmente satisfechas son:

1. nombre;
2. rol de la organización;
3. al menos una finalidad;
4. al menos una categoría de datos;
5. al menos una categoría de titulares;
6. al menos una fuente de datos;
7. regla de conservación.

## Siguiente paso

Continuar con M2-T3.4:

**Sistemas utilizados -> potencial 8/10**

Después:

- proveedores/terceros -> potencial 9/10;
- transferencias internacionales -> potencial 10/10;
- revisión y activación.
