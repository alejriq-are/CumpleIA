# Paso 2: revisión guiada del alcance mixto del RAT

## Estado vigente

Implementación local de NAV-UX-005 en `feature/alcance-mixto-guiado`, base `8d2cc889a6263dcd8ff449824d9089331e0bd718`. Validación asistida aceptada por el usuario y commit/push autorizados. Sin merge ni despliegue. Confirmación y activación EIPD siguen bloqueadas. Solo datos ficticios.

## Qué cambia

Desde Determinar aplicabilidad, el acceso **Revisar o actualizar alcance del RAT asociado** permite revisar el mismo tratamiento cuando incluye adultos y menores, sin obligar a elegir el ejemplo de otro tratamiento. Desde Alcance se puede abrir Titulares y edades, Categorías o Finalidades del RAT y regresar mediante **Volver a revisar alcance de la misma evaluación**.

Guardar el RAT no adopta automáticamente ese cambio en esta evaluación. Se consulta el RAT actual, se seleccionan titulares/categorías y se compara el alcance guardado con el propuesto. Solo **Actualizar alcance de esta evaluación**, con motivo y declaración de revisión ficticia, adopta la propuesta. Conserva el identificador, finalidad de la serie y número de versión de la evaluación. Agrega una revisión de alcance con antes/después, motivo, fecha y autor; no crea otra evaluación ni una versión documental.

Las edades se describen en las notas de los titulares del RAT, junto a sus indicadores de infancia/adolescencia; este paso no introduce un catálogo nuevo de edades. Si cambia la finalidad sustancial del trabajo, debe evaluarse otra finalidad/evaluación mediante el circuito existente: no se crea ni copia automáticamente.

## Determinaciones y documentos

Al cambiar el alcance, la determinación anterior se conserva como antecedente y deja de ser actual. Hay que revisar y guardar de nuevo EIPD e infancia por separado. Incorporar menores no determina por sí solo una EIPD. Ambos accesos pueden coexistir si cada conclusión guardada corresponde y tiene fundamento.

El nuevo circuito no modifica ni vuelve a vincular documentos EIPD, documentos de infancia, LIA, fundamentos previos, anexos, versiones documentales ni revisiones históricas. Los borradores abiertos permanecen en esta pestaña durante la visita; recargar puede perder los cambios sin guardar. Conservar evidencia no equivale a acreditar que está revisada para el nuevo alcance.

## Contrato técnico

- `POST /licitud/treatments/{tid}/assessments/{aid}/scope-review/preview`: comparación sin escritura; devuelve huella y antecedentes de revisiones de alcance.
- `POST /licitud/treatments/{tid}/assessments/{aid}/scope-review`: aplica con huella vigente, UUID idempotente, motivo y `data_kind=ficticios`.
- Permisos y suscripción se validan en servidor; lectura permitida a roles de consulta, escritura solo a roles autorizados y evaluación borrador. Organización y tratamiento se comprueban; RLS sigue como segunda barrera.
- Si cambió el RAT después de comparar, se rechaza la propuesta; se debe comparar nuevamente. Dos adopciones concurrentes de la misma comparación no generan dos revisiones.
- Migración append-only `a84f6e2c9103`, posterior a `f6a24c8e9102`: amplía las restricciones de `assessment_support_records` para antecedentes de alcance. Conserva RLS e inmutabilidad existentes. Aplicada en la base aislada y en la base local de desarrollo verificada.

### Límite de compatibilidad pendiente

La ruta histórica PATCH de evaluación recompone el contexto RAT al guardar según su contrato previo. Este paso agrega un circuito explícito con auditoría propia; no sustituye todavía todos los caminos históricos de actualización ni garantiza auditoría de alcance en ellos. Unificar ese contrato requiere una tarea separada con sus regresiones. No declarar una auditoría completa del expediente.

## Evidencia técnica

- Suite aislada EIPD: **1.148 pruebas aprobadas** en la ejecución integral que incluía los primeros tres casos nuevos.
- Después de ampliar cobertura: **9 pruebas aprobadas** entre revisión de alcance (7) y API de anexos (2). Incluye alcance adultos/menores, idempotencia, concurrencia, comparación desactualizada, permisos/RLS, inmutabilidad, conservación de versiones/revisiones y conservación de metadatos y bytes de anexos. Hay solapamiento con la suite anterior; no sumar como pruebas distintas.
- Navegación conectada Chromium: **135 pruebas aprobadas**, con respuestas controladas y componentes/estilos de la aplicación. Incluye ida/retorno al RAT, conservación de borradores, comparación y rechazo recuperable. No es una sesión de navegador contra API real.
- Tipos, lint y formato comprobados sobre los cambios. La aceptación asistida y la lectura manual con tecnología de asistencia no se atribuyen a estas pruebas.

## Checklist para validar juntos

Usar `/dashboard/trabajo`, no `/dashboard/maqueta`. Mantener la pestaña anterior si contiene pendientes; abrir una pestaña nueva para cargar la implementación actual.

- [x] En una evaluación ficticia de clientes adultos, escribir una nota pendiente EIPD y volver a Determinar aplicabilidad. Abrir el nuevo acceso de revisión de alcance; verificar misma organización, tratamiento, finalidad y evaluación.
- [x] Abrir Titulares y edades del RAT; conservar adultos e incorporar los titulares menores que correspondan, indicando edades ficticias en notas. Guardar esa sección y usar el botón de regreso a la misma evaluación.
- [x] Consultar RAT actual, seleccionar titulares/categorías y comparar. Verificar que la consulta no haya guardado el alcance. Revisar ambos contenidos y aplicar con motivo y declaración ficticia.
- [x] Volver a Determinar aplicabilidad: comprobar que la conclusión anterior exige revisión. Guardar EIPD e infancia de manera independiente con sus fundamentos. Verificar ambos accesos cuando corresponden.
- [x] Volver al borrador EIPD: la nota pendiente continúa. Consultar los documentos/versiones/anexos previos y la revisión de alcance sin modificar originales.
- [x] Probar comparación y regreso en ventana estrecha; teclado/foco y cierre del panel. Registrar navegador, ancho, contexto y resultado.
- [x] Aceptación y hallazgos registrados; el usuario autoriza commit/push de este paso.

## Ajuste surgido en validación asistida

El usuario confirmó los accesos y retorno al RAT. Detectó que el campo de notas perdía su identificación al contener texto y que el resumen usaba otro nombre. Se unificó «Notas sobre los titulares y edades (opcional)», con etiqueta visible y ayuda asociada en titulares estándar y personalizados. El resumen separa el grupo, sus indicadores y sus notas. Se aclara que las edades escritas no cambian las casillas y cómo distinguir «Hijos de clientes» mediante una categoría adicional. No se reclasifican ni modifican automáticamente los datos ingresados. Revisión visual asistida del ajuste aceptada por el usuario.

Segunda observación asistida: la comparación dependía del orden de claves JSON/JSONB. La presentación de ambas columnas ahora usa un orden fijo de campos y ordena categorías por código, sin mutar el contenido ni las huellas guardadas. Se identifican Grupo vulnerable y las notas de titulares. La prueba de navegador invierte deliberadamente las claves del alcance previo y verifica la misma secuencia de rótulos en ambas columnas.

## Cierre asistido

El usuario confirmó todos los recorridos anteriores. Además reportó OK en retirada/restauración de aplicabilidad, cambio del RAT entre comparación y adopción, error de conexión con reintento conservando campos y consulta en otra pestaña con alcance del servidor y motivo pendiente independiente. Aceptó las etiquetas visibles y el orden uniforme de comparación. Autorizó commit y push; no merge ni despliegue. Los controles de permisos/RLS/concurrencia y anexos se sustentan en pruebas técnicas; no se atribuyen al usuario pruebas manuales no reportadas.

NAV-UX-005 queda aceptado para el nuevo circuito guiado conectado. Sigue pendiente unificar el camino PATCH histórico con la auditoría de alcance, según el límite descrito arriba; la aceptación no cierra esa compatibilidad ni certifica cumplimiento jurídico.

Verificación final previa al commit (31/10/2026): repetidas las 135 pruebas de navegación tras los ajustes de etiquetas y orden de comparación, todas aprobadas. Tipos, ESLint, Prettier y comprobación de espacios del diff aprobados.
