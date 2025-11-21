import type { ViewType } from "../../../types";
import { Database } from "lucide-react";

interface KnowledgeBaseButtonProps {
  handleSetActiveView: (view: ViewType) => void;
}

export default function KnowledgeBaseButton({
  handleSetActiveView,
}: KnowledgeBaseButtonProps) {
  return (
    <button
      className="knowledge-base-button"
      onClick={() => handleSetActiveView("knowledgeBase")}
    >
      <Database size={18} />
      <span>Knowledge Base</span>
    </button>
  );
}
