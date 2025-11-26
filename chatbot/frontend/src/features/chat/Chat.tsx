import { useState } from "react";
import type { ChatObject, MessageObject } from "../../types";
import MessageList from "./components/MessageList";
import { getAssistantResponse } from "./services/ChatApi";
import ChatInputBox from "./components/InputBox";
import { generateUUID } from "../../utils/uuid";

interface ChatProps {
  selectedChat: ChatObject;
  handleUpdateChatMessageList: (
    id: string,
    message: MessageObject,
    sessionId?: string
  ) => void;
  onSessionExpired?: (chatId: string) => void;
}

export default function Chat({
  selectedChat,
  handleUpdateChatMessageList,
  onSessionExpired,
}: ChatProps) {
  const [inputBoxValue, setInputBoxValue] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  function handleSetInputBox(userInput: string) {
    setInputBoxValue(userInput);
  }

  async function handleUserNewMessage(chatId: string, content: string) {
    const newMessage: MessageObject = {
      id: generateUUID(),
      role: "USER",
      content: content,
      timestamp: new Date(),
      citation: [],
    };

    // Add user message to chat immediately
    handleUpdateChatMessageList(chatId, newMessage);
    setInputBoxValue("");
    setIsLoading(true);
    setError(null);

    try {
      // Prepare messages for backend (include the new user message)
      const updatedMessages = [...selectedChat.messages, newMessage];

      // Send request with current sessionId
      const response = await getAssistantResponse(
        updatedMessages,
        selectedChat.sessionId
      );

      // Only update if we're still on the same chat
      if (selectedChat.id === chatId) {
        // Add assistant response to chat with sessionId for chat management
        handleUpdateChatMessageList(
          chatId,
          response.message,
          response.sessionId
        );
      }
    } catch (error) {
      console.error("Error at handleUserNewMessage:", error);

      if (error instanceof Error) {
        if (error.message === "SESSION_EXPIRED") {
          setError("Session expired. Please start a new chat.");
          if (onSessionExpired) {
            onSessionExpired(chatId);
          }
        } else {
          setError(error.message);
        }
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">{selectedChat.title}</div>

      {error && (
        <div className="error-banner">
          <span className="error-text">{error}</span>
          <button className="error-dismiss" onClick={() => setError(null)}>
            ×
          </button>
        </div>
      )}

      <div className="chat-message-list" id="ChatMessageList">
        <MessageList messages={selectedChat.messages} />
      </div>

      <ChatInputBox
        inputBoxValue={inputBoxValue}
        isLoading={isLoading}
        selectedChat={selectedChat}
        handleSetInputBox={handleSetInputBox}
        handleUserNewMessage={handleUserNewMessage}
        disabled={!!error}
      />
    </div>
  );
}
