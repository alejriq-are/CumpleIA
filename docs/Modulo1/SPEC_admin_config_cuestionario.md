# Especificación funcional — Panel de administrador: configuración del cuestionario

**Módulo:** Módulo 1 (Autodiagnóstico) · **Alcance:** interno de CumpleIA (rol `superadmin`), no visible para las empresas cliente.

## Contexto

Los 50 preguntas y las 8 obligaciones del cuestionario son fijas (fuente CCS). Los pesos por sección y el nivel de riesgo por pregunta son reglas de negocio propias que conviene poder ajustar con la experiencia, sin depender de un despliegue de código. Este documento especifica las pantallas para hacerlo.

## Permisos

Solo el rol `superadmin` (equipo CumpleIA) accede. No existe ruta ni enlace visible para el rol `admin_pyme` ni `usuario`. Cada cambio queda asociado al usuario que lo hizo (`modificado_por`).

## Pantalla 1 — Pesos por sección

Lista de las 10 secciones (I-X), cada fila muestra: número y nombre de sección (solo lectura), obligación asociada (badge, solo lectura — el mapeo obligación↔sección no es editable aquí), y un campo numérico `peso_pct` editable (0-100, enteros).

Validación: el total debe sumar exactamente 100%. El indicador de suma se muestra en rojo y el botón "Guardar cambios" queda deshabilitado mientras la suma sea distinta de 100; en verde cuando cuadra. No hay guardado parcial fila por fila — se edita la tabla completa y se guarda junto.

## Pantalla 2 — Riesgo por pregunta

Las 50 preguntas agrupadas por sección (acordeón, colapsadas por defecto salvo la que se esté editando). Cada fila: texto de la pregunta (solo lectura en v1 — cambiar el texto de una pregunta CCS es una decisión de producto distinta, fuera de este panel) y un selector `riesgo` con tres valores: Alto, Medio, Bajo.

## Encabezado común a ambas pantallas

Banner de versión activa: número de versión, fecha de aplicación y usuario que la generó, con enlace a "Ver historial de versiones" (lista de versiones pasadas, de solo lectura — no se editan versiones anteriores, solo se consulta qué valores estuvieron vigentes en cada fecha).

## Flujo de guardado

1. El usuario edita uno o más campos (pesos y/o riesgos pueden ajustarse en la misma sesión de edición).
2. Al presionar "Guardar cambios", si la suma de pesos ≠ 100% el botón permanece deshabilitado (no se llega a enviar).
3. Al guardar con éxito se crea una nueva versión (no se sobreescribe la anterior): incrementa el número de versión, registra usuario y fecha, y queda como la versión activa desde ese momento.
4. Los autodiagnósticos ya generados **no se recalculan**: cada informe guarda snapshot de los pesos/riesgos vigentes cuando se generó, para preservar la evidencia tal como se presentó al cliente en su momento. Este texto de advertencia se muestra siempre visible junto a los botones de acción.

## Fuera de alcance de este panel (v1)

Agregar o quitar preguntas/secciones, cambiar qué sección pertenece a qué obligación, y editar el texto de las preguntas. Estos tres cambian el contenido citable de la fuente CCS y ameritan su propio flujo de revisión, no un ajuste operativo de pesos/riesgo.

## Próximo paso técnico

Estas dos pantallas requieren que `cuestionario_autodiagnostico_config.json` deje de ser un archivo estático y pase a vivir en base de datos con versionado (tablas `config_secciones`, `config_preguntas`, `config_version`) — ver conversación pendiente sobre el esquema de datos.
