import type { DocumentObject } from "../../../types";
import DocumentItem from "./DocumentItem";
import { DocumentItemIconView } from "./DocumentItem";
import { useState } from "react";

interface DocumentListProps {
  selectedDocId: string | null;
  documentList: DocumentObject[];
  onSelectDocument: (docId: string) => void;
  inSelectionView: boolean;
  selectedDocuments: string[];
}

export default function DocumentList({
  selectedDocId,
  documentList,
  onSelectDocument,
  inSelectionView,
  selectedDocuments,
}: DocumentListProps) {
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");

  if (documentList.length === 0) {
    return <div>Upload document</div>;
  }

  console.log(documentList);

  return (
    <div className="document-list-container">
      <div className="view-controls">
        <div className="view-toggle">
          <button
            className={viewMode === "list" ? "active" : ""}
            onClick={() => setViewMode("list")}
          >
            List
          </button>
          <button
            className={viewMode === "grid" ? "active" : ""}
            onClick={() => setViewMode("grid")}
          >
            Grid
          </button>
        </div>
      </div>

      {/* Document List */}
      <div
        className={`knowledge-base-document-list ${
          inSelectionView ? "selection-mode" : ""
        } ${viewMode === "grid" ? "grid-view" : ""}`}
      >
        {documentList.map((document: DocumentObject) => {
          const isSelected = inSelectionView
            ? selectedDocuments.includes(document.id)
            : selectedDocId === document.id;

          // Use icon view for grid mode, regular view for list mode
          if (viewMode === "grid") {
            return (
              <DocumentItemIconView
                key={document.id}
                document={document}
                isSelected={isSelected}
                onSelect={() => onSelectDocument(document.id)}
                inSelectionView={inSelectionView}
              />
            );
          }

          return (
            <DocumentItem
              key={document.id}
              document={document}
              isSelected={isSelected}
              onSelect={() => onSelectDocument(document.id)}
              inSelectionView={inSelectionView}
            />
          );
        })}
      </div>
    </div>
  );
}
