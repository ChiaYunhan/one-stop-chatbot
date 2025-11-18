import { type ChatObject } from "../../../types";
import ChatItem from "./ChatItem";
import { useState } from "react";
import { MessageSquare, Plus } from "lucide-react";

interface ChatDirectoryProps {
  chats: Record<string, ChatObject>;
  selectedChatId: string | null;
  handleCreateNewChat: () => ChatObject;
  handleDeleteChat: (chatId: string) => void;
  handleRenameChat: (chatId: string, newTitle: string) => void;
  handleSelectChat: (chatId: string) => void;
}

export default function ChatDirectory({
  chats,
  selectedChatId,
  handleCreateNewChat,
  handleDeleteChat,
  handleRenameChat,
  handleSelectChat,
}: ChatDirectoryProps) {
  const [openMenuChatId, setOpenMenuChatId] = useState<string | null>(null);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);

  function handleSetOpenMenuChatId(chatId: string | null) {
    setOpenMenuChatId((prevId) => (prevId === chatId ? null : chatId));
  }

  function handleSelectChatWrapper(chatId: string) {
    setOpenMenuChatId(null);
    handleSelectChat(chatId);
  }

  function handleSetEditingChatId(chatId: string | null) {
    setEditingChatId(chatId);
  }

  return (
    <div className="chat-directory">
      <div className="chat-directory-header">
        <div className="chat-directory-title">
          <MessageSquare size={18} />
          <span>Chats</span>
        </div>
        <button
          className="new-chat-button"
          onClick={() => {
            handleCreateNewChat();
          }}
        >
          <Plus size={18} />
        </button>
      </div>
      <div className="chat-list">
        {Object.values(chats).map((chat) => (
          <ChatItem
            key={chat.id}
            chat={chat}
            isSelected={chat.id === selectedChatId}
            isKebabMenuOpen={chat.id === openMenuChatId}
            isEditingMode={chat.id === editingChatId}
            onSelect={handleSelectChatWrapper}
            onDelete={handleDeleteChat}
            onRename={handleRenameChat}
            setOpenMenuId={handleSetOpenMenuChatId}
            setEditingChatId={handleSetEditingChatId}
          />
        ))}
      </div>
    </div>
  );
}
