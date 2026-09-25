/**
 * Remote PC Keyboard Web Client
 * Connects via WebSocket to simulate standard PC keyboard input.
 */

(function () {
  'use strict';

  // --- State ---
  let socket = null;
  let isConnected = false;
  let pingStartTime = 0;
  let pingInterval = null;

  // Modifiers state
  const modifiers = {
    ctrl: false,
    alt: false,
    shift: false,
    cmd: false, // Windows / Super key
    caps_lock: false
  };

  let latchMode = true; // Latch modifier on mobile touch
  let hapticEnabled = true;

  // Active touches map (identifier -> { element, keyInfo })
  const activeTouches = new Map();

  // --- DOM Elements ---
  const statusBadge = document.getElementById('connection-status');
  const statusText = document.getElementById('status-text');
  const pingBadge = document.getElementById('ping-badge');
  const tagCtrl = document.getElementById('tag-ctrl');
  const tagAlt = document.getElementById('tag-alt');
  const tagShift = document.getElementById('tag-shift');
  const tagWin = document.getElementById('tag-win');
  const tagCaps = document.getElementById('tag-caps');

  const btnToggleFn = document.getElementById('btn-toggle-fn');
  const btnToggleNav = document.getElementById('btn-toggle-nav');
  const btnToggleNumpad = document.getElementById('btn-toggle-numpad');
  const btnToggleShortcuts = document.getElementById('btn-toggle-shortcuts');
  const btnLatchMode = document.getElementById('btn-latch-mode');
  const btnHaptic = document.getElementById('btn-haptic');
  const btnFullscreen = document.getElementById('btn-fullscreen');

  const fnRow = document.getElementById('fn-row');
  const navRow = document.getElementById('nav-row');
  const numpad = document.getElementById('numpad');
  const shortcutsBar = document.getElementById('shortcuts-bar');

  // --- Haptic Feedback ---
  function vibrate(ms = 12) {
    if (hapticEnabled && navigator.vibrate) {
      try {
        navigator.vibrate(ms);
      } catch (e) {
        // ignore
      }
    }
  }

  // --- WebSocket Connection ---
  function connectWebSocket() {
    const loc = window.location;
    const protocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${loc.host}/ws`;

    updateStatus(false, 'Menghubungkan...');

    try {
      socket = new WebSocket(wsUrl);
    } catch (e) {
      console.error('WebSocket init error:', e);
      setTimeout(connectWebSocket, 2000);
      return;
    }

    socket.onopen = () => {
      isConnected = true;
      updateStatus(true, 'Terhubung');
      startPing();
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'pong') {
          const latency = Math.round(performance.now() - pingStartTime);
          pingBadge.textContent = `${latency} ms`;
        }
      } catch (err) {
        console.error('Error parsing WS message:', err);
      }
    };

    socket.onclose = () => {
      isConnected = false;
      updateStatus(false, 'Terputus');
      stopPing();
      setTimeout(connectWebSocket, 1500);
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
      socket.close();
    };
  }

  function startPing() {
    stopPing();
    pingInterval = setInterval(() => {
      if (isConnected && socket.readyState === WebSocket.OPEN) {
        pingStartTime = performance.now();
        socket.send(JSON.stringify({ type: 'ping' }));
      }
    }, 3000);
  }

  function stopPing() {
    if (pingInterval) {
      clearInterval(pingInterval);
      pingInterval = null;
    }
    pingBadge.textContent = '-- ms';
  }

  function updateStatus(connected, text) {
    if (connected) {
      statusBadge.classList.remove('disconnected');
      statusBadge.classList.add('connected');
    } else {
      statusBadge.classList.remove('connected');
      statusBadge.classList.add('disconnected');
    }
    statusText.textContent = text;
  }

  function sendSocket(payload) {
    if (isConnected && socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    }
  }

  // --- Modifier Updates ---
  function updateModifierUI() {
    tagCtrl.classList.toggle('active', modifiers.ctrl);
    tagAlt.classList.toggle('active', modifiers.alt);
    tagShift.classList.toggle('active', modifiers.shift);
    tagWin.classList.toggle('active', modifiers.cmd);
    tagCaps.classList.toggle('active', modifiers.caps_lock);

    // Update active visual on modifier buttons
    document.querySelectorAll('.key-ctrl').forEach(el => el.classList.toggle('latched', modifiers.ctrl));
    document.querySelectorAll('.key-alt').forEach(el => el.classList.toggle('latched', modifiers.alt));
    document.querySelectorAll('.key-shift').forEach(el => el.classList.toggle('latched', modifiers.shift));
    const winBtn = document.getElementById('key-win');
    if (winBtn) winBtn.classList.toggle('latched', modifiers.cmd);
    const capsBtn = document.getElementById('key-caps');
    if (capsBtn) capsBtn.classList.toggle('latched', modifiers.caps_lock);

    // Swap case / symbol visual display when Shift or Caps is active
    const isShifted = modifiers.shift || modifiers.caps_lock;
    document.querySelectorAll('.key[data-char]').forEach(keyEl => {
      const char = keyEl.dataset.char;
      const shiftChar = keyEl.dataset.shift;
      const mainSpan = keyEl.querySelector('.main');
      if (mainSpan && char.length === 1 && char.match(/[a-z]/i)) {
        mainSpan.textContent = isShifted ? char.toUpperCase() : char.toLowerCase();
      }
    });
  }

  // --- Key Input Handling ---
  function getKeyInfo(element) {
    if (!element) return null;
    const keyBtn = element.closest('.key');
    if (!keyBtn) return null;

    return {
      element: keyBtn,
      key: keyBtn.dataset.key || null,
      char: keyBtn.dataset.char || null,
      shiftChar: keyBtn.dataset.shift || null,
      code: keyBtn.dataset.code || ''
    };
  }

  function handleKeyPress(keyInfo) {
    if (!keyInfo) return;
    const { element, key, char, shiftChar } = keyInfo;
    vibrate(12);

    element.classList.add('pressed');

    // Modifier keys (Ctrl, Alt, Shift, Win/Cmd, Caps)
    if (key === 'ctrl' || key === 'alt' || key === 'shift' || key === 'cmd' || key === 'caps_lock') {
      if (latchMode) {
        // Toggle latch
        modifiers[key] = !modifiers[key];
        updateModifierUI();
        sendSocket({
          type: modifiers[key] ? 'keydown' : 'keyup',
          key: key
        });
        return;
      } else {
        modifiers[key] = true;
        updateModifierUI();
        sendSocket({ type: 'keydown', key: key });
        return;
      }
    }

    // Regular character or special key
    let characterToSend = char;
    if (char) {
      if (modifiers.shift && shiftChar) {
        characterToSend = shiftChar;
      } else if (modifiers.shift || modifiers.caps_lock) {
        characterToSend = char.toUpperCase();
      }
    }

    sendSocket({
      type: 'keypress',
      key: key || null,
      char: characterToSend || null,
      modifiers: {
        ctrl: modifiers.ctrl,
        alt: modifiers.alt,
        shift: modifiers.shift,
        cmd: modifiers.cmd
      }
    });

    // If modifier was latched and not caps, release modifier after normal key press
    if (latchMode) {
      let releasedAny = false;
      ['ctrl', 'alt', 'shift', 'cmd'].forEach(mod => {
        if (modifiers[mod]) {
          modifiers[mod] = false;
          sendSocket({ type: 'keyup', key: mod });
          releasedAny = true;
        }
      });
      if (releasedAny) {
        updateModifierUI();
      }
    }
  }

  function handleKeyRelease(keyInfo) {
    if (!keyInfo) return;
    const { element, key } = keyInfo;
    element.classList.remove('pressed');

    // In non-latch mode, release modifier on touch up
    if (!latchMode) {
      if (key === 'ctrl' || key === 'alt' || key === 'shift' || key === 'cmd') {
        modifiers[key] = false;
        updateModifierUI();
        sendSocket({ type: 'keyup', key: key });
      }
    }
  }

  // --- Multi-touch Event Listeners ---
  const mainContainer = document.getElementById('app');

  mainContainer.addEventListener('touchstart', (e) => {
    // If touched on top-bar or shortcuts, let standard click work
    if (e.target.closest('.top-bar') || e.target.closest('.shortcuts-bar')) {
      return;
    }
    e.preventDefault(); // prevent zoom and magnifier

    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      const targetEl = document.elementFromPoint(touch.clientX, touch.clientY);
      const keyInfo = getKeyInfo(targetEl);

      if (keyInfo) {
        activeTouches.set(touch.identifier, keyInfo);
        handleKeyPress(keyInfo);
      }
    }
  }, { passive: false });

  mainContainer.addEventListener('touchend', (e) => {
    if (e.target.closest('.top-bar') || e.target.closest('.shortcuts-bar')) {
      return;
    }
    e.preventDefault();

    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      const keyInfo = activeTouches.get(touch.identifier);
      if (keyInfo) {
        handleKeyRelease(keyInfo);
        activeTouches.delete(touch.identifier);
      }
    }
  }, { passive: false });

  mainContainer.addEventListener('touchcancel', (e) => {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      const keyInfo = activeTouches.get(touch.identifier);
      if (keyInfo) {
        handleKeyRelease(keyInfo);
        activeTouches.delete(touch.identifier);
      }
    }
  }, { passive: false });

  // Mouse Fallback (for testing in desktop browser)
  let mouseKeyInfo = null;
  mainContainer.addEventListener('mousedown', (e) => {
    if (e.target.closest('.top-bar') || e.target.closest('.shortcuts-bar')) {
      return;
    }
    const keyInfo = getKeyInfo(e.target);
    if (keyInfo) {
      mouseKeyInfo = keyInfo;
      handleKeyPress(keyInfo);
    }
  });

  window.addEventListener('mouseup', () => {
    if (mouseKeyInfo) {
      handleKeyRelease(mouseKeyInfo);
      mouseKeyInfo = null;
    }
  });

  // --- Shortcut Buttons (Ctrl+C, Ctrl+V, etc.) ---
  document.querySelectorAll('.shortcut-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      vibrate(20);
      const keys = (btn.dataset.keys || '').split(',');
      if (keys.length > 0) {
        sendSocket({
          type: 'combo',
          keys: keys
        });
      }
    });
  });

  // --- Header Tool Buttons ---
  btnToggleFn.addEventListener('click', () => {
    fnRow.classList.toggle('hidden');
    btnToggleFn.classList.toggle('active', !fnRow.classList.contains('hidden'));
  });

  btnToggleNav.addEventListener('click', () => {
    navRow.classList.toggle('hidden');
    btnToggleNav.classList.toggle('active', !navRow.classList.contains('hidden'));
  });

  btnToggleNumpad.addEventListener('click', () => {
    numpad.classList.toggle('hidden');
    btnToggleNumpad.classList.toggle('active', !numpad.classList.contains('hidden'));
  });

  btnToggleShortcuts.addEventListener('click', () => {
    shortcutsBar.classList.toggle('hidden');
    btnToggleShortcuts.classList.toggle('active', !shortcutsBar.classList.contains('hidden'));
  });

  btnLatchMode.addEventListener('click', () => {
    latchMode = !latchMode;
    btnLatchMode.classList.toggle('active', latchMode);
    vibrate(15);
  });

  btnHaptic.addEventListener('click', () => {
    hapticEnabled = !hapticEnabled;
    btnHaptic.classList.toggle('active', hapticEnabled);
    if (hapticEnabled) vibrate(30);
  });

  btnFullscreen.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  });

  // Prevent contextmenu popup
  window.addEventListener('contextmenu', (e) => e.preventDefault());

  // Initialize
  updateModifierUI();
  connectWebSocket();
})();
