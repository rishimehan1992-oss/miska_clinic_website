/**
 * Miska Hair Transplant & Skin Clinic
 * Lead generation, chat widget, navigation
 */

(function () {
  'use strict';

  // Year in footer
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Mobile nav toggle
  const navToggle = document.querySelector('.nav-toggle');
  const headerInner = document.querySelector('.header-inner');
  if (navToggle && headerInner) {
    navToggle.addEventListener('click', () => {
      const open = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', !open);
      headerInner.classList.toggle('nav-open');
    });
  }

  // Mobile dropdown toggle (submenus)
  document.querySelectorAll('.has-dropdown').forEach((item) => {
    const link = item.querySelector(':scope > a');
    if (link) {
      link.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
          e.preventDefault();
          const wasOpen = item.classList.contains('is-open');
          document.querySelectorAll('.has-dropdown').forEach((other) => other.classList.remove('is-open'));
          if (!wasOpen) item.classList.add('is-open');
        }
      });
    }
  });

  // Chat widget
  const chatWidget = document.getElementById('chatWidget');
  const chatToggle = document.getElementById('chatToggle');
  const chatClose = document.getElementById('chatClose');
  const chatPanel = document.getElementById('chatPanel');

  if (chatToggle && chatPanel) {
    chatToggle.addEventListener('click', () => {
      const isOpen = chatWidget.classList.contains('open');
      chatWidget.classList.toggle('open', !isOpen);
      chatWidget.setAttribute('aria-hidden', isOpen);
    });
  }
  if (chatClose && chatWidget) {
    chatClose.addEventListener('click', () => {
      chatWidget.classList.remove('open');
      chatWidget.setAttribute('aria-hidden', 'true');
    });
  }

  // Lead form – sends to Google Sheets
  const leadForm = document.getElementById('leadForm');
  if (leadForm) {
    leadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const sheetsUrl = 'https://script.google.com/macros/s/AKfycbw161634j-ygURP7gc12WfCSd6xwhovYxHBxKMULgQ78dj0G6TVdNKxzQAhHPS1f_GgNw/exec';
      const btn = leadForm.querySelector('button[type="submit"]');
      const originalText = btn.textContent;

      btn.disabled = true;
      btn.textContent = 'Submitting…';

      const fd = new FormData(leadForm);
      const data = { formType: 'contact', source: 'contact_page' };
      fd.forEach((v, k) => { data[k] = v; });

      try {
        await fetch(sheetsUrl, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'text/plain' },
          body: JSON.stringify(data)
        });
      } catch (err) {
        console.warn('Form submit to sheet failed:', err);
      }

      btn.textContent = 'Thank you! We will call you soon.';
      btn.style.background = '#059669';
      leadForm.reset();

      setTimeout(() => {
        btn.disabled = false;
        btn.textContent = originalText;
        btn.style.background = '';
      }, 4000);
    });
  }

  // Smooth scroll for anchor links (same page)
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    const href = a.getAttribute('href');
    if (href === '#') return;
    const target = document.querySelector(href);
    if (target) {
      a.addEventListener('click', (e) => {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        headerInner?.classList.remove('nav-open');
        navToggle?.setAttribute('aria-expanded', 'false');
      });
    }
  });
})();
