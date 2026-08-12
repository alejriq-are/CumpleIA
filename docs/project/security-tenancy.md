# Seguridad, autenticación y multi-tenancy

## Autenticación

El backend valida JWT de Supabase usando JWKS público y ES256, incluyendo firma, expiración, audiencia y emisor.

La identidad se deriva del JWT validado. El backend aprovisiona el `Profile` en forma JIT mediante `INSERT ... ON CONFLICT DO NOTHING`.

## Aislamiento multi-tenant

La protección no depende solo del frontend ni del header enviado por el cliente:

1. El cliente envía `X-Organization-Id`.
2. El backend valida membresía/permiso.
3. La transacción configura el `sub` del JWT en PostgreSQL.
4. El runtime usa `APP_DATABASE_URL` con `app_user`, sin `BYPASSRLS`.
5. Las políticas RLS restringen filas por organización.

Este patrón es una de las decisiones más importantes del proyecto y no debe relajarse.

## Superadmin

`Profile.is_superadmin` representa administración global de la plataforma y puede otorgar acceso a cualquier organización sin membresía, según ADR 0001.

## Secretos

Hallazgo positivo: Git solo trackea `.env.example`; los `.env.local` están ignorados.

Hallazgo de higiene: el ZIP recibido sí contenía `.env.local`, `frontend/.env.local` y archivos de sesión de Claude. Aunque estén ignorados por Git, **no deberían incluirse en archivos ZIP compartidos**.

## Reglas para agentes

- Nunca usar la conexión propietaria de Postgres en runtime.
- Nunca confiar únicamente en un `organization_id` del cliente.
- Toda tabla de dominio nueva debe definir estrategia de tenant/RLS desde la primera migración.
- No registrar tokens completos.
- No copiar secretos reales a documentación, prompts o fixtures.
