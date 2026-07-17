-- ============================================================
-- CumpleIA — Esquema base de datos (Fase 0)
-- PostgreSQL 16 + pgvector (compatible con Supabase)
-- Referencia para generar las migraciones Alembic.
-- Ajustar la dimensión del vector (1024) si cambias el modelo de embeddings.
-- ============================================================

-- ---------- Extensiones ----------
create extension if not exists "pgcrypto";   -- gen_random_uuid()
create extension if not exists "vector";     -- pgvector (embeddings RAG)

-- ---------- Tipos ----------
create type user_role as enum ('owner', 'admin', 'editor', 'viewer');
create type risk_level as enum ('alto', 'medio', 'bajo');
create type finding_status as enum ('abierto', 'en_proceso', 'cerrado', 'no_aplica');
create type legal_basis as enum (
  'consentimiento', 'contrato', 'obligacion_legal', 'interes_legitimo', 'otra'
);
create type third_party_role as enum ('encargado', 'cesion', 'transferencia_internacional');
create type document_type as enum (
  'politica_proteccion_datos', 'politica_privacidad', 'politica_conservacion',
  'politica_seguridad', 'procedimiento_arsop', 'procedimiento_incidentes'
);
create type document_status as enum ('borrador', 'aprobado', 'archivado');

-- ============================================================
-- Núcleo multi-tenant
-- ============================================================

-- Organización = tenant
create table organizations (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,
  rut           text,
  industry      text,            -- rubro (para plantillas por industria)
  size          text,            -- micro / pequena / mediana
  plan          text default 'free',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- Perfil de usuario (se enlaza al usuario de Supabase Auth por auth_user_id)
create table profiles (
  id            uuid primary key default gen_random_uuid(),
  auth_user_id  uuid unique not null,   -- = auth.users.id de Supabase
  email         text not null,
  full_name     text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- Membresía: un usuario pertenece a una organización con un rol
create table memberships (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  profile_id       uuid not null references profiles(id) on delete cascade,
  role             user_role not null default 'owner',
  created_at       timestamptz not null default now(),
  unique (organization_id, profile_id)
);

-- Helper: organizaciones a las que pertenece el usuario autenticado (para RLS)
create or replace function auth_org_ids()
returns setof uuid
language sql stable security definer set search_path = public as $$
  select m.organization_id
  from memberships m
  join profiles p on p.id = m.profile_id
  where p.auth_user_id = auth.uid();
$$;

-- ============================================================
-- Módulo 1 — Diagnóstico
-- ============================================================
create table diagnostics (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  global_score     numeric(5,2),
  section_scores   jsonb,          -- { "gobernanza": 40, "inventario": 60, ... }
  status           text default 'en_progreso',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  created_by       uuid references profiles(id),
  updated_by       uuid references profiles(id)
);

create table diagnostic_answers (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  diagnostic_id    uuid not null references diagnostics(id) on delete cascade,
  section          text not null,        -- una de las 10 secciones CCS
  question_code    text not null,
  answer           text,                 -- si / parcial / no / na
  notes            text,
  created_at       timestamptz not null default now()
);

-- Brechas / hallazgos
create table findings (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  diagnostic_id    uuid references diagnostics(id) on delete set null,
  description      text not null,
  risk             risk_level not null,
  corrective_action text,
  responsible      text,
  status           finding_status not null default 'abierto',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

-- ============================================================
-- Módulo 2 — Inventario (RAT), sistemas y proveedores
-- ============================================================
create table systems (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  name             text not null,
  provider         text,
  hosting_location text,          -- pais/region (para detectar transferencias)
  is_international  boolean default false,
  created_at       timestamptz not null default now()
);

create table vendors (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  name             text not null,
  role             third_party_role,
  is_international  boolean default false,
  has_dpa          boolean default false,
  created_at       timestamptz not null default now()
);

create table treatments (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  name             text not null,
  purpose          text,                 -- finalidad
  data_categories  text[],               -- categorias de datos
  data_subjects    text[],               -- clientes / trabajadores / proveedores
  has_sensitive    boolean default false,
  retention        text,                 -- plazo de conservacion
  is_international  boolean default false,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  created_by       uuid references profiles(id),
  updated_by       uuid references profiles(id)
);

-- ============================================================
-- Módulo 3 — Bases de licitud y LIA
-- ============================================================
create table legal_bases (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  treatment_id     uuid not null references treatments(id) on delete cascade,
  basis            legal_basis not null,
  justification    text,
  confidence       numeric(4,3),          -- confianza de la sugerencia IA (0-1)
  approved         boolean default false,
  lia              jsonb,                 -- analisis de interes legitimo (tests)
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

-- ============================================================
-- Módulo 4 — Documentos generados
-- ============================================================
create table documents (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  type             document_type not null,
  version          int not null default 1,
  status           document_status not null default 'borrador',
  storage_path     text,                  -- ref en object storage
  content_hash     text,                  -- sha-256 del archivo
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  created_by       uuid references profiles(id)
);

-- ============================================================
-- Módulo 5 — Bitácora de evidencia (append-only, hash encadenado)
-- ============================================================
create table evidence_events (
  id               uuid primary key default gen_random_uuid(),
  organization_id  uuid not null references organizations(id) on delete cascade,
  event_type       text not null,         -- ej: documento_aprobado, rat_actualizado
  actor_profile_id uuid references profiles(id),
  payload          jsonb,                 -- datos del evento
  payload_hash     text not null,         -- sha-256 del payload
  prev_hash        text,                  -- hash del evento anterior de la org (cadena)
  event_hash       text not null,         -- sha-256(payload_hash + prev_hash)
  created_at       timestamptz not null default now()
);
-- Regla de negocio (reforzar en backend y con permisos): esta tabla es
-- INSERT-only. No conceder UPDATE ni DELETE al rol de la aplicación.

-- ============================================================
-- RAG — Base de conocimiento (global, no por tenant)
-- ============================================================
create table knowledge_chunks (
  id            uuid primary key default gen_random_uuid(),
  source        text not null,            -- 'ley_21719' | 'guia_ccs' | 'plantilla'
  reference     text,                     -- articulo / seccion / pagina
  content       text not null,
  embedding     vector(1024),             -- ajustar a la dimension del modelo
  created_at    timestamptz not null default now()
);
create index on knowledge_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- ============================================================
-- Índices por tenant
-- ============================================================
create index on diagnostics(organization_id);
create index on diagnostic_answers(organization_id);
create index on findings(organization_id);
create index on systems(organization_id);
create index on vendors(organization_id);
create index on treatments(organization_id);
create index on legal_bases(organization_id);
create index on documents(organization_id);
create index on evidence_events(organization_id);
create index on memberships(organization_id);

-- ============================================================
-- Row-Level Security (aislamiento multi-tenant)
-- Activar RLS en toda tabla de negocio y limitar a las orgs del usuario.
-- ============================================================
alter table organizations     enable row level security;
alter table memberships       enable row level security;
alter table diagnostics       enable row level security;
alter table diagnostic_answers enable row level security;
alter table findings          enable row level security;
alter table systems           enable row level security;
alter table vendors           enable row level security;
alter table treatments        enable row level security;
alter table legal_bases       enable row level security;
alter table documents         enable row level security;
alter table evidence_events   enable row level security;

-- Política genérica: el usuario solo ve/gestiona filas de sus organizaciones.
-- (Repetir por tabla; se muestra el patrón con 'treatments'.)
create policy tenant_isolation_select on treatments
  for select using (organization_id in (select auth_org_ids()));
create policy tenant_isolation_modify on treatments
  for all using (organization_id in (select auth_org_ids()))
  with check (organization_id in (select auth_org_ids()));

-- organizations: el usuario ve las organizaciones donde es miembro
create policy org_visibility on organizations
  for select using (id in (select auth_org_ids()));

-- evidence_events: SELECT e INSERT permitidos; sin UPDATE/DELETE (inmutable)
create policy evidence_select on evidence_events
  for select using (organization_id in (select auth_org_ids()));
create policy evidence_insert on evidence_events
  for insert with check (organization_id in (select auth_org_ids()));

-- NOTA: replicar las políticas tenant_isolation_* en cada tabla de negocio
-- (diagnostics, diagnostic_answers, findings, systems, vendors, legal_bases, documents).
-- knowledge_chunks NO lleva RLS por tenant: es conocimiento global de solo lectura.
