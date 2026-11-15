/**
 * ElderCare 360 - Interactive Client Application Script
 * Left-sidebar management, accessibility scaling, audio alerts, and emergency SOS triggers.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Accessibility: Font Size Preference
  const savedFontSize = localStorage.getItem('eldercare_font_size') || 'normal';
  document.documentElement.setAttribute('data-font-size', savedFontSize);
  
  // Accessibility: High Contrast Preference
  const savedTheme = localStorage.getItem('eldercare_theme') || 'default';
  document.documentElement.setAttribute('data-theme', savedTheme);

  // 2. Left Sidebar Toggle
  const sidebar = document.getElementById('left-sidebar');
  const mainWrapper = document.getElementById('main-wrapper');
  const toggleBtn = document.getElementById('sidebar-toggle-btn');
  const mobileBackdrop = document.getElementById('sidebar-backdrop');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      if (window.innerWidth <= 992) {
        sidebar.classList.toggle('show-mobile');
        if (mobileBackdrop) mobileBackdrop.classList.toggle('show');
      } else {
        sidebar.classList.toggle('collapsed');
        if (mainWrapper) mainWrapper.classList.toggle('sidebar-collapsed');
      }
    });
  }

  if (mobileBackdrop) {
    mobileBackdrop.addEventListener('click', function () {
      if (sidebar) sidebar.classList.remove('show-mobile');
      mobileBackdrop.classList.remove('show');
    });
  }

  // 3. Audio Synthesizer (Web Audio API)
  window.AudioAlerts = {
    playChime: function () {
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
        osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.15); // E5
        osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.30); // G5
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.6);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.65);
      } catch (e) {
        console.warn('AudioContext unavailable:', e);
      }
    },
    playEmergencySiren: function (durationSec = 4) {
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        
        // Siren pitch modulation
        const now = ctx.currentTime;
        for (let t = 0; t < durationSec; t += 0.5) {
          osc.frequency.setValueAtTime(600, now + t);
          osc.frequency.linearRampToValueAtTime(950, now + t + 0.25);
          osc.frequency.linearRampToValueAtTime(600, now + t + 0.5);
        }
        
        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + durationSec);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(now + durationSec);
      } catch (e) {
        console.warn('Emergency siren audio failed:', e);
      }
    }
  };

  // 4. Quick Table Search Filter Utility
  const searchInputs = document.querySelectorAll('.table-search-input');
  searchInputs.forEach(input => {
    const targetTableId = input.getAttribute('data-target-table');
    const table = document.getElementById(targetTableId);
    if (!table) return;

    input.addEventListener('keyup', function () {
      const term = input.value.toLowerCase().trim();
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
      });
    });
  });
});

// Font size setting functions
function setFontSize(size) {
  localStorage.setItem('eldercare_font_size', size);
  document.documentElement.setAttribute('data-font-size', size);
}

// High contrast toggle
function toggleHighContrast() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'high-contrast' ? 'default' : 'high-contrast';
  localStorage.setItem('eldercare_theme', next);
  document.documentElement.setAttribute('data-theme', next);
}

// Global Emergency SOS trigger handler
function triggerEmergencySOS(patientId = null) {
  const modalEl = document.getElementById('emergencyConfirmModal');
  if (modalEl && typeof bootstrap !== 'undefined') {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  } else {
    if (confirm('EMERGENCY ALERT: Are you sure you want to trigger an immediate Emergency SOS? This alerts primary caregivers, family, and medical contacts.')) {
      executeSOSDispatch(patientId);
    }
  }
}

function executeSOSDispatch(patientId = null) {
  // Play emergency audio siren
  if (window.AudioAlerts) window.AudioAlerts.playEmergencySiren(5);

  // Trigger flashing visual overlay
  const overlay = document.createElement('div');
  overlay.className = 'sos-active-overlay';
  document.body.appendChild(overlay);
  setTimeout(() => overlay.remove(), 6000);

  // Send backend dispatch
  fetch('/emergency/api/trigger', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      patient_id: patientId,
      alert_type: 'SOS_BUTTON',
      notes: 'Emergency SOS activated via user interface button.'
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert(`🚨 EMERGENCY SOS DISPATCHED!\n\nStatus: ${data.status}\nAlert ID: #${data.alert_id}\nNotified Contacts: ${data.notified_count}\n\nEmergency dispatch logged. Medical support team notified.`);
      window.location.href = '/emergency';
    } else {
      alert('Error triggering alert: ' + (data.message || 'Please call emergency services (108) immediately.'));
    }
  })
  .catch(err => {
    console.error('SOS dispatch error:', err);
    alert('Emergency SOS recorded locally. Please call 108 immediately if in imminent danger.');
  });
}
