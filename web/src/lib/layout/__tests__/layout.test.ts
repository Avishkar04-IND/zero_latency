/**
 * Unit tests for the Layout Engine service (web/src/services/api/layout.ts).
 *
 * All Layout Engine HTTP calls are mocked — tests do NOT require port 8001.
 * Pattern mirrors the assistant test (node --experimental-strip-types --test).
 */

import { describe, it, mock, before, after } from "node:test";
import assert from "node:assert/strict";

import { optimizeLayout, previewLayout, downloadLayoutPdf } from "../../../services/api/layout.ts";

// ─── Mock fetch globally before running tests ──────────────────────────────────

let mockFetchImpl: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

const globalAny = globalThis as unknown as { fetch: typeof fetch };
const originalFetch = globalAny.fetch;

before(() => {
  globalAny.fetch = ((input: RequestInfo | URL, init?: RequestInit) =>
    mockFetchImpl(input, init)) as typeof fetch;
});

after(() => {
  if (originalFetch !== undefined) {
    globalAny.fetch = originalFetch;
  }
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

function makeJsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function makeErrorResponse(detail: string, status: number): Response {
  return new Response(JSON.stringify({ detail }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const MINIMAL_REQUEST = {
  package: {
    package_width_mm: 120,
    package_height_mm: 60,
    printing_area_width_mm: 105,
    printing_area_height_mm: 50,
  },
  tablet: { tablet_count: 10, tablet_diameter_mm: 9 },
};

const MOCK_OPTIMIZE_RESPONSE = {
  id: "layout_recommendation_001",
  success: true,
  recommended_strategy: "ACCESSIBILITY",
  score: 0.6648,
  space_utilization: 0.72,
  readability: 0.88,
  print_efficiency: 0.65,
  cost_efficiency: 0.55,
  scan_reliability: 0.91,
  balanced_score: 0.64,
  accessibility_score: 0.66,
  used_printable_area: 4100.0,
  unused_printable_area: 1150.0,
  candidates_evaluated: 3,
  elements: [
    { id: "el-1", type: "text", content: "Dolo 650", x_mm: 5, y_mm: 5, width_mm: 40, height_mm: 5 },
  ],
  validation: { valid: true, errors: [], warnings: [] },
  alternatives: [
    { strategy: "COST", score: 0.62, space_utilization: 0.70, readability: 0.80, print_efficiency: 0.68, cost_efficiency: 0.75, scan_reliability: 0.85, warnings: [], errors: [] },
  ],
  warnings: [],
  errors: [],
  layout: { package_width_mm: 120, package_height_mm: 60 },
};

const MOCK_PREVIEW_RESPONSE = {
  success: true,
  layout_id: "layout_preview_001",
  svg: '<svg xmlns="http://www.w3.org/2000/svg" width="120mm" height="60mm"></svg>',
  validation: { valid: true, errors: [], warnings: [] },
};

// ─── Tests ────────────────────────────────────────────────────────────────────

describe("Layout Engine Service — optimizeLayout", () => {
  it("A. Returns LayoutOptimizeResponse on success", async () => {
    mockFetchImpl = async () => makeJsonResponse(MOCK_OPTIMIZE_RESPONSE);
    const result = await optimizeLayout(MINIMAL_REQUEST);
    assert.equal(result.success, true);
    assert.equal(result.recommended_strategy, "ACCESSIBILITY");
    assert.ok(typeof result.score === "number");
    assert.ok(Array.isArray(result.elements));
    assert.equal(result.elements.length, 1);
  });

  it("B. Sends request to /api/v1/layout/optimize with POST + JSON body", async () => {
    let capturedUrl = "";
    let capturedMethod = "";
    let capturedBody = "";
    mockFetchImpl = async (url, init) => {
      capturedUrl = url as string;
      capturedMethod = init?.method ?? "";
      capturedBody = init?.body as string;
      return makeJsonResponse(MOCK_OPTIMIZE_RESPONSE);
    };
    await optimizeLayout(MINIMAL_REQUEST);
    assert.ok(capturedUrl.includes("/api/v1/layout/optimize"), `URL was: ${capturedUrl}`);
    assert.equal(capturedMethod, "POST");
    const body = JSON.parse(capturedBody);
    assert.ok(body.package, "body.package is missing");
    assert.ok(body.tablet, "body.tablet is missing");
  });

  it("C. Passes medicine, batch, code fields when provided", async () => {
    let capturedBody = "";
    mockFetchImpl = async (_url, init) => {
      capturedBody = init?.body as string;
      return makeJsonResponse(MOCK_OPTIMIZE_RESPONSE);
    };
    const requestWithContext = {
      ...MINIMAL_REQUEST,
      medicine: { name: "Amaryl 1mg", dosage: "1 mg", manufacturer: "Sanofi India" },
      batch: { batch_number: "BTH-AMAR-2026A1", manufacturing_date: "2026-09-11", expiry_date: "2028-09-10" },
      code: { type: "QR", value: "MED-2714-E5B9-6485", min_size_mm: 13.0, serial_number: "MED-2714-E5B9-6485" },
    };
    await optimizeLayout(requestWithContext);
    const body = JSON.parse(capturedBody);
    assert.equal(body.medicine.name, "Amaryl 1mg");
    assert.equal(body.batch.batch_number, "BTH-AMAR-2026A1");
    assert.equal(body.code.serial_number, "MED-2714-E5B9-6485");
  });

  it("D. Throws LayoutEngineError on HTTP 422 (invalid layout)", async () => {
    mockFetchImpl = async () => makeErrorResponse("Printing area width exceeds package width", 422);
    await assert.rejects(
      () => optimizeLayout(MINIMAL_REQUEST),
      (err: Error) => {
        assert.ok(err.message.includes("Layout Engine returned an error"), err.message);
        return true;
      }
    );
  });

  it("E. Throws LayoutEngineError with status 0 when fetch throws (engine down)", async () => {
    mockFetchImpl = async () => { throw new TypeError("fetch failed"); };
    await assert.rejects(
      () => optimizeLayout(MINIMAL_REQUEST),
      (err: Error & { status?: number }) => {
        assert.ok(err.message.includes("unreachable"), err.message);
        assert.equal(err.status, 0);
        return true;
      }
    );
  });

  it("F. Returns alternatives array when present", async () => {
    mockFetchImpl = async () => makeJsonResponse(MOCK_OPTIMIZE_RESPONSE);
    const result = await optimizeLayout(MINIMAL_REQUEST);
    assert.ok(Array.isArray(result.alternatives));
    assert.equal(result.alternatives!.length, 1);
    assert.equal(result.alternatives![0].strategy, "COST");
  });

  it("G. Score is a normalised float between 0 and 1", async () => {
    mockFetchImpl = async () => makeJsonResponse(MOCK_OPTIMIZE_RESPONSE);
    const result = await optimizeLayout(MINIMAL_REQUEST);
    assert.ok(result.score != null && result.score >= 0 && result.score <= 1);
  });

  it("H. Returns empty warnings array when no warnings", async () => {
    mockFetchImpl = async () => makeJsonResponse(MOCK_OPTIMIZE_RESPONSE);
    const result = await optimizeLayout(MINIMAL_REQUEST);
    assert.deepEqual(result.warnings, []);
  });
});

describe("Layout Engine Service — previewLayout", () => {
  it("I. Returns SVG string on success", async () => {
    mockFetchImpl = async () => makeJsonResponse(MOCK_PREVIEW_RESPONSE);
    const result = await previewLayout(MINIMAL_REQUEST);
    assert.equal(result.success, true);
    assert.ok(typeof result.svg === "string");
    assert.ok(result.svg!.includes("<svg"), "SVG string should contain <svg tag");
  });

  it("J. Sends request body wrapped in { request: ... } to /api/layouts/preview", async () => {
    let capturedBody = "";
    mockFetchImpl = async (url, init) => {
      capturedBody = init?.body as string;
      return makeJsonResponse(MOCK_PREVIEW_RESPONSE);
    };
    await previewLayout(MINIMAL_REQUEST);
    const body = JSON.parse(capturedBody);
    assert.ok(body.request, "body.request wrapper is missing");
    assert.ok(body.request.package, "body.request.package is missing");
  });

  it("K. Throws on network error", async () => {
    mockFetchImpl = async () => { throw new TypeError("fetch failed"); };
    await assert.rejects(
      () => previewLayout(MINIMAL_REQUEST),
      (err: Error & { status?: number }) => {
        assert.equal(err.status, 0);
        return true;
      }
    );
  });
});

describe("Layout Engine Service — downloadLayoutPdf", () => {
  it("L. Returns a Blob on success", async () => {
    const pdfBytes = new Uint8Array([0x25, 0x50, 0x44, 0x46]); // %PDF magic bytes
    mockFetchImpl = async () =>
      new Response(pdfBytes, {
        status: 200,
        headers: { "Content-Type": "application/pdf" },
      });
    const blob = await downloadLayoutPdf(MINIMAL_REQUEST);
    assert.ok(blob instanceof Blob);
    assert.ok(blob.size > 0);
  });

  it("M. Sends request body as { request: ... } to /api/layouts/pdf", async () => {
    let capturedUrl = "";
    let capturedBody = "";
    mockFetchImpl = async (url, init) => {
      capturedUrl = url as string;
      capturedBody = init?.body as string;
      return new Response(new Uint8Array([0x25, 0x50, 0x44, 0x46]), {
        status: 200,
        headers: { "Content-Type": "application/pdf" },
      });
    };
    await downloadLayoutPdf(MINIMAL_REQUEST);
    assert.ok(capturedUrl.includes("/api/layouts/pdf"), `URL was: ${capturedUrl}`);
    const body = JSON.parse(capturedBody);
    assert.ok(body.request, "body.request wrapper is missing");
  });

  it("N. Throws on HTTP 500 error", async () => {
    mockFetchImpl = async () => makeErrorResponse("PDF generation failed", 500);
    await assert.rejects(
      () => downloadLayoutPdf(MINIMAL_REQUEST),
      (err: Error) => {
        assert.ok(err.message.includes("PDF error") || err.message.includes("Layout Engine"), err.message);
        return true;
      }
    );
  });
});
