import { useState } from "react";
import "./App.css";
import { type ViewType, type ChatObject } from "./types";
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
    // sidebar
    // width will be 10%, adjustable later one
    // two containers? knowledge base and chat
    // knowledge base is a single element in the sidebar. fixed
    // chat will have two sub containers, the first will just have "Chats [plus icon]" plus icon will create new chat and set selectchatid
    // potentially a sort function in the future

    // only one will be displayed at a time

    // knowledge base
    // three containers, top, left and right

    // chat
    // display current content from selectedChatId, if content is empty list then show a default starting chat page

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

      {/* <div className="main-content">
        {activeView === "knowledgeBase" ? (
          <KnowledgeBase />
        ) : (
          <Chat
            selectedChat={
              selectedChatId && Object.keys(chats).length > 0
                ? chats[selectedChatId]
                : null
            }
          />
        )}
      </div> */}
    </div>
  );
}

export default App;
