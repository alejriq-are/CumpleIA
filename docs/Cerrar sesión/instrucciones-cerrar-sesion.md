# Instrucciones: agregar "Cerrar sesión" en CumpleIA

## Objetivo
Agregar una opción de "Cerrar sesión" visible para el usuario autenticado, que termine la sesión de Supabase de forma segura y lo regrese al login.

## Requisitos funcionales

1. **Ubicación del control**
   Agregar un botón/enlace "Cerrar sesión" en el header, navbar o menú de usuario (donde ya exista, ej. junto al nombre/avatar del usuario) — visible en todas las páginas protegidas (dashboard, admin, etc.), no solo en una.

2. **Acción al hacer clic**
   ```js
   const { error } = await supabase.auth.signOut()
   ```
   - Si `error` es null, redirigir a `/login`.
   - Si hay error, mostrar un mensaje simple y no dejar al usuario en un estado ambiguo (igual limpiar el estado local y redirigir).

3. **Limpieza de estado en el cliente**
   Después del `signOut()`, asegurarse de:
   - Limpiar cualquier estado global/contexto de usuario (ej. `AuthContext`, store de usuario) para que la UI no muestre datos obsoletos tras cerrar sesión.
   - Si hay datos en caché sensibles (React Query, SWR, etc.), invalidar o limpiar las queries relacionadas al usuario.

4. **Middleware / rutas protegidas**
   Confirmar que `frontend/middleware.ts` (ya existente, tocado en el flujo de recuperación) redirige correctamente a `/login` cuando ya no hay sesión activa, para que después del logout no se pueda volver atrás con el botón del navegador y quedar en una página protegida con datos cacheados.

5. **Confirmación opcional (UX)**
   Si aplica al patrón de la app, considerar un pequeño confirm ("¿Seguro que quieres cerrar sesión?") antes de ejecutar el signOut, sobre todo si el botón está en un lugar donde un clic accidental sería molesto (ej. dentro de un menú desplegable).

## Criterios de aceptación
- Desde cualquier página protegida, el usuario puede cerrar sesión en un clic.
- Tras cerrar sesión, cae en `/login` y no puede acceder a rutas protegidas usando el botón "atrás" del navegador.
- No quedan datos del usuario anterior visibles en la UI tras el logout.
