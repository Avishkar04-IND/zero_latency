/**
 * Web service for Member 3's Layout Engine.
 *
 * Base URL configured via: NEXT_PUBLIC_LAYOUT_ENGINE_URL
 * Default: http://127.0.0.1:8001
 *
 * Endpoints used:
 *   POST /api/v1/layout/optimize   → full optimization with alternatives
 *   POST /api/layouts/preview      → SVG preview
 *   POST /api/layouts/pdf          → PDF download (binary)
 */

import type {
  LayoutOptimizeRequest,
  LayoutOptimizeResponse,
  LayoutPreviewResponse,
  LayoutPdfRequest,
} from "@/types/layout";

export const LAYOUT_ENGINE_BASE_URL =
  process.env.NEXT_PUBLIC_LAYOUT_ENGINE_URL || "http://127.0.0.1:8001";

class LayoutEngineError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "LayoutEngineError";
    this.status = status;
  }
}

/**
 * Calls POST /api/v1/layout/optimize on the Layout Engine.
 * Returns a LayoutOptimizeResponse with recommended_strategy, score,
 * alternatives, elements, and layout metadata.
 */
export async function optimizeLayout(
  request: LayoutOptimizeRequest
): Promise<LayoutOptimizeResponse> {
  const url = `${LAYOUT_ENGINE_BASE_URL}/api/v1/layout/optimize`;
  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  } catch {
    throw new LayoutEngineError(
      `Layout Engine is unreachable at ${LAYOUT_ENGINE_BASE_URL}. ` +
        "Ensure the layout engine service is running on port 8001.",
      0
    );
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail || JSON.stringify(err);
    } catch { /* ignore */ }
    throw new LayoutEngineError(
      `Layout Engine returned an error: ${detail}`,
      response.status
    );
  }

  return response.json() as Promise<LayoutOptimizeResponse>;
}

/**
 * Calls POST /api/layouts/preview on the Layout Engine.
 * Returns LayoutPreviewResponse containing a { svg: string } field.
 */
export async function previewLayout(
  request: LayoutOptimizeRequest
): Promise<LayoutPreviewResponse> {
  const url = `${LAYOUT_ENGINE_BASE_URL}/api/layouts/preview`;
  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request }),
    });
  } catch {
    throw new LayoutEngineError(
      `Layout Engine preview unavailable at ${LAYOUT_ENGINE_BASE_URL}.`,
      0
    );
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail || JSON.stringify(err);
    } catch { /* ignore */ }
    throw new LayoutEngineError(
      `Layout Engine preview error: ${detail}`,
      response.status
    );
  }

  return response.json() as Promise<LayoutPreviewResponse>;
}

/**
 * Calls POST /api/layouts/pdf on the Layout Engine.
 * Returns a Blob (application/pdf) for download.
 */
export async function downloadLayoutPdf(
  request: LayoutOptimizeRequest
): Promise<Blob> {
  const url = `${LAYOUT_ENGINE_BASE_URL}/api/layouts/pdf`;
  const pdfRequest: LayoutPdfRequest = { request };
  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pdfRequest),
    });
  } catch {
    throw new LayoutEngineError(
      `Layout Engine PDF service unavailable at ${LAYOUT_ENGINE_BASE_URL}.`,
      0
    );
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail || JSON.stringify(err);
    } catch { /* ignore */ }
    throw new LayoutEngineError(
      `Layout Engine PDF error: ${detail}`,
      response.status
    );
  }

  return response.blob();
}
