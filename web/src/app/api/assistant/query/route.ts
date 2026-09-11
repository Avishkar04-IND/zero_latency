import { NextRequest, NextResponse } from "next/server";
import { processAssistantQuery } from "@/lib/assistant/engine";
import { AssistantQueryRequest } from "@/types/assistant";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: CORS_HEADERS,
  });
}

export async function POST(request: NextRequest) {
  let body: AssistantQueryRequest;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "MALFORMED_JSON",
          message: "Request body must be valid JSON.",
        },
      },
      { status: 400, headers: CORS_HEADERS }
    );
  }

  // Validate presence of query text
  const query = body?.query || body?.query_text;
  if (!query || typeof query !== "string" || !query.trim()) {
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "MISSING_QUERY",
          message: "A non-empty 'query' string is required.",
        },
      },
      { status: 400, headers: CORS_HEADERS }
    );
  }

  try {
    const response = processAssistantQuery(body);
    return NextResponse.json(response, {
      status: 200,
      headers: CORS_HEADERS,
    });
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "INTERNAL_ERROR",
          message: error?.message || "An unexpected error occurred processing assistant query.",
        },
      },
      { status: 500, headers: CORS_HEADERS }
    );
  }
}
