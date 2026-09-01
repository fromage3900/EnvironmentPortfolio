/* PBR Texture Catalog dashboard controller.
   Reads window.TEXTURE_CATALOG (from catalog-data.js), binds search + channel
   filter chips, and renders the grid in batches via IntersectionObserver for
   smooth 60 FPS scrolling. */
(function () {
  "use strict";

  var DATA = window.TEXTURE_CATALOG || [];
  var BATCH = 48;

  var grid = document.getElementById("texture-grid");
  var search = document.getElementById("texture-search");
  var filterGroup = document.getElementById("filter-group");
  var emptyState = document.getElementById("empty-state");
  var sentinel = document.getElementById("grid-sentinel");

  var state = { query: "", channel: "all" };
  var rendered = 0;
  var currentVisible = [];

  function channelList() {
    var seen = {};
    DATA.forEach(function (item) { seen[item.channel] = true; });
    return Object.keys(seen).sort();
  }

  function familiesList() {
    var seen = {};
    DATA.forEach(function (item) { if (item.family) seen[item.family] = true; });
    return Object.keys(seen);
  }

  function badgeClass(channel) {
    return {
      "BaseColor": "badge-bc", "Normal": "badge-n", "ORM": "badge-orm",
      "Roughness": "badge-r", "Metallic": "badge-m", "AO": "badge-ao",
      "Height": "badge-h", "Emissive": "badge-e", "Mask": "badge-mask",
      "Specialty": "badge-spec", "UI": "badge-ui"
    }[channel] || "";
  }

  function channels() {
    return ["all"].concat(channelList());
  }

  function setupFilterChips() {
    channels().forEach(function (ch) {
      var chip = document.createElement("button");
      chip.className = "filter-chip";
      chip.setAttribute("data-filter", ch);
      chip.setAttribute("aria-pressed", ch === "all" ? "true" : "false");
      chip.setAttribute("type", "button");
      chip.textContent = ch === "all" ? "All" : ch;
      chip.addEventListener("click", function () {
        state.channel = ch;
        refreshFilterChips();
        resetAndRender();
      });
      filterGroup.appendChild(chip);
    });
  }

  function refreshFilterChips() {
    var chips = filterGroup.querySelectorAll(".filter-chip");
    chips.forEach(function (chip) {
      chip.setAttribute("aria-pressed", chip.getAttribute("data-filter") === state.channel ? "true" : "false");
    });
  }

  function matches(item) {
    if (state.channel !== "all" && item.channel !== state.channel) return false;
    var q = state.query.trim().toLowerCase();
    if (!q) return true;
    var hay = [item.name, item.family, item.usage_context, item.channel].join(" ").toLowerCase();
    return q.split(/\s+/).every(function (term) { return hay.indexOf(term) !== -1; });
  }

  function visibleItems() {
    return DATA.filter(matches);
  }

  function cardFor(item) {
    var card = document.createElement("div");
    card.className = "texture-card";
    card.setAttribute("data-channel", item.channel || "");
    card.setAttribute("data-family", item.family || "");

    var img = document.createElement("img");
    img.setAttribute("loading", "lazy");
    img.setAttribute("decoding", "async");
    var src = item.thumbnail_path || item.source_rel_path || "";
    if (src) img.setAttribute("src", src);
    img.setAttribute("alt", item.name || "texture");
    img.addEventListener("error", function () {
      img.setAttribute("src", "assets/placeholder_texture.svg");
      img.removeAttribute("onerror");
    });

    var body = document.createElement("div");
    body.className = "card-body";

    var name = document.createElement("p");
    name.className = "card-name";
    name.textContent = item.name || "";

    var meta = document.createElement("div");
    meta.className = "card-meta";

    var badge = document.createElement("span");
    badge.className = "badge " + badgeClass(item.channel);
    badge.textContent = item.channel_badge || item.channel || "";
    meta.appendChild(badge);

    var fam = document.createElement("span");
    fam.textContent = item.family || "";
    meta.appendChild(fam);

    body.appendChild(name);
    body.appendChild(meta);
    card.appendChild(img);
    card.appendChild(body);
    return card;
  }

  function renderChunk() {
    var until = Math.min(rendered + BATCH, currentVisible.length);
    for (var i = rendered; i < until; i++) {
      grid.appendChild(cardFor(currentVisible[i]));
    }
    rendered = until;
    if (rendered >= currentVisible.length) {
      grid.removeChild(sentinel);
      emptyState.hidden = currentVisible.length !== 0;
    }
  }

  function setupObserver() {
    if (typeof IntersectionObserver === "undefined") {
      document.body.appendChild(sentinel);
      renderChunk();
      while (rendered < currentVisible.length) renderChunk();
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      if (entries.some(function (e) { return e.isIntersecting; })) renderChunk();
    }, { rootMargin: "400px 0px" });
    observer.observe(sentinel);
  }

  function statsTotal() {
    var el = document.getElementById("stat-total");
    if (el) el.textContent = DATA.length + " textures";
    var ec = document.getElementById("stat-channels");
    if (ec) ec.textContent = channelList().length + " channels";
    var ef = document.getElementById("stat-families");
    if (ef) ef.textContent = familiesList().length + " families";
  }

  function resetAndRender() {
    rendered = 0;
    grid.innerHTML = "";
    grid.appendChild(sentinel);
    currentVisible = visibleItems();
    if (currentVisible.length === 0) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    setupObserver();
  }

  search.addEventListener("input", function () {
    state.query = search.value;
    resetAndRender();
  });

  // init
  if (!grid || !search || !filterGroup) return;
  setupFilterChips();
  statsTotal();
  resetAndRender();
})();