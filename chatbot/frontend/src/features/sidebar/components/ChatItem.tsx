import { useState, useEffect } from "react";
import type { ChatObject } from "../../../types";

interface ChatItemProps {
  chat: ChatObject;
  isSelected: boolean;
  isKebabMenuOpen: boolean;
  isEditingMode: boolean;
  onSelect: (chatId: string) => void;
  onDelete: (chatId: string) => void;
  onRename: (chatId: string, newTitle: string) => void;
  setOpenMenuId: (chatId: string | null) => void;
  setEditingChatId: (chatId: string | null) => void;
}

export default function ChatItem({
  chat,
  isSelected,
  isKebabMenuOpen,
  isEditingMode,
  onSelect,
  onDelete,
  onRename,
  setOpenMenuId,
  setEditingChatId,
}: ChatItemProps) {
  const [editValue, setEditValue] = useState(chat.title);

  useEffect(() => {
    setEditValue(chat.title);
  }, [chat.title]);

  return (
    <li
      className={
        isSelected
          ? "chat-directory-list-item active"
          : "chat-directory-list-item"
      }
      onClick={() => onSelect(chat.id)}
    >
      {isEditingMode ? (
        <input
          type="text"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={() => {
            onRename(chat.id, editValue);
            setEditingChatId(null);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onRename(chat.id, editValue);
              setEditingChatId(null);
            } else if (e.key === "Escape") {
              setEditValue(chat.title);
              setEditingChatId(null);
            }
          }}
          onClick={(e) => e.stopPropagation()}
          autoFocus
        ></input>
      ) : (
        <span>{chat.title}</span>
      )}
      <button
        className={
          isKebabMenuOpen
            ? "chat-item-kebab-menu active"
            : "chat-item-kebab-menu"
        }
        onClick={(e) => {
          e.stopPropagation();
          setOpenMenuId(chat.id);
        }}
      >
        kebab
      </button>
      {isKebabMenuOpen && (
        <div>
          <button
            className="chat-item-kebab-item"
            onClick={(e) => {
              e.stopPropagation();
              setEditingChatId(chat.id);
              setOpenMenuId(null);
            }}
          >
            Rename
          </button>
          <button
            className="chat-item-kebab-item"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(chat.id);
              setOpenMenuId(null);
            }}
          >
            Delete
          </button>
        </div>
      )}
    </li>
  );
}
