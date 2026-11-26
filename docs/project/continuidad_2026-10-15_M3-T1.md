# Continuidad M3-T1 — 2026-10-15

## 1. Alcance y procedencia

Verificacion de los hallazgos H1-H4 comunicados por el usuario tras revision con
Claude. No es una copia del adjunto original: ese archivo no estaba disponible
en el workspace. Rama feature/m3-t1-licitud-persistencia; base 507aa74.
Datos ficticios, sin merge/despliegue; confirmacion/activacion EIPD bloqueadas.

## 2. Hallazgos y correccion

- H1: test real contra PostgreSQL aislado, con migraciones del repositorio y
  runtime app_user. Antes el DELETE del padre no era rechazado; ahora RESTRICT
  protege ambos vinculos. c95f0a2b6d43 append-only; modelos alineados; downgrade
  rechaza restaurar cascadas con historial. Limpieza explicita solo en fixtures
  administrativas de prueba. Ninguna ruta de borrado agregada.
- H2: opt-in EIPD_CHILD_TEST_WRITES_ENABLED false por defecto, separado del
  entorno; escritura solo en development/test con habilitacion explicita.
  CI y runner aislado lo habilitan en sus procesos; .env.example mantiene false.
- H3: data_kind=ficticios permanece fijado en SQL. Plan MVP exige migracion nueva,
  politica/contratos revisados y conserva procedencia historica. No habilitado.
- H4: panel actualizado a MVP en desarrollo; status y balance vigentes distinguen
  evidencia actual de historia. Archivo/compactacion de documentos extensos
  pendiente, sin eliminar antecedentes en este bloque.

## 3. Validacion verificada

CI 507aa74: success en backend, frontend e integrada; 4451 backend aprobadas,
1 omitida; 76 frontend; 1 integrada.
https://github.com/alejriq-are/CumpleIA/actions/runs/38773784050

Correcciones: 78 pruebas enfocadas y 1 recorrido Chromium/API/PostgreSQL local
aprobados. c95f0a2b6d43 aplicada en base aislada y desarrollo local; checksum de
siete historiales intacto. No se crearon datos ficticios en base operativa.
Lint/formato/tipos y CI de la correccion se comprueban antes de cierre final;
consultar Actions del commit final, no extrapolar CI del commit anterior.

## 4. Pendientes

Interfaz para gestionar sucesores, verificacion/aceptacion juridica de politica,
criterios de ingreso de datos reales al MVP y compactacion documental separada.
La habilitacion explicita de pruebas no concede autoridad ni activa EIPD.
