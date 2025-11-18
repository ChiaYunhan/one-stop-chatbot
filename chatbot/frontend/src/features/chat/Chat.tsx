import { useState } from "react";
import type { ChatObject, MessageObject } from "../../types";
import MessageList from "./components/MessageList";
import { getAssistantResponse } from "./services/ChatApi";
import ChatInputBox from "./components/InputBox";

interface ChatProps {
  selectedChat: ChatObject;
  handleUpdateChatMessageList: (id: string, message: MessageObject) => void;
}

export default function Chat({
  selectedChat,
  handleUpdateChatMessageList,
}: ChatProps) {
  const [inputBoxValue, setInputBoxValue] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  function handleSetInputBox(userInput: string) {
    setInputBoxValue(userInput);
  }

  async function handleUserNewMessage(chatId: string, content: string) {
    const newMessage: MessageObject = {
      id: crypto.randomUUID(),
      role: "USER",
      content: content,
      timestamp: new Date(),
    };

    handleUpdateChatMessageList(chatId, newMessage);
    setInputBoxValue("");
    setIsLoading(true);

    try {
      const updatedMessages = [...selectedChat.messages, newMessage];
      const response = await getAssistantResponse(updatedMessages);

      if (selectedChat.id === chatId) {
        handleUpdateChatMessageList(chatId, response);
      }
    } catch (error) {
      console.error("Error at handleUserNewMessage");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">{selectedChat.title}</div>
      <div className="chat-message-list" id="ChatMessageList">
        <MessageList messages={selectedChat.messages} />
      </div>
      <ChatInputBox
        inputBoxValue={inputBoxValue}
        isLoading={isLoading}
        selectedChat={selectedChat}
        handleSetInputBox={handleSetInputBox}
        handleUserNewMessage={handleUserNewMessage}
      ></ChatInputBox>
    </div>
  );
}
