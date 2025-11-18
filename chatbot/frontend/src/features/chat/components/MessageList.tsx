import type { MessageObject } from "../../../types";
import Message from "./Message";

interface MessageListProps {
  messages: MessageObject[];
}

export default function MessageList({ messages }: MessageListProps) {
  return messages.length === 0 ? (
    <div className="chat-empty-state">Start by sending a message</div>
  ) : (
    <div className="messages-wrapper">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
    </div>
  );
}
