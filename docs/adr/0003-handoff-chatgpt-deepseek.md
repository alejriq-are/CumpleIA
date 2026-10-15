# ADR 0003 — Handoff acotado ChatGPT–Deepseek

Fecha: 2026-10-15. Estado: implementado para piloto; pendiente validar transferencia
real con Deepseek. Alcance: gobernanza del desarrollo, sin cambios al producto.

Contexto: presupuesto limitado y pausas por cuota hacen costoso reconstruir
contexto; archivos fechados, punteros rotos y roles implicitos introducen deriva.

Decision: entrada docs/HANDOFF.md, contratos por tarea con base Git y alcance
cerrado, paquetes de archivos versionados, accesos declarados por sesion y
separacion entre reglas/evidencia. ChatGPT disena/revisa/valida; Deepseek entrega
parches simples; usuario conserva prioridad y permisos. Claude no participa.
Adaptadores delgados, sin APIs ni dependencias de pago. Historia existente no se
mueve para evitar enlaces rotos. Ver docs/ai/handoff-contract.md.

Consecuencias: el chat manual necesita un traslado de ida y vuelta por el usuario.
La validacion local sigue siendo responsabilidad del ejecutor con herramientas.
Un script reduce transcripcion pero no elimina obsolescencia ni aprueba parches.
El piloto DS-001 mide friccion, reintentos, fidelidad y checks; ajustar el contrato
tras su resultado, sin atribuir al modelo un ensayo que no ejecuto.
