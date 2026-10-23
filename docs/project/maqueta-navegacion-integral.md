# Maqueta integral de navegación de CumpleIA

## Objetivo y estado

NAV-UX-001 / LIC-UX-015. Usuario solicita incorporar el Panel principal al rediseño
para que la navegación sea homogénea y preparar la maqueta completa antes de sus
pruebas asistidas. Ruta local: `/dashboard/maqueta`, dentro del dashboard protegido.
Accesos visibles desde Panel principal y Bases de licitud; la maqueta V3 previa
conserva su ruta y ofrece enlace a la propuesta integral.

Estado: implementada como demostración aislada; validación dirigida y visual local
realizada. Prueba asistida y aceptación del diseño por el usuario pendientes.
No sustituye los recorridos conectados ni implementa sus cambios pendientes.

## Estructura común aprobada a partir del bosquejo del usuario

El usuario revisó la primera maqueta y señaló que aún costaba encontrar opciones.
Aportó un PowerPoint de cuatro pantallas con menú principal izquierdo y opciones
propias de cada módulo arriba. Aceptó las recomendaciones y pidió preparar esta
segunda versión para probarla. Aceptación de la propuesta no equivale a aceptación
de la implementación ni adopción en el producto conectado.

1. Menú principal fijo a la izquierda en escritorio: Inicio / Panel principal,
   Autodiagnóstico, Inventario de tratamientos, Bases de licitud, Documentos,
   Carpeta de evidencia y Mi organización. Iconos, nombres y selección naranja
   con borde e indicador accesible. En móvil usa un botón Abrir menú.
2. Barra superior específica de cada módulo. Se elimina la capa transversal de
   cuatro tareas y el segundo menú lateral de pasos. El estado interno de tarea
   se conserva únicamente para reutilizar formularios y consultas de la maqueta.
3. RAT: Catálogo con dos tratamientos ficticios, Actividad de tratamiento con cuatro
   secciones, Documentos y revisiones e Historial y descargas.
4. Bases de licitud: Alcance RAT, Base y fundamento, Infancia cuando corresponde,
   Documentar EIPD, Anexos, Resoluciones y revisiones cuando corresponde,
   Documentos guardados e Historial y descargas. EIPD abre cinco accesos:
   Tratamiento y alcance, Necesidad y proporcionalidad, Valorar riesgos,
   Valorar medidas y Fuentes y evidencias. Preparar resolución documental es
   el primer acceso de Resoluciones y revisiones, con referencia, notas y motivo.
5. Los submenús se abren por clic, no por pasar el puntero. Permanecen abiertos
   hasta elegir, pulsar Escape, clicar fuera o cambiar tamaño de pantalla.
   Teclado: Tab/Enter, flechas, Inicio/Fin y Escape con foco al control de apertura.
   Posición horizontal ajustada al espacio de pantalla. Móvil despliega opciones
   dentro de una lista con desplazamiento propio, sin tapar toda la pantalla.
6. Formularios largos en el área central. Cabecera con organización, escenario y
   evaluación, más tratamiento/finalidad y ruta de la sección. Menús y contexto
   compacto persistentes en escritorio; móvil evita una cabecera fija demasiado alta.
   Navegar lleva el foco al contenido y conserva los cambios de la visita.
7. Ventanas breves para detalles, copia, vista previa y confirmación. Se conserva
   la separación entre consultar, guardar, revisar y decidir por la organización.

## Qué se puede probar

- Panel con seis tarjetas de módulo y acceso a continuar la evaluación.
- Diagnóstico: menú de diez secciones ilustrativas, guardado y resultados de ejemplo.
  La primera contiene una pregunta; las otras nueve prueban ubicación y navegación,
  sin reproducir el cuestionario completo ni su puntuación.
- RAT: alcance, fuentes/sistemas, conservación/eliminación, terceros/transferencias.
- Licitud: alcance consultable, base/fundamento, infancia condicional, EIPD,
  riesgos, medidas, anexos y preparación de resolución de infancia.
- Consultas dentro de Bases de licitud: campos guardados, paneles de evidencia y vínculos de riesgos.
- Documentos y Carpeta de evidencias: accesos visibles con «Próximamente», deshabilitados
  en menú principal y tarjetas del Panel. No representan módulos disponibles.
- Mi organización: abre directamente nombre, RUT, rubro/industria y tamaño, con los
  valores de demostración de la captura aportada (CumpleIA Demo, 1111111-0, Consultoría,
  Pequeña empresa PYME). Guardado solo en memoria; los mismos datos se mantienen
  al alternar escenarios. Facultades siguen consultables dentro del recorrido de infancia.
- Historial y descargas: versiones de infancia, actividad de la visita y JSON de ejemplo.

### Estado y conservación

Dos escenarios separados: Clientes adultos y Programa con menores de 10 a 13 años.
Borradores y guardados se mantienen en memoria React mientras no se recargue;
cambiar tarea/módulo/escenario no borra los textos. Los pasos con nuevas ediciones
muestran Cambios sin guardar aunque antes se hayan guardado. La consulta y el JSON
usan valores guardados; no incorporan los cambios pendientes.
No localStorage/sessionStorage, peticiones API, DB ni almacenamiento de archivos.
La ruta mantiene la autenticación existente del dashboard; el componente de maqueta
no obtiene ni utiliza tokens. Datos ficticios propios, no una copia de los expedientes
del usuario. Reiniciar solicita confirmación y recargar restaura todos los ejemplos.

### Revisiones y copias

Infancia permite consultar versiones 1/2, revisión documental separada de decisión
organizacional y facultad revocada. Copiar siempre pide confirmación, preserva el
original y abre preparación temporal con origen. Conservar no reemplaza el formulario.
Vista previa requiere referencia SIMULADA-, notas, motivo y declaración ficticia;
registro simulado exige otra confirmación. Una versión nueva no hereda revisiones
ni decisiones anteriores. No se concede facultad ni se habilita operación real.

### Límites de la simulación

- Campos de ejemplo representan las ubicaciones y jerarquía; no todos los contratos
  jurídicos completos. Consentimiento y LIA muestran el acceso previsto y explican
  que LIC-FORM-001 sigue pendiente; no se da por implementado.
- El resultado de diagnóstico es ilustrativo. La tarjeta conjunta R1/M1 es un ejemplo
  de lectura fijo, identificado como independiente de la edición de probabilidad/impacto;
  no recalcula ni acredita verificación real.
- Anexos validan extensión PDF/TXT, vacío y límite 2 MiB, preservan metadatos y
  bloquean Guardar si inválidos. Solo retienen el nombre del archivo, no sus bytes;
  no realizan análisis de contenido ni reproducen validaciones completas del servidor.
- Descarga `maqueta-cumpleia-*.json`, con marca propia y can_confirm=false,
  activation=deshabilitada. No es el contrato de expediente MVP ni contiene huellas
  auditables o aceptación jurídica. Consultas y simulación no alteran el producto.
- Documentos y Carpeta de evidencias están marcados Próximamente. Las consultas y
  los anexos dentro de Bases de licitud siguen disponibles en la maqueta.

## Validación técnica local

Archivos: frontend/components/navigation/{NavigationPrototype.tsx,prototype-data.ts},
PrototypeMenus.tsx y prototype-navigation.ts;
ruta frontend/app/dashboard/maqueta/page.tsx y accesos de dashboard/licitud.
Suite: frontend/e2e/navigation-prototype.spec.ts; comando npm run test:navigation-prototype.
Incluida también en test:eipd-client para CI. Se compila el componente real con
webpack/TypeScript y Tailwind existentes; navegador con red interceptada, sin servicios
ni credenciales. No nueva dependencia. No suite backend: no cambios backend.

Pruebas dirigidas: cobertura de todos los destinos de navegación, foco, borradores,
separación de escenarios, consulta guardada, cancelación/copia/registro conservando
originales, selección de archivo inválido y corrección, Escape/retorno de foco,
descarga solo guardada, reinicio, estados de guardado y móvil 390/320 sin desborde.
Capturas adicionales para escritorio 1440 y móvil 390. Ejecución local con
MAQUETA_SCREENSHOTS produce las imágenes; sin esa variable se omite solo la captura.
La segunda versión añade pruebas de desplegables por clic/teclado, acceso directo
a preparación y tamaños 1440/1024/768/640/390/320. Resultado previo: 13 pruebas
aprobadas (12 funcionales y una de capturas). Ajuste de organización y Próximamente
validado con la suite actualizada: 14 pruebas aprobadas en 14.6 s. Tras limitar
Mi organización a sus cuatro campos, caso específico y capturas repetidos: 2 aprobados.
Captura final de organización inspeccionada visualmente; tipos/lint/formato aprobados. Tipos, ESLint y formato
comprobados. Capturas revisadas de Panel, RAT, Infancia, menús EIPD y resoluciones,
escritorio y móvil. Ajuste final de reinicio de anexos validado con el caso dirigido.
Ruta local responde 307 hacia autenticación sin sesión; no se usaron credenciales
para estas pruebas ni se extrapola CI remota.
Tipos y ESLint de archivos afectados y formato comprobados; CI remota de este
candidato debe verificarse por HEAD, no se infiere de estos resultados.

## Guion para las pruebas asistidas del diseño

1. Abrir `/dashboard/maqueta` desde el Panel actual. Confirmar que aparece
   «Menú lateral y opciones por módulo» y seleccionar Inicio / Panel principal.
2. Encontrar Inventario de tratamientos en el menú izquierdo, abrir una actividad
   desde Catálogo y localizar sus secciones en Actividad de tratamiento.
3. Abrir Autodiagnóstico, desplegar Secciones y elegir la sección 7; volver a RAT.
4. Entrar a Bases de licitud y abrir Base y fundamento directamente. Editar un texto,
   cambiar de módulo y volver: debe conservarse sin que ello implique guardado.
5. Guardar el fundamento y localizarlo en Documentos guardados. Abrir un detalle,
   cerrar con botón o Escape y comprobar el retorno de foco.
6. Abrir Documentar EIPD, elegir Valorar riesgos y después Valorar medidas.
   Comprobar que las cinco opciones se encuentran sin buscar botones al pie.
7. Cambiar a Programa con menores. Abrir Infancia; después Resoluciones y revisiones
   y Preparar resolución documental. Comprobar ubicación, título y contenido central.
8. Consultar resolución 2, probar copiar/cancelar conservando el texto temporal;
   opcionalmente completar vista previa y registro exclusivamente simulado.
9. Localizar Revisiones, Decisiones y Facultades desde el mismo menú. Verificar
   que la facultad revocada mantiene bloqueada la decisión organizacional.
10. Probar anexo CSV rechazado y sustitución por TXT; encontrar Historial y descargas.
    Repetir navegación con teclado y en móvil; recargar solo si se desea reiniciar.

Registrar dificultad para encontrar opciones, número de clics, comprensión del
contexto y diferencia entre consulta/guardar/registrar. Ajustar la maqueta antes de
trasladar el patrón al producto conectado. NAV-UX-001 y LIC-UX-015 siguen abiertos
hasta la validación asistida y la adopción correspondiente.
