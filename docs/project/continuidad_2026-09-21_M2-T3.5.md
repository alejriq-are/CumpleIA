# Continuidad — M2-T3.5 Proveedores y terceros

Fecha de cierre: 2026-09-21

## Estado

M2-T3.5 quedó funcionalmente completado y validado.

Avance RAT validado en interfaz: **9/10 requisitos de activación**.

El requisito resuelto en esta etapa corresponde a:

- `vendors_declaration` en estado `si` o `no`.

La activación completa del RAT continúa pendiente del requisito de transferencias internacionales.

## Alcance implementado

### Frontend

Se incorporó `TreatmentVendorsSection.tsx` a la ficha RAT.

La sección permite:

- declarar si intervienen proveedores u otras organizaciones externas;
- estados `si`, `no` y `pendiente`;
- seleccionar organizaciones existentes desde el catálogo;
- crear una nueva organización directamente desde el selector;
- crear múltiples relaciones proveedor/tratamiento;
- seleccionar el tipo de relación:
  - encargado de tratamiento;
  - cesionario;
  - otro tercero;
- registrar finalidad de la relación;
- indicar acceso a datos personales;
- indicar existencia de contrato o acuerdo documentado;
- exigir identificación o referencia del contrato/acuerdo cuando se declara su existencia;
- registrar objeto y duración del encargo únicamente cuando la relación es `encargado`;
- registrar uso de subencargados únicamente para relaciones de tipo `encargado`;
- limpiar campos específicos del encargo al cambiar a `cesionario` u `otro`;
- eliminar relaciones de una actividad;
- administrar el catálogo de organizaciones;
- eliminar organizaciones del catálogo cuando no se encuentran asociadas a actividades.

Se incorporó ayuda contextual para orientar al usuario en la clasificación:

- encargado de tratamiento;
- cesionario;
- otro tercero.

También se incorporó ayuda contextual sobre el documento contractual y sobre el uso de la referencia como mecanismo de trazabilidad en CumpleIA.

### API client

Se incorporaron tipos y operaciones para:

- `VendorCreate`
- `VendorUpdate`
- `VendorOut`
- `VendorRelationshipType`
- `TreatmentVendorIn`
- `TreatmentVendorOut`

Operaciones incorporadas:

- listar vendors;
- crear vendor;
- actualizar vendor;
- eliminar vendor;
- reemplazar relaciones de vendors de un tratamiento.

`TreatmentDetailOut.vendors` quedó tipado como `TreatmentVendorOut[]`.

### Backend

Se reforzó `eliminar_vendor()` para impedir eliminar una organización del catálogo cuando todavía se encuentra asociada a una o más actividades de tratamiento.

En ese caso el servicio responde con `HTTP 409 Conflict` y evita que el `ON DELETE CASCADE` elimine silenciosamente relaciones RAT existentes.

Se agregó cobertura API para verificar:

- DELETE de vendor asociado → `409`;
- la relación y el vendor permanecen disponibles después del intento.

## Validación funcional

Caso utilizado: actividad RAT `Gestión de clientes`.

Se verificó:

- declaración de proveedores;
- creación inline de proveedor;
- selección automática del proveedor creado;
- relaciones encargado / cesionario / otro;
- campos específicos de encargado;
- contrato/acuerdo y referencia obligatoria;
- ayuda contextual;
- administración del catálogo;
- creación y eliminación de proveedores;
- progreso RAT de **8/10 a 9/10**.

Resultado: PASS.

## Validación técnica

Backend completo:

`166 passed in 13.38s`

API RAT:

`6 passed in 1.49s`

Frontend:

`npm run type-check` → PASS

Calidad backend:

`ruff` → PASS

Integridad del diff:

`git diff --check` → PASS

## Nota de entorno

Después de una hibernación del notebook se detectó una desalineación local entre la credencial `APP_DATABASE_URL` del `.env` y la utilizada por el contenedor backend.

La credencial local fue resincronizada con la configuración activa del backend Docker sin incorporar secretos al repositorio.

La conexión de tests fue nuevamente validada como rol restringido `app_user`.

## Archivos principales de M2-T3.5

- `backend/app/services/rat.py`
- `backend/tests/test_api_rat.py`
- `frontend/components/rat/TreatmentGeneralForm.tsx`
- `frontend/components/rat/TreatmentVendorsSection.tsx`
- `frontend/lib/api/client.ts`

## Próximo paso

Implementar **Transferencias internacionales**, con el objetivo de completar el requisito restante y llevar el RAT de **9/10 a 10/10**.

La activación del tratamiento y la revisión final permanecen como etapas posteriores.
