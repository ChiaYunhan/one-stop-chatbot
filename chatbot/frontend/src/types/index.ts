export type DocumentStatus =
  | "INDEXED"
  | "PARTIALLY_INDEXED"
  | "PENDING"
  | "FAILED"
  | "METADATA_PARTIALLY_INDEXED"
  | "METADATA_UPDATE_FAILED"
  | "IGNORED"
  | "NOT_FOUND"
  | "STARTING"
  | "IN_PROGRESS"
  | "DELETING"
  | "DELETE_IN_PROGRESS";

export type ChatRole = "USER" | "ASSISTANT";

export type ViewType = "knowledgeBase" | "chat";

export interface Message {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: Date;
}

export interface ChatObject {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Document {
  knowledgeBaseId: string;
  dataSourceId: string;
  status: DocumentStatus;
  s3Key: string;
  updatedAt: Date;
  displayName: string;
}
