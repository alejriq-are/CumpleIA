export type DataSubjectDefinition = {
  code: string;
  name: string;
  description: string;
};

export const DATA_SUBJECTS: DataSubjectDefinition[] = [
  {
    code: "clientes",
    name: "Clientes",
    description: "Personas naturales que mantienen o han mantenido una relación comercial.",
  },
  {
    code: "trabajadores",
    name: "Trabajadores",
    description: "Trabajadores, ex trabajadores y personal de la organización.",
  },
  {
    code: "proveedores",
    name: "Proveedores",
    description: "Personas naturales proveedoras o representantes de proveedores.",
  },
  {
    code: "usuarios",
    name: "Usuarios",
    description: "Usuarios de sitios web, aplicaciones, plataformas o servicios.",
  },
  {
    code: "terceros",
    name: "Terceros",
    description: "Otras personas naturales relacionadas con la actividad de tratamiento.",
  },
];
