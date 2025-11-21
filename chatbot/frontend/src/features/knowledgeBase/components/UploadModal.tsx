import { Upload } from "lucide-react";
import { useState } from "react";
import Modal from "react-modal";

Modal.setAppElement("#root");

interface UploadResult {
  fileName: string;
  success: boolean;
  key?: string;
  error?: string;
}

function UploadModal() {
  const [modalIsOpen, setIsOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);

  const openModal = () => {
    setIsOpen(true);
    setUploadResults([]);
  };

  const closeModal = () => {
    setIsOpen(false);
    setSelectedFiles([]);
    setUploadResults([]);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert("Please select files to upload.");
      return;
    }

    setIsUploading(true);

    try {
      const response = await fetch(
        "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/documents/uploadpresignedurl",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            files: selectedFiles.map((file) => ({
              fileName: file.name,
              fileType: file.type,
            })),
          }),
        }
      );

      const data = await response.json();
      if (!response.ok) throw new Error(data.message);

      const uploadedFiles: Array<{ fileName: string; key: string }> = [];

      const uploadPromises = data.results.map(
        async (result: any, index: number) => {
          if (!result.success) {
            return {
              fileName: result.fileName,
              success: false,
              error: result.error,
            };
          }

          try {
            const file = selectedFiles[index];
            const formData = new FormData();

            Object.entries(result.fields).forEach(([key, value]) => {
              formData.append(key, value as string);
            });
            formData.append("file", file);

            const uploadResponse = await fetch(result.url, {
              method: "POST",
              body: formData,
            });

            if (!uploadResponse.ok) throw new Error("Upload failed");

            uploadedFiles.push({ fileName: file.name, key: result.key });

            return { fileName: file.name, success: true, key: result.key };
          } catch (error: any) {
            return {
              fileName: selectedFiles[index].name,
              success: false,
              error: error.message,
            };
          }
        }
      );

      const results = await Promise.all(uploadPromises);
      setUploadResults(results);
    } catch (error: any) {
      console.error("Upload error:", error);
      alert("Upload failed: " + error.message);
    } finally {
      setIsUploading(false);
      // Don't close modal - let user see results first
    }
  };

  return (
    <div className="kb-upload-modal-container">
      <button className="kb-icon-btn" onClick={openModal} title="Upload Files">
        <Upload size={18} />
      </button>

      <Modal
        overlayClassName="kb-upload-modal-overlay"
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        contentLabel="Upload Files"
      >
        <h2 className="kb-upload-title">Upload Files to Knowledge Base</h2>

        <input
          className="kb-upload-input"
          type="file"
          onChange={handleFileChange}
          multiple
          disabled={isUploading}
          accept=".pdf,.png,.jpg,.jpeg"
        />

        {selectedFiles.length > 0 && (
          <div className="kb-upload-selected-list-container">
            <p className="kb-upload-subtitle">
              <strong>Selected files ({selectedFiles.length}):</strong>
            </p>

            <ul className="kb-upload-selected-list">
              {selectedFiles.map((file, index) => (
                <li key={index}>
                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </li>
              ))}
            </ul>
          </div>
        )}

        {uploadResults.length > 0 && (
          <div className="kb-upload-results-container">
            <p className="kb-upload-subtitle">
              <strong>Upload Results:</strong>
            </p>

            <ul className="kb-upload-results-list">
              {uploadResults.map((result, index) => (
                <li
                  key={index}
                  className={result.success ? "kb-success" : "kb-error"}
                >
                  {result.fileName}:{" "}
                  {result.success ? "✓ Success" : `✗ ${result.error}`}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="kb-upload-buttons">
          <button
            className="kb-upload-button"
            onClick={handleUpload}
            disabled={isUploading || selectedFiles.length === 0}
          >
            {isUploading ? "Uploading..." : "Upload"}
          </button>

          <button
            className="kb-cancel-button"
            onClick={closeModal}
            disabled={isUploading}
          >
            Close
          </button>
        </div>
      </Modal>
    </div>
  );
}

export default UploadModal;
