
# Probamos que un usuario pueda registrarse correctamente
def test_register_user(client):

    # Preparamos los datos de un usuario nuevo
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Twilight123!"
    }

    # Enviamos una solicitud para registrar al usuario
    response = client.post(
        "/auth/register",
        json=user_data
    )

    # Verificamos que el registro sea exitoso
    assert response.status_code == 201

    # Convertimos la respuesta a un diccionario
    data = response.json()

    # Verificamos que se guarden los datos correctos
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["is_active"] is True

    # Verificamos que la contraseña no aparezca en la respuesta
    assert "password" not in data
    assert "hashed_password" not in data


# Probamos que no se puedan registrar correos duplicados
def test_register_duplicate_email(client):

    # Preparamos los datos del primer usuario
    first_user = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Twilight123!"
    }

    # Registramos el primer usuario
    first_response = client.post(
        "/auth/register",
        json=first_user
    )

    # Confirmamos que el primer registro fue exitoso
    assert first_response.status_code == 201

    # Intentamos registrar otro usuario con el mismo correo
    second_user = {
        "username": "rosalie",
        "email": "alice@example.com",
        "password": "Twilight456!"
    }

    response = client.post(
        "/auth/register",
        json=second_user
    )

    # Verificamos que el backend rechace el correo duplicado
    assert response.status_code == 409



# Probamos que un usuario pueda iniciar sesión correctamente
def test_login_user(client):

    # Registramos un usuario en la base de datos temporal
    user_data = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Twilight123!"
    }

    client.post("/auth/register", json=user_data)

    # Intentamos iniciar sesión con sus credenciales
    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "Twilight123!"
        }
    )

    # Verificamos que el inicio de sesión sea exitoso
    assert response.status_code == 200

    # Verificamos que recibimos un token JWT
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert data["token_type"] == "bearer"


# Probamos que una contraseña incorrecta sea rechazada
def test_login_wrong_password(client):

    # Registramos un usuario de prueba
    client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Twilight123!"
        }
    )

    # Intentamos ingresar con una contraseña incorrecta
    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "WrongPassword123!"
        }
    )

    # Verificamos que el acceso sea rechazado
    assert response.status_code == 401


# Probamos que un correo inexistente sea rechazado
def test_login_unknown_email(client):

    # Intentamos ingresar con una cuenta que no existe
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "Twilight123!"
        }
    )

    # Verificamos que el acceso sea rechazado
    assert response.status_code == 401


# Probamos que no se puedan registrar nombres de usuario duplicados
def test_register_duplicate_username(client):

    # Registramos el primer usuario
    first_response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Twilight123!"
        }
    )

    assert first_response.status_code == 201

    # Intentamos registrar otro usuario con el mismo nombre
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "another@example.com",
            "password": "Twilight456!"
        }
    )

    # Verificamos que el nombre duplicado sea rechazado
    assert response.status_code == 409


# Probamos que no se acepten contraseñas demasiado cortas
def test_register_short_password(client):

    # Intentamos registrar una contraseña menor a 8 caracteres
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "123"
        }
    )

    # FastAPI debe rechazar los datos inválidos
    assert response.status_code == 422


# Probamos que un usuario normal no pueda subir documentos
def test_regular_user_cannot_upload(client):

    # Registramos un usuario normal
    client.post(
        "/auth/register",
        json={
            "username": "edward",
            "email": "edward@example.com",
            "password": "Twilight123!"
        }
    )

    # Iniciamos sesión para obtener su token
    login_response = client.post(
        "/auth/login",
        json={
            "email": "edward@example.com",
            "password": "Twilight123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Intentamos subir un archivo con sus credenciales
    response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "test.txt",
                b"Twilight test document",
                "text/plain"
            )
        }
    )

    # El usuario normal no debe tener permisos
    assert response.status_code == 403

    # Verificamos el mensaje de autorización
    assert response.json()["detail"] == (
        "Administrator permissions required."
    )


# Probamos que un usuario sin token no pueda subir documentos
def test_unauthenticated_user_cannot_upload(client):

    # Intentamos subir un documento sin iniciar sesión
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                b"Twilight test document",
                "text/plain"
            )
        }
    )

    # El backend debe rechazar la solicitud
    assert response.status_code in (401, 403)
