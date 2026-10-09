# M3-T1 — Plan de rotacion real del canal local EIPD

Fecha: 2026-10-09. §125. Estado: PREPARADO; ROTACION NO EJECUTADA.
Base revisada: 4b7a19d7071a36c7f4db90cbae18add05d146618.

## Destino y comprobaciones realizadas

| Elemento | Resultado |
| --- | --- |
| Entorno | Desarrollo local, host loopback |
| Login a rotar | eipd_backend_local; mismo grupo limitado eipd_policy_admin |
| Archivo privado | admin.env del directorio externo de configuracion local, modo 0600 |
| Preflight | ok; permisos/canal y auditoria coherentes |
| Migracion aplicada | b17d95c0286f |
| Selector | Revision 1; politica deshabilitada |
| Conexiones observadas | 2 idle durante diagnostico, incluido el propio diagnostico; ninguna activa en esa consulta |
| Backend existente 8000 | Fuera del cambio; proceso de validacion separado 8001 |

La cuenta anterior es una observacion, no garantia de drenaje futuro. El diagnostico
cerro su propio pool al terminar. Volver a comprobar sesiones inmediatamente antes
del cambio. No inferir que NOLOGIN o cambiar password cierra sesiones ya existentes.

## Secuencia concreta preparada

1. Capturar snapshot validado completo en memoria y su fingerprint; confirmar
   1 publicacion, 1 seleccion, revision 1 y activacion deshabilitada. Comprobar
   identidad local, login/permisos y head. No imprimir actores ni cadenas privadas.
2. Detener solo el proceso de validacion 8001 que iniciamos; cerrar su pool.
   Verificar que no quedan sesiones del login dedicado. Si quedan sesiones ajenas,
   no terminarlas automaticamente: identificar su responsable antes de proceder.
3. Generar nueva clave aleatoria en memoria. Preparar reemplazo privado 0600 y
   copia de recuperacion privada 0600 fuera del repositorio; ninguna URL/clave en
   argumentos de proceso, chat o logs. Mantener el destino y rol originales.
4. Cambiar password del login mediante mantenimiento revisado, sin modificar
   flags, membresias, perfil, publicaciones, eventos ni selector. Sustituir el
   archivo privado de forma atomica. Si falla la coordinacion DB/archivo, restaurar
   la credencial anterior y comprobar recuperacion antes de reiniciar el servicio.
5. Abrir conexion NUEVA con clave anterior: debe fallar 28P01. Abrir conexion nueva
   con clave actual: preflight ok. Disponer ambas conexiones/pools. No inferir
   revocacion de clave anterior por una conexion que ya estaba autenticada.
6. Comparar snapshot y fingerprint exactos con el previo; deben permanecer iguales.
   No limpiar ni reescribir auditoria para hacer pasar la comprobacion.
7. Reiniciar el proceso de validacion 8001 con la nueva credencial desde archivo
   privado, DEBUG=false y sin access log. Comprobar rechazo anonimo 401 y solicitar
   al usuario Comprobar acceso/Consultar registro con su sesion personal real.
8. Registrar resultados sanitizados y recuperacion. Retirar copia privada anterior
   solo despues de confirmar servicio y sesion personal; nunca eliminar auditoria.

## Limites y recuperacion

La rotacion no retira definitivamente el canal ni revoca el perfil personal. No
cambia fuentes/aceptacion ni autoriza activacion. Si el login/DB/archivo no coincide
con los previamente verificados, detener el cambio antes de ALTER ROLE. Conservar
credencial anterior privada hasta confirmar la recuperacion; no subirla al repo.

La ejecucion real y el nuevo acceso personal aun estan pendientes. Este documento
es una propuesta concreta para el siguiente cambio, no evidencia de rotacion hecha.
M3-T1 EN PROGRESO; Ley 21.719/19.628 reformada fija y activacion EIPD bloqueada.
