# Instrucciones: agregar "Recuperar contraseña" en CumpleIA

## Objetivo
En la página de inicio/login de la app, agregar un enlace "¿Olvidaste tu contraseña?" que permita al usuario recuperar el acceso sin depender de un administrador, usando Supabase Auth.

## Problema actual a corregir
Al enviar el correo de recuperación desde el dashboard de Supabase, el link deja al usuario logueado directamente en la app, sin pedirle una nueva contraseña. Esto ocurre porque no existe una ruta/página que capture el evento de recuperación y muestre un formulario para definir la nueva clave. Hay que corregir esto como parte de esta tarea.

## Requisitos funcionales

1. **Enlace en el login**
   Agregar un link "¿Olvidaste tu contraseña?" debajo del formulario de inicio de sesión.

2. **Formulario de solicitud**
   Al hacer clic, mostrar un formulario que pida el email y llame a:
   ```js
   await supabase.auth.resetPasswordForEmail(email, {
     redirectTo: 'https://<dominio-de-cumpleia>/reset-password',
   })
   ```
   Mostrar un mensaje de confirmación ("Revisa tu correo") sin indicar si el email existe o no (evitar filtrar qué correos están registrados).

3. **Nueva ruta `/reset-password`**
   Crear una página/ruta dedicada que:
   - Detecte que el usuario llegó desde un link de recuperación. Con supabase-js v2, escuchar el evento `PASSWORD_RECOVERY`:
     ```js
     supabase.auth.onAuthStateChange((event, session) => {
       if (event === 'PASSWORD_RECOVERY') {
         // mostrar formulario de nueva contraseña
       }
     })
     ```
   - Mostrar un formulario con "Nueva contraseña" + "Confirmar contraseña".
   - Al enviar, llamar a:
     ```js
     const { error } = await supabase.auth.updateUser({ password: nuevaClave })
     ```
   - Si `error` es null, redirigir al login (o a la app) con mensaje de éxito.
   - Validar longitud mínima (Supabase exige 6 caracteres por defecto; usar al menos 8).

4. **No permitir acceso silencioso**
   Mientras el usuario esté en el flujo de recuperación (evento `PASSWORD_RECOVERY` activo) y no haya definido la nueva clave, no debe poder navegar libremente por la app con esa sesión temporal — debe quedar forzado en `/reset-password` hasta completar el cambio.

## Configuración requerida en Supabase (fuera del código)
En el dashboard: **Authentication → URL Configuration → Redirect URLs**, agregar:
```
https://<dominio-de-cumpleia>/reset-password
```
Sin esto, Supabase rechaza el `redirectTo` y el link de recuperación no funcionará.

## Criterios de aceptación
- Un usuario que olvidó su clave puede recuperarla sin intervención manual del administrador.
- Al hacer clic en el link del correo, se le pide explícitamente una nueva contraseña antes de darle acceso pleno a la app.
- El flujo funciona de principio a fin: solicitud → correo → nueva clave → login exitoso con la nueva clave.
