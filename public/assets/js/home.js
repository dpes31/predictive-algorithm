(() => {
  "use strict";

  const elements = {
    status: document.querySelector("#app-status"),
    statusTitle: document.querySelector("#status-title"),
    statusDetail: document.querySelector("#status-detail"),
    latestDraw: document.querySelector("#latest-draw"),
    targetDraw: document.querySelector("#target-draw"),
    overlayCount: document.querySelector("#overlay-count"),
    predictButton: document.querySelector("#predict-button"),
    resultPanel: document.querySelector("#result-panel"),
    resultTarget: document.querySelector("#result-target"),
    resultSets: document.querySelector("#result-sets"),
    resultGeneratedAt: document.querySelector("#result-generated-at"),
    resultSeed: document.querySelector("#result-seed"),
    resultHash: document.querySelector("#result-hash"),
    resultDataHash: document.querySelector("#result-data-hash"),
    resultReason: document.querySelector("#result-reason"),
    error: document.querySelector("#prediction-error"),
  };

  let canonical = null;
  let overlayMode = "client";
  let serverOverlayRecords = [];

  function setStatus(type, title, detail) {
    elements.status.className = `status-strip ${type || ""}`.trim();
    elements.statusTitle.textContent = title;
    elements.statusDetail.textContent = detail;
  }

  function localState() {
    return PAData.latestState(canonical, PAData.readOverlay());
  }

  function currentState() {
    if (overlayMode === "server") {
      const latest = serverOverlayRecords.length
        ? serverOverlayRecords[serverOverlayRecords.length - 1]
        : canonical.records[canonical.records.length - 1];
      return { overlay: serverOverlayRecords, latest, target_draw_no: latest.draw_no + 1 };
    }
    return localState();
  }

  function refreshSummary() {
    if (!canonical) return;
    try {
      const state = currentState();
      elements.latestDraw.textContent = `${state.latest.draw_no}회`;
      elements.targetDraw.textContent = `${state.target_draw_no}회`;
      elements.overlayCount.textContent = `${state.overlay.length}건`;
      document.querySelector("#hero-title").textContent = `${state.target_draw_no}회차 예측하기`;
      const sourceLabel = overlayMode === "server" ? "공유 저장소 입력" : "사용자 입력";
      setStatus(
        "ready",
        "데이터 준비 완료",
        `canonical ${canonical.first_draw}~${canonical.last_draw}회 + ${sourceLabel} ${state.overlay.length}건`
      );
      elements.predictButton.disabled = false;
      elements.resultPanel.classList.add("hidden");
      elements.error.classList.add("hidden");
    } catch (error) {
      setStatus("error", "사용자 입력 데이터 오류", error.message);
      elements.predictButton.disabled = true;
    }
  }

  function renderPrediction(payload) {
    if (!payload || payload.final_distribution !== "M0_ONLY") {
      throw new Error("CONTROL_M0 결과가 아닙니다.");
    }
    if (!Array.isArray(payload.candidate_sets) || payload.candidate_sets.length !== 5) {
      throw new Error("후보세트가 정확히 5개가 아닙니다.");
    }
    elements.resultSets.replaceChildren();
    payload.candidate_sets.forEach((item) => {
      if (!Array.isArray(item.numbers) || item.numbers.length !== 6) {
        throw new Error("후보세트의 번호 개수가 올바르지 않습니다.");
      }
      const row = document.createElement("article");
      row.className = "result-row";
      const rank = document.createElement("div");
      rank.className = "result-rank";
      rank.textContent = `${item.rank}세트`;
      const balls = document.createElement("div");
      balls.className = "ball-row";
      item.numbers.forEach((number) => balls.append(PAData.createBall(number)));
      row.append(rank, balls);
      elements.resultSets.append(row);
    });
    elements.resultTarget.textContent = `대상 ${payload.target_draw_no}회 · ${payload.input_last_draw}회까지 반영`;
    elements.resultGeneratedAt.textContent = payload.generated_at;
    elements.resultSeed.textContent = payload.seed;
    elements.resultHash.textContent = payload.hashes.prediction_hash;
    elements.resultDataHash.textContent = payload.hashes.effective_data_hash;
    elements.resultReason.textContent = payload.reason;
    elements.resultPanel.classList.remove("hidden");
    elements.resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function predict() {
    if (!canonical) return;
    elements.predictButton.disabled = true;
    elements.predictButton.textContent = "생성 중…";
    elements.error.classList.add("hidden");
    try {
      const overlay = overlayMode === "server"
        ? []
        : PAData.validateOverlaySequence(canonical, PAData.readOverlay());
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ overlay }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`);
      renderPrediction(payload);
    } catch (error) {
      elements.error.textContent = `예측 결과를 생성하지 못했습니다: ${error.message}`;
      elements.error.classList.remove("hidden");
    } finally {
      elements.predictButton.disabled = false;
      elements.predictButton.textContent = "예측하기";
    }
  }

  async function init() {
    setStatus("", "데이터 불러오는 중", "canonical 데이터와 사용자 입력을 대조하고 있습니다.");
    elements.predictButton.disabled = true;
    try {
      canonical = await PAData.loadCanonical();
      try {
        const serverState = await PAOverlayStore.fetchServerOverlay();
        if (serverState.configured) {
          overlayMode = "server";
          serverOverlayRecords = serverState.records;
        }
      } catch (error) {
        overlayMode = "client";
      }
      refreshSummary();
      elements.predictButton.addEventListener("click", predict);
      if (overlayMode === "client") {
        window.addEventListener("pa:overlay-changed", refreshSummary);
        window.addEventListener("storage", refreshSummary);
      }
    } catch (error) {
      setStatus("error", "데이터 로드 실패", error.message);
      elements.error.textContent = error.message;
      elements.error.classList.remove("hidden");
    }
  }

  init();
})();
