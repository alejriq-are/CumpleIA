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

## Estructura común

1. Navegación superior persistente de módulos, siempre en el mismo orden: Panel principal,
   Diagnóstico, Inventario RAT, Bases de licitud, Documentos, Evidencia, Organización.
2. Cabecera con módulo, escenario ficticio, finalidad y contexto de evaluación.
3. Cuatro tareas homogéneas: Resumen, Completar datos, Documentos y revisiones,
   Historial y descargas. Panel principal usa su resumen y una ayuda de recorrido.
4. Menú lateral con pasos explícitos, selección actual, números y estado documental.
   En móvil se convierte en selector de pasos, y los módulos usan un selector compacto.
   La altura de la navegación persistente se mide para no ocultar el contenido al
   desplazar o focalizar una sección. Navegar dirige foco y desplazamiento
   al contenido, incluso al seleccionar de nuevo el mismo paso.
5. Área principal para formularios largos, con acciones cercanas al guardado y
   Anterior/Siguiente. Botones de apertura destacados y texto que indica el destino.
6. Panel lateral de detalles en escritorio, ventana ajustada a pantalla en móvil.
   Diálogos nativos modales para copia, revisión previa, registro simulado y reinicio;
   cierre por botón/Escape y retorno de foco al control que abrió la consulta.

## Qué se puede probar

- Panel con seis tarjetas de módulo y acceso a continuar la evaluación.
- Diagnóstico: respuesta de ejemplo, guardado y resultados explícitamente ilustrativos.
- RAT: alcance, fuentes/sistemas, conservación/eliminación, terceros/transferencias.
- Licitud: alcance consultable, base/fundamento, infancia condicional, EIPD,
  riesgos, medidas, anexos y preparación de resolución de infancia.
- Documentos: consulta de campos guardados, paneles de evidencia y vínculos de riesgos.
- Evidencia: localización de respaldos y acceso a añadir un anexo simulado.
- Organización: datos ficticios, equipo e historial de facultad revocada.
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
- Documentos y Evidencia incluyen pantallas conceptuales para probar homogeneidad;
  no habilitan módulos futuros en el dashboard conectado.

## Validación técnica local

Archivos: frontend/components/navigation/{NavigationPrototype.tsx,prototype-data.ts},
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
Resultado local: 10 pruebas aprobadas (9 funcionales y 1 de capturas), en 9.6 s.
Tipos y ESLint de archivos afectados y formato comprobados; CI remota de este
candidato debe verificarse por HEAD, no se infiere de estos resultados.

## Guion para las pruebas asistidas del diseño

1. Abrir desde el Panel actual → Abrir maqueta integral de CumpleIA.
2. Encontrar Inventario RAT sin instrucciones de posición; comprobar título y retorno.
3. Entrar a Bases de licitud, Completar datos y Base y fundamento; editar un texto,
   ir a otro módulo y volver. Guardar y localizarlo en Documentos y revisiones.
4. Abrir evidencia y cerrar con botón/Escape, comprobando orientación y foco.
5. Cambiar a Programa con menores y localizar Infancia y Preparar resolución en menú.
6. Consultar resolución 2, abrir copia, cancelar y comprobar texto temporal conservado;
   opcionalmente completar vista previa/registro solo simulado y revisar versiones.
7. Encontrar Decisiones y Facultades sin confundir revisión con decisión organizacional.
8. Adjuntar un CSV de ejemplo, corregir por TXT y comprobar estado de Guardar.
9. Encontrar Historial/Descargas y bajar JSON de demostración; comprobar el aviso.
10. Repetir tareas principales en móvil/zoom; reiniciar para otra visita.

Registrar dificultad para encontrar opciones, número de pasos, comprensión del
contexto y diferencia entre consulta/guardar/registrar. Ajustar la maqueta con las
observaciones y obtener aceptación antes de trasladar el patrón a la aplicación
conectada. LIC-UX-015 y LIC-UX-004 permanecen abiertos hasta esa adopción/validación.
