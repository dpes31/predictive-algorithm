(() => {
  "use strict";

  const state = {
    data: null,
    filtered: [],
    visibleLimit: 30,
  };

  const elements = {
    status: document.querySelector("#data-status"),
    summaryCount: document.querySelector("#summary-count"),
    summaryLatest: document.querySelector("#summary-latest"),
    summaryVerified: document.querySelector("#summary-verified"),
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

  function ballClass(number) {
    if (number <= 10) return "ball-yellow";
    if (number <= 20) return "ball-blue";
    if (number <= 30) return "ball-red";
    if (number <= 40) return "ball-gray";
    return "ball-green";
  }

  function createBall(number, compact = false) {
    const ball = document.createElement("span");
    ball.className = compact
      ? `frequency-number ${ballClass(number)}`
      : `lotto-ball ${ballClass(number)}`;
    ball.textContent = String(number);
    ball.setAttribute("aria-label", `${number}번`);
    return ball;
  }

  function statusLabel(draw) {
    if (draw.locked && draw.verification_status === "verified") {
      return { text: "공식 대조 완료", className: "verified" };
    }
    if (draw.verification_status === "auto_checked") {
      return { text: "자동 형식 검증", className: "" };
    }
    if (draw.verification_status === "pending_manual") {
      return { text: "공식 확인 대기", className: "" };
    }
    return { text: draw.verification_status, className: "" };
  }

  function renderSummary() {
    const data = state.data;
    const verifiedCount = data.draws.filter(
      (draw) => draw.locked && draw.verification_status === "verified"
    ).length;
    elements.summaryCount.textContent = `${data.record_count.toLocaleString("ko-KR")}회`;
    elements.summaryLatest.textContent = `${data.last_draw}회`;
    elements.summaryVerified.textContent = `${verifiedCount.toLocaleString("ko-KR")}회`;
    elements.summaryVersion.textContent = data.data_version;

    Object.keys(data.years).forEach((year) => {
      const option = document.createElement("option");
      option.value = year;
      option.textContent = `${year}년 · ${data.years[year]}회`;
      elements.year.append(option);
    });
  }

  function createDrawCard(draw) {
    const fragment = elements.template.content.cloneNode(true);
    const card = fragment.querySelector(".draw-card");
    card.dataset.drawNo = String(draw.draw_no);

    fragment.querySelector(".draw-number").textContent = `${draw.draw_no}회`;
    const time = fragment.querySelector(".draw-date");
    time.dateTime = draw.draw_date;
    time.textContent = draw.draw_date.replaceAll("-", ".");

    const badgeData = statusLabel(draw);
    const badge = fragment.querySelector(".verification-badge");
    badge.textContent = badgeData.text;
    if (badgeData.className) badge.classList.add(badgeData.className);

    const mainBalls = fragment.querySelector(".main-balls");
    draw.numbers.forEach((number) => mainBalls.append(createBall(number)));
    fragment.querySelector(".bonus-ball").append(createBall(draw.bonus_number));

    const source = fragment.querySelector(".draw-source");
    const sourceLink = document.createElement("a");
    sourceLink.href = draw.source_reference;
    sourceLink.target = "_blank";
    sourceLink.rel = "noreferrer noopener";
    sourceLink.textContent = draw.source;
    source.append(sourceLink);

    fragment.querySelector(".draw-status").textContent = `${draw.verification_status} / locked: ${draw.locked}`;
    fragment.querySelector(".draw-checksum").textContent = draw.checksum;
    return card;
  }

  function renderDraws() {
    elements.list.replaceChildren();
    const visible = state.filtered.slice(0, state.visibleLimit);
    if (visible.length === 0) {
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
    const selectedYear = elements.year.value;
    const order = elements.sort.value;

    let filtered = [...state.data.draws];
    if (query) {
      filtered = filtered.filter((draw) => String(draw.draw_no).includes(query));
    }
    if (selectedYear !== "all") {
      filtered = filtered.filter((draw) => draw.draw_date.startsWith(selectedYear));
    }
    filtered.sort((a, b) => (order === "asc" ? a.draw_no - b.draw_no : b.draw_no - a.draw_no));
    state.filtered = filtered;
    state.visibleLimit = 30;
    renderDraws();
  }

  function renderFrequency() {
    const windowName = elements.statWindow.value;
    const frequencies = state.data.statistics.frequencies[windowName];
    const values = Object.values(frequencies);
    const maximum = Math.max(...values, 1);
    elements.frequencyGrid.replaceChildren();

    for (let number = 1; number <= 45; number += 1) {
      const count = frequencies[String(number)] ?? 0;
      const item = document.createElement("div");
      item.className = "frequency-item";
      item.append(createBall(number, true));

      const track = document.createElement("div");
      track.className = "frequency-track";
      const fill = document.createElement("div");
      fill.className = "frequency-fill";
      fill.style.width = `${(count / maximum) * 100}%`;
      track.append(fill);
      item.append(track);

      const countElement = document.createElement("span");
      countElement.className = "frequency-count";
      countElement.textContent = String(count);
      item.append(countElement);
      elements.frequencyGrid.append(item);
    }
  }

  function bindEvents() {
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
    elements.loadMore.addEventListener("click", () => {
      state.visibleLimit += 30;
      renderDraws();
    });
  }

  async function loadArchive() {
    try {
      const response = await fetch("./data/archive_index.json", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      state.data = await response.json();
      state.filtered = [...state.data.draws];
      renderSummary();
      renderDraws();
      renderFrequency();
      bindEvents();
      elements.status.classList.add("ready");
      elements.status.lastChild.textContent = ` 데이터 준비 완료 · ${state.data.record_count}회`;
    } catch (error) {
      console.error(error);
      elements.status.classList.add("error");
      elements.status.lastChild.textContent = " 데이터 로드 실패";
      elements.list.replaceChildren();
      const errorState = document.createElement("div");
      errorState.className = "error-state";
      errorState.textContent = "아카이브 데이터를 불러오지 못했습니다. 로컬에서는 웹 서버로 실행해야 합니다.";
      elements.list.append(errorState);
    }
  }

  loadArchive();
})();
