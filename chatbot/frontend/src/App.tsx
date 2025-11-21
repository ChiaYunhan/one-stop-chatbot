import { useState } from "react";
import "./App.css";
import { type ViewType, type ChatObject, type MessageObject } from "./types";
import Sidebar from "./features/sidebar/Sidebar";
import KnowledgeBase from "./features/knowledgeBase/KnowledgeBase";
import Chat from "./features/chat/Chat";

function App() {
  const [activeView, setActiveView] = useState<ViewType>("knowledgeBase");
  const [chats, setChats] = useState<Record<string, ChatObject>>({});
  const [selectedChatId, setChatId] = useState<string | null>(null);
  const [chatCounter, setChatCounter] = useState<number>(1);

  function handleSetActiveView(view: ViewType) {
    setActiveView(view);
  }

  function handleSelectChat(chatId: string) {
    setChatId(chatId);
    setActiveView("chat");
  }

  function handleCreateNewChat() {
    const newId = crypto.randomUUID();
    const newChat: ChatObject = _createChatObject(newId);
    setChats({ ...chats, [newId]: newChat });
    setChatCounter(chatCounter + 1);
    handleSelectChat(newId);
    return newChat;
  }

  function handleDeleteChat(chatId: string) {
    if (chatId === selectedChatId) {
      const newId = crypto.randomUUID();
      const newChat = _createChatObject(newId);
      const { [chatId]: _, ...rest } = chats;

      setChats({ ...rest, [newId]: newChat });
      setChatCounter(chatCounter + 1);
      handleSelectChat(newId);
    } else {
      const { [chatId]: _, ...rest } = chats;
      setChats(rest);
    }
  }

  function handleRenameChat(id: string, newTitle: string) {
    const newChatTitle = newTitle.trim() === "" ? chats[id].title : newTitle;
    setChats({
      ...chats,
      [id]: { ...chats[id], title: newChatTitle, updatedAt: new Date() },
    });
  }

  function handleUpdateChatMessageList(id: string, newMessage: MessageObject) {
    setChats((prevChats) => {
      if (!prevChats[id]) {
        return prevChats; // No-op, return unchanged state
      }
      return {
        ...prevChats,
        [id]: {
          ...prevChats[id],
          updatedAt: new Date(),
          messages: [...prevChats[id].messages, newMessage],
        },
      };
    });
  }

  function _createChatObject(newId: string) {
    const currentDateTime: Date = new Date();
    return {
      id: newId,
      title: `New Chat ${chatCounter}`,
      messages: [],
      createdAt: currentDateTime,
      updatedAt: currentDateTime,
    };
  }

  return (
    <div className="app-container">
      <div className="sidebar">
        <Sidebar
          chats={chats}
          selectedChatId={selectedChatId}
          handleCreateNewChat={handleCreateNewChat}
          handleDeleteChat={handleDeleteChat}
          handleRenameChat={handleRenameChat}
          handleSelectChat={handleSelectChat}
          handleSetActiveView={handleSetActiveView}
        />
      </div>
      <div className="main-content">
        {activeView === "knowledgeBase" ? (
          <KnowledgeBase />
        ) : selectedChatId && chats[selectedChatId] ? (
          <Chat
            selectedChat={chats[selectedChatId]}
            handleUpdateChatMessageList={handleUpdateChatMessageList}
          />
        ) : (
          <div>Select a chat to get started</div>
        )}
      </div>
    </div>
  );
}

export default App;
