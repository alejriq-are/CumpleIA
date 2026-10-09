# M3-T1 — Cierre de la validacion local del canal EIPD

Fecha: 2026-10-09. Checkpoint §122. Base de codigo revisada:
6a6fd27f878a7612d0ceeb9abdcdf968b9f2bf0e.
Estado: SECUENCIA LOCAL DESHABILITADA VALIDADA; M3-T1 EN PROGRESO.

## Evidencia y limites

| Comprobacion | Resultado | Evidencia |
| --- | --- | --- |
| Acceso administrativo con sesion personal | Confirmado por el usuario | Captura §118; sin conservar JWT/PII |
| Consulta inicial | Revision 0, publicaciones 0, selecciones 0 | Capturas §119 |
| Publicacion deshabilitada | 1 publicacion, sin seleccion | Captura §120 |
| Seleccion deshabilitada | Revision 1, 1 publicacion y 1 seleccion | Capturas §121 |
| Prevencion de reseleccion en pantalla | Publicacion ya seleccionada; no ofrece nueva seleccion | Segunda captura §121 |
| Persistencia y coherencia | Evento, publicacion, hash, actor y selector coinciden | Lectura tecnica readonly §121 |
| Canal y permisos efectivos | Preflight ok, salida 0; alcance catalogo public/roles | Preflight real §122 |
| Migraciones del destino local | b17d95c0286f | Lectura separada alembic_version §122 |
| Pruebas focalizadas | 56 aprobadas | Base aislada §121; no ejecutarlas contra registro operacional |
| Frontend | Tipos/lint/formato aprobados | §121; capturas del usuario |
| Fuentes y aceptacion | Pendientes | Politica seleccionada conserva ambos estados pendientes |
| Activacion excepcional | Bloqueada | Politica deshabilitada; activation_authorized false |

La evidencia visual acredita los resultados mostrados por el usuario; no constituye
inspeccion independiente del JWT ni de la solicitud HTTP original. Las lecturas
tecnicas posteriores acreditan persistencia/coherencia, sin emitir tokens ni escribir.
La seleccion de una politica deshabilitada no habilita gates ni confirmacion excepcional.
El CLI no verifica por si mismo identidad del entorno, head ni sesion personal; sus
banderas false describen limites del diagnostico y no anulan las evidencias separadas.

## Pendientes para el cierre integral

| Pendiente | Criterio verificable | Siguiente accion |
| --- | --- | --- |
| Ejecucion aislada de pruebas | Suites de escritura no apuntan al registro operacional | Ejecutor focalizado preparado §123; 60 pruebas aprobadas. Pytest directo fuera de esta guarda |
| Rotacion y retiro del canal | Credencial anterior rechazada tras renovar procesos/conexiones; historial preservado | Preparar ensayo local con procedimiento de recuperacion |
| Fuentes complementarias | Referencias oficiales/version/aplicabilidad verificadas | Completar expediente de fuentes sin inferir inexistencia por busqueda vacia |
| Aceptacion | Responsable y evidencia reales, asociados al codigo revisado | Revisar matriz integral antes de cualquier habilitacion |
| Regimenes especiales y representacion pendientes | Alcance y validador/gates/evidencia definidos y probados | Priorizar segun matriz de aceptacion; no declarar ilicitud por falta de soporte |

La Ley 21.719 / 19.628 reformada permanece como base fija, independientemente de
cambios en fechas de aplicacion. No se amplian reglas juridicas ni se autoriza produccion
en este cierre. La interfaz local de diagnostico no representa la interfaz integral M3.

No se rotan secretos, retiran permisos ni publican/seleccionan nuevas politicas en §122.
