(() => {
  "use strict";

  const elements = {
    status: document.querySelector("#update-status"),
    statusSide: document.querySelector("#update-status .status-side"),
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
    notice: document.querySelector(".form-panel .notice"),
  };

  let canonical = null;
  let mode = "client"; // "server" once a configured Supabase overlay is confirmed
  let overlayRecords = [];

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

  function currentState() {
    const latest = overlayRecords.length
      ? overlayRecords[overlayRecords.length - 1]
      : canonical.records[canonical.records.length - 1];
    return { overlay: overlayRecords, latest, target_draw_no: latest.draw_no + 1 };
  }

  function render() {
    const state = currentState();
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
        badge.textContent = mode === "server" ? "공유 overlay" : "브라우저 overlay";
        row.append(info, badge);
        elements.overlayList.append(row);
      });
    }
    elements.removeLast.disabled = state.overlay.length === 0;
    if (mode === "server") {
      elements.clearAll.style.display = "none";
    } else {
      elements.clearAll.disabled = state.overlay.length === 0;
    }
    elements.status.className = "status-strip ready";
    elements.status.querySelector("strong").textContent = "입력 준비 완료";
    elements.status.querySelector("span:not(.status-dot)").textContent = `다음 입력 회차 ${state.latest.draw_no + 1}회 · 예측 대상 ${state.target_draw_no}회`;
    if (elements.statusSide) {
      elements.statusSide.textContent = mode === "server"
        ? "공유 저장소(Supabase) 저장 · 모든 기기에서 동일하게 표시"
        : "localStorage 저장 · 외부 자동수집 없음";
    }
    if (elements.notice) {
      elements.notice.textContent = mode === "server"
        ? "사용자 입력은 공식 검증 데이터가 아니며, 공유 저장소에 저장되어 모든 기기에서 동일한 예측에 반영됩니다."
        : "사용자 입력은 공식 검증 데이터가 아니며 현재 브라우저에만 저장됩니다. 다른 기기나 브라우저에는 자동 동기화되지 않습니다.";
    }
  }

  function resetNumberFields() {
    elements.numberInputs.forEach((input) => { input.value = ""; });
    elements.bonus.value = "";
    elements.numberInputs[0].focus();
  }

  async function migrateLocalStorageIfNeeded() {
    const local = PAData.readOverlay();
    if (!local.length) return;
    let expected = overlayRecords.length
      ? overlayRecords[overlayRecords.length - 1].draw_no + 1
      : canonical.last_draw + 1;
    const toMigrate = [];
    for (const record of local) {
      if (Number(record.draw_no) !== expected) break;
      toMigrate.push(record);
      expected += 1;
    }
    if (!toMigrate.length) return;
    let migrated = 0;
    for (const record of toMigrate) {
      try {
        overlayRecords = await PAOverlayStore.saveServerRecord({
          draw_no: Number(record.draw_no),
          draw_date: record.draw_date,
          numbers: record.numbers,
          bonus_number: record.bonus_number,
        });
        migrated += 1;
      } catch (error) {
        break;
      }
    }
    if (migrated > 0) {
      PAData.writeOverlay(local.slice(migrated));
    }
  }

  async function submit(event) {
    event.preventDefault();
    elements.message.classList.add("hidden");
    const raw = {
      draw_no: Number(elements.drawNo.value),
      draw_date: elements.drawDate.value,
      numbers: elements.numberInputs.map((input) => Number(input.value)),
      bonus_number: Number(elements.bonus.value),
    };
    if (mode === "server") {
      try {
        overlayRecords = await PAOverlayStore.saveServerRecord(raw);
        resetNumberFields();
        render();
        setMessage("success", `${raw.draw_no}회 당첨번호를 공유 overlay에 저장했습니다. canonical 원본은 변경되지 않았습니다.`);
      } catch (error) {
        if (error.code === "overlay_store_unavailable" || error.code === "overlay_store_not_configured") {
          mode = "client";
          try {
            PAData.appendOverlay(canonical, raw);
            overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
            resetNumberFields();
            render();
            setMessage("error", `${error.message} 이 브라우저에만 임시로 저장했습니다.`);
          } catch (fallbackError) {
            setMessage("error", fallbackError.message);
          }
          return;
        }
        setMessage("error", error.message);
      }
      return;
    }
    try {
      PAData.appendOverlay(canonical, raw);
      overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
      resetNumberFields();
      render();
      setMessage("success", `${raw.draw_no}회 당첨번호를 사용자 overlay에 저장했습니다. canonical 원본은 변경되지 않았습니다.`);
    } catch (error) {
      setMessage("error", error.message);
    }
  }

  async function removeLast() {
    if (!overlayRecords.length) return;
    const latest = overlayRecords[overlayRecords.length - 1];
    if (!window.confirm(`${latest.draw_no}회 사용자 입력을 삭제하시겠습니까?`)) return;
    if (mode === "server") {
      try {
        overlayRecords = await PAOverlayStore.deleteServerLast(latest.draw_no);
        render();
        setMessage("success", `${latest.draw_no}회 사용자 입력을 삭제했습니다.`);
      } catch (error) {
        setMessage("error", error.message);
      }
      return;
    }
    PAData.removeLastOverlay(canonical);
    overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
    render();
    setMessage("success", `${latest.draw_no}회 사용자 입력을 삭제했습니다.`);
  }

  function clearAll() {
    if (mode === "server") return;
    if (!window.confirm("이 브라우저에 저장된 모든 사용자 입력 회차를 삭제하시겠습니까?")) return;
    PAData.clearOverlay();
    overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
    render();
    setMessage("success", "사용자 overlay를 모두 삭제했습니다. canonical 데이터는 그대로 유지됩니다.");
  }

  async function init() {
    try {
      canonical = await PAData.loadCanonical();
      try {
        const serverState = await PAOverlayStore.fetchServerOverlay();
        if (serverState.configured && !serverState.warning) {
          mode = "server";
          overlayRecords = serverState.records;
          await migrateLocalStorageIfNeeded();
        } else {
          mode = "client";
          overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
          if (serverState.configured && serverState.warning) {
            setMessage("error", `${serverState.warning} 이 브라우저에 임시로 저장합니다.`);
          }
        }
      } catch (error) {
        mode = "client";
        overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
      }
      render();
      elements.form.addEventListener("submit", submit);
      elements.removeLast.addEventListener("click", removeLast);
      elements.clearAll.addEventListener("click", clearAll);
      window.addEventListener("storage", () => {
        if (mode === "client") {
          overlayRecords = PAData.validateOverlaySequence(canonical, PAData.readOverlay());
          render();
        }
      });
    } catch (error) {
      elements.status.className = "status-strip error";
      elements.status.querySelector("strong").textContent = "데이터 로드 실패";
      elements.status.querySelector("span:not(.status-dot)").textContent = error.message;
      elements.form.querySelectorAll("input, button").forEach((element) => { element.disabled = true; });
    }
  }

  init();
})();
