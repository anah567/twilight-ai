
import { useEffect, useRef, useState } from "react";

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "../services/documentService";

import "../styles/DocumentLibrary.css";

// Iconos de la biblioteca
function DocumentIcon({ name, size = 22 }) {
  const icons = {
    upload: (
      <>
        <path d="M12 16V8m0 0-4 4m4-4 4 4" />
        <path d="M20 16.5a4.5 4.5 0 0 0-2.5-8.2A6 6 0 0 0 6 9a4 4 0 0 0-1 7.8" />
      </>
    ),
    file: (
      <>
        <path d="M7 3h7l5 5v13H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
        <path d="M14 3v6h5M9 13h6M9 17h6" />
      </>
    ),
    trash: (
      <>
        <path d="M4 7h16M10 4h4M6 7l1 14h10l1-14M10 11v6M14 11v6" />
      </>
    ),
    arrow: <path d="M19 12H5m0 0 6-6m-6 6 6 6" />,
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {icons[name]}
    </svg>
  );
}

// Solo permitimos archivos TXT
function isValidFile(file) {
  return Boolean(file && /\.txt$/i.test(file.name));
}

// Obtenemos el tipo de archivo a partir del nombre
function getFileType(filename) {
  const extension = filename?.split(".").pop()?.toUpperCase();
  return extension || "FILE";
}

export default function DocumentLibrary({ onBack }) {
  // Documentos guardados en FastAPI
  const [documents, setDocuments] = useState([]);
  const [totalDocuments, setTotalDocuments] = useState(0);

  // Estados de carga y mensajes
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  // Archivo seleccionado
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  // Documento que queremos eliminar
  const [documentToDelete, setDocumentToDelete] = useState(null);

  // Cargamos los documentos al entrar
  useEffect(() => {
    let mounted = true;

    getDocuments()
      .then((data) => {
        if (!mounted) return;

        setDocuments(data.documents);
        setTotalDocuments(data.total_documents);
        setError("");
      })
      .catch((error) => {
        if (mounted) {
          setError(error.message || "Unable to load documents.");
        }
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  // Seleccionamos un archivo
  const selectFile = (file) => {
    setUploadSuccess("");
    setError("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!isValidFile(file)) {
      setSelectedFile(null);
      setError("Only TXT files are supported.");
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    setSelectedFile(file);
  };

  // Abrimos el selector de archivos
  const handleBrowse = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  // Permitimos arrastrar archivos
  const handleDragOver = (event) => {
    event.preventDefault();

    if (!isUploading) {
      setIsDragging(true);
    }
  };

  // Detectamos cuando el archivo sale del recuadro
  const handleDragLeave = (event) => {
    event.preventDefault();

    if (!event.currentTarget.contains(event.relatedTarget)) {
      setIsDragging(false);
    }
  };

  // Recibimos el archivo arrastrado
  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    if (isUploading) return;

    const files = event.dataTransfer.files;

    if (files.length !== 1) {
      setSelectedFile(null);
      setError("Please select one TXT file at a time.");
      return;
    }

    selectFile(files[0]);
  };

  // Subimos el archivo a FastAPI
  const handleUpload = async (event) => {
    event.preventDefault();

    if (!selectedFile || isUploading) return;

    setIsUploading(true);
    setError("");
    setUploadSuccess("");

    try {
      const result = await uploadDocument(selectedFile);

      // Actualizamos la lista después de subirlo
      const updatedData = await getDocuments();

      setDocuments(updatedData.documents);
      setTotalDocuments(updatedData.total_documents);

      setUploadSuccess(
        `${result.filename} uploaded and indexed successfully.`
      );

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      setError(error.message || "Unable to upload document.");
    } finally {
      setIsUploading(false);
    }
  };

  // Eliminamos un documento después de confirmar
  const handleDelete = async () => {
    if (!documentToDelete || isDeleting) return;

    setIsDeleting(true);
    setError("");
    setUploadSuccess("");

    try {
      await deleteDocument(documentToDelete.document_id);

      const updatedData = await getDocuments();

      setDocuments(updatedData.documents);
      setTotalDocuments(updatedData.total_documents);
      setDocumentToDelete(null);
    } catch (error) {
      setError(error.message || "Unable to delete document.");
      setDocumentToDelete(null);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="document-library">
      {/* Encabezado */}
      <div className="document-library-header">
        <button
          type="button"
          className="document-back-button"
          onClick={onBack}
        >
          <DocumentIcon name="arrow" size={17} />
          Back to Chat
        </button>

        <div className="document-library-heading">
          <span className="document-library-moon">☾</span>

          <h1>
            Document <span>Library</span>
          </h1>

          <p>Explore the knowledge behind Twilight AI.</p>
        </div>
      </div>

      {/* Contador de documentos */}
      <div className="document-library-summary">
        <span>✧ KNOWLEDGE BASE</span>

        <strong>
          {totalDocuments}{" "}
          {totalDocuments === 1 ? "document" : "documents"}
        </strong>
      </div>

      {/* Subir documentos */}
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

        {/* Zona para seleccionar o arrastrar archivos */}
        <div
          className={`document-dropzone ${
            isDragging ? "document-dropzone-active" : ""
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <DocumentIcon name="upload" size={36} />

          <h4>Drop your documents here</h4>
          <p>or browse files from your device</p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,text/plain"
            className="document-file-input"
            onChange={(event) =>
              selectFile(event.target.files?.[0] || null)
            }
            disabled={isUploading}
            aria-label="Select a TXT document"
          />

          <button
            type="button"
            className="document-browse-button"
            onClick={handleBrowse}
            disabled={isUploading}
          >
            Browse Files
          </button>

          <span className="document-file-hint">
            TXT files only
          </span>
        </div>

        {/* Archivo seleccionado y botón de subida */}
        <div className="document-upload-actions">
          <div className="document-selected-file">
            {selectedFile ? (
              <>
                <DocumentIcon name="file" size={17} />
                <span title={selectedFile.name}>
                  {selectedFile.name}
                </span>
              </>
            ) : (
              <span>No file selected</span>
            )}
          </div>

          <button
            type="submit"
            disabled={!selectedFile || isUploading}
          >
            {isUploading ? "Uploading..." : "Upload Document"}
          </button>
        </div>
      </form>

      {/* Mensaje de éxito */}
      {uploadSuccess && (
        <p className="document-upload-success" role="status">
          ✧ {uploadSuccess}
        </p>
      )}

      {/* Mensajes de error */}
      {error && (
        <p className="document-library-error" role="alert">
          {error}
        </p>
      )}

      {/* Cargando documentos */}
      {isLoading && (
        <p className="document-library-status">
          Loading documents...
        </p>
      )}

      {/* Biblioteca vacía */}
      {!isLoading && !error && documents.length === 0 && (
        <p className="document-library-status">
          No documents available yet.
        </p>
      )}

      {/* Lista de documentos */}
      {!isLoading && (
        <div className="document-library-grid">
          {documents.map((document) => (
            <div
              key={document.document_id}
              className="document-library-card"
            >
              <div className="document-library-icon">
                <DocumentIcon name="file" size={23} />
              </div>

              <div className="document-library-card-info">
                <h3 title={document.filename}>
                  {document.filename}
                </h3>

                <p>{getFileType(document.filename)} document</p>

                {/* Mostramos el estado solo si existe */}
                {["ready", "processing", "failed"].includes(
                  String(document.status || "").toLowerCase()
                ) && (
                  <span className="document-card-status">
                    {document.status}
                  </span>
                )}
              </div>

              {/* Eliminar documento */}
              <button
                type="button"
                className="document-delete-button"
                onClick={() => setDocumentToDelete(document)}
                aria-label={`Delete ${document.filename}`}
                title="Delete document"
              >
                <DocumentIcon name="trash" size={19} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Confirmación para eliminar */}
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

            <h2 id="delete-document-title">
              Delete document?
            </h2>

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
