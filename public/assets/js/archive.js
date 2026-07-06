(() => {
  "use strict";

  const state = { canonical: null, overlay: [], records: [], filtered: [], visibleLimit: 30, overlayMode: "client" };
  const elements = {
    status: document.querySelector("#data-status"),
    summaryCount: document.querySelector("#summary-count"),
    summaryLatest: document.querySelector("#summary-latest"),
    summaryOverlay: document.querySelector("#summary-overlay"),
    summaryVersion: document.querySelector("#summary-version"),
    search: document.querySelector("#draw-search"),
    year: document.querySelector("#year-filter"),
    sort: document.querySelector("#sort-order"),
    reset: document.querySelector("#reset-filter"),
    visibleCount: document.querySelector("#visible-count"),
    list: document.querySelector("#draw-list"),
    loadMore: document.querySelector("#load-more"),
    statWindow: document.querySelector("#stat-window"),
    frequencyGrid: document.querySelector("#frequency-grid"),
    template: document.querySelector("#draw-card-template"),
  };

  function badge(draw) {
    if (draw.source === "user_overlay") return { text: "사용자 입력", className: "overlay" };
    if (draw.locked && draw.verification_status === "verified") return { text: "공식 대조 완료", className: "verified" };
    return { text: "자동 형식 검증", className: "" };
  }

  function rebuild() {
    state.overlay = state.overlayMode === "server"
      ? state.serverOverlayRecords
      : PAData.validateOverlaySequence(state.canonical, PAData.readOverlay());
    state.records = [...state.canonical.records, ...state.overlay];
    state.filtered = [...state.records].sort((a, b) => b.draw_no - a.draw_no);
    state.visibleLimit = 30;
    renderSummary();
    populateYears();
    applyFilters();
    renderFrequency();
  }

  function renderSummary() {
    const latest = state.records[state.records.length - 1];
    elements.summaryCount.textContent = `${state.records.length.toLocaleString("ko-KR")}회`;
    elements.summaryLatest.textContent = `${latest.draw_no}회`;
    elements.summaryOverlay.textContent = `${state.overlay.length}건`;
    elements.summaryVersion.textContent = state.canonical.data_version;
  }

  function populateYears() {
    const current = elements.year.value || "all";
    elements.year.replaceChildren(new Option("전체 연도", "all"));
    const counts = new Map();
    state.records.forEach((draw) => {
      const year = draw.draw_date.slice(0, 4);
      counts.set(year, (counts.get(year) || 0) + 1);
    });
    [...counts.entries()].sort((a, b) => b[0].localeCompare(a[0])).forEach(([year, count]) => {
      elements.year.append(new Option(`${year}년 · ${count}회`, year));
    });
    if ([...elements.year.options].some((option) => option.value === current)) elements.year.value = current;
  }

  function createDrawCard(draw) {
    const fragment = elements.template.content.cloneNode(true);
    const card = fragment.querySelector(".draw-card");
    if (draw.source === "user_overlay") card.classList.add("user-overlay");
    fragment.querySelector(".draw-number").textContent = `${draw.draw_no}회`;
    const time = fragment.querySelector(".draw-date");
    time.dateTime = draw.draw_date;
    time.textContent = draw.draw_date.replaceAll("-", ".");
    const badgeData = badge(draw);
    const badgeElement = fragment.querySelector(".verification-badge");
    badgeElement.textContent = badgeData.text;
    if (badgeData.className) badgeElement.classList.add(badgeData.className);
    const main = fragment.querySelector(".main-balls");
    draw.numbers.forEach((number) => main.append(PAData.createBall(number)));
    fragment.querySelector(".bonus-ball").append(PAData.createBall(draw.bonus_number));
    fragment.querySelector(".draw-source").textContent = draw.source === "user_overlay" ? "브라우저 사용자 입력 overlay" : draw.source;
    fragment.querySelector(".draw-status").textContent = `${draw.verification_status} / locked: ${Boolean(draw.locked)}`;
    fragment.querySelector(".draw-checksum").textContent = draw.checksum || "사용자 입력 · canonical checksum 없음";
    return card;
  }

  function renderDraws() {
    elements.list.replaceChildren();
    const visible = state.filtered.slice(0, state.visibleLimit);
    if (!visible.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "조건에 맞는 회차가 없습니다.";
      elements.list.append(empty);
    } else {
      const fragment = document.createDocumentFragment();
      visible.forEach((draw) => fragment.append(createDrawCard(draw)));
      elements.list.append(fragment);
    }
    elements.visibleCount.textContent = `${state.filtered.length.toLocaleString("ko-KR")}개 결과`;
    elements.loadMore.hidden = visible.length >= state.filtered.length;
  }

  function applyFilters() {
    const query = elements.search.value.trim();
    const year = elements.year.value;
    const order = elements.sort.value;
    let records = [...state.records];
    if (query) records = records.filter((draw) => String(draw.draw_no).includes(query));
    if (year !== "all") records = records.filter((draw) => draw.draw_date.startsWith(year));
    records.sort((a, b) => order === "asc" ? a.draw_no - b.draw_no : b.draw_no - a.draw_no);
    state.filtered = records;
    state.visibleLimit = 30;
    renderDraws();
  }

  function renderFrequency() {
    const windowValue = elements.statWindow.value;
    const count = windowValue === "all" ? state.records.length : Number(windowValue);
    const source = state.records.slice(-count);
    const frequencies = Array(46).fill(0);
    source.forEach((draw) => draw.numbers.forEach((number) => { frequencies[number] += 1; }));
    const maximum = Math.max(...frequencies, 1);
    elements.frequencyGrid.replaceChildren();
    for (let number = 1; number <= 45; number += 1) {
      const item = document.createElement("div");
      item.className = "frequency-item";
      item.append(PAData.createBall(number, true));
      const track = document.createElement("div");
      track.className = "frequency-track";
      const fill = document.createElement("div");
      fill.className = "frequency-fill";
      fill.style.width = `${(frequencies[number] / maximum) * 100}%`;
      track.append(fill);
      item.append(track);
      const value = document.createElement("span");
      value.className = "frequency-count";
      value.textContent = String(frequencies[number]);
      item.append(value);
      elements.frequencyGrid.append(item);
    }
  }

  function bind() {
    elements.search.addEventListener("input", applyFilters);
    elements.year.addEventListener("change", applyFilters);
    elements.sort.addEventListener("change", applyFilters);
    elements.statWindow.addEventListener("change", renderFrequency);
    elements.reset.addEventListener("click", () => {
      elements.search.value = "";
      elements.year.value = "all";
      elements.sort.value = "desc";
      applyFilters();
    });
    elements.loadMore.addEventListener("click", () => { state.visibleLimit += 30; renderDraws(); });
    window.addEventListener("pa:overlay-changed", rebuild);
    window.addEventListener("storage", rebuild);
  }

  async function init() {
    try {
      state.canonical = await PAData.loadCanonical();
      try {
        const serverState = await PAOverlayStore.fetchServerOverlay();
        if (serverState.configured && !serverState.warning) {
          state.overlayMode = "server";
          state.serverOverlayRecords = serverState.records;
        }
      } catch (error) {
        state.overlayMode = "client";
      }
      rebuild();
      bind();
      elements.status.classList.add("ready");
      elements.status.lastChild.textContent = ` 데이터 준비 완료 · canonical ${state.canonical.record_count}회`;
    } catch (error) {
      console.error(error);
      elements.status.classList.add("error");
      elements.status.lastChild.textContent = ` 데이터 로드 실패 · ${error.message}`;
      elements.list.innerHTML = `<div class="empty-state">${error.message}</div>`;
    }
  }

  init();
})();
