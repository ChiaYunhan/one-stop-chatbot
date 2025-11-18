import type { MessageObject } from "../../../types";

interface MessageProps {
  message: MessageObject;
}

export default function Message({ message }: MessageProps) {
  return (
    <div
      className={
        message.role === "USER" ? "chat-message-user" : "chat-message-assistant"
      }
    >
      <span>{message.content}</span>
    </div>
  );
}
