export type Requirement = {
  criterion_id: string | null;
  field: string;
  code: string;
  resolution: "no_aplica" | "respaldo_equivalente" | null;
};
export type Finding = Omit<Requirement, "resolution"> & { classification: string };
export type BaseMaterial = {
  document_type: "base_fundamento";
  saved_assessment: Record<string, unknown> & {
    id: string;
    organization_id: string;
    treatment_id: string;
  };
  primary_form: { kind: string; content: Record<string, unknown> | null } | null;
  alternatives: Record<string, unknown>;
  annexes: { id: string; reference: string; revision: number; version: number; sha256: string }[];
  diagnostic: {
    criteria: { id: string; label: string }[];
    findings: Finding[];
    coverage_pending: string[];
  };
};
export type BasePreview = {
  source_hash: string;
  latest_version: number;
  bundle: BaseMaterial;
  favorable_requirements: Requirement[];
};
export type BaseVersionItem = { id: string; version: number; reason: string; created_at: string };
export type BaseVersion = BaseVersionItem & {
  organization_id: string;
  treatment_id: string;
  assessment_id: string;
  created_by: string;
  request_id: string;
  source_hash: string;
  bundle: BaseMaterial;
  favorable_requirements: Requirement[];
};
