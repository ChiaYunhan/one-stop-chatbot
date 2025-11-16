import { type ChatObject } from "../../../types";
import ChatItem from "./ChatItem";
import { useState, useEffect } from "react";

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
    <div>
      <div>
        <span className="ChatDirectoryTitle" id="ChatDirectoryTitleText">
          Chats
        </span>
        <button
          className="ChatDirectoryTitle"
          id="CreateChatButton"
          onClick={() => {
            handleCreateNewChat();
          }}
        >
          Create Chat
        </button>
      </div>
      <div>
        <ul className="chat-directory-list" id="ChatDirectorList">
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
        </ul>
      </div>
    </div>
  );
}
