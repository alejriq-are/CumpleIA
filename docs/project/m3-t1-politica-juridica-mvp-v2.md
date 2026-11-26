# M3-T1 — Aceptación por la organización: gobierno del flujo

Estado vigente: responsabilidad definida por el usuario; flujo de aceptación
por organización pendiente de implementación. Solo datos ficticios hasta MVP,
EIPD bloqueada. Esta revisión sustituye la asignación de responsabilidad y el
bloqueo de desarrollo del [expediente V1](m3-t1-politica-juridica-mvp.md), cuyos
artefactos se conservan como antecedentes. No declara una aceptación real.

## Quién decide y quién registra

La organización responsable del tratamiento revisa y acepta sus políticas,
documentos y conclusiones mediante una persona facultada para actuar por ella.
El apoyo de un asesor jurídico es opcional en este diseño; no se exige nombrar
un revisor externo para seguir desarrollando. La organización y la persona que
registra su decisión son identidades distintas y ambas deben quedar trazadas.
No asumir que un usuario owner/admin acredita por sí solo representación o
facultad de aceptar; esa facultad debe definirse y comprobarse en el flujo.

El RAT aportado por el usuario, versión indicada en su nombre 20/11/2025,
distingue el rol por actividad: ClaveÚnica/FirmaGob como responsable y SIMPLE
como encargado (página 1). Apoya la distinción de roles, no acredita un acta de
aceptación ni una facultad personal de aprobación. Su checksum se conserva en
el [registro V2](policy-evidence/review-package-v2.json); no se sube el PDF aportado.
La definición legal de responsable atiende a quién decide fines y medios:
[BCN, artículo 2 letra n del texto reformado](https://www.bcn.cl/leychile/navegar?i=1209272).

CumpleIA es el producto que estamos construyendo. Debe registrar la decisión,
identidad y facultad del actor, organización, rol respecto del tratamiento,
versión/hash del documento y contexto, fecha, fundamento, alcance y evidencia.
En desarrollo, esos registros y actores se prueban con datos ficticios. No se
requiere una identidad de una plataforma operativa ni un acta real para desarrollar.
Un registro ficticio nunca se presenta como aprobación de una empresa real.

## Dos decisiones con alcances diferentes

- Aceptación de la organización: decisión sobre sus documentos y tratamientos;
  aislada por tenant. Cuando actúe como encargada, documentar el responsable por
  cuya cuenta actúa y la autoridad correspondiente, sin atribuirle automáticamente
  decisiones sobre fines/medios ajenos.
- Validación y publicación técnica de reglas globales de CumpleIA: gestión del
  producto, compatibilidad, pruebas y canales privilegiados. No es la aceptación
  jurídica de la organización. Su autorización no se concede por un acto del tenant.

El `accepted_by` del contrato global actual pertenece a ese control global;
no se reutiliza como acta de adopción de una organización. El flujo tenant necesita
su propio contrato versionado y evidencia append-only. No cambiar V1 de infancia,
sus snapshots, ni permisos globales para implementar ese flujo.

## Criterios de aceptación del próximo bloque funcional

1. Identificar organización responsable, rol por actividad y actor facultado;
   validar permiso en servidor, no solo en interfaz.
2. Registrar aceptación/rechazo/requiere cambios sobre documento y contexto exactos;
   conservar fundamento, evidencia y fecha, sin actualizar registros históricos.
3. Impedir aceptación por otro tenant/actor no facultado y marcar obsolescencia
   documental ante cambios; nunca transportar aceptación a una versión nueva.
4. Probar con organizaciones y personas ficticias: permisos, aislamiento,
   inmutabilidad, conflictos, contexto obsoleto y conservación del historial.
5. Mantener separados aceptación documental, confirmación y activación EIPD.
   Una aceptación no cambia la política global ni habilita positivos.

## Ajuste de salida a MVP

Se conservan los gates G1-G7 de V1 como propuesta de controles de producto.
G2 corresponde a la revisión/aceptación por el responsable de la organización
piloto, con persona facultada y evidencia; la calidad jurídica de las reglas
generales sigue requiriendo verificación de fuentes y control del producto.
G3 corresponde a contrato/controles técnicos, no a un aprobador jurídico externo.
G6 (datos reales) y G7 (activación EIPD) siguen separados y pendientes; no se
levanta ninguno por esta aclaración. Fuentes complementarias siguen por revisar.

La aclaración resuelve quién revisa y elimina ese bloqueo de diseño/desarrollo.
No cierra los gates de salida a MVP ni crea una aceptación real. Próximo paso:
implementar el flujo de aceptación documental de organización con datos ficticios.
