# Propuesta de experiencia de licitud

Estado: propuesta aceptada por el usuario el 18/10/2026. Implementacion pendiente.
Esta entrega documenta y publica la decision de diseno; no modifica la aplicacion.
Base inspeccionada: 4cb7ae1. Alcance: navegacion y presentacion del flujo existente;
no ampliar reglas juridicas, facultades, API de aprobacion ni activacion EIPD.

## Problema observado

La prueba manual exigio instrucciones para encontrar acciones, diferenciar notas
editables de registros historicos y distinguir revision negativa de decision de
organizacion. Se completo un fundamento sobre version 2 consultando version 1.
ChildAdolescentPage apila expediente, editor e historial. ChildEipdHistory mezcla
creacion, consulta, decision de organizacion, copia sucesora y revision negativa.
OrganizationAcceptancePanel incluye facultades y decisiones dentro de la consulta.
Varios botones carecen de estilo reconocible. Guardar fundamento exige recargar
para actualizar paneles inferiores. El dossier presenta contenido JSON como vista
principal. La estructura actual obliga al usuario a conocer el modelo interno.

## Navegacion propuesta

Cabecera persistente: organizacion, tratamiento, finalidad, evaluacion y version,
estado documental y aviso de entorno de pruebas. Separar claramente version de
la evaluacion, numero de resolucion y etiqueta documental; nunca un unico numero
ambiguo. En revisiones indicar siempre documento/referencia/version objetivo.

Cuatro pestanas por intencion:

| Pestana | Contenido | Accion principal |
| --- | --- | --- |
| Resumen y siguientes pasos | Esquema, situacion por seccion, pendientes y motivos | Continuar tarea pendiente |
| Completar datos | Alcance RAT asociado, base/fundamento, LIA disponible, infancia y preparacion documental segun corresponda | Guardar borrador y continuar |
| Revisar documentos | Seleccion explicita de documento/version, lectura y formularios separados de revision y decision organizacional | Registrar revision o decision identificada |
| Historial y descargas | Versiones, revisiones, decisiones, facultades y expediente | Consultar o descargar |

Facultades: acceso secundario Gestionar facultades visible segun permisos,
fuera del formulario de revision. La persona revisora ve su estado y motivo de
bloqueo; la administracion puede gestionar otorgamiento/revocacion. Mantener
lecturas historicas disponibles segun permisos actuales.

## Esquema de trabajo

```mermaid
flowchart TD
    A[Revisar alcance RAT] --> B[Completar evaluacion]
    B --> C[Preparar documento cuando corresponda]
    C --> D[Seleccionar version y revisar]
    D --> E[Consultar resultado, historial y descargas]
    D -->|Requiere cambios| B
```

El retorno al editor conserva el historial; un documento registrado se corrige
preparando otra version. La revision y la decision organizacional tienen facultades
y contratos propios; este esquema no impone una secuencia juridica universal.

Revisar alcance RAT -> Completar evaluacion -> Preparar documento/version cuando
corresponda -> Revisar version seleccionada -> Registrar revision/decision segun
facultad -> Consultar historial/exportar. Requiere cambios vuelve a preparar
borrador o nueva version; no modifica el registro historico. No continuar mantiene
el resultado visible sin ofrecer activacion. Los pasos documentales no equivalen
a autorizacion juridica y no todos aplican a todas las evaluaciones.

Resumen ofrece siguiente accion contextual, no un porcentaje general de cumplimiento.
Ejemplos: completar fuente, guardar cambios, seleccionar version, revisar documento
o facultad revocada. Estado separado: sin iniciar, borrador guardado, cambios sin
guardar, pendiente de revision, requiere cambios, no continuar y solo consulta.
No mostrar revisado/aprobado por el mero guardado, ni inferir una EIPD obligatoria
solo por nombre de tratamiento o seleccion de infancia. Usar contrato/diagnostico
servidor y explicar cuando no permite determinar el siguiente paso.

## Completar datos

Secciones cortas con indice propio: alcance, base/fundamento, analisis disponibles,
infancia cuando corresponda, documento EIPD cuando proceda. Por seccion indicar
objetivo, quien completa, campos requeridos para guardar y pendientes documentales.
Mostrar resumen RAT en lectura y enlace para editarlo; advertir diferencias con
el snapshot asociado sin sobrescribirlo. No presentar nueve campos LIA como un
cuestionario juridico completo. Distinguir borrador editable y version registrada.
Guardar borrador y continuar solo avanza tras respuesta confirmada; guardar no
registra automaticamente resolucion, revision ni decision inmutable.

## Revisar documentos

Lista de versiones con referencia y estado, seleccion visible y lectura resumida
antes del formulario. Dos acciones identificadas: Revision del documento (contrato
actual solo requiere cambios/no continuar) y Decision documental de organizacion
(con facultad vigente). No son pasos obligatoriamente consecutivos ni equivalentes.
Mostrar fecha, alcance y version objetivo junto al boton final; confirmar objetivo
al registrar un evento inmutable. Crear nueva version desde esta seccion conduce
al editor, informa origen y no guarda automaticamente.

Cada bloqueo explica su causa junto al control: falta declaracion ficticia,
facultad revocada, solo lectura, material cambiado, resultado incierto o escritura
de pruebas deshabilitada. Distinguir permiso de editar, revisar y decidir. No
preseleccionar una decision favorable. No ocultar el historial al revocar facultad.

## Presentacion y estados

Botones primarios visibles, secundarios con borde y enlaces solo para navegacion.
Etiquetas junto a controles, ayudas cortas, campos condicionales justificados,
resumen legible antes de detalles tecnicos/JSON. Aviso global persistente de pruebas
y avisos especificos en acciones, evitando repetir parrafos identicos por panel.
Fechas locales legibles con UTC accesible en detalle; hashes en detalle tecnico.

Datos cargados del servidor indican borrador guardado; editar marca cambios sin
guardar. Al cambiar pestana o version, preservar borrador o permitir guardar/seguir
editando/descartar explicitamente. Nunca perder datos por desmontar componentes.
Tras guardar, refrescar datos y diagnosticos dependientes automaticamente; impedir
operaciones contra material obsoleto y no mostrar exito ante respuesta incierta.
Navegacion por teclado, foco visible, roles de pestanas, enlaces directos que
conserven organizacion/evaluacion/version y vista movil sin formularios comprimidos.

## Implementacion propuesta y verificacion

Un bloque coherente de experiencia: estructura de cuatro pestanas y esquema,
separacion de editor/consulta/revision/facultades, contexto de version compartido,
estados de guardado/bloqueo y refresco de dependencias. Reutilizar servicios y
contratos existentes; no cambiar politicas ni migrar historiales. Separar el criterio
de completitud de fuentes como tarea de validacion con contrato propio.

Antes de implementar: maqueta navegable con escenarios adulto, infancia y facultad
revocada para comprobar nombres y transiciones. Luego implementacion y pruebas
centradas en riesgos: cambios entre pestanas sin perdida, version objetivo exacta,
roles y revocacion, contexto actualizado tras guardar, respuestas inciertas,
conservacion de historial y lectura/exportacion con escrituras deshabilitadas.
Validacion asistida: usuario identifica sin ayuda donde completar, donde revisar,
que version revisa, por que una accion esta bloqueada y que sigue. EIPD y datos
reales bloqueados antes y despues. No ampliar alcance a habilitar aprobaciones.

## Aceptacion y siguiente entrega

El usuario acepta la propuesta y autoriza su documentacion, commit y push.
Proximo entregable: maqueta navegable de las cuatro pestanas con los escenarios
adultos, infancia y facultad revocada; validar claridad de nombres, version objetivo
y siguiente accion antes de modificar los formularios existentes. La maqueta debe
identificar los datos simulados y no registrar eventos ni cambiar configuraciones.
La implementacion y sus pruebas se ejecutaran como bloque posterior; no se marcan
como realizadas por aprobar o publicar este documento.

Criterios de aceptacion del bloque de experiencia:

- Identificar donde completar, revisar y consultar historial sin instrucciones externas.
- Mostrar siempre documento y version objetivo junto a una revision o decision.
- Conservar cambios al navegar y distinguir guardado confirmado, cambios pendientes
  y resultado incierto; sin recarga manual obligatoria tras guardar.
- Explicar el motivo de cada bloqueo y mantener consulta historica tras revocacion.
- Mostrar pasos aplicables y siguiente accion sin equivaler avance a aprobacion juridica.
- Mantener permisos de servidor, aislamiento, registros inmutables y bloqueos EIPD/datos reales.
- Verificar teclado, foco, pantallas pequenas y los tres escenarios con el usuario.

Backlog de referencia: LIC-UX-004 integra esta reorganizacion y recoge LIC-UX-002,
LIC-UX-003 y el patron de guardado RAT-UX-001 cuando corresponda. RAT-VAL-001
mantiene su propio contrato de completitud; no se considera resuelto por el rediseno.
