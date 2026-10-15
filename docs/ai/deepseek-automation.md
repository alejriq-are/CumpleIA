# Modalidad recomendada: lanzador local + API Deepseek

Estado: implementado y probado con transporte simulado. Sin llamadas pagadas,
sin clave configurada por Codex y sin validacion real de credenciales/servicio.
No necesita que ChatGPT tenga cuota disponible para preparar o recibir tareas.
La revision/aceptacion del parche sigue pendiente del responsable con herramientas.

## Operacion

Desde WSL Ubuntu-24.04, checkout limpio:

    python3 scripts/deepseek_run.py DS-001

Genera el paquete y muestra resumen sin consultar API ni leer su clave.
Resultado en /tmp/cumpleia-deepseek/DS-001-HEAD. Ningun copiar/pegar del contexto.
Mantener una tarea activa y el mismo directorio para la misma base.

Tras decidir presupuesto y configurar privadamente una clave dedicada en la
variable CUMPLEIA_DEEPSEEK_HANDOFF_KEY (fuera del chat/repo/producto):

    python3 scripts/deepseek_run.py DS-001 --send

Una llamada HTTPS a api.deepseek.com, modelo deepseek-flash, pensamiento
inactivo, JSON y maximo 4096 tokens de salida. Sin herramientas del modelo ni
reintentos. Reserva request-started.json antes del envio; si hay timeout/fallo,
se conserva para revisar antes de cualquier repeticion deliberada. No cambiar
salida para repetir una solicitud cuyo costo/resultado sea incierto.

Guarda respuesta/uso y candidate.patch; comprueba ID/HEAD, alcance y aplicabilidad.
No aplica parche, ejecuta codigo recibido, ni hace commit/push. El modelo API no
tiene terminal: se rechazan afirmaciones de pruebas ejecutadas. Codex revisa y
valida el bloque en una sola pasada cuando este disponible. CI no sustituye esa
revision ni amplifica permisos de Deepseek.

## Presupuesto y requisitos pendientes

La API cobra consumo desde saldo recargado; falta la decision del usuario sobre
presupuesto y la configuracion privada de la cuenta/clave. No se solicitan claves
por chat. El modo por defecto no gasta. No se promete un limite monetario estricto:
4096 tokens y un paquete acotado limitan volumen; costo real depende de tarifas y
uso devuelto. No hay tope mensual automatico en esta version ni recarga automatica.
Antes de habilitar un flujo desatendido, acordar control contable del presupuesto
y validar una llamada real. Nunca confundir una simulacion con operacion verificada.

Fuentes consultadas 2026-10-15:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/
- https://api-docs.deepseek.com/guides/json_mode/

Fallback: traslado manual por chat si el usuario decide no usar saldo API.
Esta modalidad es independiente de LLM_PROVIDER y de las claves del producto.

## Piloto autorizado con credito existente

Usuario autorizo una prueba pagada DS-001 el 2026-10-15. Captura de Harness:
USD4.70 recargados y CNY5.39 de bono; no sumar monedas ni asumir que la credencial
API dedicada comparte ese saldo hasta consultarlo. La clave dedicada no estaba
configurada en Windows/WSL; no se extrajeron tokens de la sesion de Harness.

Antes/despues se consulta /user/balance; se guardan saldos por moneda, usage del
modelo y estimacion USD segun tarifas Flash consultadas el 15/10. El delta de
saldo no acredita por si solo costo exacto si hubo llamadas concurrentes,
redondeo o liquidacion pendiente. Evitar usar Harness durante la medicion.
Un parche invalido tambien puede consumir; expense.json se guarda antes de
validar el contenido. Una sola generacion, sin repeticion automatica.
Fuente saldo: https://api-docs.deepseek.com/api/get-user-balance/

Bloqueo pendiente: configurar privadamente CUMPLEIA_DEEPSEEK_HANDOFF_KEY. No
pegar la clave en chats/capturas; mantenerla separada de las claves del producto.
