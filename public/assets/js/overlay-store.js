(() => {
  "use strict";

  async function fetchServerOverlay() {
    const response = await fetch("/api/overlay", { cache: "no-store" });
    if (!response.ok) throw new Error(`서버 overlay 응답 오류: HTTP ${response.status}`);
    const payload = await response.json();
    return {
      configured: Boolean(payload.configured),
      records: Array.isArray(payload.records) ? payload.records : [],
      warning: payload.warning || null,
    };
  }

  async function saveServerRecord(record) {
    const response = await fetch("/api/overlay", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify({ record }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(payload.detail || `HTTP ${response.status}`);
      error.status = response.status;
      error.code = payload.error;
      throw error;
    }
    return payload.records || [];
  }

  async function deleteServerLast(drawNo) {
    const response = await fetch("/api/overlay", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify({ draw_no: drawNo }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const error = new Error(payload.detail || `HTTP ${response.status}`);
      error.status = response.status;
      error.code = payload.error;
      throw error;
    }
    return payload.records || [];
  }

  window.PAOverlayStore = {
    fetchServerOverlay,
    saveServerRecord,
    deleteServerLast,
  };
})();
