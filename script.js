/* FitWeb — landing page interactions
 * Vanilla JS, no build step. Runs after DOMContentLoaded thanks to defer.
 */
(() => {
  'use strict';

  // ── Nav: tint the bar once the page has scrolled past the hero edge ─────
  const nav = document.getElementById('nav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ── Mobile menu ─────────────────────────────────────────────────────────
  const menu = document.getElementById('menu');
  const toggle = document.querySelector('.nav__toggle');
  const close = document.querySelector('.menu__close');
  if (menu && toggle) {
    const setMenu = (state) => {
      menu.classList.toggle('is-open', state);
      menu.setAttribute('aria-hidden', String(!state));
      toggle.setAttribute('aria-expanded', String(state));
      document.body.style.overflow = state ? 'hidden' : '';
    };
    toggle.addEventListener('click', () => setMenu(true));
    close?.addEventListener('click', () => setMenu(false));
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
    // close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false);
    });
  }

  // ── FAQ accordion ───────────────────────────────────────────────────────
  document.querySelectorAll('.faq__item').forEach(item => {
    const btn = item.querySelector('.faq__q');
    if (!btn) return;
    btn.addEventListener('click', () => {
      const isOpen = item.classList.contains('is-open');
      item.classList.toggle('is-open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  // ── Hero headline: drop overflow:hidden once the rise animation finishes
  // so descenders ('g', 'p', 'y') aren't clipped by the line-mask.
  document.querySelectorAll('.hero__headline .reveal-line').forEach(line => {
    const inner = line.querySelector('span');
    if (!inner) return;
    inner.addEventListener('animationend', () => line.classList.add('is-done'), { once: true });
  });

  // ── Reveal on scroll ────────────────────────────────────────────────────
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  } else {
    // graceful fallback — show everything
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-in'));
  }

  // ── Enquiry form ────────────────────────────────────────────────────────
  // Progressive enhancement: if JS is on, submit via fetch and show inline status.
  // If JS is off, the form submits natively to its `action` URL.
  const form = document.querySelector('.form');
  if (form) {
    const status = form.querySelector('.form__status');
    const submit = form.querySelector('button[type="submit"]');

    const setStatus = (msg, kind) => {
      if (!status) return;
      status.textContent = msg;
      status.dataset.kind = kind || '';
    };

    form.addEventListener('submit', async (e) => {
      // Honeypot — bots fill the hidden 'website' field; humans never see it.
      const honey = form.querySelector('input[name="website"]');
      if (honey && honey.value.trim() !== '') {
        e.preventDefault();
        setStatus('Thanks — we\'ll be in touch.', 'ok'); // silently swallow
        return;
      }

      // Only intercept if fetch is available; otherwise let the browser submit natively
      if (typeof fetch !== 'function') return;

      e.preventDefault();
      submit?.setAttribute('disabled', 'disabled');
      setStatus('Sending…', 'pending');

      try {
        const data = new FormData(form);
        const res = await fetch(form.action, {
          method: form.method || 'POST',
          body: data,
          headers: { 'Accept': 'application/json' }
        });

        if (res.ok) {
          form.reset();
          setStatus('Thanks — we\'ll be in touch within one business day.', 'ok');
        } else {
          setStatus('Something went wrong. Email hello@fitweb.co.nz instead?', 'error');
        }
      } catch (err) {
        setStatus('Network error. Email hello@fitweb.co.nz instead?', 'error');
      } finally {
        submit?.removeAttribute('disabled');
      }
    });
  }

})();
