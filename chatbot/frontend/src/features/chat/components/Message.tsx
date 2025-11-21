import type { MessageObject, CitationObject } from "../../../types";
import ReactMarkdown from "react-markdown";

interface MessageProps {
  message: MessageObject;
}

interface CitationDisplayProps {
  citations: CitationObject[];
}

function CitationDisplay({ citations }: CitationDisplayProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="message-citations">
      <div className="citations-header">📚 Sources ({citations.length})</div>
      <div className="citations-list">
        {citations.map((citation, index) => (
          <div key={index} className="citation-item">
            <div className="citation-file">
              📄 Page: {citation.page} [{citation.file}]
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Message({ message }: MessageProps) {
  const isUser = message.role === "USER";
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={isUser ? "chat-message-user" : "chat-message-assistant"}>
      <div className="message-header">
        <span className="message-role">{isUser ? "You" : "Assistant"}</span>
        <span className="message-timestamp">{timestamp}</span>
      </div>

      <div className="message-content">
        {isUser ? (
          <span>{message.content}</span>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>

      {!isUser && message.citation && message.citation.length > 0 && (
        <CitationDisplay citations={message.citation} />
      )}
    </div>
  );
}
