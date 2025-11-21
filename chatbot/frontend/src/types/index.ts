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
  | "DELETE_IN_PROGRESS"
  | "NOT_INDEXED";

export type ChatRole = "USER" | "ASSISTANT";

export type ViewType = "knowledgeBase" | "chat";

export interface CitationObject {
  text: string;
  file: string;
}

export interface MessageObject {
  id: string;
  role: ChatRole;
  content: string;
  citation?: CitationObject[];
  timestamp: Date;
}

export interface ChatObject {
  id: string;
  title: string;
  messages: MessageObject[];
  createdAt: Date;
  updatedAt: Date;
  sessionId?: string;
}

export interface ChatRequest {
  messages: MessageObject[];
  sessionId?: string;
}

export interface DocumentObject {
  id: string;
  knowledgeBaseId: string;
  dataSourceId: string;
  status: DocumentStatus;
  s3Key: string;
  updatedAt: Date;
  displayName: string;
  statusReason: string;
}

export interface ListDocumentObjectResponse {
  documentDetails: DocumentObject[];
  nextToken: string;
}
