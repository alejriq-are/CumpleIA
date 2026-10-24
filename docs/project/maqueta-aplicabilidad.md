# Aplicabilidad de EIPD e infancia en la maqueta

Fecha: 24/10/2026. Continuación de NAV-UX-001, base 546f4bf.

## Solicitud y resultado

El usuario señala que la presencia de formularios EIPD e infancia en Preparar
sugiere que se completan siempre. Solicita determinar primero si corresponden y
mostrar después sus accesos. Implementado únicamente en /dashboard/maqueta.

Bases de licitud abre ahora Determinar aplicabilidad, también accesible desde
Preparar. Cada evaluación parte con dos determinaciones independientes pendientes.

| Estado guardado | Efecto en el menú |
|---|---|
| Pendiente de analizar | No muestra Completar para ese bloque. |
| Corresponde | Muestra Completar EIPD o Completar infancia y adolescencia. |
| No corresponde | No muestra Completar; exige fundamento. |
| Información insuficiente | No muestra Completar; exige fundamento y conserva el pendiente de análisis. |

Todo estado distinto de Pendiente requiere fundamento. Seleccionar una opción no
cambia el menú: se aplica solo después de Guardar determinación en la maqueta.
La pantalla distingue el estado guardado de los campos de edición. Ofrece accesos
directos a los bloques habilitados y orientación normativa desplegable.

## Coherencia y límites

La presencia de infancia no activa automáticamente EIPD, ni EIPD activa infancia.
No se implementa un clasificador jurídico ni una puntuación automática de riesgo.
Las dos decisiones son documentales, ficticias y separadas por evaluación.

Se comprueba coherencia con los dos alcances sintéticos: el programa con edades
10–13 no permite concluir No corresponde infancia mientras mantiene ese alcance;
el fixture de clientes adultos orienta a seleccionar el programa con menores para
probar documentación infantil. Estas comprobaciones de fixtures NO constituyen
reglas de autorización ni sustituyen el alcance estructurado del servidor.

Referencias revisadas: artículos 15 ter y 16 quáter incorporados por Ley 21.719,
texto con vigencia desde el 1/12/2026, Biblioteca del Congreso Nacional:
https://www.bcn.cl/leychile/Navegar?idNorma=1209272&idVersion=2026-12-01
No se presume publicada ni se inventa una lista orientativa de la Agencia.

## Conservación y accesos alternativos

- El mismo filtro aplica a menú, Siguiente/Anterior, Continuar, regreso al módulo,
  cambio de evaluación y enlaces/historial del navegador. Un destino no disponible
  vuelve a Determinar aplicabilidad y normaliza el fragmento de dirección.
- Cambiar la determinación no elimina borradores, guardados, archivos referenciados
  ni versiones previas. Al volver a Corresponde, reaparecen los campos con su contenido.
- Las consultas muestran las determinaciones guardadas. Los documentos EIPD/infancia
  guardados previamente siguen consultables como antecedentes, con aviso cuando
  la determinación actual no permite completar ese bloque.
- Las resoluciones históricas de infancia siguen consultables. Preparar sucesor
  exige aplicabilidad positiva de infancia; de lo contrario lleva al análisis.
- El JSON incluye el estado y fundamento actuales de ambas determinaciones, además
  de conservar los campos guardados previos. No exporta borradores como guardados.
- Confirmación y activación EIPD siguen bloqueadas. No hay cambios de servidor,
  permisos, migraciones, dependencias ni almacenamiento persistente del navegador.
- Las determinaciones actuales son campos editables de la maqueta, no actas jurídicas
  inmutables. La trazabilidad formal/versionado de decisiones pertenece a integración.

## Validación

29 pruebas Chromium aprobadas (incluidas capturas), tipos y ESLint aprobados.
Casos nuevos: pendientes sin acceso; fundamento obligatorio; cambio de menú solo
tras guardar; EIPD e infancia independientes; negativa incompatible con alcance de
10–13 bloqueada; información insuficiente conserva borrador de infancia; EIPD previa
consultable tras retirar aplicabilidad; Atrás/enlaces no eluden filtro; aislamiento
por evaluación y descarga de estado/fundamento sin habilitación jurídica.

Capturas separadas en outputs/maqueta-aplicabilidad, sin sobrescribir evidencia
anterior. Revisión asistida del usuario, CI remota y adopción conectada pendientes.

## Prueba breve del usuario

1. Bases de licitud → Preparar → Determinar aplicabilidad.
2. Cambiar EIPD a Corresponde: sin fundamento no se puede guardar; sin guardar no
   aparece Completar EIPD.
3. Añadir fundamento ficticio y guardar: aparece Completar EIPD con sus cinco pasos.
4. Seleccionar programa con menores: las determinaciones de esa evaluación siguen
   pendientes. Registrar infancia Corresponde y fundamento: aparece su acceso,
   manteniéndose EIPD pendiente hasta analizarla por separado.
5. Escribir una nota en infancia. Registrar Información insuficiente; el menú se
   oculta. Volver a Corresponde: la nota se conserva.

## Integración posterior

Adoptar el análisis de aplicabilidad con datos autorizados del servidor, referencias
normativas vigentes y revisión humana. Registrar fundamento, autoría, versión y
cambios de alcance; reexaminar determinaciones cuando cambian los antecedentes.
Separar gestión general de riesgos del expediente formal de EIPD cuando se diseñe
el producto conectado. No deducir No requerida del simple cierre del formulario o
de la ausencia de un botón. Mantener el estado pendiente visible y verificable.
