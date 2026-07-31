# Backlog — CumpleIA

> Primer archivo de backlog trackeado en git. Hasta ahora el seguimiento de tareas vivía en archivos `Claude_*`/`Fase 1`/`Modulo 1` sin trackear (`git status` los marca `??`); este archivo empieza a fijar en el repo los ítems con criterios de aceptación explícitos, empezando por el de este trabajo.

## Modelo de organizaciones, roles y suscripción

Ver `docs/adr/0001-modelo-organizaciones-roles-suscripcion.md`.

- [x] Existen las entidades `Organization`, `Profile` (usuario), rol de organización (`Membership.role`), admin de plataforma (`profiles.is_superadmin`) y `Subscription`, migradas y documentadas.
- [x] Toda tabla nueva de este trabajo (`subscriptions`) incluye `organization_id` con RLS.
- [x] Existe una función de autorización (`has_permission`/`role_has_permission`, `app/services/authorization.py`) y una de estado de suscripción (`get_subscription_status`/`is_subscription_active`, `app/services/subscriptions.py`), ambas con tests unitarios.
- [x] Existe una organización semilla con un admin para desarrollo (`scripts/seed_dev.py`), ahora también con su `Subscription`.
- [x] El ADR está commiteado y referenciado desde este backlog.
- [x] No se tocó ninguna pantalla de administración de organizaciones ni integración de pagos (fuera de alcance).

### Backlog derivado — fase de Monetización (no construir todavía)

- [ ] Integración con pasarela de pago real (Stripe/Mercado Pago) que actualice `subscriptions.status` según el resultado de cobro.
- [ ] Job/flujo de dunning: mover `active` → `grace` (con `grace_until`) en compromisos anuales ante un fallo de cobro mensual aislado, y `active` → `suspended` directo en planes mensuales puros.
- [ ] UI de administración de organizaciones y de suscripción.
- [ ] Flujo de invitación de un segundo usuario a una organización existente, con asignación de rol por el admin de organización (`Permission.manage_members`, ya modelado en `app/services/authorization.py`, sin endpoint todavía).

## Autodiagnóstico (Fase 1, Módulo 1)

Ver `Fase 1/plan-fase1-modulo1-autodiagnostico.md`. Tareas 0 y 1 completas (catálogo CCS + modelo `Diagnostic`/`DiagnosticAnswer`/`Finding` con RLS). Pendiente: Tarea 2 (motor de puntaje, determinista, sin LLM) en adelante — puede usar `require_permission(Permission.edit_content)` / `require_permission(Permission.view_content)` desde el primer endpoint de la Tarea 3.
