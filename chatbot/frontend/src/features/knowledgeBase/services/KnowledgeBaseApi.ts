import type {
  DocumentObject,
  ListDocumentObjectResponse,
} from "../../../types";

export async function getKnowledgeBaseDocuments(): Promise<ListDocumentObjectResponse> {
  const response = await fetch(
    "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/documents/list",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return response.json();
}

export const getViewDocumentS3Link = async (
  document: DocumentObject,
  signal?: AbortSignal
) => {
  const response = await fetch(
    "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/documents/downloadpresignedurl",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        s3Key: document.s3Key,
        action: "view", // Add this for viewing
      }),
      signal,
    }
  );
  return response.json();
};

export const getDownloadDocumentS3Link = async (
  document: DocumentObject,
  signal?: AbortSignal
) => {
  const response = await fetch(
    "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/documents/downloadpresignedurl",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        s3Key: document.s3Key,
        action: "download", // Add this for downloads
      }),
      signal,
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch download link");
  }

  return response.json();
};

// services/DocumentService.ts

export interface DeleteDocumentsResponse {
  success: boolean;
  deletedCount: number;
  failedIds: string[];
  message: string;
}

export const deleteDocuments = async (
  documents: DocumentObject[]
): Promise<DeleteDocumentsResponse> => {
  try {
    const response = await fetch(
      "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/documents/delete",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          documents,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: DeleteDocumentsResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to delete documents:", error);
    throw new Error("Failed to delete documents. Please try again.");
  }
};

export const triggerSyncKnowledgeBase = async () => {
  const response = await fetch(
    "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/documents/sync",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }
  );

  return response;
};
