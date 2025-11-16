import type { ViewType } from "../../../types";

interface KnowledgeBaseButtonProps {
  handleSetActiveView: (view: ViewType) => void;
}

export default function KnowledgeBaseButton({
  handleSetActiveView,
}: KnowledgeBaseButtonProps) {
  return (
    <button
      id="KnowledgeBaseButton"
      onClick={() => handleSetActiveView("knowledgeBase")}
    >
      Knowledge Base
    </button>
  );
}
