import { AssistantQueryRequest, AssistantQueryResponse } from "@/types/assistant";

/**
 * Sends a natural language query and verified medicine context to the General Assistant API.
 * Calls POST /api/assistant/query
 */
export async function queryAssistant(
  payload: AssistantQueryRequest
): Promise<AssistantQueryResponse> {
  const res = await fetch("/api/assistant/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(
      errorBody?.error?.message || `HTTP ${res.status}: Failed to process assistant query.`
    );
  }

  return await res.json();
}
