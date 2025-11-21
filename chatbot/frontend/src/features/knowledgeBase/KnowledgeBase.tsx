import type { DocumentObject } from "../../types";
import { useEffect, useState } from "react";
import { getKnowledgeBaseDocuments } from "./services/KnowledgeBaseApi";
import { deleteDocuments } from "./services/KnowledgeBaseApi";

import TopBar from "./components/TopBar/TopBar";
import DocumentList from "./components/DocumentList";
import PDFViewer from "./components/PDFViewer/PDFViewer";

function KnowledgeBase() {
  const [documentList, setDocumentList] = useState<DocumentObject[]>([]);
  const [selectedDocId, setDocId] = useState<string | null>(null);
  const [inSelectionView, setInSelectionView] = useState<boolean>(false);
  const [selectedDocuments, setSelectedDocuments] = useState<DocumentObject[]>(
    []
  );
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const selectedDocument = documentList.find((doc) => doc.id === selectedDocId);

  useEffect(() => {
    async function fetchDocs() {
      const response = await getKnowledgeBaseDocuments("");
      setDocumentList(response.documentDetails);
    }

    fetchDocs();
  }, []);

  // Clear selections when exiting selection mode
  useEffect(() => {
    if (!inSelectionView) {
      setSelectedDocuments([]);
    }
  }, [inSelectionView]);

  const handleDocumentSelect = (docId: string) => {
    if (inSelectionView) {
      const document = documentList.find((doc) => doc.id === docId);
      if (!document) return;

      setSelectedDocuments((prev) => {
        const isAlreadySelected = prev.some((doc) => doc.id === docId);
        if (isAlreadySelected) {
          return prev.filter((doc) => doc.id !== docId);
        } else {
          return [...prev, document];
        }
      });
    } else {
      setDocId(docId);
    }
  };

  const handleSelectAll = () => {
    if (selectedDocuments.length === documentList.length) {
      setSelectedDocuments([]);
    } else {
      setSelectedDocuments([...documentList]);
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedDocuments.length === 0) return;

    const confirmMessage =
      selectedDocuments.length === 1
        ? `Are you sure you want to delete "${selectedDocuments[0].displayName}"?`
        : `Are you sure you want to delete ${
            selectedDocuments.length
          } documents?\n\n${selectedDocuments
            .map((doc) => doc.displayName)
            .join("\n")}`;

    const confirmDelete = window.confirm(confirmMessage);
    if (!confirmDelete) return;

    setIsDeleting(true);

    try {
      // Send full DocumentObject array to backend
      const result = await deleteDocuments(selectedDocuments);

      if (result.success) {
        // Remove successfully deleted documents from local state
        const deletedIds = selectedDocuments
          .filter((doc) => !result.failedIds.includes(doc.id))
          .map((doc) => doc.id);

        setDocumentList((prev) =>
          prev.filter((doc) => !deletedIds.includes(doc.id))
        );

        // Clear selected document if it was deleted
        if (selectedDocId && deletedIds.includes(selectedDocId)) {
          setDocId(null);
        }

        // Show success message
        let message = `${result.deletedCount} document(s) deleted successfully`;
        if (result.failedIds.length > 0) {
          message += `\n${result.failedIds.length} document(s) failed to delete`;
          if (result.failedDocuments && result.failedDocuments.length > 0) {
            message += `:\n${result.failedDocuments
              .map((doc) => `- ${doc.displayName} (Status: ${doc.status})`)
              .join("\n")}`;
          }
        }
        alert(message);

        // Clear selections and exit selection mode
        setSelectedDocuments([]);
        setInSelectionView(false);
      } else {
        alert(`Failed to delete documents: ${result.message}`);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to delete documents";
      alert(errorMessage);
      console.error("Delete error:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCancelSelection = () => {
    setInSelectionView(false);
    setSelectedDocuments([]);
  };

  // Helper function to get selected document IDs for the DocumentList component
  const selectedDocumentIds = selectedDocuments.map((doc) => doc.id);

  return (
    <div className="knowledge-base-container">
      <div className="knowledge-base-top">
        <TopBar
          inSelectionView={inSelectionView}
          onSelectionView={setInSelectionView}
          selectedCount={selectedDocuments.length}
          totalCount={documentList.length}
          onSelectAll={handleSelectAll}
          onDeleteSelected={handleDeleteSelected}
          onCancel={handleCancelSelection}
          isDeleting={isDeleting}
          selectedDocuments={selectedDocuments}
        />
      </div>
      <div className="knowledge-base-main">
        <DocumentList
          selectedDocId={selectedDocId}
          documentList={documentList}
          onSelectDocument={handleDocumentSelect}
          inSelectionView={inSelectionView}
          selectedDocuments={selectedDocumentIds}
        />
        {!inSelectionView && <PDFViewer selectedDocument={selectedDocument} />}
      </div>
    </div>
  );
}

export default KnowledgeBase;
