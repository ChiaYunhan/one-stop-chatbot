import type { MessageObject } from "../../../types";

export async function getAssistantResponse(
  messages: MessageObject[]
): Promise<MessageObject> {
  const response = await fetch(
    "https://xjogjcajp4.execute-api.us-east-1.amazonaws.com/chatbot/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages }),
    }
  );

  return response.json();
}
