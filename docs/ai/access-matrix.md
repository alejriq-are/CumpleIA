# Accesos por sesion

| Sesion | Confirmado en esta preparacion | No asumir |
| --- | --- | --- |
| Codex desktop, WSL Ubuntu-24.04 | Git/gh, Python, Node, Chromium, PostgreSQL aislado; pruebas previas verificadas | Acceso universal a otros equipos o permisos de merge/despliegue |
| ChatGPT web | Capacidad pendiente de declarar en cada chat | Shell, Git o ejecucion local |
| Deepseek | Modalidad pendiente de confirmar por el usuario; paquete sirve para chat manual | Repo, shell, Node, PostgreSQL, Actions o escritura externa |

Al aceptar DS-001 devolver: archivos recibidos, HEAD recibido, lectura de repo,
terminal, red/GitHub, Node/Playwright, PostgreSQL y escritura disponibles: si/no/no
comprobado. Lectura permite inspeccion estatica con referencias concretas; no
permite afirmar ejecucion. Verificar una CI por API exige el SHA exacto y URL,
no solo el nombre de rama. Declarar tambien limites y falta de archivos.
