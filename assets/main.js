/* intellirefactor.com — 交互：工作流重构动画 · 询价邮件合成 · 复制邮箱 */
(function () {
  "use strict";

  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 签名动画：工作流重构 ---------- */

  var panel = document.getElementById("workflow");
  var pieces = panel
    ? Array.prototype.slice.call(panel.querySelectorAll(".workflow-step, .workflow-arrow"))
    : [];
  var replayBtn = panel ? panel.querySelector(".workflow-replay") : null;
  var timers = [];

  function clearTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }

  function play() {
    if (!panel || prefersReduced) return;
    clearTimers();
    panel.classList.add("play");
    pieces.forEach(function (piece) { piece.classList.remove("on"); });

    var t = 280;
    pieces.forEach(function (piece) {
      t += piece.classList.contains("workflow-arrow") ? 260 : 115;
      (function (item, at) {
        timers.push(setTimeout(function () {
          item.classList.add("on");
        }, at));
      })(piece, t);
    });
  }

  if (panel && "IntersectionObserver" in window && !prefersReduced) {
    var seen = false;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !seen) { seen = true; play(); io.disconnect(); }
      });
    }, { threshold: 0.35 });
    io.observe(panel);
  }
  if (replayBtn) replayBtn.addEventListener("click", play);

  /* ---------- 复制邮箱 ---------- */

  var toast = document.querySelector(".toast");
  var toastTimer = null;

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.hidden = false;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.classList.remove("show");
      toast.hidden = true;
    }, 1800);
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy") ? resolve() : reject(); }
      catch (err) { reject(err); }
      finally { document.body.removeChild(ta); }
    });
  }

  document.querySelectorAll(".js-copy-email").forEach(function (btn) {
    btn.addEventListener("click", function () {
      copyText(btn.dataset.email || "").then(
        function () { showToast("已复制：" + (btn.dataset.email || "")); },
        function () { showToast("复制失败，请手动选择邮箱地址"); }
      );
    });
  });

  /* ---------- 询价表单 → 生成邮件 ---------- */

  var form = document.getElementById("offer-form");
  if (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var name = (form.elements.name.value || "").trim();
      var offer = (form.elements.offer.value || "").trim();
      var message = (form.elements.message.value || "").trim();

      var subject = "【域名询价】intellirefactor.com" + (offer ? " — 报价 $" + offer : "");
      var body = "你好，我想询价 intellirefactor.com 这个域名。\n\n"
        + "称呼：" + (name || "（未填写）") + "\n"
        + "期望报价：" + (offer ? "$" + offer : "（待商议）") + "\n"
        + (message ? "留言：" + message + "\n" : "")
        + "\n（由 intellirefactor.com 页面生成）";

      var mailto = "mailto:vague0307@gmail.com"
        + "?subject=" + encodeURIComponent(subject)
        + "&body=" + encodeURIComponent(body);
      window.location.href = mailto;
      showToast("已打开邮件客户端，发送即可完成询价");
    });
  }
})();
