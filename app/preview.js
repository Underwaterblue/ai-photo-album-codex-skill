// Local shell: collect parameters and build the equivalent CLI command.
// This page does NOT execute Python and does not read/upload any photo.
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  function currentParams() {
    return {
      inputDir: $("inputDir").value.trim() || "./photos",
      outputDir: $("outputDir").value.trim() || "./output",
      albumCount: parseInt($("albumCount").value, 10) || 3,
      pageCount: parseInt($("pageCount").value, 10) || 12,
      ratio: $("ratio").value,
      dpi: parseInt($("dpi").value, 10) || 300,
      styleMode: $("styleMode").value,
      styleStrength: $("styleStrength").value
    };
  }

  function buildCommand(p) {
    return [
      "python src/main.py",
      "--input " + p.inputDir,
      "--albums " + p.albumCount,
      "--pages " + p.pageCount,
      "--ratio " + p.ratio,
      "--dpi " + p.dpi,
      "--style-mode " + p.styleMode,
      "--style-strength " + p.styleStrength,
      "--output " + p.outputDir
    ].join(" \\\n  ");
  }

  function render() {
    $("cmd").textContent = buildCommand(currentParams());
  }

  function copyCommand() {
    var text = $("cmd").textContent;
    var done = function () {
      $("copyBtn").textContent = "已复制";
      setTimeout(function () { $("copyBtn").textContent = "复制命令"; }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text, done); });
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
    done();
  }

  // Rebuild the command on any form change.
  $("form").addEventListener("input", render);
  $("form").addEventListener("change", render);
  $("buildBtn").addEventListener("click", render);
  $("copyBtn").addEventListener("click", copyCommand);

  render();
})();
