
import { useEffect, useState } from "react";
import {
    getDocuments,
    uploadDocument,
    deleteDocument,
} from "../services/documentService";
import "../styles/DocumentLibrary.css";

export default function DocumentLibrary({ onBack }) {

    // Guardamos los documentos recibidos desde FastAPI
    const [documents, setDocuments] = useState([]);

    // Guardamos el número total de documentos
    const [totalDocuments, setTotalDocuments] = useState(0);

    // Controlamos el estado de carga
    const [isLoading, setIsLoading] = useState(true);

    // Guardamos posibles errores
    const [error, setError] = useState("");

    // Archivo seleccionado para subir
    const [selectedFile, setSelectedFile] = useState(null);

    // Controlamos si se está subiendo un documento
    const [isUploading, setIsUploading] = useState(false);

    // Mensaje de éxito al subir un documento
    const [uploadSuccess, setUploadSuccess] = useState("");

    // Documento que el administrador desea eliminar
    const [documentToDelete, setDocumentToDelete] = useState(null);

    // Indicamos si estamos eliminando un documento
    const [isDeleting, setIsDeleting] = useState(false);

    // Consultamos los documentos cuando se abre la biblioteca
    useEffect(() => {
        const loadDocuments = async () => {
            try {
                const data = await getDocuments();

                setDocuments(data.documents);
                setTotalDocuments(data.total_documents);
                setError("");

            } catch (error) {
                setError(
                    error.message || "Unable to load documents."
                );

            } finally {
                setIsLoading(false);
            }
        };

        loadDocuments();
    }, []);

    // Subimos un documento y actualizamos la biblioteca
    const handleUpload = async (event) => {
        event.preventDefault();

        // Guardamos el formulario para poder limpiarlo después
        const form = event.currentTarget;

        if (!selectedFile || isUploading) return;

        setIsUploading(true);
        setUploadSuccess("");
        setError("");

        try {
            // Enviamos el archivo a FastAPI
            const result = await uploadDocument(selectedFile);

            // Consultamos nuevamente los documentos
            const updatedData = await getDocuments();

            setDocuments(updatedData.documents);
            setTotalDocuments(updatedData.total_documents);

            // Mostramos el mensaje de éxito
            setUploadSuccess(
                `${result.filename} uploaded and indexed successfully.`
            );

            // Limpiamos el archivo seleccionado
            setSelectedFile(null);

            // Reiniciamos el campo de selección
            form.reset();
        } catch (error) {
            setError(
                error.message || "Unable to upload document."
            );
        } finally {
            setIsUploading(false);
        }
    };

    // Eliminamos un documento después de confirmar
    const handleDelete = async () => {
        if (!documentToDelete || isDeleting) return;

        setIsDeleting(true);
        setError("");

        try {
            // Solicitamos al backend eliminar el documento
            await deleteDocument(documentToDelete.document_id);

            // Actualizamos el listado desde FastAPI
            const updatedData = await getDocuments();

            setDocuments(updatedData.documents);
            setTotalDocuments(updatedData.total_documents);

            // Cerramos la confirmación
            setDocumentToDelete(null);
        } catch (error) {
            setError(
                error.message || "Unable to delete document."
            );
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <div className="document-library">

            {/* Encabezado de la biblioteca */}
            <div className="document-library-header">

                <button
                    type="button"
                    className="document-back-button"
                    onClick={onBack}
                >
                    ← Back to Chat
                </button>

                <div className="document-library-heading">
                    <span className="document-library-moon">☾</span>

                    <h1>
                        Document <span>Library</span>
                    </h1>

                    <p>
                        Explore the knowledge behind Twilight AI.
                    </p>
                </div>

            </div>

            {/* Resumen de documentos */}
            <div className="document-library-summary">
                <span>✧ KNOWLEDGE BASE</span>

                <strong>
                    {totalDocuments} {totalDocuments === 1 ? "document" : "documents"}
                </strong>
            </div>

            {/* Formulario para subir documentos */}
            <form
                className="document-upload-form"
                onSubmit={handleUpload}
            >
                <div className="document-upload-info">
                    <span className="document-upload-icon">✧</span>

                    <div>
                        <h3>Expand the Twilight universe</h3>
                        <p>Upload a new document to the knowledge base.</p>
                    </div>
                </div>

                <div className="document-upload-actions">
                    <input
                        type="file"
                        accept=".txt,text/plain"
                        onChange={(event) => {
                            setSelectedFile(event.target.files?.[0] || null);
                            setUploadSuccess("");
                        }}
                        disabled={isUploading}
                        aria-label="Select a document"
                    />

                    <button
                        type="submit"
                        disabled={!selectedFile || isUploading}
                    >
                        {isUploading ? "Uploading..." : "Upload Document"}
                    </button>
                </div>
            </form>

            {uploadSuccess && (
                <p className="document-upload-success" role="status">
                    ✧ {uploadSuccess}
                </p>
            )}

            {/* Estado de carga */}
            {isLoading && (
                <p className="document-library-status">
                    Loading documents...
                </p>
            )}

            {/* Mensajes de error */}
            {!isLoading && error && (
                <p className="document-library-error" role="alert">
                    {error}
                </p>
            )}

            {/* Biblioteca vacía */}
            {!isLoading && !error && documents.length === 0 && (
                <p className="document-library-status">
                    No documents available yet.
                </p>
            )}

            {/* Documentos registrados */}
            {!isLoading && !error && (
                <div className="document-library-grid">

                    {documents.map((document) => (
                        <div
                            key={document.document_id}
                            className="document-library-card"
                        >
                            <div className="document-library-icon">
                                ▤
                            </div>

                            <div className="document-library-card-info">
                                <h3>{document.filename}</h3>
                                <p>Twilight knowledge document</p>
                            </div>

                            <button
                                type="button"
                                className="document-delete-button"
                                onClick={() => setDocumentToDelete(document)}
                                aria-label={`Delete ${document.filename}`}
                                title="Delete document"
                            >
                                🗑
                            </button>
                        </div>
                    ))}

                </div>
            )}

            {/* Confirmación antes de eliminar un documento */}
            {documentToDelete && (
                <div className="document-delete-overlay">
                    <div
                        className="document-delete-modal"
                        role="alertdialog"
                        aria-modal="true"
                        aria-labelledby="delete-document-title"
                        aria-describedby="delete-document-description"
                    >
                        <span className="document-delete-moon">☾</span>

                        <h2 id="delete-document-title">Delete document?</h2>

                        <p id="delete-document-description">
                            Are you sure you want to delete{" "}
                            <strong>{documentToDelete.filename}</strong>?
                            This action cannot be undone.
                        </p>

                        <div className="document-delete-actions">
                            <button
                                type="button"
                                className="document-delete-cancel"
                                onClick={() => setDocumentToDelete(null)}
                                disabled={isDeleting}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="document-delete-confirm"
                                onClick={handleDelete}
                                disabled={isDeleting}
                            >
                                {isDeleting ? "Deleting..." : "Delete Document"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
}
