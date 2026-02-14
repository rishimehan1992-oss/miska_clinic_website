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

  // Lead form – sends to Google Sheets (handles both page form and popup form)
  const sheetsUrl = 'https://script.google.com/macros/s/AKfycbw161634j-ygURP7gc12WfCSd6xwhovYxHBxKMULgQ78dj0G6TVdNKxzQAhHPS1f_GgNw/exec';

  function handleLeadSubmit(e, source) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Submitting…';
    const fd = new FormData(form);
    const data = { formType: 'contact', source: source || 'contact_page' };
    fd.forEach((v, k) => { data[k] = v; });
    fetch(sheetsUrl, { method: 'POST', mode: 'no-cors', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify(data) }).catch(() => {});
    btn.textContent = 'Thank you! We will call you soon.';
    btn.style.background = '#059669';
    form.reset();
    setTimeout(() => { btn.disabled = false; btn.textContent = originalText; btn.style.background = ''; }, 4000);
    if (form.closest('.contact-popup-overlay')) document.getElementById('contactPopup')?.classList.remove('open');
  }

  document.querySelectorAll('.js-lead-form').forEach((form) => {
    form.addEventListener('submit', (e) => handleLeadSubmit(e, form.closest('.contact-popup-overlay') ? 'popup' : 'contact_page'));
  });

  // Contact form popup – appears after 45 seconds (skip on contact page)
  (function initContactPopup() {
    if (window.location.pathname.endsWith('contact.html') || window.location.pathname.endsWith('/contact') || window.location.href.includes('contact.html')) return;
    const storageKey = 'miska_contact_popup_shown';
    const popupHtml = `
      <div class="contact-popup-overlay" id="contactPopup" aria-hidden="true">
        <div class="contact-popup">
          <button class="contact-popup-close" aria-label="Close">&times;</button>
          <h3>Book Consultation</h3>
          <p>Fill in your details and we'll call you back within 24 hours.</p>
          <form class="consult-form js-lead-form" aria-label="Consultation request">
            <input type="text" name="name" placeholder="Your Name" required autocomplete="name" />
            <input type="tel" name="phone" placeholder="Phone Number" required autocomplete="tel" />
            <label style="display:block; margin-bottom: 8px; font-size: 0.95rem; color: var(--grey, #555);">Service required</label>
            <select name="serviceRequired">
              <option value="">Select service</option>
              <option value="Hair">Hair</option>
              <option value="Skin">Skin</option>
              <option value="Dental">Dental</option>
            </select>
            <label style="display:block; margin-bottom: 8px; font-size: 0.95rem; color: var(--grey, #555);">Preferred time to contact</label>
            <select name="preferredTime">
              <option value="">Select a time slot</option>
              <option value="9 AM - 12 PM">9 AM – 12 PM</option>
              <option value="12 PM - 3 PM">12 PM – 3 PM</option>
              <option value="3 PM - 6 PM">3 PM – 6 PM</option>
              <option value="6 PM - 7 PM">6 PM – 7 PM</option>
            </select>
            <textarea name="message" placeholder="Message (optional)" rows="2"></textarea>
            <button type="submit" class="btn btn-primary btn-block">Submit — We'll Call You</button>
          </form>
        </div>
      </div>`;
    const wrap = document.createElement('div');
    wrap.innerHTML = popupHtml;
    const popup = wrap.firstElementChild;
    document.body.appendChild(popup);

    const closePopup = () => {
      popup.classList.remove('open');
      popup.setAttribute('aria-hidden', 'true');
    };
    popup.querySelector('.contact-popup-close').addEventListener('click', closePopup);
    popup.addEventListener('click', (e) => { if (e.target === popup) closePopup(); });

    const popupForm = popup.querySelector('.js-lead-form');
    popupForm.addEventListener('submit', (e) => handleLeadSubmit(e, 'popup'));

    const showPopup = () => {
      if (sessionStorage.getItem(storageKey)) return;
      sessionStorage.setItem(storageKey, '1');
      popup.classList.add('open');
      popup.setAttribute('aria-hidden', 'false');
    };
    setTimeout(showPopup, 45000);
  })();

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
