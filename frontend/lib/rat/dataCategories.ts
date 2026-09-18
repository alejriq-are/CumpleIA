export type DataCategoryDefinition = {
  code: string;
  name: string;
  description: string;
  isSensitive: boolean;
};

export const DATA_CATEGORIES: DataCategoryDefinition[] = [
  {
    code: "identificacion",
    name: "Datos de identificación",
    description: "Nombre, apellidos, RUT, fecha de nacimiento, nacionalidad, estado civil.",
    isSensitive: false,
  },
  {
    code: "contacto",
    name: "Datos de contacto",
    description: "Dirección, correo electrónico, teléfono y dirección postal.",
    isSensitive: false,
  },
  {
    code: "laborales",
    name: "Datos laborales",
    description: "Cargo, remuneración, historial laboral, evaluaciones y asistencia.",
    isSensitive: false,
  },
  {
    code: "comerciales_financieros",
    name: "Datos comerciales y financieros",
    description: "Compras, facturación, datos bancarios e información crediticia.",
    isSensitive: false,
  },
  {
    code: "tecnologicos",
    name: "Datos tecnológicos",
    description:
      "Dirección IP, identificadores de dispositivos, cookies, geolocalización y navegación.",
    isSensitive: false,
  },
  {
    code: "origen_racial_etnico",
    name: "Origen racial o étnico",
    description: "Información relativa al origen racial o étnico.",
    isSensitive: true,
  },
  {
    code: "convicciones_religiosas_filosoficas_morales",
    name: "Convicciones religiosas, filosóficas o morales",
    description: "Información sobre convicciones religiosas, filosóficas o morales.",
    isSensitive: true,
  },
  {
    code: "opiniones_afiliaciones_politicas",
    name: "Opiniones o afiliaciones políticas",
    description: "Información sobre opiniones o afiliaciones políticas.",
    isSensitive: true,
  },
  {
    code: "afiliacion_sindical_gremial_asociativa",
    name: "Afiliación sindical, gremial o asociativa",
    description: "Información sobre afiliación sindical, gremial o asociativa.",
    isSensitive: true,
  },
  {
    code: "salud",
    name: "Datos de salud",
    description: "Información relativa a la salud de una persona.",
    isSensitive: true,
  },
  {
    code: "vida_sexual_afectiva_orientacion_sexual",
    name: "Vida sexual, afectiva u orientación sexual",
    description: "Información relativa a la vida sexual, afectiva u orientación sexual.",
    isSensitive: true,
  },
  {
    code: "biometricos",
    name: "Datos biométricos",
    description: "Por ejemplo, huella digital o reconocimiento facial.",
    isSensitive: true,
  },
  {
    code: "perfil_biologico_humano",
    name: "Perfil biológico humano",
    description: "Información relativa al perfil biológico humano.",
    isSensitive: true,
  },
  {
    code: "situacion_socioeconomica",
    name: "Situación socioeconómica",
    description: "Información relativa a la situación socioeconómica.",
    isSensitive: true,
  },
];
