import type { DocumentObject } from "../../../types";

interface DocumentItemProps {
  document: DocumentObject;
  isSelected: boolean;
  onSelect: () => void;
  inSelectionView: boolean;
}

export default function DocumentItem({
  document,
  isSelected,
  onSelect,
  inSelectionView,
}: DocumentItemProps) {
  const handleClick = () => {
    onSelect();
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    onSelect();
  };

  return (
    <div
      className={`knowledge-base-document-item ${
        isSelected ? "selected" : ""
      } ${inSelectionView ? "selection-mode" : ""}`}
      onClick={handleClick}
    >
      {inSelectionView && (
        <div className="document-checkbox">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={handleCheckboxChange}
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
      <div className="document-content">
        <span className="document-name">
          {document.displayName}
          <br></br>
          {document.status}
          <br></br>
          {document.statusReason}
        </span>
      </div>
    </div>
  );
}

interface DocumentItemIconViewProps {
  document: DocumentObject;
  isSelected: boolean;
  onSelect: () => void;
  inSelectionView: boolean;
}

export function DocumentItemIconView({
  document,
  isSelected,
  onSelect,
  inSelectionView,
}: DocumentItemIconViewProps) {
  const handleClick = () => {
    onSelect();
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation();
    onSelect();
  };

  // Get file extension for icon display
  const getFileExtension = (filename: string) => {
    return filename.split(".").pop()?.toUpperCase() || "PDF";
  };

  return (
    <div
      className={`knowledge-base-document-item icon-view ${
        isSelected ? "selected" : ""
      } ${inSelectionView ? "selection-mode" : ""}`}
      onClick={handleClick}
    >
      {inSelectionView && (
        <div className="document-checkbox">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={handleCheckboxChange}
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
      <div className="document-content">
        <div className="document-icon">
          {getFileExtension(document.displayName)}
        </div>
        <span className="document-name" title={document.displayName}>
          {document.displayName}
          <br></br>
          {document.status}
          <br></br>
          {document.statusReason}
        </span>
      </div>
    </div>
  );
}
