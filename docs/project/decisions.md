# Decisiones arquitectónicas vigentes

## ADR 0001 - Organizaciones, roles y suscripción

Decisiones centrales:

- roles fijos en código;
- un rol por membresía;
- `owner/admin/editor/viewer`;
- superadmin global separado;
- permisos definidos en aplicación, no tabla dinámica;
- `Subscription` una por organización;
- estado de suscripción preparado para `active/grace/suspended/cancelled`.

## ADR 0002 - Lógica adaptativa, riesgo y remediación

Decisiones centrales:

- no inventar aplicabilidad por rubro/tamaño si la fuente no la define;
- riesgo Alto/Medio/Bajo sí puede derivarse del catálogo/fuente;
- CumpleIA no debe fijar plazos normativos propios sin sustento;
- documentos de referencia y futuros instructivos de la Agencia se modelan por separado;
- profundidad del reporte puede variar por riesgo sin convertirse en una regla normativa.

## Decisiones posteriores relevantes

- scoring sin LLM;
- “Parcial” genera brecha con riesgo degradado un nivel;
- “N/A” se excluye del denominador;
- informe usa RAG y guardarraíles;
- anexo detallado de respuestas se reserva para la Carpeta de Evidencia de pago;
- Módulo 1 es freemium;
- gate de suscripción debe estar en backend cuando empiecen módulos pagados.

Las copias originales de los ADR están en `reference/decisions/`.
