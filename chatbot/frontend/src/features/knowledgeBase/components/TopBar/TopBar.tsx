import { useState } from "react";
import UploadModal from "../UploadModal";
import SyncKnowledgeBaseButton from "./SyncKnowledgeBaseButton";
import type { DocumentObject } from "../../../../types";
import { getKnowledgeBaseDocuments } from "../../services/KnowledgeBaseApi";

interface TopBarProps {
  inSelectionView: boolean;
  onSelectionView: (status: boolean) => void;
  selectedCount: number;
  totalCount: number;
  onSelectAll: () => void;
  onDeleteSelected: () => void;
  onCancel: () => void;
  isDeleting: boolean;
  selectedDocuments: DocumentObject[];
  setDocumentList: (documentList: DocumentObject[]) => void;
}

export default function TopBar({
  inSelectionView,
  onSelectionView,
  selectedCount,
  totalCount,
  onSelectAll,
  onDeleteSelected,
  onCancel,
  isDeleting,
  selectedDocuments,
  setDocumentList,
}: TopBarProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Helper to check if any selected documents have a specific status
  const hasDocumentsWithStatus = (status: string) => {
    return selectedDocuments.some((doc) => doc.status === status);
  };

  // Show warning if trying to delete documents that are processing
  const getDeleteButtonText = () => {
    if (isDeleting) return "Deleting...";

    const processingCount = selectedDocuments.filter(
      (doc) =>
        doc.status === "STARTING" ||
        doc.status === "IN_PROGRESS" ||
        doc.status === "PENDING"
    ).length;

    if (processingCount > 0) {
      return `Delete Selected (${selectedCount}) - ${processingCount} processing`;
    }

    return `Delete Selected (${selectedCount})`;
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      const response = await getKnowledgeBaseDocuments();
      setDocumentList(response.documentDetails);
    } catch (error) {
      console.error("Failed to refresh documents:", error);
      alert("Failed to refresh documents. Please try again.");
    } finally {
      setIsRefreshing(false);
    }
  };

  if (inSelectionView) {
    return (
      <div className="Knowledge-base-top-bar selection-mode">
        <div className="selection-info">
          <span>
            {selectedCount} of {totalCount} selected
          </span>
          {selectedCount > 0 && hasDocumentsWithStatus("PROCESSING") && (
            <small
              style={{ display: "block", color: "#fbbf24", fontSize: "12px" }}
            >
              ⚠ Some documents are still processing
            </small>
          )}
        </div>
        <div className="selection-actions">
          <button
            onClick={onSelectAll}
            disabled={isDeleting || totalCount === 0}
          >
            {selectedCount === totalCount ? "Deselect All" : "Select All"}
          </button>
          <button
            onClick={onDeleteSelected}
            disabled={selectedCount === 0 || isDeleting}
            className="delete-btn"
            title={
              hasDocumentsWithStatus("PROCESSING")
                ? "Some documents are processing and may not delete cleanly"
                : ""
            }
          >
            {isDeleting ? (
              <>
                <span className="spinner"></span>
                Deleting...
              </>
            ) : (
              getDeleteButtonText()
            )}
          </button>
          <button
            onClick={onCancel}
            className="cancel-btn"
            disabled={isDeleting}
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="Knowledge-base-top-bar">
      <UploadModal />
      <button
        onClick={handleRefresh}
        disabled={isRefreshing}
        className="kb-icon-btn"
        title="Sync Document List"
      >
        {isRefreshing ? (
          <>
            <span className="spinner"></span>
            Refreshing...
          </>
        ) : (
          "Sync Document List"
        )}
      </button>
      <SyncKnowledgeBaseButton />
      <button
        className="knowledge-base-top-bar-select"
        onClick={() => onSelectionView(true)}
        disabled={totalCount === 0}
      >
        Select
      </button>
    </div>
  );
}
