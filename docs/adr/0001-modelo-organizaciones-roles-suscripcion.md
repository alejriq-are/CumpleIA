# ADR 0001 — Modelo de organizaciones, roles y suscripción

**Fecha:** 2026-07-31
**Estado:** Aceptado

> Primer ADR del repositorio. No existía una convención previa de ADRs en CumpleIA; este documento la establece: Contexto / Decisión / Consecuencias, en español, versionado en `docs/adr/`.

## Contexto

Fase 0 cerró con autenticación, multi-tenancy con RLS real y las bases del RAG. Antes de seguir con Autodiagnóstico (Fase 1, Módulo 1, Tarea 2 en adelante), había que fijar el modelo base de organizaciones/roles/permisos y de suscripción (vigencia de acceso), para que los módulos de negocio nazcan con scoping y control de acceso completos y no requieran refactor después.

Al revisar el estado real del código (no se asumió que se partía de cero), ya existía gran parte de la base:

- `Organization`, `Profile`, `Membership` (`backend/app/db/models.py`), con RLS real por organización desde la migración `0001_initial_schema`.
- `Membership.role`: enum `user_role` con 4 valores (`owner`, `admin`, `editor`, `viewer`). En la práctica, hoy solo se asigna `owner` (alta de organización por autoservicio, `POST /organizations`) y ningún endpoint distingue comportamiento por rol — `admin`/`editor`/`viewer` son valores muertos.
- `profiles.is_superadmin`: bandera global de plataforma (staff CumpleIA), independiente de cualquier organización, con la función SQL `is_superadmin()` (migración `0002`) y la dependencia `require_superadmin` (`app/core/deps.py`).
- Toda tabla de dominio (`diagnostics`, `findings`, `systems`, `treatments`, etc.) ya lleva `organization_id` desde su primera migración.

Lo que no existía y motiva este ADR:

- Ninguna noción de **suscripción**: `Organization.plan` es un campo de texto libre sin lógica ni consumidores.
- Ninguna función de autorización más allá de "es miembro / no es miembro" y el chequeo aislado de `is_superadmin`.
- Ningún ADR ni backlog trackeado en git (el historial de decisiones de Fase 0/Módulo 1 vivía en archivos de trabajo sin trackear).

## Decisión

### Entidades y relaciones

- **`Organization`** y **`Profile`**: sin cambios.
- **Admin de plataforma**: `profiles.is_superadmin`, sin cambios. No es un rol de organización — un superadmin tiene acceso pleno a cualquier organización independientemente de su membresía (`has_permission` lo trata como bypass, ver más abajo).
- **Rol de organización**: se mantiene el enum `user_role` existente (`owner/admin/editor/viewer`) en vez de introducir los dos nombres literales que proponía el encargo original (*admin de organización* / *responsable de organización*). Migrar el enum, y con él `organizations.py`, `seed_dev.py`, `conftest.py` y los tests que ya lo usan, sería puro renombre: hoy nada distingue comportamiento entre los 4 valores, así que reducir a 2 no gana nada y pierde la granularidad de `editor`/`viewer` que ya está disponible sin costo. Mapeo conceptual, documentado aquí y no en el código:
  - `owner` ≈ responsable de organización (el que da de alta la organización vía autoservicio; conceptualmente irremovible/intransferible — regla que se aplicará cuando exista gestión de miembros, no antes).
  - `admin` ≈ admin de organización.
  - `editor`/`viewer` quedan reservados para cuando se necesite diferenciar "puede editar contenido" de "solo puede ver", sin requerir otra migración.
- **Un rol por membresía**, no roles apilables. Simplificación explícita: no hay ningún caso de uso hoy que requiera que un mismo perfil tenga más de un rol dentro de la misma organización.
- **`Subscription`** (nueva, migración `0004`): una fila por organización. Campos: `commitment_type` (`monthly` | `annual_commitment_monthly_billing`), `status` (`active` | `grace` | `suspended` | `cancelled`), `grace_until` (fecha límite del estado `grace`, nullable). Regla de negocio que aplicará el futuro job de facturación (no se construye en este trabajo): un compromiso anual no debe cortar acceso por un fallo de cobro mensual aislado — pasa a `grace` con fecha límite; un plan mensual puro puede pasar directo a `suspended` al primer fallo.

### Autorización

- `hasPermission(user, permission, organizationId)` → `backend/app/services/authorization.py::has_permission`. Catálogo de `Permission` (`view_content`, `edit_content`, `manage_members`, `manage_organization`) definido en código, no en una tabla: con 4 roles fijos y sin necesidad de que una organización personalice sus propios permisos, una tabla `permissions` dinámica sería sobre-ingeniería para el segmento objetivo (micro/pequeña empresa, autoservicio). Si en el futuro una organización necesitara permisos a medida, se revisita esta decisión.
- Jerarquía acumulativa: `viewer` ⊂ `editor` ⊂ `admin` = `owner`.
- Un perfil con `is_superadmin=true` tiene todos los permisos sobre cualquier organización, sin necesidad de membresía — es admin de plataforma, no de una organización puntual.

### Suscripción

- `getSubscriptionStatus(organizationId)` → `backend/app/services/subscriptions.py::get_subscription_status`, lee la fila real de `subscriptions` (no un valor fijo hardcodeado): toda organización tiene exactamente una fila desde que se crea (`POST /organizations` y `seed_dev.py` la insertan; la migración `0004` hace backfill de las que ya existían). Por ahora todas nacen `active` — el cálculo real de vigencia según facturación es trabajo futuro, pero la interfaz y el dato ya existen.
- `is_subscription_active(status)` responde la pregunta de vigencia (`active`/`grace` → vigente) sin acoplarla a cómo se llegó a ese estado.

## Fuera de alcance (explícito)

- Integración con pasarela de pago real (Stripe/Mercado Pago).
- UI de administración de organizaciones o de suscripciones.
- Flujo de invitación/delegación de permisos a un segundo usuario de una organización — hoy no existe forma de agregar un segundo miembro a una organización, y este ADR no la agrega. `has_permission`/`require_permission` quedan listos para cuando ese flujo exista.
- Dunning/reintentos de cobro.

Estos quedan como ítems de backlog separados para la fase de Monetización (ver `docs/backlog.md`).

## Consecuencias

- Autodiagnóstico (Tarea 3 en adelante) puede usar `require_permission(Permission.edit_content)` / `require_permission(Permission.view_content)` (`app/core/deps.py`) desde el primer endpoint, sin otra migración de por medio.
- `subscriptions` queda con RLS: cualquier miembro puede ver el estado de su propia organización; el `INSERT` inicial lo hace la propia organización al crearse (`POST /organizations` inserta Organization+Membership+Subscription en una transacción) o un superadmin, pero **cambiar** el status después de creado (`UPDATE`) es exclusivo de `is_superadmin()` — no hay autoservicio de facturación todavía, y no queremos que un admin de organización pueda cambiarse a sí mismo a `active` una vez que algo lo haya puesto en `suspended`/`cancelled`. La unicidad de `organization_id` evita que el `INSERT` de autoservicio sirva para otra cosa que no sea la fila inicial.
- El enum `user_role` queda con dos valores sin comportamiento diferenciado (`editor`, `viewer`) hasta que un módulo real los necesite; se documenta aquí para que no se lean como error sino como capacidad reservada.
