import { useState } from "react";
import { triggerSyncKnowledgeBase } from "../../services/KnowledgeBaseApi";

interface SyncResponse {
  success: boolean;
  message: string;
  ingestionJobId?: string;
  status?: string;
}

export default function SyncKnowledgeBaseButton() {
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  async function handleSync() {
    setIsSyncing(true);
    try {
      const response = await triggerSyncKnowledgeBase();
      const data: SyncResponse = await response.json();

      if (response.ok) {
        alert(
          `Knowledge base sync started successfully!\nJob ID: ${data.ingestionJobId}`
        );
      } else {
        if (response.status === 409) {
          alert("A sync is already in progress. Please try again later.");
        } else {
          alert(`Failed to trigger sync: ${data.message}`);
        }
      }
    } catch {
      alert("Failed to trigger knowledge base sync");
    } finally {
      setIsSyncing(false);
    }
  }

  return (
    <button
      className="kb-icon-btn"
      onClick={handleSync}
      disabled={isSyncing}
      title="Sync Knowledge Base"
    >
      Sync Knowledge Base
    </button>
  );
}
