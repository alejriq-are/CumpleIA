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

## 2026-10-14 — M3-T1 §231: controles globales backend aprobados

Preflight CI detecto imports seed_e2e y migracion historica, mas formato de seed,
servicio RAT y test activacion. Ruff ordena imports seed; Black normaliza los tres
archivos. Comparacion AST confirma codigo identico en servicio/test y cuerpo seed
identico excluyendo imports ordenados. Seed no ejecutado, ningun dato creado.

Migracion aplicada 5997a757f17b intacta por regla append-only AGENTS.md. Excepcion
Ruff por archivo exacto limitada a I001 (orden imports); sin exclusion de otras
reglas o migraciones. Ruff global aprobado; Black global 230 archivos correctos.
No cambio funcional, tests de regresion §230 no repetidos para formato. No suite
integral del producto ni CI remoto. Politica/datos/permisos sin cambios; M3-T1 EN
PROGRESO, pruebas ficticias hasta MVP; confirmacion/activacion bloqueadas.

## 2026-10-14 — M3-T1 §232: CI remoto aprobado en PR borrador

PR #30 creado en borrador sobre main y adjunto al chat:
https://github.com/alejriq-are/CumpleIA/pull/30
CI success para commit 7f94bbf1924792a7a11b1a4b6d314d1bdcc35f5d:
https://github.com/alejriq-are/CumpleIA/actions/runs/38593979233
Backend: pytest tests/ completo, 3977 passed en 624.62 s; job 11m21s. Lint, Black,
preparacion DB, migraciones y seed cuestionario correctos en runner GitHub aislado.
Frontend Node 22: instalacion lockfile, ESLint, tipos, instalacion Chromium,
23 pruebas ficticias EIPD y Prettier aprobados; job 59 s.

Resultado ligado a ese commit, no garantia de futuros commits. PR sigue draft,
sin reviewDecision registrado; mergeStateStatus CLEAN no equivale a revision o
permiso para merge. No fusion ni despliegue. Suite completa backend aprobada en
CI no prueba login real/frontend RAT autenticado ni valida externamente fuentes.

Pendientes de esta entrega: revision tecnica del alcance/migraciones; desarrollo
y validacion restantes del MVP. Fuentes/aceptacion operativas pendientes, politica
deshabilitada; empresa/revision autentica diferidas hasta MVP por acuerdo usuario.
Pruebas ficticias hasta MVP, M3-T1 EN PROGRESO y confirmacion/activacion bloqueadas.
Solo registro documental; codigo/politica/datos locales sin cambios.

## 2026-10-14 — M3-T1 §233: revision focal de rutas sensibles

Inspeccion manual de api/licitud.py, api/eipd_admin.py, db/eipd_admin.py y caminos
de revision/historia/politica seleccionada en services/licitud.py; contexto
services/eipd_confirmation.py. Lecturas view_content y escrituras edit_content,
suscripcion requerida y header tenant UUID. Historia valida padre y filtra evento
por assessment/organization; escritura revalida serie/borrador con filtros tenant
bajo locks y rechaza continuar con contexto V2. Politica habilitada no admitida en
canal operativo revisado. Dependencia admin verifica JWT, canal limitado y actor
personal antes de operar, con commit/rollback transaccional.

No hallazgo accionable nuevo en estos caminos. Revision focal, NO revision completa
de 198 archivos del PR ni aprobacion independiente/humana/seguridad global. No
nuevos tests para lectura de codigo; evidencia automatizada §232 referida al commit
7f94bbf. CI del ultimo commit documental 35cb46f en curso al iniciar esta revision;
no se presume aprobado por el resultado anterior.

PR #30 draft; sin merge/despliegue/cambio de permisos o politica. M3-T1 EN PROGRESO;
pruebas ficticias hasta MVP; confirmacion/activacion operativas bloqueadas.
