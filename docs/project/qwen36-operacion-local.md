# Qwen3.6 local — Runbook operativo

## 1. Objetivo

Guía operativa para iniciar, detener, revisar y recuperar el modelo local principal de CumpleIA.

Configuración canónica:

- Modelo: `Qwen3.6-35B-A3B IQ4_XS`
- Runtime: `llama.cpp`
- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8 GB VRAM
- Endpoint directo: `http://127.0.0.1:8080`
- Endpoint operativo: `http://llm-local.cumpleia:18080`
- Contexto: `65536`
- MoE CPU: `-ncmoe 32`
- Template: `qwen36-claude-code.jinja`

Qwen3.6 fue ratificado como modelo local principal después de F1.28/F1.29.

## 2. Inicio rápido de jornada

Primero:

`cumpleia-qwen status`

Si muestra:

- `llama-server : OK`
- `SRT bridge   : OK`

el entorno está listo para trabajar.

Si está detenido:

`cumpleia-qwen start`

El modelo puede tardar aproximadamente 4 minutos en cargar desde `/mnt/d`.

## 3. Comandos operativos

### cumpleia-qwen start

Inicia y prepara el entorno completo de Qwen3.6.

Funciones:

1. Comprueba si Qwen ya está activo.
2. Evita iniciar una segunda instancia.
3. Detecta si el modelo ya está cargando.
4. Inicia `llama-server` si corresponde.
5. Espera hasta que `/health` responda correctamente.
6. Verifica `llm-local.cumpleia`.
7. Inicia el bridge `socat`.
8. Comprueba el bridge.
9. Muestra el estado final.

Después de `wsl --shutdown`, normalmente éste es el único comando necesario:

`cumpleia-qwen start`

### cumpleia-qwen status

Consulta el estado sin modificar el entorno.

`cumpleia-qwen status`

Informa:

- estado de `llama-server`;
- hostname `llm-local.cumpleia`;
- estado del bridge SRT;
- GPU;
- VRAM usada y total;
- temperatura GPU.

Estados posibles del servidor:

- `OK`
- `LOADING`
- `OFF`

### cumpleia-qwen stop

Detiene el entorno:

`cumpleia-qwen stop`

Detiene:

- `llama-server`;
- bridge `socat`;
- procesos administrados por el script.

Usarlo al terminar la jornada o cuando se quiera liberar RAM/VRAM.

### cumpleia-qwen restart

Reinicia completamente el entorno:

`cumpleia-qwen restart`

Flujo:

STOP
→ START llama-server
→ esperar HEALTH OK
→ START socat
→ verificar bridge

Usarlo cuando el servidor o el bridge queden inconsistentes o se necesite una inicialización limpia.

### cumpleia-qwen log

Muestra en tiempo real el log de `llama-server`:

`cumpleia-qwen log`

Usos:

- observar carga del modelo;
- diagnosticar errores;
- revisar actividad;
- comprobar requests.

Salir con `Ctrl+C`.

Esto no detiene Qwen.

## 4. Flujo técnico

Claude Code
→ `llm-local.cumpleia:18080`
→ `socat`
→ `127.0.0.1:8080`
→ `llama-server`
→ Qwen3.6-35B-A3B IQ4_XS
→ RTX 5060 + CPU MoE

## 5. Flujo recomendado antes de comenzar a trabajar

### Paso 1

Entrar al repositorio:

`cd ~/projects/CumpleIA`

### Paso 2

Revisar estado:

`cumpleia-qwen status`

### Paso 3

Si está OFF:

`cumpleia-qwen start`

### Paso 4

Confirmar:

`cumpleia-qwen status`

Debe mostrar:

- `llama-server : OK`
- `SRT bridge   : OK`

### Paso 5

Comenzar trabajo con Claude Code.

Endpoint operativo:

`http://llm-local.cumpleia:18080`

Variables habituales:

`ANTHROPIC_BASE_URL=http://llm-local.cumpleia:18080`

`ANTHROPIC_API_KEY=local`

`CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1`

`CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1`

`TMPDIR=/home/cumplebench/runtime/tmp`

## 6. Después de wsl --shutdown

WSL termina normalmente:

- `llama-server`;
- `socat`.

No reconstruir manualmente el entorno.

Ejecutar:

`cumpleia-qwen start`

El script realiza:

verificar hostname
→ iniciar llama-server
→ esperar carga
→ health check
→ iniciar socat
→ health check del bridge

## 7. Health checks manuales

Servidor directo:

`curl -sS http://127.0.0.1:8080/health`

Respuesta normal:

`{"status":"ok"}`

Durante la carga puede responder:

`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`

`Loading model` significa que Qwen está cargando; no es un fallo.

Bridge:

`curl -sS http://llm-local.cumpleia:18080/health`

Proceso:

`pgrep -af llama-server`

Puerto servidor:

`ss -ltnp | grep ':8080'`

Puerto bridge:

`ss -ltnp | grep ':18080'`

## 8. Configuración canónica

Modelo:

`/mnt/d/CumpleIA-LLM/models/Qwen_Qwen3.6-35B-A3B-IQ4_XS.gguf`

Runtime:

`/home/cumplebench/runtime/llama.cpp-qwen36`

Template:

`/home/cumplebench/runtime/llama.cpp-qwen36/qwen36-claude-code.jinja`

Parámetros principales:

- `-ngl 99`
- `-ncmoe 32`
- `--ctx-size 65536`
- `--flash-attn on`
- `--reasoning off`
- `--no-reasoning-preserve`
- `-np 1`
- `--host 127.0.0.1`
- `--port 8080`

## 9. Validación end-to-end

Se validó correctamente el flujo:

Claude Code
→ bridge local
→ llama-server
→ Qwen3.6
→ Read tool
→ resultado correcto.

La prueba utilizó un archivo con UUID aleatorio no incluido en el prompt.

Resultado:

- tool-use real;
- dos turnos;
- lectura correcta;
- respuesta final exacta.

## 10. Checklist de 30 segundos

Antes de trabajar:

`cumpleia-qwen status`

Si muestra `OK` para servidor y bridge:

→ comenzar a trabajar.

Si está detenido:

`cumpleia-qwen start`

Si hay problemas:

`cumpleia-qwen log`

Para recuperación completa:

`cumpleia-qwen restart`

Al terminar:

`cumpleia-qwen stop`

## 11. Regla operativa

Qwen3.6 es el modelo local principal para desarrollo cotidiano de CumpleIA.

Claude o DeepSeek cloud pueden utilizarse como segunda revisión para tareas críticas, arquitectura, revisiones complejas o decisiones de alto impacto.

No reabrir la selección de modelos salvo que exista un candidato claramente superior, una mejora importante del runtime, un cambio de hardware o una limitación funcional concreta de Qwen3.6.
