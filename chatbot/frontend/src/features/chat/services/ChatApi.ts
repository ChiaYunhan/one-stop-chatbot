import type { MessageObject } from "../../../types";
import { API_BASE_URL } from "../../../config";

interface ChatApiResponse {
  message: MessageObject;
  sessionId: string;
}

export async function getAssistantResponse(
  messages: MessageObject[],
  sessionId?: string
): Promise<ChatApiResponse> {
  try {
    const requestPayload: any = {
      messages: messages,
    };

    // Add sessionId if provided
    if (sessionId) {
      requestPayload.sessionId = sessionId;
    }

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestPayload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      if (response.status === 410) {
        throw new Error("SESSION_EXPIRED");
      }

      throw new Error(errorData.message || `HTTP Error: ${response.status}`);
    }

    const data = await response.json();

    // Handle your backend's response structure
    if (data.statusCode !== 200) {
      throw new Error(data.message || "Backend returned error");
    }

    // Convert backend response to frontend format
    const assistantMessage: MessageObject = {
      id: data.assistantMessage.id,
      role: data.assistantMessage.role,
      content: data.assistantMessage.content,
      citation: data.assistantMessage.citation || [],
      timestamp: new Date(data.assistantMessage.timestamp),
    };

    return {
      message: assistantMessage,
      sessionId: data.sessionId,
    };
  } catch (error) {
    console.error("Error in getAssistantResponse:", error);
    throw error;
  }
}
