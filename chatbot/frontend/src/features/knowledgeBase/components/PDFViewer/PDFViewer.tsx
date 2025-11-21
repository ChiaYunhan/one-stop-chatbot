import type { DocumentObject } from "../../../../types";
import { useState, useEffect } from "react";
import { getViewDocumentS3Link } from "../../services/KnowledgeBaseApi";
import { PDFSkeleton } from "./PDFSkeleton";

interface PDFViewerProps {
  selectedDocument: DocumentObject;
}

export default function PDFViewer({ selectedDocument }: PDFViewerProps) {
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load PDF document
  useEffect(() => {
    if (!selectedDocument) {
      setUrl(null);
      return;
    }

    const abort = new AbortController();
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        setUrl(null);

        const res = await getViewDocumentS3Link(selectedDocument, abort.signal);

        if (!cancelled) {
          setUrl(res.url);
          setLoading(false);
        }
      } catch (err: any) {
        if (err.name === "AbortError") return;
        if (!cancelled) {
          console.error(err);
          setError("Failed to load document");
          setLoading(false);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
      abort.abort();
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [selectedDocument]);

  useEffect(() => {
    return () => {
      if (url && url.startsWith("blob:")) {
        URL.revokeObjectURL(url);
      }
    };
  }, [url]);

  // UI States
  if (!selectedDocument) {
    return (
      <div className="pdf-viewer-container inactive">
        <div className="pdf-viewer-empty-state">
          <h3>No Document Selected</h3>
          <p>Select a document from the list to view it here.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pdf-viewer-container error">
        <div className="pdf-viewer-error-state">
          <h3>Error Loading Document</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    );
  }

  if (loading || !url) {
    return <PDFSkeleton />;
  }

  return (
    <div className="pdf-viewer-container active">
      <iframe src={url} width="100%" height="100%" title="PDF Viewer" />
    </div>
  );
}
