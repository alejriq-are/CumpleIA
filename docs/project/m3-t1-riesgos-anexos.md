# Valoración de riesgos y anexos de evaluación

Estado: implementado para ensayo con datos ficticios; EIPD permanece bloqueada.
No habilita revisión formal de EIPD general, aceptación jurídica ni operación real.

## Método CUMPLEIA-CUALITATIVA-1

El daño se refiere a las personas titulares: discriminación, exposición, pérdida
de control e impedimentos para ejercer derechos. No mide pérdidas de la empresa.
Se declara horizonte temporal (12 meses editable), antecedentes de frecuencia y
exposición, probabilidad, gravedad y fundamento por riesgo.

Probabilidad: baja (circunstancias excepcionales), media (escenario plausible),
alta (exposición recurrente o antecedentes relevantes), muy alta (condiciones
favorables al daño presentes persistentemente). Impacto: bajo (limitado/reversible),
moderado (relevante/recuperable), grave (perjuicio serio o dificultad significativa
para ejercer derechos), muy grave (extremo o difícilmente reversible).

| Probabilidad / impacto | Bajo | Moderado | Grave | Muy grave |
| --- | --- | --- | --- | --- |
| Baja | Bajo | Bajo | Medio | Alto |
| Media | Bajo | Medio | Alto | Alto |
| Alta | Medio | Alto | Alto | Muy alto |
| Muy alta | Alto | Alto | Muy alto | Muy alto |

Es una matriz interna y versionada, no una escala impuesta por la ley. Referencias:
[Ley 21.719, BCN](https://nuevo.leychile.cl/navegar?idNorma=1209272) y
[guía de gestión del riesgo/EIPD, AEPD](https://www.aepd.es/guias/gestion-riesgo-y-evaluacion-impacto-en-tratamientos-datos-personales.pdf).
La guía se utiliza como referencia metodológica, no como norma chilena.

Inherente: antes de controles. Cada control identifica riesgos relacionados,
dimensión de mitigación (probabilidad, impacto o ambas), eficacia cualitativa
(no evaluada, insuficiente, parcial, suficiente), estado y evidencias.
Residual previsto: planificación. Residual actual: requiere todos los controles
asociados verificados, declarados implementados y con referencias de evidencia
registradas en el documento/anexos. Reducir una dimensión exige un control parcial
o suficiente que actúe en esa dimensión. No se descuentan porcentajes.
El resumen conserva el máximo residual y señala riesgos sin resolver por separado;
no promedia ni transforma faltantes en riesgo bajo. No sustituye la declaración
residual del contrato EIPD anterior ni altera sus decisiones o hashes.

## Persistencia y anexos

Registros independientes append-only, revisión y huella del material guardado.
Si cambia la evaluación, la valoración queda histórica; se vuelve a consultar y
revisar antes de guardar otra. No se atribuyen niveles históricos al documento actual.
Las respuestas inciertas bloquean reintento hasta consultar; errores conservan ediciones.

Anexos ficticios PDF o TXT UTF-8, hasta 2 MiB por archivo y 20 MiB/50 registros por
evaluación (incluidas versiones). Referencia SIMULADA-, descripción, sección,
riesgos y medidas asociados. Misma referencia agrega versión, sin reemplazar anteriores.
Se guardan bytes en PostgreSQL con permisos y RLS por organización; runtime app_user
sin BYPASSRLS. Descarga autenticada como adjunto, no ejecución inline; navegador
comprueba tamaño/SHA-256. El expediente JSON incluye índice/hashes, no archivos binarios.
No se incorporaron servicios, cuentas ni dependencias externas.

Migración aditiva e67a4b829c10. En desarrollo local, 38 tablas previas conservaron
conteos/checksums. Los modelos reflejan cuatro índices históricos que ya existían;
no se eliminaron ni modificaron índices en la base. Sin merge/despliegue.

## Experiencia y validación

Revisar documentos reúne alcance RAT asociado, licitud/LIA, EIPD, valoración y
anexos. Distingue etiquetas/respuestas; tabla por riesgo muestra niveles,
probabilidad/impacto, controles, mitigación y residual actual/previsto.
Preparar resolución documental de infancia solo aparece para el alcance aplicable;
la consulta histórica sigue disponible. Las evidencias de autoridad están plegadas
si no hay consulta/datos; seleccionar estado aplicable las abre y los datos existentes
se conservan. Guardar descarta únicamente filas opcionales totalmente vacías;
una evidencia parcial conserva sus datos y requiere identificar su tipo.

Validación local: 24 backend dirigidas de matriz/API/RLS/expediente/runner;
35 Chromium de soporte, recorrido, tabla y expediente, más 50 regresiones de
editores e historial de infancia. Cuatro pruebas de listado/integración real con
Chromium, API y PostgreSQL aislado; incluye guardar/reabrir valoración y anexo,
descarga exacta y bloqueo de confirmación. También pasó el recorrido integrado de
resoluciones, revisiones negativas, decisión y actas ficticias: la prueba exige una
sola referencia visible a la ley y procedencia opcional, en lugar de contar enlaces.
Tipos/lint/formato y escritorio/móvil.
Alembic check sin operaciones nuevas tras alinear índices históricos de modelos.
Los ensayos de migraciones ancestrales aíslan/restablecen la FK nueva solo dentro
de una transacción revertida, en base exclusiva de pruebas y con soporte vacío;
no eliminan historial ni cambian migraciones publicadas. Dos ensayos de migración
más 14 regresiones de soporte aprobados tras ajustar esa dependencia.
No se ejecutó otra batería backend completa sin causa. CI del commit publicado
se comprueba por HEAD; validación local no equivale a CI aprobada.

Pendientes fuera del bloque: validación asistida de la interfaz ampliada, revisión
jurídica/metodológica humana y contrato de revisión/adopción formal EIPD general/RAT-LIA.
Uso de archivos reales y habilitación operativa permanecen fuera de este ensayo.
