import { useState, useEffect } from "react";
import type { ChatObject } from "../../../types";
import { Ellipsis, PencilLine, Trash2 } from "lucide-react";

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
  const [isHover, setIsHovered] = useState(false);

  useEffect(() => {
    setEditValue(chat.title);
  }, [chat.title]);

  return (
    <div
      className={`chat-item ${isSelected ? "selected" : ""}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
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
          isKebabMenuOpen ? "kebab-menu-button active" : "kebab-menu-button"
        }
        onClick={(e) => {
          e.stopPropagation();
          setOpenMenuId(chat.id);
        }}
      >
        <Ellipsis size={18} />
      </button>
      {isKebabMenuOpen && (
        <div>
          <button
            className="kebab-menu-button-item"
            onClick={(e) => {
              e.stopPropagation();
              setEditingChatId(chat.id);
              setOpenMenuId(null);
            }}
          >
            <PencilLine size={18} />
          </button>
          <button
            className="kebab-menu-button-item"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(chat.id);
              setOpenMenuId(null);
            }}
          >
            <Trash2 size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
