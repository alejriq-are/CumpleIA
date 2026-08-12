# Modelo de datos

## Núcleo multi-tenant

- `Organization`
- `Profile`
- `Membership`
- `Subscription`

Roles de membresía: `owner`, `admin`, `editor`, `viewer`. El superadmin de plataforma se representa con `Profile.is_superadmin`.

## Catálogo/configuración del Autodiagnóstico

- `Obligacion`
- `Seccion`
- `Pregunta`
- `ConfigVersion`
- `ConfigSeccionPeso`
- `ConfigPreguntaRiesgo`

Cada diagnóstico queda asociado a una versión de configuración para mantener reproducibilidad histórica de pesos/riesgos.

## Módulo 1

- `Diagnostic`
- `DiagnosticAnswer`
- `Finding`
- `ReferenceDocument`

### Restricción importante

`Diagnostic.organization_id` es `unique=True`. En el modelo actual existe **como máximo un diagnóstico por organización**. Esto impide implementar comparación histórica/re-evaluaciones sin cambiar esa decisión.

## Scaffolding para módulos 2-5

Los modelos ya existen, aunque los módulos todavía no están construidos:

- `System`
- `Vendor`
- `Treatment`
- `LegalBase`
- `Document`
- `EvidenceEvent`

Esto es una base útil, pero **no debe confundirse con funcionalidad disponible**.

## RAG

- `KnowledgeChunk`
  - `source`
  - `reference`
  - `content`
  - `embedding Vector(1024)`

La dimensión 1024 está acoplada al modelo de embeddings actual. Cambiar a un proveedor/modelo con otra dimensión exige migración o estrategia de compatibilidad.

## Fuente autoritativa del esquema

1. Migraciones Alembic.
2. Modelos SQLAlchemy, que deben concordar con las migraciones.
3. `schema.sql` solamente como documento histórico de Fase 0.
