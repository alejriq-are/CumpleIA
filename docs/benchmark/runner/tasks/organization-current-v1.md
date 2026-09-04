# Ronda 2 — Organización actual segura

Implementa una lectura explícita de la organización seleccionada por el
usuario. La aplicación ya permite listar las organizaciones propias y editar
la organización actual a quien posee el permiso correspondiente, pero no
expone un endpoint de lectura de la organización activa.

## Comportamiento requerido

1. Agrega `GET /organizations/current`.
2. El endpoint toma la organización seleccionada exclusivamente desde el
   header `X-Organization-Id`; no acepta un identificador de organización en
   path, query ni body.
3. Requiere autenticación, membresía válida en la organización indicada y el
   permiso `view_content`. Un `viewer` miembro puede leer; un usuario sin
   membresía en esa organización recibe `403`.
4. Con una selección válida devuelve `200` y exactamente los campos `id`,
   `name`, `rut`, `industry` y `size` de esa misma organización. No debe
   devolver datos de otra organización ni información de membresías o perfiles.
5. Si una organización seleccionada válidamente no existe, devuelve `404`.
6. Mantén sin cambios el comportamiento de `POST /organizations`,
   `PATCH /organizations` y `GET /me/organizations`; no agregues migraciones
   ni dependencias.
7. Agrega o modifica pruebas de backend que cubran lectura autorizada, rol
   `viewer`, intento cruzado entre tenants y la respuesta `404`.

## Restricciones

- No modifiques archivos bajo `docs/benchmark/runner/`.
- No cambies políticas RLS, migraciones, seeds ni privilegios de `app_user`.
- No ejecutes seeds ni uses credenciales externas.
- Mantén compatibilidad con Python 3.12 y los contratos FastAPI actuales.
- Limita los cambios a este endpoint, sus esquemas y sus pruebas directamente
  relacionadas.

El resultado autoritativo será determinado por verificadores trusted fuera del
workspace candidato. Los tests modificables por el candidato no constituyen por
sí solos un PASS.
