# Navegación conectada al servidor

Fecha: 25/10/2026. Base: 6612076. Rama: feature/navegacion-servidor.

Solicitud: adoptar la navegación de la maqueta aceptada en los módulos conectados.
Reutilizar formularios RAT, Autodiagnóstico (catálogo completo del servidor),
licitud, infancia, riesgos/anexos y organización, sin reemplazarlos por ejemplos.
Contexto explícito autorizado: organización, tratamiento, finalidad y evaluación.
Conservar borradores durante la visita por contexto; recuperar guardados desde API
al recargar. No sincronizar la selección de contexto entre ventanas. No guardar
contenido sensible en localStorage/sessionStorage. Conflictos no sobrescriben historial.

Aplicabilidad documental independiente y persistente por evaluación, con fundamento,
autoría y revisiones append-only; no es un clasificador jurídico ni autorización.
Al cambiar el contexto RAT asociado exigir revisión de la determinación anterior.
Conservar consultas de documentos anteriores y controles de servidor existentes.
No habilitar confirmación/activación EIPD; solo pruebas ficticias, sin merge/despliegue.

Aceptación: navegación escritorio/móvil/teclado, aislamiento entre contextos,
retorno con borradores, carga/errores/permisos, guardado y reapertura, aplicabilidad
condicional conservando antecedentes, 50 preguntas originales, anexos/resoluciones
con contratos actuales. Pruebas asistidas de documentos/historial/descargas diferidas
por usuario hasta integración. Las capacidades faltantes no se simulan como guardadas.


## Resultado implementado — 25/10/2026

- `/dashboard` y `/dashboard/trabajo` presentan el espacio conectado autenticado.
  Las rutas anteriores de Autodiagnóstico, RAT, creación y licitud redirigen al
  contexto correspondiente; la creación de organización sin membresías y el acceso
  administrativo especial anterior se conservan. Sin ampliación de permisos.
- Menú principal, Secciones junto a Menú, paneles laterales con Escape/clic exterior,
  foco confinado y retorno de foco. Opciones de escritorio por tarea; ubicación,
  contexto y nombres visibles. Continuar y Atrás/Adelante recuerdan rutas de visita.
- Contexto seleccionado desde API: membresía autorizada, tratamiento y serie de
  finalidad con sus versiones. El listado expone `series_id` estable; no se deduce
  identidad desde textos ni se crean evaluaciones al cambiar una selección.
- El selector espera validación antes de aplicar. Cancelar o navegar invalida
  respuestas atrasadas. Las respuestas de aplicabilidad se comprueban por tenant,
  tratamiento, evaluación, revisión y bloqueos; no se usan respuestas cacheadas.
- Formularios reales montados por contexto conservan borradores durante la visita.
  Recargar recupera lo guardado en el servidor, no ediciones pendientes. Hay aviso
  de cambios pendientes y confirmación para cerrar sesión o salir hacia la maqueta.
- Autodiagnóstico reutiliza las 50 preguntas/10 secciones del catálogo real y sus
  respuestas API, no los campos ilustrativos. Pertenece a la organización, no a una
  evaluación de licitud. RAT y organización reutilizan sus editores existentes.
- Bases de licitud reutiliza AssessmentFlow: base/LIA, documento EIPD de siete pasos,
  valoración, anexos, infancia, preparación, consulta y revisiones/historial actuales.
  Las brechas de formularios completos de consentimiento/LIA siguen en LIC-FORM-001.
- Determinar aplicabilidad guarda decisiones independientes, fundamento y autoría
  con revisiones append-only en el soporte documental existente. EIPD e infancia
  no se habilitan por seleccionar un valor sin guardar. Negativas y pendientes
  conservan los documentos anteriores consultables; los editores se ocultan.
- GET/POST `.../assessments/{assessment_id}/applicability`: mismos permisos,
  suscripción, tenant y rol runtime que soporte documental. Solo pruebas ficticias.
  Control de revisión esperada, hash del contexto guardado, request_id idempotente
  y bloqueo por serie. Un conflicto conserva el formulario y permite actualizar el
  estado guardado sin descartar el borrador. No modifica la evaluación ni sus hashes.
- La asociación se revisa al cambiar el snapshot RAT de la evaluación. Editar el
  RAT en vivo no sustituye automáticamente ese snapshot ni es una decisión legal.
  La actualización guiada de alcance mixto continúa como NAV-UX-005; no se afirma
  implementado el flujo completo por este cambio de navegación.

## Persistencia y operación local

Migración append-only f6a24c8e9102 sobre e67a4b829c10: extiende los tipos permitidos
por las restricciones de `assessment_support_records` para determinaciones sin
contenido binario. Conserva políticas RLS, FK compuesta, roles y privilegios de solo
SELECT/INSERT; no permite UPDATE/DELETE ni borra historial. Aplicada primero en la
base aislada y después en desarrollo local `cumpleia`, comprobando mismo número de
evaluaciones y registros documentales antes/después. No se insertaron fixtures en
la base de desarrollo. No hay servicios, dependencias o credenciales nuevas.

Backend local health 200 y rutas GET/POST presentes en OpenAPI. Login 200;
/dashboard, /dashboard/trabajo, /dashboard/rat y maqueta sin sesión redirigen a
/login (307). La sesión personal no se inspeccionó ni se utilizó para las pruebas.
Las ventanas conservan selección de contexto independiente; no hay sincronización
en tiempo real de formularios abiertos. Actualizar estado o recargar consulta el
servidor, con control de concurrencia para las determinaciones. Confirmación y
activación EIPD permanecen bloqueadas. Sin merge ni despliegue remoto.

## Evidencia

- 1.145 pruebas del runner EIPD aprobadas en base aislada.
- 194 pruebas de las APIs de licitud/Autodiagnóstico aprobadas, incluido catálogo
  real de 50 preguntas y 10 secciones. No se suman a las anteriores como cobertura
  única; son ejecuciones de conjuntos declarados.
- 55 pruebas de interfaz y regresión aprobadas; una captura opcional omitida en
  esa corrida (maqueta/licitud/primeras seis conectadas).
- Batería conectada ampliada: 10 Chromium, tipos y ESLint aprobados.
- Recorrido Chromium → API real → PostgreSQL aislado aprobado: guardar ambas
  determinaciones y fundamento, recargar, recuperar contexto/datos y abrir infancia.
  Autenticación sintética de fixture; no login personal ni autorización jurídica.
- Compilación de producción en copia temporal con configuración ficticia aprobada.
  Capturas escritorio/móvil revisadas en outputs/navegacion-servidor; sin sobreescribir
  evidencia de la maqueta. Pruebas conectadas incorporadas a CI, ejecución remota pendiente.

## Prueba asistida siguiente

1. Abrir `/dashboard` con la sesión habitual. Verificar aviso Espacio conectado.
2. Cambiar contexto: organización → RAT → finalidad → evaluación existente. Si aún
   no existe evaluación, usar Bases de licitud → Preparar → Evaluaciones y creación
   de borrador; requiere permisos y datos ficticios.
3. Determinar aplicabilidad, guardar y comprobar los accesos correspondientes.
4. Editar/guardar, cambiar módulo y recargar para verificar persistencia real.
5. Probar los recorridos diferidos por usuario: documentos guardados, anexos,
   resoluciones, historial y descargas, en cada contexto y con los roles permitidos.

La aceptación previa corresponde a la maqueta. La aceptación asistida del espacio
conectado y de los recorridos diferidos sigue pendiente. Publicación de esta rama autorizada por el usuario al pausar el 25/10; verificar
HEAD remoto y CI al retomar. 6612076 ya publicó resultados aceptados de la maqueta.

## Checklist para reanudar

Pausa solicitada el 25/10/2026 por unas horas. No hay trabajo funcional programado.
Commit/push autorizado de integración y registro; sin merge ni despliegue remoto.

1. [ ] Comprobar rama `feature/navegacion-servidor`, HEAD/estado local/remoto y CI
   exacta del commit. Si los servicios locales no están disponibles, iniciarlos con
   su configuración existente; no crear credenciales ni cambiar permisos.
2. [ ] Abrir `/dashboard/trabajo` con sesión habitual. Elegir organización → RAT →
   finalidad/serie → evaluación existente y confirmar identidad/versión. No crear
   duplicados ni asumir que dos ventanas deban compartir su selección.
3. [ ] Verificar las 50 preguntas/10 secciones del Autodiagnóstico organizacional,
   retorno con borrador y lectura del guardado. Distinguirlo de licitud por evaluación.
4. [ ] Guardar aplicabilidad EIPD/infancia con fundamentos, comprobar menús condicionales,
   retorno entre módulos y recuperación tras recarga de valores guardados. Antes de
   recargar, guardar o descartar conscientemente los cambios pendientes.
5. [ ] Consultar documentos guardados, base/LIA y EIPD en la evaluación correcta;
   distinguir borrador, guardado y revisión histórica. No sustituir el snapshot RAT
   implícitamente ni dar por resueltos los formularios LIC-FORM-001.
6. [ ] Anexos: PDF/TXT ficticio válido, rechazo CSV/vacío/tamaño, conservación de campos,
   vínculos opcionales R/M, versiones y descarga íntegra de la versión seleccionada.
   Registrar si persiste LIC-UX-014; no declarar corregido por pruebas de maqueta.
7. [ ] Infancia cuando corresponda: preparar resolución, cancelar copia/vista previa
   conservando borrador; registrar solo prueba deliberada, consultar originales y
   sucesor sin heredar revisión/decisión. Comprobar contexto antes de cada registro.
8. [ ] Revisiones, decisiones y facultades: historial consultable y permisos vigentes;
   revocación bloquea nuevas decisiones sin borrar antecedentes. No conceder facultades
   solo para probar navegación ni activar EIPD.
9. [ ] Historial/descargas: identidad, versión, contenido y asociaciones correctas;
   separación entre evaluaciones y organizaciones; bloqueos conservados. Contrastar
   archivos con lo guardado, no con cambios pendientes del formulario.
10. [ ] Escritorio/móvil/teclado: Menú y Secciones accesibles al bajar, Escape/Cerrar
    y clic en fondo sombreado cierran panel y devuelven foco; selección abre área de
    trabajo sin desborde. Atrás/Adelante, cambio de contexto y salida con borrador.
11. [ ] Registrar resultado por paso (OK, fallo o no probado), contexto ficticio y
    evidencia; actualizar checklist y backlog. Cerrar solo criterios efectivamente
    verificados. Resolver hallazgos acotados antes de nueva publicación autorizada.

Referencias: [maqueta aceptada](maqueta-navegacion-integral.md),
[recorrido histórico de licitud](m3-t1-checklist-recorrido-licitud.md),
[backlog](../backlog.md). NAV-UX-005 y LIC-FORM-001 siguen pendientes; no abordar
nuevas funciones por el solo hecho de reanudar estas pruebas.
