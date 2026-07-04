(() => {
  "use strict";

  const OVERLAY_KEY = "predictive-algorithm.draw-overlay.v1";

  function readOverlay() {
    try {
      const parsed = JSON.parse(localStorage.getItem(OVERLAY_KEY) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      console.error(error);
      return [];
    }
  }

  function writeOverlay(records) {
    localStorage.setItem(OVERLAY_KEY, JSON.stringify(records));
    window.dispatchEvent(new CustomEvent("pa:overlay-changed", { detail: records }));
  }

  async function loadCanonical() {
    const response = await fetch("/api/archive", { cache: "no-store" });
    if (!response.ok) throw new Error(`과거 데이터 응답 오류: HTTP ${response.status}`);
    const payload = await response.json();
    if (!Array.isArray(payload.records) || payload.records.length !== payload.record_count) {
      throw new Error("과거 데이터 계약이 올바르지 않습니다.");
    }
    return payload;
  }

  function validateNumbers(numbers, bonusNumber) {
    if (!Array.isArray(numbers) || numbers.length !== 6) {
      throw new Error("당첨번호는 정확히 6개여야 합니다.");
    }
    const normalized = numbers.map((value) => Number(value));
    if (normalized.some((value) => !Number.isInteger(value) || value < 1 || value > 45)) {
      throw new Error("당첨번호는 1~45 사이의 정수여야 합니다.");
    }
    if (new Set(normalized).size !== 6) {
      throw new Error("당첨번호 6개에 중복이 있습니다.");
    }
    const bonus = Number(bonusNumber);
    if (!Number.isInteger(bonus) || bonus < 1 || bonus > 45) {
      throw new Error("보너스번호는 1~45 사이의 정수여야 합니다.");
    }
    if (normalized.includes(bonus)) {
      throw new Error("보너스번호는 당첨번호와 중복될 수 없습니다.");
    }
    normalized.sort((a, b) => a - b);
    return { numbers: normalized, bonus_number: bonus };
  }

  function validateOverlaySequence(canonical, overlay) {
    if (!canonical?.records?.length) throw new Error("canonical 데이터가 없습니다.");
    let expected = Number(canonical.last_draw) + 1;
    let previousDate = canonical.records[canonical.records.length - 1].draw_date;
    return overlay.map((record) => {
      const drawNo = Number(record.draw_no);
      if (!Number.isInteger(drawNo) || drawNo !== expected) {
        throw new Error(`사용자 입력 회차는 ${expected}회부터 연속이어야 합니다.`);
      }
      if (typeof record.draw_date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(record.draw_date)) {
        throw new Error(`${drawNo}회 추첨일 형식이 올바르지 않습니다.`);
      }
      if (record.draw_date <= previousDate) {
        throw new Error(`${drawNo}회 추첨일은 이전 회차보다 늦어야 합니다.`);
      }
      const validated = validateNumbers(record.numbers, record.bonus_number);
      previousDate = record.draw_date;
      expected += 1;
      return {
        draw_no: drawNo,
        draw_date: record.draw_date,
        numbers: validated.numbers,
        bonus_number: validated.bonus_number,
        source: "user_overlay",
        verification_status: "user_entered",
        locked: false,
      };
    });
  }

  function mergedRecords(canonical, overlay) {
    const validatedOverlay = validateOverlaySequence(canonical, overlay);
    return [...canonical.records, ...validatedOverlay];
  }

  function latestState(canonical, overlay) {
    const validatedOverlay = validateOverlaySequence(canonical, overlay);
    const latest = validatedOverlay.length
      ? validatedOverlay[validatedOverlay.length - 1]
      : canonical.records[canonical.records.length - 1];
    return {
      canonical,
      overlay: validatedOverlay,
      latest,
      target_draw_no: latest.draw_no + 1,
      records: [...canonical.records, ...validatedOverlay],
    };
  }

  function appendOverlay(canonical, rawRecord) {
    const current = validateOverlaySequence(canonical, readOverlay());
    const expected = canonical.last_draw + current.length + 1;
    const drawNo = Number(rawRecord.draw_no);
    if (drawNo !== expected) throw new Error(`다음 입력 회차는 ${expected}회입니다.`);
    const previousDate = current.length
      ? current[current.length - 1].draw_date
      : canonical.records[canonical.records.length - 1].draw_date;
    if (rawRecord.draw_date <= previousDate) throw new Error("추첨일은 이전 회차보다 늦어야 합니다.");
    const validated = validateNumbers(rawRecord.numbers, rawRecord.bonus_number);
    const record = {
      draw_no: drawNo,
      draw_date: rawRecord.draw_date,
      numbers: validated.numbers,
      bonus_number: validated.bonus_number,
      source: "user_overlay",
      verification_status: "user_entered",
      locked: false,
    };
    const next = [...current, record];
    writeOverlay(next);
    return next;
  }

  function removeLastOverlay(canonical) {
    const current = validateOverlaySequence(canonical, readOverlay());
    current.pop();
    writeOverlay(current);
    return current;
  }

  function clearOverlay() {
    writeOverlay([]);
  }

  function ballClass(number) {
    if (number <= 10) return "ball-yellow";
    if (number <= 20) return "ball-blue";
    if (number <= 30) return "ball-red";
    if (number <= 40) return "ball-gray";
    return "ball-green";
  }

  function createBall(number, compact = false) {
    const element = document.createElement("span");
    element.className = compact
      ? `frequency-number ${ballClass(number)}`
      : `lotto-ball ${ballClass(number)}`;
    element.textContent = String(number);
    element.setAttribute("aria-label", `${number}번`);
    return element;
  }

  window.PAData = {
    OVERLAY_KEY,
    readOverlay,
    writeOverlay,
    loadCanonical,
    validateNumbers,
    validateOverlaySequence,
    mergedRecords,
    latestState,
    appendOverlay,
    removeLastOverlay,
    clearOverlay,
    ballClass,
    createBall,
  };
})();
