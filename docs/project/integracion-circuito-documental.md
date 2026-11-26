# Plan de integración del circuito documental

Base comparada `origin/main` en `8d27280`. Entrega publicada `07d4422` en `origin/feature/base-fundamento-5d1`. La simulación de merge encontró un camino sin conflictos. El alcance acumulado comprende 321 commits y 501 archivos.

| Orden | Lote | Corte candidato y condición |
| --- | --- | --- |
| 1 | Fundamentos de Licitud sobre RAT | `2fd8881`. Incluye persistencia, RLS, contexto RAT y borrador de evaluación. Validar los servicios desde el esquema de main. Este corte todavía carece de rutas HTTP de Licitud. |
| 2 | Controles de EIPD y administración de políticas | `82e0b50` como punto de revisión. Confirmar migraciones, roles de administración y política deshabilitada. |
| 3 | Expedientes, formularios y navegación acumulados | Inventariar desde `82e0b50` hasta `a5a51c3`. El corte final incluye el contrato 5A. Dividir por hitos publicados tras comprobar que cada corte es ejecutable. |
| 4 | Versiones EIPD general | `f9a3b31` reúne servidor e interfaz de 5B.1 y 5B.2. Depende de la persistencia, el contexto y la navegación anteriores. |
| 5 | Revisión y decisión EIPD general | `5de7b10` cierra el recorrido de revisión. `7087c47` incluye decisión y guía de actuaciones. Revisar como dos PRs si el primer corte es integrable por sí solo. |
| 6 | Base y fundamento | `b9f91ab` para 5D.1 y `07d4422` para 5D.2. Verificar las migraciones en secuencia y los historiales por versión. |

## Primer PR candidato

Comparar `8d27280..2fd8881`. El corte comprende cuatro commits y nueve archivos. Revisar los contratos de persistencia y borrador, la cadena de migraciones y el volumen de documentación incluido antes de abrir el PR.

1. Preparar un checkout limpio en el corte candidato.
2. Aplicar en PostgreSQL aislado las migraciones desde el estado de main. Verificar que los datos RAT sigan consultables.
3. Probar en la capa de servicios la creación y edición de borradores, construcción del contexto RAT y aislamiento por organización con el rol real de aplicación.
4. Registrar los resultados y preparar el PR. Usar el nuevo estado de main como base efectiva del lote siguiente.

Los cortes de la tabla son candidatos de revisión. Si se usan PRs encadenados, conservar la ascendencia con merges o actualizar la base de cada PR tras un squash. Comprobar el diff efectivo antes de cada integración.

La primera incorporación de rutas HTTP de Licitud aparece en `6d9bb76`. Ese corte acumulado amplía la comparación con main a cinco commits y 70 archivos. Si la primera entrega debe exponer una API, revisar ese salto y sus dependencias antes de seleccionarlo.

## Validación del primer corte

El esquema de `8d27280` llegó a `48fe0b9c21e4` en PostgreSQL aislado. Sobre esa base se aplicó la migración `5997a757f17b` del corte `2fd8881`. Pasaron 97 pruebas de esquemas, servicios de Licitud y aislamiento RLS con el rol de aplicación. En una segunda base aislada se creó un tratamiento RAT ficticio con su finalidad antes de aplicar la migración. Las filas completas coincidieron antes y después. La consulta con `app_user` devolvió ambos registros con la identidad de la organización y quedó filtrada cuando faltaba esa identidad.

## Primer PR listo para revisión

El [PR #31](https://github.com/alejriq-are/CumpleIA/pull/31) apunta a main desde `integration/licitud-persistencia`. GitHub aprobó Backend y Frontend en `fde0787`, que añadió ajustes de importaciones y formato para cumplir la CI del corte.

Base `main` en `8d27280`. Corte candidato `2fd8881`, con cuatro commits y nueve archivos. Incorpora la migración `5997a757f17b`, el contexto documental de RAT y los servicios de borrador. La validación incluye 97 pruebas dirigidas y la conservación de un tratamiento RAT y su finalidad preexistentes en PostgreSQL aislado. La primera entrega corresponde a persistencia y servicios internos. Las rutas HTTP quedan para un corte posterior.

Próximo paso. Revisar el PR #31 antes de integrarlo y volver a comparar el lote siguiente con la base efectiva de main.
