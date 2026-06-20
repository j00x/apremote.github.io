/* Minimal, dependency-free Markdown -> HTML renderer.
   Supports: headings, bold, italic, inline code, links, ordered/unordered
   lists, and paragraphs. Input is HTML-escaped first to prevent injection. */
(function (global) {
  "use strict";

  function escapeHtml(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function inline(text) {
    // Links: [label](url) — only http(s)/mailto allowed
    text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)/g,
      function (_, label, url) {
        return '<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + label + "</a>";
      });
    // Inline code
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
    // Bold then italic
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
    return text;
  }

  function render(md) {
    if (!md) return "";
    var lines = escapeHtml(String(md)).split(/\r?\n/);
    var html = [];
    var listType = null; // 'ul' | 'ol'

    function closeList() {
      if (listType) { html.push("</" + listType + ">"); listType = null; }
    }

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var trimmed = line.trim();

      if (trimmed === "") { closeList(); continue; }

      var h = /^(#{1,4})\s+(.*)$/.exec(trimmed);
      if (h) {
        closeList();
        var level = h[1].length + 1; // shift down so page h1/h2 stay dominant
        if (level > 4) level = 4;
        html.push("<h" + level + ">" + inline(h[2]) + "</h" + level + ">");
        continue;
      }

      var ol = /^\d+\.\s+(.*)$/.exec(trimmed);
      if (ol) {
        if (listType !== "ol") { closeList(); html.push("<ol>"); listType = "ol"; }
        html.push("<li>" + inline(ol[1]) + "</li>");
        continue;
      }

      var ul = /^[-*]\s+(.*)$/.exec(trimmed);
      if (ul) {
        if (listType !== "ul") { closeList(); html.push("<ul>"); listType = "ul"; }
        html.push("<li>" + inline(ul[1]) + "</li>");
        continue;
      }

      closeList();
      html.push("<p>" + inline(trimmed) + "</p>");
    }
    closeList();
    return html.join("\n");
  }

  global.MiniMarkdown = { render: render };
})(window);
