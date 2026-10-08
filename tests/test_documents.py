
# Importamos herramientas para simular la base vectorial
from unittest.mock import MagicMock, patch

# Importamos herramientas para consultar usuarios
from sqlalchemy import select

# Importamos nuestra función auxiliar para crear usuarios
from tests.test_chat import create_user_token

# Importamos la base de datos y el modelo de usuario
from backend.database.database import get_db
from backend.database.models import User
from backend.main import app


# Comprobamos que un usuario normal no pueda eliminar documentos
def test_regular_user_cannot_delete_document(client):

    # Registramos a Edward y obtenemos su token
    token = create_user_token(
        client,
        "edward",
        "edward@example.com"
    )

    # Edward intenta eliminar un documento
    response = client.delete(
        "/documents/example-document-id",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    # El backend debe rechazar la operación
    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Administrator permissions required."
    )


# Comprobamos que no se puedan eliminar documentos sin iniciar sesión
def test_unauthenticated_user_cannot_delete_document(client):

    # Intentamos eliminar un documento sin enviar un token
    response = client.delete(
        "/documents/example-document-id"
    )

    # El backend debe exigir autenticación
    assert response.status_code in (401, 403)


# Comprobamos que un administrador pueda eliminar documentos
def test_admin_can_delete_document(client, tmp_path):

    # Registramos a Bella y obtenemos su token
    token = create_user_token(
        client,
        "bella",
        "bella@example.com"
    )

    # Accedemos a la base de datos temporal de la prueba
    db = next(app.dependency_overrides[get_db]())

    try:

        # Buscamos a Bella y le asignamos permisos de administrador
        bella = db.scalar(
            select(User).where(User.username == "bella")
        )

        bella.is_admin = True
        db.commit()

    finally:

        # Cerramos la sesión temporal
        db.close()

    # Creamos un identificador válido para el documento de prueba
    document_id = "a92c4cfd52f249b5ac9d89112d12707c"

    # Creamos una base vectorial simulada
    fake_vectorstore = MagicMock()

    # Simulamos que existe un documento con un fragmento
    fake_vectorstore.get.return_value = {
        "ids": ["test-chunk-1"],
        "metadatas": [
            {
                "document_id": document_id
            }
        ]
    }

    # Creamos un archivo ficticio dentro de la carpeta temporal
    test_file = tmp_path / f"{document_id}.txt"
    test_file.write_text(
        "Twilight test document",
        encoding="utf-8"
    )

    # Simulamos ChromaDB y la carpeta de almacenamiento
    with (
        patch(
            "backend.services.document_router.get_vectorstore",
            return_value=fake_vectorstore
        ),
        patch(
            "backend.services.document_router.UPLOAD_DIRECTORY",
            tmp_path
        )
    ):

        # Enviamos la solicitud con el token de Bella
        response = client.delete(
            f"/documents/{document_id}",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    # Verificamos que la eliminación sea exitosa
    assert response.status_code == 200

    # Comprobamos que ChromaDB recibió la orden de eliminar
    fake_vectorstore.delete.assert_called_once_with(
        ids=["test-chunk-1"]
    )

    # Verificamos que el archivo temporal también fue eliminado
    assert not test_file.exists()
