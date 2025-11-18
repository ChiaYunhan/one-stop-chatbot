import type { MessageObject } from "../../../types";

export async function getAssistantResponse(
  messages: MessageObject[]
): Promise<MessageObject> {
  await sleep(5000);
  const response: MessageObject = {
    id: crypto.randomUUID(),
    role: "ASSISTANT",
    content: "assistant response here",
    timestamp: new Date(),
  };

  return response;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
