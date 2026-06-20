(function () {
  "use strict";

  var root = document.getElementById("health-root");
  var homeTeaser = document.getElementById("home-briefing");

  // baseurl: prefer the data attribute on the health page, else derive from this script's src.
  var baseurl = root ? (root.getAttribute("data-baseurl") || "") : deriveBaseurl();
  function deriveBaseurl() {
    var s = document.currentScript || (function () {
      var els = document.getElementsByTagName("script");
      return els[els.length - 1];
    })();
    if (!s) return "";
    var m = s.src.match(/^(.*)\/assets\/js\/health\.js/);
    try { return m ? new URL(m[1]).pathname : ""; } catch (e) { return m ? m[1] : ""; }
  }

  var INDEX_URL = baseurl + "/health/index.json";
  function briefingUrl(date) { return baseurl + "/health/briefings/" + date + ".json"; }

  var ICONS = {
    sparkle: "✦", bolt: "⚡", anchor: "⚓", ribbon: "🎗", moon: "🌙", pulse: "❤"
  };

  var LINK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>';

  function fmtDate(iso) {
    var parts = String(iso).split("-");
    if (parts.length !== 3) return iso;
    var d = new Date(Date.UTC(+parts[0], +parts[1] - 1, +parts[2]));
    return d.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric", timeZone: "UTC" });
  }

  function fetchJson(url) {
    return fetch(url, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " for " + url);
      return r.json();
    });
  }

  function renderSources(sources) {
    if (!sources || !sources.length) return "";
    var chips = sources.map(function (s) {
      var label = s.publisher || s.title || "Source";
      return '<a class="source-chip" href="' + encodeURI(s.url || "#") +
        '" target="_blank" rel="noopener noreferrer" title="' +
        String(s.title || label).replace(/"/g, "&quot;") + '">' +
        LINK_SVG + "<span>" + label + "</span></a>";
    }).join("");
    return '<div class="sources">' + chips + "</div>";
  }

  function renderBriefing(data) {
    var container = document.getElementById("briefing-sections");
    var dateEl = document.getElementById("briefing-date");
    var introEl = document.getElementById("briefing-intro");
    if (dateEl) dateEl.textContent = fmtDate(data.date);
    if (introEl) introEl.textContent = data.intro || "";

    if (!data.sections || !data.sections.length) {
      container.innerHTML = '<div class="state-msg glass">No sections in today\'s briefing.</div>';
      return;
    }

    container.innerHTML = data.sections.map(function (sec) {
      var icon = ICONS[sec.icon] || ICONS.pulse;
      return '<article class="briefing-section glass">' +
        '<div class="briefing-section__head">' +
          '<span class="briefing-section__icon" aria-hidden="true">' + icon + "</span>" +
          "<h2>" + escapeText(sec.topic || "") + "</h2>" +
        "</div>" +
        '<div class="briefing-body">' + window.MiniMarkdown.render(sec.body || "") + "</div>" +
        renderSources(sec.sources) +
      "</article>";
    }).join("");
  }

  function escapeText(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function renderArchive(briefings, activeDate) {
    var list = document.getElementById("archive-list");
    if (!list) return;
    list.innerHTML = briefings.map(function (b) {
      return "<li><button type=\"button\" data-date=\"" + b.date + "\"" +
        (b.date === activeDate ? ' aria-current="true"' : "") + ">" +
        fmtDate(b.date) + "</button></li>";
    }).join("");

    list.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-date]");
      if (!btn) return;
      var date = btn.getAttribute("data-date");
      loadDay(date, briefings);
      Array.prototype.forEach.call(list.querySelectorAll("button"), function (b) {
        b.removeAttribute("aria-current");
      });
      btn.setAttribute("aria-current", "true");
    });
  }

  function loadDay(date, briefings) {
    var container = document.getElementById("briefing-sections");
    if (container) container.innerHTML = '<div class="state-msg glass">Loading…</div>';
    fetchJson(briefingUrl(date))
      .then(renderBriefing)
      .catch(function (err) {
        if (container) container.innerHTML =
          '<div class="state-msg glass">Could not load this briefing.</div>';
        console.error(err);
      });
  }

  function renderTeaser(data) {
    if (!homeTeaser) return;
    var topics = (data.sections || []).map(function (s) { return s.topic; }).filter(Boolean);
    var chips = topics.map(function (t) { return '<span class="tag">' + escapeText(t) + "</span>"; }).join("");
    homeTeaser.innerHTML =
      '<h2 class="card__title">Daily Health Briefing</h2>' +
      '<p class="card__meta">' + fmtDate(data.date) + "</p>" +
      '<div class="teaser-topics">' + chips + "</div>";
  }

  // --- Boot ---
  fetchJson(INDEX_URL).then(function (index) {
    var briefings = (index && index.briefings) || [];
    if (!briefings.length) {
      if (root) document.getElementById("briefing-sections").innerHTML =
        '<div class="state-msg glass">No briefings published yet.</div>';
      if (homeTeaser) homeTeaser.innerHTML =
        '<h2 class="card__title">Daily Health Briefing</h2><p class="card__body">No briefing yet — check back soon.</p>';
      return;
    }
    var latest = briefings[0].date;

    if (root) {
      renderArchive(briefings, latest);
      loadDay(latest, briefings);
    }
    if (homeTeaser) {
      fetchJson(briefingUrl(latest)).then(renderTeaser).catch(function () {});
    }
  }).catch(function (err) {
    console.error(err);
    if (root) document.getElementById("briefing-sections").innerHTML =
      '<div class="state-msg glass">Could not load the briefing index.</div>';
    if (homeTeaser) homeTeaser.innerHTML =
      '<h2 class="card__title">Daily Health Briefing</h2><p class="card__body">Briefing unavailable right now.</p>';
  });
})();
