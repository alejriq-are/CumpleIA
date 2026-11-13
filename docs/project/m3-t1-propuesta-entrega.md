# M3-T1 — Propuesta de alcance de entrega inicial

Fecha: 2026-10-06. Estado: NO ADOPTADA como recorte de cierre.
Decisión del usuario 2026-10-06: continuar alcance integral (§43).
Se conserva esta propuesta como antecedente histórico.
M3-T1 permanece EN PROGRESO. Este documento no difiere requisitos por sí solo,
no habilita rutas y no autoriza commit, merge ni despliegue.

## Entrega propuesta

Backend de evaluación por finalidad: contratos cerrados/versionados, persistencia,
snapshot/hash M2, series/versiones, permisos y RLS, borrador, preparación,
confirmación/reemplazo y protección histórica.

| Capacidad | Alcance que se propone aceptar |
| --- | --- |
| Bases ordinarias | consentimiento_art12, interes_legitimo_art13d, contrato_precontractual_art13c, obligacion_legal_art13b, defensa_derechos_art13e y obligaciones_economicas_art13a, cada una con preparación propia |
| Sensibles | Consentimiento expreso del titular, condición consentimiento_expreso_art16, alcance conservador coincidente y expedientes completos |
| Geolocalización | Expediente específico preparado; no exime base ordinaria ni barreras concurrentes |
| Salud/perfil biológico | Primer soporte por consentimiento expreso, responsable, contexto otro documentado, fundamento sanitario y preparación general/sensible; cesión/muestras conservan sus condicionales propios |
| Screening EIPD | Respuestas y asociaciones vigentes; positivos y pendientes impiden confirmar |
| Rutas fuera de soporte | Detección, conservación documental y motivos explícitos de incompletitud/revisión; no aprobación automática |

Preparación es evaluación documental del producto, no verificación externa de
normas/evidencia ni certificación de licitud. Consentimiento de un régimen no
resuelve otro. Sin soporte granular por pares categoría/grupo.

## Trabajo que requiere continuar o diferir explícitamente

| Pendiente funcional | Resultado actual que debe conservarse | Próximo trabajo si se incorpora |
| --- | --- | --- |
| Representación sensible: representante legal/mandatario | Revisión aun con checklist general completo | Diseño de acreditación, vínculo, alcance y vigencia; contrato, asociaciones, evaluador y pruebas |
| Excepciones sensibles sin consentimiento | Ruta no implementada/revisión | Elegir supuesto concreto y diseñar expediente propio |
| Excepciones de salud y contextos restringidos | Revisión aun con referencias documentadas | Delimitar rutas/contextos y requisitos antes de habilitar |
| Biometría, infancia/adolescencia e investigación | Regímenes concurrentes detectados y bloqueados | Priorizar un régimen; diseño y aceptación independientes |
| Vulnerabilidad y cobertura parcial categoría/grupo | Revisión y cobertura conservadora actual | Delimitar criterios; matriz explícita de alcance cuando corresponda |

Estos pendientes no se marcan completados. Si se acepta la entrega inicial,
se conservarán como backlog explícito para ampliaciones posteriores, sin cambiar
los bloqueos actuales. Si se mantiene el alcance integral, M3-T1 debe continuar
implementando los regímenes pendientes; esta propuesta no permite cerrarlo.

Workflow completo EIPD ya está diferido por diseño. Interfaz frontend M3 no se
incorpora como requisito de esta propuesta backend; necesita roadmap propio.

## Evidencia disponible y límites

Suite completa posterior a corrección de metadata: 1429 passed en 140.69s.
Alembic check global aprobado; head único e28a0c3f6d97 aplicado localmente.
Formato/lint y whitespace correctos. Históricos especiales v1–v8/EIPD v1–v9.
HTTP real verifica seis bases y primer alcance de salud; concurrencia con RAT
real verifica consentimiento_art12 y coexistencia sensible/geolocalización/salud.
Concurrencia de las otras cinco bases conserva RAT simulado y PostgreSQL real.
No extrapolar cobertura de todas las combinaciones ni ensayo de downgrade.

## Condiciones para resolver cierre

1. Decidir expresamente entre entrega inicial y alcance integral.
2. Si se acepta entrega inicial, registrar diferimientos funcionales en backlog
   y actualizar la matriz de aceptación alrededor de ese alcance aprobado.
3. Revisar el conjunto completo de archivos, incluidos los nuevos sin seguimiento,
   y las limitaciones de evidencia; resolver cualquier hallazgo material.
4. Solo después evaluar el cambio de estado a DONE. No confundir aceptación
   de alcance, finalización funcional y publicación del código.

Siguiente paso dependiente: decisión de alcance. Este paso solo crea propuesta
revisable; sin cambios de código, pruebas reejecutadas, migraciones ni commit.
