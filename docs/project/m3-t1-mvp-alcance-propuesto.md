# Siguiente bloque M3-T1: evidencia y alcance MVP propuestos

16/10/2026. Alcance documental confirmado por el usuario; no acta de liberacion.
EIPD bloqueada; pruebas ficticias; sin habilitacion de datos reales ni despliegue.

## Alcance confirmado

Propuesta: expediente documental de Bases de Licitud que incluya RAT, evaluacion
juridica/LIA y documento EIPD. Cada artefacto necesita identidad/version/contexto,
alcance de facultad y revision de obsolescencia propios; no reutilizar sin cambios
la FK de aceptacion actual, que solo referencia resoluciones sucesoras de infancia.
Consulta y descarga del expediente confirmadas: RAT asociado, evaluacion de
licitud/LIA y EIPD. No se extiende la aceptacion a otros documentos por inferencia.
La adopcion/versionado propio del RAT o LIA requieren otro contrato; este bloque
reune los documentos existentes sin modificar sus tablas o historial.

## Evidencia disponible y humana pendiente

La evidencia normativa publica es real; los datos de organizaciones de pruebas
siguen siendo ficticios. Consulta oficial realizada 16/10/2026:

- [Ley 21.719 en BCN](https://www.bcn.cl/leychile/navegar?i=1209272): texto
  normativo y disposiciones transitorias consultados. Conservar diferencia entre
  texto reformado y regimen temporal aplicable; revalidar para empresa piloto.
- [Publicacion original DO](https://www.diariooficial.interior.gob.cl/publicaciones/2024/12/13/44023/01/2583630.pdf):
  copia/checksum ya conservados en paquete V2, sin modificarlos.
- [Decreto 662, Hacienda, publicado 09/09/2026](https://www.leychile.cl/navegar?idNorma=1227971):
  reglamento sobre modelos de prevencion de infracciones. Articulos 1 y 3:
  adopcion voluntaria, caracterizacion mediante RAT y base de licitud/interes
  legitimo dentro del programa. No es lista de operaciones EIPD ni prueba de
  certificacion; aplicabilidad y vigencia requieren revision para el piloto.
- Lista/orientaciones especificas EIPD: no verificadas en busqueda oficial
  acotada. No se concluye inexistencia ni se cierra el pendiente por el Decreto 662.

Ninguna consulta automatica sustituye la decision de la persona facultada de la
organizacion. Faltan identidad/facultad/evidencia autenticas de empresa piloto,
fundamento y alcance revisados. No crear actas reales ni declarar aprobacion con
fixtures; no cargar datos reales durante desarrollo.

## Gates y evidencia de candidato

G1 alcance: definido como expediente documental, sin acto de liberacion. G2 revision juridica: pendiente de
organizacion piloto y fuentes aplicables. G3 contrato/politica: no promover V1;
G4 pruebas: aceptar solo CI del candidato exacto. G5 operacion: restauracion,
accesos/retencion/soporte e incidentes por validar. G6 datos reales: decision
separada y migracion/controles previos. G7 activacion EIPD: bloqueada por instruccion.
No simular cierre de gates con actas ficticias; un MVP documental puede excluir G7.

CI 5b3f29d: frontend/integrada aprobados; backend 4471 aprobadas, una omitida y
un fallo en prueba de roundtrip: faltaba retirar/restaurar migracion de aceptacion
antes/despues de la de infancia. Correccion local: orden de dependencias, sin
CASCADE ni cambio de migracion aplicada; 72 pruebas dirigidas aprobadas. CI del
commit corrector debe verificarse despues de publicar; no usar CI previa como pase.


## Implementacion y validacion

GET `/licitud/treatments/{tid}/assessments/{aid}/mvp-dossier/v1`, solo
entorno development/test, permiso view_content y suscripcion activa. API conserva
RLS y scope exacto. Bloqueo compartido de serie protege la lectura M3 frente a
escritores de la misma serie; no se bloquea ni publica el selector de politica.
Panel en la pagina del expediente permite consultar/descargar JSON sin guardar
contenido en almacenamiento local del navegador. Error de consulta retira paquete
y descarga anteriores; respuesta incompatible bloquea descarga.

Tres documentos: snapshot RAT asociado a la evaluacion (no inventario completo
ni certificacion de actualidad M2); evaluacion completa con LIA si fue aportada;
ultima resolucion sucesora EIPD, o documento previo identificado expresamente,
o ausencia explicita. Hashes de contenido y del paquete observado; fecha UTC.
Documento anterior no se promueve a cobertura infancia. Eventos de organizacion
solo sobre la resolucion exacta; sucesores no heredan eventos. Vigencia mostrada
es orientativa. Datos de RAT/M3 no tienen procedencia verificada por esta consulta.

Fuentes oficiales consultadas, copia DO con checksum comprobado y notas de
aplicabilidad; verificador juridico permanece null. G1 definido; G2-G5 pendientes,
G6/G7 bloqueados. mvp_ready/allows_real_data/authorizes_action/can_confirm false,
activacion deshabilitada. G4 no se cierra automaticamente por una CI aprobada.

78 backend dirigidas, ocho nuevas UI/cliente, tipos/lint/formato y una integrada
real: descarga JSON contrastada con resolucion/evento, scope y gates bloqueados.
No migraciones ni cambios de opt-in/politica global. Cierre juridico real,
operacion piloto, datos reales y activacion siguen fuera de este bloque.
