import { type ChatObject } from "../../types";
import { type ViewType } from "../../types";
import KnowledgeBaseButton from "./components/KnowledgeBaseButton";
import ChatDirectory from "./components/ChatDirectory";

interface SidebarProps {
  chats: Record<string, ChatObject>;
  selectedChatId: string | null;
  handleCreateNewChat: () => ChatObject;
  handleDeleteChat: (chatId: string) => void;
  handleRenameChat: (chatId: string, newTitle: string) => void;
  handleSelectChat: (chatId: string) => void;
  handleSetActiveView: (view: ViewType) => void;
}

export default function Sidebar({
  chats,
  selectedChatId,
  handleCreateNewChat,
  handleDeleteChat,
  handleRenameChat,
  handleSelectChat,
  handleSetActiveView,
}: SidebarProps) {
  return (
    <>
      <KnowledgeBaseButton handleSetActiveView={handleSetActiveView} />
      <ChatDirectory
        chats={chats}
        selectedChatId={selectedChatId}
        handleCreateNewChat={handleCreateNewChat}
        handleDeleteChat={handleDeleteChat}
        handleRenameChat={handleRenameChat}
        handleSelectChat={handleSelectChat}
      />
    </>
  );
}
