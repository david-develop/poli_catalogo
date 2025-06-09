# POLI APP

pre-requisitos:

- instalar python 3.12
- crear un entorno virtual

ejecutar:

- crear un entorno virtual
  ```python3 -m venv .venv```

- activar el entorno virtual
  ```.venv\Scripts\activate```

- instalar las dependencias
  ```pip install -r requirements.txt```

- ejecutar el programa
  ```python main.py```

## Uso de Swagger y autenticación OAuth2

### Acceso a la documentación interactiva (Swagger)

Después de iniciar la aplicación, abre tu navegador y accede a:

```http://localhost:8000/docs```

Aquí encontrarás la documentación interactiva generada automáticamente por FastAPI (Swagger UI). Puedes probar los
endpoints directamente desde esta interfaz.

### Primeros pasos:

1. Crea un usuario administrador:
    - Usa el endpoint `/auth/register` para registrar un nuevo usuario con el rol de administrador.
    - Proporciona un `username`, `password`, y `role` (debe ser "admin").
2. Crea un usuario normal:
    - Usa el mismo endpoint `/auth/register` para registrar un usuario normal.
    - Proporciona un `username`, `password`, y `role` (debe ser "shopper").
3. Agrega productos al catálogo:
    - Usa el endpoint `/productos/catalogo` para agregar productos.
    - Proporciona un `nombre`, `descripcion`, `precio`, y `cantidad`.
4. Para consultar productos debes loguearte (como shopper o admin) y obtener un token de acceso.


### Autenticación basada en tokens (OAuth2)

Para acceder a los endpoints protegidos necesitas token de acceso. Sigue estos pasos:

1. **Obtener un token:**
    - Haz una petición `POST` al endpoint `/auth/token` desde Swagger UI o usando `curl`.
    - Ingresa tu usuario y contraseña.
    - Recibirás un `access_token` en la respuesta.

2. **Usar el token con `curl`:**
    - Incluye el token en la cabecera `Authorization`:
      ```
      curl -H "Authorization: Bearer TU_TOKEN_AQUI" http://localhost:8000/productos/catalogo
      ```
3. **Usar autenticación en Swagger:**
    - En la interfaz de Swagger, haz clic en el botón "Authorize".
    - Ingresa las credenciales de usuario y contraseña. Puedes dejar el client_id y client_secret en blanco.
    - Swagger almacenará el token y lo incluirá automáticamente en las peticiones a los endpoints protegidos.
    