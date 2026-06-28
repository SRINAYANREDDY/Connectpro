/* ==========================================
   ConnectPro — main.js
   ========================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* ---------- THEME TOGGLE ---------- */
  const themeToggle = document.getElementById('themeToggle');
  const themeIcon = document.getElementById('themeIcon');

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      fetch('/accounts/theme/', {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
      })
      .then(r => r.json())
      .then(data => {
        document.documentElement.setAttribute('data-theme', data.theme);
        if (themeIcon) {
          themeIcon.className = data.theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
      });
    });
  }

  /* ---------- LIKE BUTTONS ---------- */
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.like-btn');
    if (!btn) return;
    e.preventDefault();
    const postId = btn.dataset.postId;
    const isLiked = btn.dataset.liked === 'true';

    fetch(`/posts/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    })
    .then(r => r.json())
    .then(data => {
      btn.dataset.liked = data.liked ? 'true' : 'false';
      const icon = btn.querySelector('i');
      const countEl = btn.querySelector('.like-count');
      if (icon) icon.className = data.liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
      if (countEl) countEl.textContent = data.count;
      btn.classList.toggle('liked', data.liked);
    });
  });

  /* ---------- BOOKMARK BUTTONS ---------- */
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.bookmark-btn');
    if (!btn) return;
    e.preventDefault();
    const postId = btn.dataset.postId;

    fetch(`/posts/${postId}/bookmark/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    })
    .then(r => r.json())
    .then(data => {
      btn.dataset.bookmarked = data.bookmarked ? 'true' : 'false';
      const icon = btn.querySelector('i');
      if (icon) icon.className = data.bookmarked ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
      btn.classList.toggle('bookmarked', data.bookmarked);
    });
  });

  /* ---------- COMMENT FORMS ---------- */
  document.addEventListener('submit', function (e) {
    const form = e.target.closest('.comment-form');
    if (!form) return;
    e.preventDefault();

    const postId = form.dataset.postId;
    const parentId = form.dataset.parentId || '';
    const input = form.querySelector('.comment-input');
    const content = input.value.trim();
    if (!content) return;

    const body = new URLSearchParams({ content, parent_id: parentId, csrfmiddlewaretoken: CSRF_TOKEN });

    fetch(`/posts/${postId}/comment/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString()
    })
    .then(r => r.json())
    .then(data => {
      if (data.status !== 'ok') return;
      input.value = '';
      const commentEl = buildCommentElement(data);

      if (data.is_reply && parentId) {
        let repliesList = document.querySelector(`#comment-${parentId} .replies-list`);
        if (!repliesList) {
          repliesList = document.createElement('div');
          repliesList.className = 'replies-list';
          document.querySelector(`#comment-${parentId} .comment-body`)?.appendChild(repliesList);
        }
        repliesList.appendChild(commentEl);
        form.classList.add('hidden');
      } else {
        const commentsList = document.getElementById('commentsList');
        if (commentsList) {
          const empty = commentsList.querySelector('.empty-text');
          if (empty) empty.remove();
          commentsList.appendChild(commentEl);
        }
      }
    });
  });

  function buildCommentElement(data) {
    const div = document.createElement('div');
    div.className = 'comment-item';
    div.id = `comment-${data.comment_id}`;
    div.innerHTML = `
      <img src="${data.author_avatar}" class="comment-avatar" alt="">
      <div class="comment-body">
        <div class="comment-header">
          <a href="/accounts/${data.author}/"><strong>${data.author}</strong></a>
          <span class="comment-time">just now</span>
        </div>
        <p class="comment-text">${escapeHtml(data.content)}</p>
      </div>`;
    return div;
  }

  function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  /* ---------- POST MENU TOGGLE ---------- */
  document.addEventListener('click', function (e) {
    const menuBtn = e.target.closest('.post-menu-btn');
    if (menuBtn) {
      const dropdown = menuBtn.nextElementSibling;
      document.querySelectorAll('.post-dropdown.show').forEach(d => {
        if (d !== dropdown) d.classList.remove('show');
      });
      dropdown?.classList.toggle('show');
      e.stopPropagation();
      return;
    }
    document.querySelectorAll('.post-dropdown.show').forEach(d => d.classList.remove('show'));
  });

  /* ---------- REPLY TOGGLE ---------- */
  document.addEventListener('click', function (e) {
    const toggle = e.target.closest('.reply-toggle');
    if (!toggle) return;
    const commentId = toggle.dataset.commentId;
    const replyForm = document.querySelector(`.reply-form[data-parent-id="${commentId}"]`);
    replyForm?.classList.toggle('hidden');
  });

  /* ---------- SHARE POST ---------- */
  window.sharePost = function (url) {
    const full = window.location.origin + url;
    if (navigator.share) {
      navigator.share({ url: full });
    } else {
      navigator.clipboard.writeText(full).then(() => showToast('Link copied!'));
    }
  };

  /* ---------- DELETE POST ---------- */
  window.deletePost = function (postId) {
    if (!confirm('Delete this post?')) return;
    fetch(`/posts/${postId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'deleted') {
        document.getElementById(`post-${postId}`)?.remove();
      }
    });
  };

  /* ---------- HIDE POST ---------- */
  window.hidePost = function (postId) {
    fetch(`/posts/${postId}/hide/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN }
    })
    .then(r => r.json())
    .then(() => {
      const card = document.getElementById(`post-${postId}`);
      if (card) {
        card.style.opacity = '0';
        card.style.transition = 'opacity 0.3s ease';
        setTimeout(() => card.remove(), 300);
      }
    });
  };

  /* ---------- TOAST NOTIFICATION ---------- */
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    Object.assign(toast.style, {
      position: 'fixed', bottom: '24px', right: '24px', zIndex: '9999',
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius)', padding: '12px 20px',
      boxShadow: 'var(--shadow-lg)', fontSize: '0.9rem',
      color: 'var(--text)', transition: 'all 0.3s ease'
    });
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
  }
  window.showToast = showToast;

  /* ---------- AUTO-DISMISS ALERTS ---------- */
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s ease';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  /* ---------- WEBSOCKET NOTIFICATIONS ---------- */
  if (IS_AUTHENTICATED) {
    try {
      const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const ws = new WebSocket(`${wsScheme}://${window.location.host}/ws/notifications/`);
      const badge = document.getElementById('notifBadge');

      ws.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.type === 'init') {
          updateBadge(data.unread_count);
        } else if (data.type === 'notification') {
          updateBadge(data.unread_count);
          showToast(`🔔 ${data.message}`);
        }
      };

      ws.onerror = function (e) { console.warn('WS error:', e); };
      ws.onclose = function () { console.log('WS closed'); };

      function updateBadge(count) {
        if (!badge) return;
        badge.textContent = count;
        badge.classList.toggle('hidden', count === 0);
      }

      // Mark as read when visiting notifications page
      if (window.location.pathname.startsWith('/notifications')) {
        ws.addEventListener('open', () => {
          ws.send(JSON.stringify({ type: 'mark_read' }));
        });
      }
    } catch (err) {
      console.warn('WebSocket not available:', err);
    }
  }

  /* ---------- IMAGE PREVIEW ON UPLOAD ---------- */
  document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
    input.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function (e) {
        let preview = input.parentElement.querySelector('.file-preview');
        if (!preview) {
          preview = document.createElement('img');
          preview.className = 'file-preview';
          preview.style.cssText = 'max-height:160px;border-radius:8px;margin-top:8px;object-fit:cover;';
          input.parentElement.appendChild(preview);
        }
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  });

  /* ---------- MODAL CLOSE ON BACKDROP ---------- */
  document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal')) {
      e.target.classList.remove('show');
    }
  });

  /* ---------- KEYBOARD SHORTCUTS ---------- */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal.show').forEach(m => m.classList.remove('show'));
      document.querySelectorAll('.post-dropdown.show').forEach(d => d.classList.remove('show'));
    }
  });

});
/**
 * messaging_reels.js
 * ConnectPro — Reels + Messaging client-side JavaScript
 *
 * Exports (via window):
 *   initReelsFeed()     — vertical scroll feed with autoplay
 *   initSingleReel()    — single reel page interactions
 *   initReelUpload()    — upload form preview + submit UX
 *   initInbox()         — inbox search + new message modal
 *   initChat()          — WebSocket chat + file upload
 */

/* ════════════════════════════════════════════════════════════
   UTILITY HELPERS
   ════════════════════════════════════════════════════════════ */

/** Return the CSRF token from the cookie or a meta/hidden field. */
function getCsrfToken() {
  // 1. Try a cookie named csrftoken (Django default)
  const cookie = document.cookie
    .split(";")
    .map(c => c.trim())
    .find(c => c.startsWith("csrftoken="));
  if (cookie) return cookie.split("=")[1];

  // 2. Try a hidden input on the page
  const input = document.querySelector('[name=csrfmiddlewaretoken]');
  if (input) return input.value;

  return "";
}

/**
 * Light JSON POST helper.
 * @param {string} url
 * @param {Object|FormData} body
 * @param {boolean} isFormData  — skip JSON encoding when true
 */
async function postJSON(url, body, isFormData = false) {
  const headers = { "X-CSRFToken": getCsrfToken(), "X-Requested-With": "XMLHttpRequest" };
  if (!isFormData) headers["Content-Type"] = "application/json";

  const res = await fetch(url, {
    method: "POST",
    headers,
    body: isFormData ? body : JSON.stringify(body),
    credentials: "same-origin",
  });
  return res;
}

/** Escape text for safe innerHTML insertion. */
function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

/** Format a JS Date as "g:i A" equivalent. */
function fmtTime(date) {
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

/* ════════════════════════════════════════════════════════════
   REELS — FEED
   ════════════════════════════════════════════════════════════ */

/**
 * Initialise the vertical scroll reel feed.
 * Call after DOMContentLoaded on reels_feed.html.
 */
window.initReelsFeed = function () {
  const feed = document.getElementById("reels-feed");
  if (!feed) return;

  const cards = feed.querySelectorAll(".reel-card");
  if (!cards.length) return;

  // Auto-play via Intersection Observer (pause all others)
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        const video = entry.target.querySelector(".reel-video");
        if (!video) return;
        if (entry.isIntersecting) {
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      });
    },
    { root: feed, threshold: 0.6 }
  );

  cards.forEach(card => {
    observer.observe(card);
    _bindReelCard(card);
  });
};

/**
 * Initialise the single reel page.
 */
window.initSingleReel = function () {
  const card = document.querySelector(".single-reel-card");
  if (card) _bindReelCard(card);
  _bindCommentForms();
};

/**
 * Wire up interactions on a single reel card element.
 * @param {HTMLElement} card
 */
function _bindReelCard(card) {
  const video     = card.querySelector(".reel-video");
  const tapOverlay= card.querySelector(".reel-tap-overlay");
  const playInd   = card.querySelector(".reel-play-indicator");
  const muteBtn   = card.querySelector(".reel-mute-btn");
  const likeBtn   = card.querySelector(".reel-like-btn");
  const commentBtn= card.querySelector(".reel-comment-btn");
  const shareBtn  = card.querySelector(".reel-share-btn");

  if (!video) return;

  // ── Play / pause on tap ──────────────────────────────────
  let playIndicatorTimer;
  function flashPlayIndicator() {
    if (!playInd) return;
    playInd.classList.add("visible");
    clearTimeout(playIndicatorTimer);
    playIndicatorTimer = setTimeout(() => playInd.classList.remove("visible"), 600);
  }

  tapOverlay && tapOverlay.addEventListener("click", () => {
    if (video.paused) {
      video.play().catch(() => {});
      flashPlayIndicator();
    } else {
      video.pause();
      flashPlayIndicator();
    }
  });

  // ── Mute toggle ──────────────────────────────────────────
  if (muteBtn) {
    const iconSound = muteBtn.querySelector(".icon-sound");
    const iconMuted = muteBtn.querySelector(".icon-muted");

    muteBtn.addEventListener("click", () => {
      video.muted = !video.muted;
      if (iconSound) iconSound.style.display = video.muted ? "none" : "";
      if (iconMuted) iconMuted.style.display = video.muted ? "" : "none";
    });
  }

  // ── Like button ──────────────────────────────────────────
  if (likeBtn) {
    likeBtn.addEventListener("click", async () => {
      const url = likeBtn.dataset.url;
      if (!url) return;

      // Optimistic update
      const wasLiked = likeBtn.classList.contains("liked");
      likeBtn.classList.toggle("liked", !wasLiked);
      likeBtn.classList.add("like-pop");
      likeBtn.addEventListener("animationend", () => likeBtn.classList.remove("like-pop"), { once: true });

      const countEl = likeBtn.querySelector(".reel-like-count");

      try {
        const res  = await postJSON(url, {});
        const data = await res.json();
        if (countEl) countEl.textContent = data.count;
        likeBtn.classList.toggle("liked", data.liked);
      } catch {
        // Roll back on failure
        likeBtn.classList.toggle("liked", wasLiked);
      }
    });
  }

  // ── Comment button (opens drawer) ────────────────────────
  if (commentBtn) {
    const reelId  = commentBtn.dataset.reelId;
    const drawer  = reelId ? document.getElementById(`comments-drawer-${reelId}`) : null;
    const closeBtn= drawer  ? drawer.querySelector(".reel-comments-close") : null;

    commentBtn.addEventListener("click", () => {
      if (!drawer) return;
      drawer.classList.add("open");
      drawer.setAttribute("aria-hidden", "false");
      const input = drawer.querySelector(".reel-comment-input");
      input && setTimeout(() => input.focus(), 300);
    });

    closeBtn && closeBtn.addEventListener("click", () => {
      drawer.classList.remove("open");
      drawer.setAttribute("aria-hidden", "true");
    });
  }

  // ── Share button ─────────────────────────────────────────
  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const url = window.location.origin + shareBtn.dataset.url;
      if (navigator.share) {
        try {
          await navigator.share({ url, title: "Check out this reel on ConnectPro!" });
        } catch { /* user dismissed */ }
      } else {
        await navigator.clipboard.writeText(url).catch(() => {});
        _showToast("Link copied!");
      }
    });
  }

  // ── Caption "more/less" toggle ───────────────────────────
  const captionToggle = card.querySelector(".reel-caption-toggle");
  if (captionToggle) {
    const captionText = card.querySelector(".reel-caption-text");
    const fullText    = card.querySelector(".reel-caption")?.dataset.full;
    captionToggle.addEventListener("click", () => {
      if (captionToggle.textContent === "more") {
        captionText.textContent = fullText;
        captionToggle.textContent = "less";
      } else {
        captionText.textContent = (fullText || "").slice(0, 80) + "…";
        captionToggle.textContent = "more";
      }
    });
  }

  // Wire inline comment forms
  _bindCommentForms(card);
}

/** Bind AJAX comment submission for all reel comment forms in scope. */
function _bindCommentForms(scope = document) {
  scope.querySelectorAll(".reel-comment-form").forEach(form => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const input   = form.querySelector(".reel-comment-input, input[name=content]");
      const content = input ? input.value.trim() : "";
      if (!content) return;

      const url = form.dataset.url;
      if (!url) return;

      const fd = new FormData(form);
      try {
        const res  = await postJSON(url, fd, true);
        const data = await res.json();
        if (data.success) {
          const reelId    = form.dataset.reelId;
          const listEl    = document.getElementById(`comments-list-${reelId}`);
          const noMsg     = listEl ? listEl.querySelector(".no-comments-msg, #no-comments-msg") : null;
          noMsg && noMsg.remove();

          if (listEl) {
            const item = _buildCommentNode(data.comment);
            listEl.appendChild(item);
            listEl.scrollTop = listEl.scrollHeight;
          }

          // Update count badge
          const countEl = scope.querySelector(".reel-action-count:not(.reel-like-count)");
          if (countEl) countEl.textContent = data.count;
          const badge = document.querySelector(".comment-count-badge");
          if (badge) badge.textContent = data.count;

          if (input) input.value = "";
        }
      } catch { /* network error; degrade gracefully */ }
    });
  });
}

function _buildCommentNode(c) {
  const div = document.createElement("div");
  div.className = "reel-comment-item";
  div.id = `comment-${c.id}`;
  div.innerHTML = `
    <a href="/accounts/${escapeHtml(c.user)}/" class="reel-comment-avatar-link">
      ${c.avatar
        ? `<img src="${escapeHtml(c.avatar)}" alt="${escapeHtml(c.user)}" class="reel-comment-avatar">`
        : `<div class="reel-comment-avatar reel-comment-avatar--placeholder">${escapeHtml(c.user[0].toUpperCase())}</div>`
      }
    </a>
    <div class="reel-comment-body">
      <a href="/accounts/${escapeHtml(c.user)}/" class="reel-comment-username">@${escapeHtml(c.user)}</a>
      <p class="reel-comment-text">${escapeHtml(c.content)}</p>
      <span class="reel-comment-time">${escapeHtml(c.created_at)}</span>
    </div>`;
  return div;
}

/** Show a brief toast notification. */
function _showToast(msg, duration = 2200) {
  let toast = document.getElementById("cp-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "cp-toast";
    Object.assign(toast.style, {
      position: "fixed", bottom: "5rem", left: "50%", transform: "translateX(-50%)",
      background: "rgba(0,0,0,0.8)", color: "#fff", padding: "0.55rem 1.1rem",
      borderRadius: "999px", fontSize: "0.85rem", zIndex: "9999",
      pointerEvents: "none", opacity: "0", transition: "opacity 0.2s",
    });
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = "1";
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.style.opacity = "0"; }, duration);
}

/* ════════════════════════════════════════════════════════════
   REELS — UPLOAD FORM
   ════════════════════════════════════════════════════════════ */

window.initReelUpload = function () {
  const form          = document.getElementById("upload-reel-form");
  if (!form) return;

  const videoInput    = document.getElementById("reel-video-input");
  const thumbInput    = document.getElementById("reel-thumbnail-input");
  const dropZone      = document.getElementById("video-drop-zone");
  const dropInner     = document.getElementById("video-drop-inner");
  const previewWrap   = document.getElementById("video-preview-wrapper");
  const previewVideo  = document.getElementById("upload-video-preview");
  const removeVideoBtn= document.getElementById("remove-video-btn");
  const thumbWrap     = document.getElementById("thumbnail-preview-wrapper");
  const thumbPreview  = document.getElementById("upload-thumbnail-preview");
  const removeThumbBtn= document.getElementById("remove-thumb-btn");
  const captionInput  = form.querySelector("textarea[name=caption]");
  const charCount     = document.getElementById("caption-char-count");
  const submitBtn     = document.getElementById("upload-submit-btn");
  const btnLabel      = submitBtn ? submitBtn.querySelector(".btn-label") : null;
  const btnSpinner    = submitBtn ? submitBtn.querySelector(".btn-spinner") : null;

  // ── Video input / drag-drop ──────────────────────────────
  if (videoInput) {
    videoInput.addEventListener("change", () => {
      const file = videoInput.files[0];
      if (file) _showVideoPreview(file);
    });
  }

  if (dropZone) {
    // Make drop zone clickable
    dropZone.addEventListener("click", (e) => {
      if (e.target.closest("#video-preview-wrapper")) return;
      videoInput && videoInput.click();
    });
    dropZone.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") videoInput && videoInput.click();
    });

    // Drag and drop
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("video/")) {
        // Assign to input (DataTransfer)
        const dt = new DataTransfer();
        dt.items.add(file);
        videoInput.files = dt.files;
        _showVideoPreview(file);
      }
    });
  }

  function _showVideoPreview(file) {
    if (!previewVideo || !previewWrap || !dropInner) return;
    const url = URL.createObjectURL(file);
    previewVideo.src = url;
    dropInner.style.display  = "none";
    previewWrap.style.display = "";
  }

  removeVideoBtn && removeVideoBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    if (previewVideo) { previewVideo.src = ""; URL.revokeObjectURL(previewVideo.src); }
    if (videoInput)   videoInput.value = "";
    dropInner.style.display   = "";
    previewWrap.style.display = "none";
  });

  // ── Thumbnail preview ────────────────────────────────────
  thumbInput && thumbInput.addEventListener("change", () => {
    const file = thumbInput.files[0];
    if (file && thumbPreview && thumbWrap) {
      thumbPreview.src = URL.createObjectURL(file);
      thumbWrap.style.display = "";
    }
  });

  removeThumbBtn && removeThumbBtn.addEventListener("click", () => {
    if (thumbInput) thumbInput.value = "";
    if (thumbPreview) thumbPreview.src = "";
    if (thumbWrap)  thumbWrap.style.display = "none";
  });

  // ── Caption character count ──────────────────────────────
  captionInput && captionInput.addEventListener("input", () => {
    if (charCount) charCount.textContent = captionInput.value.length;
  });

  // ── Submit spinner ───────────────────────────────────────
  form.addEventListener("submit", () => {
    if (submitBtn) submitBtn.disabled = true;
    if (btnLabel)   btnLabel.style.display  = "none";
    if (btnSpinner) btnSpinner.style.display = "";
  });
};

/* ════════════════════════════════════════════════════════════
   MESSAGING — INBOX
   ════════════════════════════════════════════════════════════ */

/**
 * @param {{ searchUrl: string, startUrl: string }} opts
 */
window.initInbox = function ({ searchUrl, startUrl } = {}) {
  // ── Client-side filter of existing conversations ─────────
  const searchInput = document.getElementById("inbox-search");
  const items       = document.querySelectorAll(".inbox-item");

  searchInput && searchInput.addEventListener("input", () => {
    const q = searchInput.value.toLowerCase();
    items.forEach(item => {
      const text = (item.dataset.search || "") + " " + (item.querySelector(".inbox-item-preview")?.textContent || "");
      item.classList.toggle("hidden", q.length > 0 && !text.toLowerCase().includes(q));
    });
  });

  // ── New message modal ─────────────────────────────────────
  const newBtn    = document.getElementById("new-msg-btn");
  const modal     = document.getElementById("new-msg-modal");
  const closeBtn  = document.getElementById("close-new-msg");
  const userInput = document.getElementById("user-search-input");
  const results   = document.getElementById("modal-user-results");

  if (newBtn && modal) {
    newBtn.addEventListener("click", (e) => {
      e.preventDefault();
      modal.style.display = "flex";
      setTimeout(() => userInput && userInput.focus(), 100);
    });
  }

  const _closeModal = () => { if (modal) modal.style.display = "none"; };
  closeBtn && closeBtn.addEventListener("click", _closeModal);
  modal    && modal.addEventListener("click", (e) => { if (e.target === modal) _closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") _closeModal(); });

  // User search inside modal (debounced, hits /search/ endpoint)
  let searchTimer;
  userInput && userInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    const q = userInput.value.trim();
    if (!results) return;
    if (q.length < 2) { results.innerHTML = ""; return; }

    searchTimer = setTimeout(async () => {
      try {
        const res  = await fetch(`${searchUrl}?q=${encodeURIComponent(q)}&type=users`, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const data = await res.json();
        _renderUserResults(data.users || data.results || [], results, startUrl);
      } catch {
        results.innerHTML = '<p style="color:var(--text-secondary);font-size:.85rem;padding:.5rem 0">Could not load results.</p>';
      }
    }, 300);
  });
};

function _renderUserResults(users, container, startUrl) {
  if (!users.length) {
    container.innerHTML = '<p style="color:var(--text-secondary,#888);font-size:.85rem;padding:.5rem 0">No users found.</p>';
    return;
  }
  container.innerHTML = users.map(u => `
    <a href="${escapeHtml(startUrl)}${escapeHtml(u.username)}/"
       class="inbox-item" style="border-radius:8px;margin-bottom:4px;">
      <div class="inbox-avatar-wrap">
        ${u.avatar
          ? `<img src="${escapeHtml(u.avatar)}" alt="${escapeHtml(u.username)}" class="inbox-avatar">`
          : `<div class="inbox-avatar inbox-avatar--placeholder">${escapeHtml(u.username[0].toUpperCase())}</div>`
        }
      </div>
      <div class="inbox-item-body">
        <div class="inbox-item-top">
          <span class="inbox-item-name">${escapeHtml(u.full_name || u.username)}</span>
        </div>
        <div class="inbox-item-bottom">
          <span class="inbox-item-preview">@${escapeHtml(u.username)}</span>
        </div>
      </div>
    </a>`).join("");
}

/* ════════════════════════════════════════════════════════════
   MESSAGING — CHAT (WebSocket)
   ════════════════════════════════════════════════════════════ */

window.initChat = function () {
  const page = document.getElementById("chat-page");
  if (!page) return;

  const convId        = page.dataset.convId;
  const currentUserId = parseInt(page.dataset.currentUserId, 10);
  const wsUrl         = page.dataset.wsUrl;

  // Read injected URLs
  const urlData    = JSON.parse(document.getElementById("chat-urls")?.textContent || "{}");
  const sendUrl    = urlData.sendUrl;
  const fileUrl    = urlData.fileUrl;
  const csrfToken  = urlData.csrfToken || getCsrfToken();

  const messagesEl   = document.getElementById("chat-messages");
  const input        = document.getElementById("chat-input");
  const sendBtn      = document.getElementById("chat-send-btn");
  const fileInput    = document.getElementById("file-input");
  const filePreview  = document.getElementById("chat-file-preview");
  const fileNameEl   = document.getElementById("chat-file-preview-name");
  const removeFileBtn= document.getElementById("remove-file-btn");
  const typingEl     = document.getElementById("typing-indicator");
  const typingAvatar = document.getElementById("typing-avatar");
  const statusText   = document.getElementById("status-text");
  const onlineDot    = document.getElementById("other-online-dot");

  let socket         = null;
  let wsConnected    = false;
  let typingTimer    = null;
  let isTyping       = false;
  let selectedFile   = null;

  // ── Scroll to bottom ─────────────────────────────────────
  const scrollToBottom = (smooth = false) => {
    if (!messagesEl) return;
    messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: smooth ? "smooth" : "auto" });
  };
  scrollToBottom();

  // ── WebSocket connection ──────────────────────────────────
  function connectWS() {
    if (!wsUrl) return;

    // Support both ws:// and wss:// based on page protocol
    const url = wsUrl.replace(/^http/, "ws");

    try {
      socket = new WebSocket(url);
    } catch (err) {
      console.warn("WebSocket connection failed:", err);
      return;
    }

    socket.addEventListener("open", () => {
      wsConnected = true;
      console.debug("[chat] WS connected");
    });

    socket.addEventListener("close", (e) => {
      wsConnected = false;
      console.debug("[chat] WS closed", e.code);
      // Reconnect after 3 s unless intentional close
      if (e.code !== 1000) setTimeout(connectWS, 3000);
    });

    socket.addEventListener("error", (e) => {
      console.warn("[chat] WS error", e);
    });

    socket.addEventListener("message", (e) => {
      let data;
      try { data = JSON.parse(e.data); }
      catch { return; }

      switch (data.type) {
        case "message":
          _appendMessage(data);
          _hideTypingIndicator();
          // Mark read via WS
          if (!data.is_mine && socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "read" }));
          }
          break;

        case "typing":
          if (data.is_typing) {
            _showTypingIndicator(data.username);
          } else {
            _hideTypingIndicator();
          }
          break;

        case "status":
          _updateOnlineStatus(data.status);
          break;

        default:
          break;
      }
    });
  }

  connectWS();

  // ── Input: auto-grow + enable send btn + typing indicator ─
  input && input.addEventListener("input", () => {
    // Auto-grow
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";

    // Send btn state
    const hasContent = input.value.trim().length > 0 || selectedFile;
    if (sendBtn) sendBtn.disabled = !hasContent;

    // Typing indicator (debounced)
    if (!isTyping && wsConnected && socket) {
      isTyping = true;
      socket.send(JSON.stringify({ type: "typing", is_typing: true }));
    }
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
      isTyping = false;
      if (wsConnected && socket) {
        socket.send(JSON.stringify({ type: "typing", is_typing: false }));
      }
    }, 1800);
  });

  // Enter sends (Shift+Enter = newline)
  input && input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      _sendMessage();
    }
  });

  sendBtn && sendBtn.addEventListener("click", _sendMessage);

  // ── File attachment ───────────────────────────────────────
  fileInput && fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;
    selectedFile = file;
    if (filePreview) filePreview.style.display = "flex";
    if (fileNameEl)  fileNameEl.textContent = file.name;
    if (sendBtn)     sendBtn.disabled = false;
  });

  removeFileBtn && removeFileBtn.addEventListener("click", () => {
    selectedFile = null;
    if (fileInput)   fileInput.value = "";
    if (filePreview) filePreview.style.display = "none";
    const hasContent = input && input.value.trim().length > 0;
    if (sendBtn) sendBtn.disabled = !hasContent;
  });

  // ── Send ─────────────────────────────────────────────────
  async function _sendMessage() {
    const content = input ? input.value.trim() : "";
    if (!content && !selectedFile) return;

    if (sendBtn) sendBtn.disabled = true;

    // Stop typing indicator
    clearTimeout(typingTimer);
    isTyping = false;
    if (wsConnected && socket) {
      socket.send(JSON.stringify({ type: "typing", is_typing: false }));
    }

    // File upload uses HTTP fallback (WS doesn't handle binary)
    if (selectedFile) {
      await _sendFile(content);
      return;
    }

    // Text: prefer WS, fall back to HTTP
    if (wsConnected && socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "message", content }));
      _clearInput();
    } else {
      await _sendViaHTTP(content);
    }
  }

  function _clearInput() {
    if (input) { input.value = ""; input.style.height = "auto"; }
    if (sendBtn) sendBtn.disabled = true;
  }

  async function _sendViaHTTP(content) {
    try {
      const res  = await postJSON(sendUrl, { content });
      const data = await res.json();
      if (data.success) {
        _appendMessage({ ...data.message, is_mine: true });
        _clearInput();
      }
    } catch {
      _showToast("Failed to send. Check your connection.");
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  async function _sendFile(caption = "") {
    if (!selectedFile) return;
    const fd = new FormData();
    fd.append("file", selectedFile);
    if (caption) fd.append("content", caption);
    fd.append("csrfmiddlewaretoken", csrfToken);

    try {
      const res  = await fetch(fileUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
        body: fd,
        credentials: "same-origin",
      });
      const data = await res.json();
      if (data.success) {
        _appendMessage({ ...data.message, is_mine: true });
        _clearInput();
        selectedFile = null;
        if (fileInput)   fileInput.value = "";
        if (filePreview) filePreview.style.display = "none";
      } else {
        _showToast(data.error || "Upload failed.");
        if (sendBtn) sendBtn.disabled = false;
      }
    } catch {
      _showToast("Upload failed. Check your connection.");
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  // ── Render a message bubble ───────────────────────────────
  function _appendMessage(msg) {
    if (!messagesEl) return;

    // Remove empty-state placeholder
    const empty = document.getElementById("chat-empty");
    empty && empty.remove();

    const isMine = msg.is_mine || msg.sender_id === currentUserId;
    const wrap   = document.createElement("div");
    wrap.className = `msg-bubble-wrap ${isMine ? "msg-mine" : "msg-theirs"} msg-new`;
    wrap.id = `msg-${msg.message_id || msg.id || ""}`;

    const avatar = isMine ? "" : `
      ${msg.sender_avatar
        ? `<img src="${escapeHtml(msg.sender_avatar)}" alt="${escapeHtml(msg.sender_username || "")}" class="msg-avatar">`
        : `<div class="msg-avatar msg-avatar--placeholder">${escapeHtml((msg.sender_username || "?")[0].toUpperCase())}</div>`
      }`;

    const bubbleContent = _buildBubbleContent(msg);
    const time = msg.created_at || fmtTime(new Date());

    wrap.innerHTML = `
      ${avatar}
      <div class="msg-bubble-col">
        <div class="msg-bubble ${msg.is_file ? "msg-bubble--file" : ""}">
          ${bubbleContent}
        </div>
        <span class="msg-time">${escapeHtml(time)}</span>
      </div>`;

    messagesEl.appendChild(wrap);
    scrollToBottom(true);
  }

  function _buildBubbleContent(msg) {
    if (msg.is_file && msg.file_url) {
      if (msg.is_image) {
        return `
          <a href="${escapeHtml(msg.file_url)}" target="_blank" rel="noopener">
            <img src="${escapeHtml(msg.file_url)}" alt="${escapeHtml(msg.file_name || "image")}" class="msg-image">
          </a>
          ${msg.content ? `<p class="msg-text msg-text--below-file">${escapeHtml(msg.content)}</p>` : ""}`;
      }
      return `
        <a href="${escapeHtml(msg.file_url)}" target="_blank" rel="noopener" class="msg-file-link" download>
          <div class="msg-file-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="28" height="28"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm4 18H6V4h7v5h5v11z"/></svg>
          </div>
          <div class="msg-file-info">
            <span class="msg-file-name">${escapeHtml(msg.file_name || "file")}</span>
          </div>
          <svg class="msg-download-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
        </a>
        ${msg.content ? `<p class="msg-text msg-text--below-file">${escapeHtml(msg.content)}</p>` : ""}`;
    }
    return `<p class="msg-text">${escapeHtml(msg.content || "")}</p>`;
  }

  // ── Typing indicator display ──────────────────────────────
  let typingTimeout;
  function _showTypingIndicator(username) {
    if (!typingEl) return;
    if (typingAvatar) typingAvatar.textContent = (username || "?")[0].toUpperCase();
    typingEl.style.display = "flex";
    scrollToBottom(true);
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(_hideTypingIndicator, 4000);
  }

  function _hideTypingIndicator() {
    if (typingEl) typingEl.style.display = "none";
  }

  // ── Online status update ──────────────────────────────────
  function _updateOnlineStatus(status) {
    const online = status === "online";
    if (onlineDot) onlineDot.classList.toggle("online", online);
    if (statusText) statusText.textContent = online ? "online" : "offline";
    // Update inbox indicator if present
    const inboxDot = document.querySelector(`#other-online-dot`);
    inboxDot && inboxDot.classList.toggle("online", online);
  }
};
