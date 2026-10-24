# Ejecutor reusable ChatGPT–Deepseek

Decision vigente: delegar bloques coherentes seleccionados caso a caso. No hay
bloque activo, gasto recurrente ni nueva llamada autorizada por esta mejora.
ChatGPT define criterios, revisa candidatos y acepta/publica; Deepseek implementa
el contrato. EIPD bloqueada, solo datos ficticios, sin merge/despliegue.

## Flujo unico

1. Crear contrato versionado desde docs/ai/task-template.json; elegir archivos,
   criterios, pruebas independientes y presupuesto. Checkout limpio y HEAD exacto.
2. Preparar sin gasto: `python3 scripts/deepseek_run.py ID`.
3. Una generacion autorizada, por ejemplo:

       python3 scripts/deepseek_run.py ID --send --budget-usd 0.20 --max-iterations 2 --output /tmp/ID-HEAD

   El ejemplo no autoriza consumo. Variable privada CUMPLEIA_DEEPSEEK_HANDOFF_KEY,
   independiente de claves del producto. Windows User debe heredarse a WSL mediante
   WSLENV; configurar desde PowerShell, no pegar claves en chat/repo. Node/npm
   existentes deben estar en PATH. Ejecutar herramientas locales desde WSL/Linux.
4. Revisar candidate.patch y anotar su SHA256. El modelo entrega reemplazos
   literales {path,old,new}; el ejecutor genera diff. Se admite diff antiguo,
   checks como lista u objeto, sin aceptar afirmaciones de pruebas ejecutadas.
5. Validar solo el candidato revisado:

       python3 scripts/deepseek_validate.py --root . --task docs/ai/tasks/ID.json --base HEAD_COMPLETO --patch /tmp/ID-HEAD/candidate.patch --output /tmp/ID-HEAD/validation --reviewed-sha256 HASH_REVISADO

   Copia frontend desde Git, excluye .env y no cambia el checkout original.
   Prettier primero, luego Playwright con pruebas explicitas, tipos y lint. No
   instala dependencias. Comandos fijos, timeout de grupo de procesos, entorno
   sin API keys/DB. Hash de fuentes protegidas (incluidas pruebas independientes)
   y verificacion de que los checks no modifican codigo. No shell del modelo.
   Esta copia NO es un sandbox del sistema operativo: sigue siendo necesaria la
   revision de codigo antes de ejecutar. Dependencias locales se reutilizan.
6. Si hay fallo real, validation.json y feedback.json identifican check/error.
   Una correccion requiere accion explicita y permiso del bloque vigente:

       python3 scripts/deepseek_run.py ID --send --output /tmp/ID-HEAD --repair-from /tmp/ID-HEAD/validation

   Politica de presupuesto y maximo fijada en primera llamada; no se aumenta en
   correccion. Resultado en repair-2; revisar/validar alli antes de otra correccion.
   Predeterminado una llamada, maximo tres. No se generan respuestas para corregir
   formato: lo resuelve Prettier. No editar fixtures/assertions para eludir fallos.
7. Revisar formatted.patch y resultado checks_passed_pending_acceptance. Eso no
   autoriza por si mismo aplicar/publicar: ChatGPT decide dentro del permiso del
   usuario. El ejecutor nunca hace commit, push, merge ni despliegue.

## Limites de gasto y recuperacion

Sin --send no se lee clave ni consulta API. Con --send se exige presupuesto
positivo explicito (CLI o execution.budget_usd del contrato), se reserva volumen
antes y se guarda gasto por moneda/uso incluso si el retorno es rechazado.
Admision conservadora por bytes UTF8 + margen y tarifas Flash de referencia
2026-10-15; NO es un tope monetario de facturacion del proveedor. Verificar tarifas
antes de cada nuevo bloque; no hay control mensual ni recarga automatica.
Correcciones restan gasto estimado previo y requieren uso verificable.

request-started.json reserva cada intento antes de consulta/envio. Timeout o
fallo incierto bloquea repeticion; no cambiar directorio para duplicarlo.
HTTP401/saldo no disponible identifica fase sin generacion; requiere resolver
acceso y revisar artefactos antes de otro intento deliberado. Base obsoleta,
checkout sucio, ancla old ambigua, candidato distinto al revisado o fuente
protegida alterada detienen el flujo. No rebase ni normalizacion semantica automatica.

Perfil consolidado: frontend TS/JS existentes, sin altas/bajas/renombres,
validation.test_files versionados y explicitos; checks que falle detiene los
siguientes. Backend, migraciones, RLS, reglas legales y EIPD quedan fuera de ese
perfil. No convertir los prototipos de /tmp en otros ejecutores por tarea.

## Evidencia

Consolidacion probada sin API: 36 unitarias y ensayo con 25 Chromium reales,
tipos/lint/formato; checkout original intacto. Fecha UTC 2026-10-16, fecha local
2026-10-15. Transporte simulado para presupuesto, retorno y correccion; bucle
pagado del ejecutor consolidado aun no probado. Los pilotos previos estan en
pilot-results.md; comparacion BENCH-001 en benchmarks/BENCH-001.md.
No gastar otro piloto minimo: validar operacion real cuando haya bloque adecuado.

Fuentes de referencia:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/
- https://api-docs.deepseek.com/api/get-user-balance/
