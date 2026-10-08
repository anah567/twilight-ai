
# Importamos mock para simular respuestas de la IA
from unittest.mock import patch


# Función auxiliar para registrar un usuario e iniciar sesión
def create_user_token(client, username, email):

    # Registramos un usuario en la base temporal
    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Twilight123!"
        }
    )

    assert register_response.status_code == 201

    # Iniciamos sesión para obtener su token
    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Twilight123!"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


# Comprobamos que un usuario autenticado pueda conversar
def test_authenticated_chat(client):

    # Creamos una cuenta de prueba
    token = create_user_token(
        client, "bella", "bella@example.com"
    )

    # Simulamos la respuesta de Ollama para no depender del modelo real
    with patch(
        "backend.main.ask_agent",
        return_value="Edward Cullen is a vampire."
    ):

        response = client.post(
            "/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "Who is Edward Cullen?"}
        )

    # Verificamos que se cree una conversación
    assert response.status_code == 200
    assert response.json()["answer"] == "Edward Cullen is a vampire."
    assert isinstance(response.json()["conversation_id"], int)


# Comprobamos que no se pueda conversar sin autenticación
def test_chat_requires_authentication(client):

    response = client.post(
        "/chat",
        json={"question": "Who is Bella Swan?"}
    )

    assert response.status_code in (401, 403)


# Comprobamos que el historial guarde los mensajes
def test_conversation_history(client):

    token = create_user_token(
        client, "bella", "bella@example.com"
    )

    headers = {"Authorization": f"Bearer {token}"}

    # Simulamos la respuesta del agente
    with patch(
        "backend.main.ask_agent",
        return_value="Alice Cullen can see the future."
    ):

        chat_response = client.post(
            "/chat",
            headers=headers,
            json={"question": "What is Alice Cullen's ability?"}
        )

    assert chat_response.status_code == 200

    conversation_id = chat_response.json()["conversation_id"]

    # Consultamos la conversación creada
    response = client.get(
        f"/conversations/{conversation_id}",
        headers=headers
    )

    assert response.status_code == 200

    messages = response.json()["messages"]

    # Deben existir un mensaje del usuario y otro del asistente
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


# Comprobamos que un usuario no pueda consultar conversaciones ajenas
def test_conversation_isolation(client):

    # Creamos dos usuarios diferentes
    bella_token = create_user_token(
        client, "bella", "bella@example.com"
    )

    edward_token = create_user_token(
        client, "edward", "edward@example.com"
    )

    # Bella crea una conversación
    with patch(
        "backend.main.ask_agent",
        return_value="Twilight is a vampire romance story."
    ):

        response = client.post(
            "/chat",
            headers={
                "Authorization": f"Bearer {bella_token}"
            },
            json={"question": "What is Twilight about?"}
        )

    assert response.status_code == 200

    conversation_id = response.json()["conversation_id"]

    # Edward intenta consultar la conversación de Bella
    response = client.get(
        f"/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {edward_token}"
        }
    )

    # El backend no debe permitir el acceso
    assert response.status_code == 404
