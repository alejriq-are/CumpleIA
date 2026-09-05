# Ronda 3 — Selector de organización activa

Implementa el selector de organización activa definido en F1.22A.

1. Crea `frontend/lib/active-organization.ts`, con una función exportada que
   reciba las membresías y el valor opcional de `searchParams.organization`.
   Debe devolver sólo una membresía presente en la lista: la de id coincidente
   si es válida, o la primera como fallback seguro.
2. En `/dashboard/organizacion` y `/dashboard/autodiagnostico`, lee el
   parámetro `organization`, usa el helper y propaga la membresía resultante.
   No uses directamente `organizaciones[0]` cuando exista una selección válida.
3. Crea un componente cliente reutilizable accesible con etiqueta visible o
   `aria-label` que liste las organizaciones y actualice el parámetro
   `organization` al seleccionar otra.
4. Conserva los estados de sesión ausente y lista vacía. No cambies backend,
   migraciones, RLS, contratos API ni assets bajo `docs/benchmark/runner/`.
5. Agrega o modifica tests frontend relacionados.
