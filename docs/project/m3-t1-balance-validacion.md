# M3-T1 — Balance de validacion al 2026-10-13

Estado: EN PROGRESO. Este balance consolida evidencia reciente; no aprueba el
expediente, no habilita confirmacion/activacion y no reemplaza revision juridica.

| Area | Evidencia comprobada | Limite |
| --- | --- | --- |
| Presentacion | Cabeceras y consulta a 390 px; detalle apilado; raiz sin overflow en estado medido | Emulacion Edge, no dispositivo fisico ni todos los estados |
| Sesion/formulario | Cierre, ingreso protegido, reingreso limpio, requeridos y formato invalido con recuperacion | Evidencia manual de flujos delimitados |
| Lectura entre sesiones | Segunda sesion: RAT, historial EIPD v2 y readiness 404. Original: historial v2/readiness 200 | No reciprocidad completa ni todos los endpoints; headers no inspeccionados |
| Historia | Eventos separados y lectura original preservada; vigencia de ultima revision separada del evento consultado | No inferir vigencia actual desde identidad historica |
| Escritura aislada | 14 pruebas negativas/writer v2 aprobadas (§197) | Fixtures y autenticacion sinteticas; no base operativa |
| Permisos/barreras aislados | 45 pruebas aprobadas (§198) | Corrida focalizada, no suite completa |
| Concurrencia aislada | 26 pruebas aprobadas (§199) | No usuarios reales simultaneos |

## Pendientes que impiden declarar cierre integral

- Fuentes oficiales y revision de aceptacion juridica pendientes; no inventar requisitos.
- Politica operativa local deshabilitada: continuar positivo, confirmacion y activacion
  permanecen bloqueados. Pruebas con politicas sinteticas no cambian ese estado.
- Cobertura de escritura/reciprocidad manual entre cuentas y otros endpoints pendiente.
- Regimenes no soportados y alcance excepcional requieren delimitacion y evidencia.
- Las corridas focalizadas no sustituyen una regresion integral antes de cierre/merge.

## Siguiente avance concreto

Revisar el contrato y las fuentes requeridas para la habilitacion excepcional EIPD,
identificando referencias oficiales existentes y brechas de evidencia. Resultado
esperado: matriz de fuentes/criterios revisable; sin activar politica ni expediente.
No repetir capturas ni tests aprobados salvo nuevo cambio, fallo o concern definido.

## Regresion conjunta posterior (§211)

2026-10-13: 545 aprobadas en 8.39 s en base aislada, incluyendo los tres modulos
ampliados y API de controls v3/readiness, respuesta historica v2 y negativas v2.
Corrida conjunta focalizada, no suite integral. Aceptacion de fuentes/politica sigue
pendiente; confirmacion/activacion operativas bloqueadas.

## 2026-10-13 — M3-T1 §230: regresion EIPD backend consolidada

Runner seguro scripts.run_eipd_tests ejecutado en commit 321a64c: 642 pruebas
aprobadas en 234.27 s, 26 suites focalizadas del catalogo TARGETS. Base fija aislada,
head y app_user sin bypass/superuser verificados antes; misma verificacion posterior
correcta, registro de politica de pruebas vacio. No creacion/borrado de DB ni uso
de expediente operativo. Credenciales no copiadas a documentacion.

Cubre investigacion/bindings, frontera/screening/controles, metadatos/requisitos,
escritura negativa, almacenamiento/lectura, APIs y concurrencia del catalogo.
No suite completa del backend: otros modulos y servicios fuera de TARGETS no se
presentan como probados; no nueva validacion externa de fuentes o aceptacion.
Solo registro documental, codigo/politica/datos operativos sin cambios. M3-T1 EN
PROGRESO; pruebas ficticias hasta MVP; confirmacion/activacion bloqueadas.
