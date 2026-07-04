(() => {
  "use strict";

  const elements = {
    status: document.querySelector("#update-status"),
    drawNo: document.querySelector("#draw-no"),
    drawDate: document.querySelector("#draw-date"),
    numberInputs: [...document.querySelectorAll("[data-winning-number]")],
    bonus: document.querySelector("#bonus-number"),
    form: document.querySelector("#draw-form"),
    message: document.querySelector("#form-message"),
    overlayList: document.querySelector("#overlay-list"),
    overlayCount: document.querySelector("#overlay-count"),
    removeLast: document.querySelector("#remove-last"),
    clearAll: document.querySelector("#clear-all"),
    latestCanonical: document.querySelector("#latest-canonical"),
    latestEffective: document.querySelector("#latest-effective"),
    nextTarget: document.querySelector("#next-target"),
  };

  let canonical = null;

  function setMessage(type, text) {
    elements.message.className = type === "error" ? "error-box" : "notice";
    elements.message.textContent = text;
    elements.message.classList.remove("hidden");
  }

  function defaultNextDate(previous) {
    const value = new Date(`${previous}T00:00:00Z`);
    value.setUTCDate(value.getUTCDate() + 7);
    return value.toISOString().slice(0, 10);
  }

  function render() {
    const state = PAData.latestState(canonical, PAData.readOverlay());
    elements.latestCanonical.textContent = `${canonical.last_draw}회`;
    elements.latestEffective.textContent = `${state.latest.draw_no}회`;
    elements.nextTarget.textContent = `${state.target_draw_no}회`;
    elements.drawNo.value = String(state.latest.draw_no + 1);
    elements.drawDate.min = defaultNextDate(state.latest.draw_date);
    if (!elements.drawDate.value || elements.drawDate.value <= state.latest.draw_date) {
      elements.drawDate.value = defaultNextDate(state.latest.draw_date);
    }
    elements.overlayCount.textContent = `${state.overlay.length}건`;
    elements.overlayList.replaceChildren();
    if (!state.overlay.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "저장된 사용자 입력 회차가 없습니다.";
      elements.overlayList.append(empty);
    } else {
      [...state.overlay].reverse().forEach((draw) => {
        const row = document.createElement("article");
        row.className = "overlay-row";
        const info = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = `${draw.draw_no}회 · ${draw.draw_date.replaceAll("-", ".")}`;
        const detail = document.createElement("span");
        detail.textContent = `${draw.numbers.join(" · ")} + 보너스 ${draw.bonus_number}`;
        info.append(title, detail);
        const badge = document.createElement("span");
        badge.textContent = "브라우저 overlay";
        row.append(info, badge);
        elements.overlayList.append(row);
      });
    }
    elements.removeLast.disabled = state.overlay.length === 0;
    elements.clearAll.disabled = state.overlay.length === 0;
    elements.status.className = "status-strip ready";
    elements.status.querySelector("strong").textContent = "입력 준비 완료";
    elements.status.querySelector("span:not(.status-dot)").textContent = `다음 입력 회차 ${state.latest.draw_no + 1}회 · 예측 대상 ${state.target_draw_no}회`;
  }

  function resetNumberFields() {
    elements.numberInputs.forEach((input) => { input.value = ""; });
    elements.bonus.value = "";
    elements.numberInputs[0].focus();
  }

  function submit(event) {
    event.preventDefault();
    elements.message.classList.add("hidden");
    try {
      const raw = {
        draw_no: Number(elements.drawNo.value),
        draw_date: elements.drawDate.value,
        numbers: elements.numberInputs.map((input) => Number(input.value)),
        bonus_number: Number(elements.bonus.value),
      };
      PAData.appendOverlay(canonical, raw);
      resetNumberFields();
      render();
      setMessage("success", `${raw.draw_no}회 당첨번호를 사용자 overlay에 저장했습니다. canonical 원본은 변경되지 않았습니다.`);
    } catch (error) {
      setMessage("error", error.message);
    }
  }

  function removeLast() {
    const state = PAData.latestState(canonical, PAData.readOverlay());
    if (!state.overlay.length) return;
    const latest = state.overlay[state.overlay.length - 1];
    if (!window.confirm(`${latest.draw_no}회 사용자 입력을 삭제하시겠습니까?`)) return;
    PAData.removeLastOverlay(canonical);
    render();
    setMessage("success", `${latest.draw_no}회 사용자 입력을 삭제했습니다.`);
  }

  function clearAll() {
    if (!window.confirm("이 브라우저에 저장된 모든 사용자 입력 회차를 삭제하시겠습니까?")) return;
    PAData.clearOverlay();
    render();
    setMessage("success", "사용자 overlay를 모두 삭제했습니다. canonical 데이터는 그대로 유지됩니다.");
  }

  async function init() {
    try {
      canonical = await PAData.loadCanonical();
      render();
      elements.form.addEventListener("submit", submit);
      elements.removeLast.addEventListener("click", removeLast);
      elements.clearAll.addEventListener("click", clearAll);
      window.addEventListener("storage", render);
    } catch (error) {
      elements.status.className = "status-strip error";
      elements.status.querySelector("strong").textContent = "데이터 로드 실패";
      elements.status.querySelector("span:not(.status-dot)").textContent = error.message;
      elements.form.querySelectorAll("input, button").forEach((element) => { element.disabled = true; });
    }
  }

  init();
})();
