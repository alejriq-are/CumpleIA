# Aprovisionamiento de usuarios y organizaciones (Fase 0)

Cómo pasa un usuario de "registrado en Supabase" a "tener perfil, organización y
acceso multi-tenant" en CumpleIA.

## El problema que resuelve

`supabase.auth.signUp(...)` solo crea una fila en `auth.users` **dentro de
Supabase**. La tabla local `profiles` no se toca. Sin fila en `profiles` no hay
`memberships`, y sin membresía no hay aislamiento de tenant que probar. Antes,
`GET /me` con un token válido de un usuario nuevo devolvía `401 "Perfil de
usuario no encontrado"` — código incorrecto: el usuario **sí** está autenticado.

## Mecanismo adoptado

### 1. Perfil — aprovisionamiento JIT (just-in-time) en el backend

En `get_current_profile` (`app/core/deps.py`), en cada request autenticada:

1. Se valida el JWT de Supabase (ES256/JWKS) y se extrae la identidad
   (`sub`, `email`, `full_name`) — **solo** de los claims firmados, nunca del
   cuerpo de la petición (`extract_auth_identity` en `app/core/security.py`).
2. Se inserta el perfil con `INSERT ... ON CONFLICT (auth_user_id) DO NOTHING`
   y luego se hace `SELECT`. Es idempotente y seguro ante peticiones
   concurrentes del mismo usuario recién logueado: no duplica filas ni falla por
   carrera. `auth_user_id` (= `sub` de Supabase) es la clave única e inmutable
   de vinculación.

Ventaja frente a un trigger en `auth.users`: la lógica vive en el backend
(testeable en CI, sin SQL en la base gestionada) y funciona sea cual sea la vía
de alta (signup, OAuth futuro, invitación).

### 2. Organización — onboarding explícito

`POST /organizations` (`app/api/organizations.py`) crea la `Organization` y la
`Membership` con rol `owner` **en una sola transacción**. Si cualquiera de los
dos INSERT falla, `get_db` hace rollback y no queda nada a medias. Es
autoservicio y no genera organizaciones basura.

Estado esperado de `GET /me`:

- Token inválido / ausente → `401`.
- Token válido, perfil aún sin organización → `200` (perfil creado por JIT).
- Recurso de una organización de la que no se es miembro → `403`
  (`get_org_membership`).

## Fuera de alcance de Fase 0: invitaciones

El flujo por el que un **segundo** usuario se une a una organización existente
(invitación por correo, aceptación, asignación de rol) **no** se implementa en
Fase 0.

El modelo de datos ya lo soporta sin migración destructiva: `memberships`
admite N perfiles por organización con roles `owner`/`admin`/`editor`/`viewer`
y tiene `unique (organization_id, profile_id)`. Añadir invitaciones más adelante
será lógica nueva (tabla `invitations` + endpoints), no un cambio que rompa
datos existentes.
