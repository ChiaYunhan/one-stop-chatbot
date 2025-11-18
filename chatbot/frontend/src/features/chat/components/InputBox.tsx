import { useRef, useEffect } from "react";
import type { ChatObject } from "../../../types";
import { Send } from "lucide-react";

interface ChatInputBox {
  inputBoxValue: string;
  isLoading: boolean;
  selectedChat: ChatObject;
  handleSetInputBox: (inputBoxValue: string) => void;
  handleUserNewMessage: (selectedChatId: string, inputBoxValue: string) => void;
}

export default function ChatInputBox({
  inputBoxValue,
  isLoading,
  selectedChat,
  handleSetInputBox,
  handleUserNewMessage,
}: ChatInputBox) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleInputSubmit() {
    if (inputBoxValue.trim() && !isLoading) {
      handleUserNewMessage(selectedChat.id, inputBoxValue);
    }
  }

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [inputBoxValue]);

  return (
    <div className="chat-input-container">
      <textarea
        ref={textareaRef}
        className="chat-input"
        value={inputBoxValue}
        placeholder="How can I help you today?"
        disabled={isLoading}
        onChange={(e) => handleSetInputBox(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey && inputBoxValue.trim()) {
            e.preventDefault();
            handleInputSubmit();
          }
        }}
        rows={1}
        autoFocus
      />
      <button
        className="chat-input-send-button"
        onClick={() => handleInputSubmit()}
        disabled={isLoading || !inputBoxValue.trim()}
      >
        <Send size={18} />
      </button>
    </div>
  );
}
