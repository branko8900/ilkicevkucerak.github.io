/* =============================================================================
   ILKIĆEV KUĆERAK — behaviour layer
   No dependencies. Nothing here is required to read the site: if this file
   fails to load, `html.js` is never set and every reveal stays visible.

   Contents
     1  helpers
     2  header — sticky, dropdown, drawer
     3  language memory
     4  reveals (IntersectionObserver)
     5  the steam spine — scroll-driven data rail
     6  counters
     7  hero load sequence
     8  contact form
     9  gallery lightbox
   ========================================================================== */

(function () {
  'use strict';

  /* --------------------------------------------------------- 1. helpers */

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  var mirno = window.matchMedia('(prefers-reduced-motion: reduce)');
  var tiho  = function () { return mirno.matches; };

  /* One rAF loop shared by everything that reacts to scroll, so we never stack
     listeners that each force a layout read. */
  var pretplatnici = [];
  var ceka = false;

  function naSkrol(fn) { pretplatnici.push(fn); }

  function okini() {
    var y = window.pageYOffset || document.documentElement.scrollTop;
    var vh = window.innerHeight;
    for (var i = 0; i < pretplatnici.length; i++) pretplatnici[i](y, vh);
    ceka = false;
  }

  window.addEventListener('scroll', function () {
    if (!ceka) { ceka = true; window.requestAnimationFrame(okini); }
  }, { passive: true });

  window.addEventListener('resize', function () {
    if (!ceka) { ceka = true; window.requestAnimationFrame(okini); }
  }, { passive: true });

  /* ------------------------------------------- 2. header: sticky / dd / drawer */

  var zaglavlje = $('.zaglavlje');

  if (zaglavlje) {
    naSkrol(function (y) {
      zaglavlje.classList.toggle('zalepljen', y > 12);
    });
  }

  /* Dropdown — click to toggle (works on touch), hover to preview on pointer
     devices, Escape to close, click-outside to close. The entries stay real
     links throughout. */
  $$('.nav-stavka.ima-podmeni').forEach(function (stavka) {
    var okidac = $('.nav-veza', stavka);
    var meni = $('.podmeni', stavka);
    if (!okidac || !meni) return;

    function otvori(v) {
      stavka.classList.toggle('otvoren', v);
      okidac.setAttribute('aria-expanded', v ? 'true' : 'false');
    }

    okidac.addEventListener('click', function (e) {
      /* Let the parent overview page load normally on keyboard/middle click;
         a plain left click opens the menu instead. */
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      otvori(!stavka.classList.contains('otvoren'));
    });

    if (window.matchMedia('(hover: hover)').matches) {
      stavka.addEventListener('mouseenter', function () { otvori(true); });
      stavka.addEventListener('mouseleave', function () { otvori(false); });
    }

    stavka.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { otvori(false); okidac.focus(); }
    });

    document.addEventListener('click', function (e) {
      if (!stavka.contains(e.target)) otvori(false);
    });
  });

  /* Mobile drawer */
  var burger = $('.burger');
  var fioka = $('.fioka');

  if (burger && fioka) {
    burger.addEventListener('click', function () {
      var otvoren = burger.getAttribute('aria-expanded') === 'true';
      burger.setAttribute('aria-expanded', otvoren ? 'false' : 'true');
      fioka.classList.toggle('otvoren', !otvoren);
      document.body.style.overflow = otvoren ? '' : 'hidden';
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && fioka.classList.contains('otvoren')) {
        burger.click();
        burger.focus();
      }
    });

    /* Close when a real navigation starts, so the drawer never lingers. */
    $$('a', fioka).forEach(function (a) {
      a.addEventListener('click', function () {
        burger.setAttribute('aria-expanded', 'false');
        fioka.classList.remove('otvoren');
        document.body.style.overflow = '';
      });
    });
  }

  /* --------------------------------------------------- 3. language memory */

  var html = document.documentElement;
  var jezik = html.getAttribute('lang');

  try {
    if (jezik) localStorage.setItem('kucerak:jezik', jezik);
  } catch (e) { /* private mode — the site works without it */ }

  /* ------------------------------------------------------- 4. reveals */

  var mete = $$('.otkrij');

  if (mete.length) {
    if (!('IntersectionObserver' in window) || tiho()) {
      mete.forEach(function (el) { el.classList.add('unutra'); });
    } else {
      /* Stagger by position within the nearest group, not globally — otherwise
         late items on long pages wait absurdly long. */
      $$('[data-grupa]').forEach(function (g) {
        $$('.otkrij', g).forEach(function (el, i) {
          el.style.setProperty('--i', Math.min(i, 6));
        });
      });

      var oko = new IntersectionObserver(function (unosi) {
        unosi.forEach(function (u) {
          if (u.isIntersecting) {
            u.target.classList.add('unutra');
            oko.unobserve(u.target);
          }
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

      mete.forEach(function (el) { oko.observe(el); });

      /* Failsafe: reveals start at opacity 0, so anything that keeps the
         observer from firing would hide the page. If the first screen has not
         resolved shortly after load, drop the whole mechanism and show
         everything. Copy on screen beats choreography every time. */
      setTimeout(function () {
        if (document.querySelectorAll('.otkrij.unutra').length) return;
        mete.forEach(function (el) { el.classList.add('unutra'); });
      }, 2500);
    }
  }

  /* --------------------------------------------- 5. the steam spine
     Sections that carry `data-podatak` become ticks on a fixed rail. The rail
     fills with scroll progress; each tick lights when its section reaches the
     middle of the viewport and shows the estate's real figure for that section.
     On narrow screens the rail collapses to a 2px bar under the header.        */

  var kicma = $('.kicma');
  var sina = $('.kicma-sina');
  var mobilna = $('.kicma-mobilna');
  var sekcije = $$('[data-podatak]');

  if (sekcije.length && sina) {
    var tacke = sekcije.map(function (sek, i) {
      var t = document.createElement('span');
      t.className = 'kicma-tacka';
      t.setAttribute('data-podatak', sek.getAttribute('data-podatak'));
      t.style.top = ((i / Math.max(sekcije.length - 1, 1)) * 100) + '%';
      sina.appendChild(t);
      return t;
    });

    naSkrol(function (y, vh) {
      var visina = document.documentElement.scrollHeight - vh;
      var p = visina > 0 ? Math.min(Math.max(y / visina, 0), 1) : 0;

      if (kicma) kicma.style.setProperty('--napredak', p.toFixed(4));
      if (mobilna) mobilna.style.setProperty('--napredak', p.toFixed(4));

      var sredina = y + vh * 0.5;
      sekcije.forEach(function (sek, i) {
        var vrh = sek.getBoundingClientRect().top + y;
        tacke[i].classList.toggle('zapaljen', sredina >= vrh);
      });
    });
  }

  /* ----------------------------------------------------------- 6. counters */

  var brojevi = $$('[data-broj]');

  if (brojevi.length) {
    if (!('IntersectionObserver' in window) || tiho()) {
      brojevi.forEach(function (el) { el.textContent = el.getAttribute('data-broj'); });
    } else {
      var oko2 = new IntersectionObserver(function (unosi) {
        unosi.forEach(function (u) {
          if (!u.isIntersecting) return;
          oko2.unobserve(u.target);

          var el = u.target;
          var cilj = parseFloat(el.getAttribute('data-broj'));
          var dec = (el.getAttribute('data-broj').split('.')[1] || '').length;
          var pocetak = null;
          var trajanje = 1400;

          function korak(t) {
            if (pocetak === null) pocetak = t;
            var p = Math.min((t - pocetak) / trajanje, 1);
            var e = 1 - Math.pow(1 - p, 3);           /* ease-out cubic */
            el.textContent = (cilj * e).toFixed(dec);
            if (p < 1) requestAnimationFrame(korak);
            else el.textContent = cilj.toFixed(dec);
          }
          requestAnimationFrame(korak);
        });
      }, { threshold: 0.5 });

      brojevi.forEach(function (el) {
        el.textContent = '0';
        oko2.observe(el);
      });
    }
  }

  /* ------------------------------------------------------ 6b. ambient video
     The loop is 2.2 MB — worth it on a desktop, indefensible on a phone plan.
     It ships with no sources at all; they are attached only when the section is
     approached AND the visitor is on a wide screen, is not asking to save data,
     and has not asked for reduced motion. Everyone else keeps the poster frame,
     which is the same picture standing still. */

  $$('video[data-lenta]').forEach(function (v) {
    var veza = navigator.connection || {};
    var stedi = veza.saveData === true || /2g/.test(veza.effectiveType || '');

    if (window.innerWidth < 700 || stedi || tiho()) return;

    function ucitaj() {
      if (v.dataset.spreman) return;
      v.dataset.spreman = '1';
      [['webm', 'video/webm'], ['mp4', 'video/mp4']].forEach(function (par) {
        var src = v.getAttribute('data-' + par[0]);
        if (!src) return;
        var s = document.createElement('source');
        s.src = src;
        s.type = par[1];
        v.appendChild(s);
      });
      v.load();
      var p = v.play();
      if (p && p.catch) p.catch(function () { /* autoplay refused — poster stays */ });
    }

    if (!('IntersectionObserver' in window)) { ucitaj(); return; }

    var oko3 = new IntersectionObserver(function (unosi) {
      unosi.forEach(function (u) {
        if (!u.isIntersecting) return;
        oko3.unobserve(u.target);
        ucitaj();
      });
    }, { rootMargin: '300px 0px' });

    oko3.observe(v);
  });

  /* ------------------------------------------------- 7. hero load sequence */

  function pokreni() { document.body.classList.add('ucitano'); }

  if (document.readyState === 'complete') {
    requestAnimationFrame(pokreni);
  } else {
    window.addEventListener('load', function () { requestAnimationFrame(pokreni); });
    /* Never let a slow image hold the headline hostage. */
    setTimeout(pokreni, 900);
  }

  /* ------------------------------------------------------ 8. contact form */

  var obrazac = $('.obrazac');

  if (obrazac) {
    var status = $('.status-poruke');
    var salji = $('button[type="submit"]', obrazac);
    var recnik = JSON.parse(obrazac.getAttribute('data-poruke') || '{}');

    function polje(el) { return el.closest('.polje'); }

    function proveri(el) {
      var p = polje(el);
      if (!p) return true;
      var greska = $('.greska', p);
      var ok = el.checkValidity();
      p.classList.toggle('nevalidno', !ok);
      if (greska && !ok) {
        greska.textContent = el.validity.valueMissing
          ? (recnik.obavezno || 'This field is required.')
          : (recnik.nevalidno || 'Please check this entry.');
      }
      el.setAttribute('aria-invalid', ok ? 'false' : 'true');
      return ok;
    }

    /* Validate on blur, never on keystroke — correcting someone mid-word is
       the fastest way to make a form feel hostile. */
    $$('input, textarea, select', obrazac).forEach(function (el) {
      el.addEventListener('blur', function () { proveri(el); });
      el.addEventListener('input', function () {
        if (polje(el) && polje(el).classList.contains('nevalidno')) proveri(el);
      });
    });

    obrazac.addEventListener('submit', function (e) {
      e.preventDefault();

      var polja = $$('input, textarea, select', obrazac);
      var lose = polja.filter(function (el) { return !proveri(el); });

      if (lose.length) {
        lose[0].focus();
        return;
      }

      var podaci = new FormData(obrazac);
      var krajnja = obrazac.getAttribute('data-endpoint');

      salji.disabled = true;
      salji.textContent = recnik.salje || 'Sending…';

      function uspeh() {
        status.hidden = false;
        status.className = 'status-poruke uspeh';
        status.textContent = recnik.uspeh || 'Thank you — your enquiry has been sent.';
        obrazac.reset();
        salji.disabled = false;
        salji.textContent = recnik.posalji || 'Send';
        status.focus();
      }

      function neuspeh() {
        status.hidden = false;
        status.className = 'status-poruke neuspeh';
        status.textContent = recnik.neuspeh || 'Could not send. Please call or email us directly.';
        salji.disabled = false;
        salji.textContent = recnik.posalji || 'Send';
      }

      /* With an endpoint configured, post it. Without one — the state this
         ships in — hand the message to the visitor's mail client so the form
         is never a dead end. */
      if (krajnja && krajnja.indexOf('http') === 0) {
        fetch(krajnja, { method: 'POST', body: podaci, headers: { Accept: 'application/json' } })
          .then(function (r) { r.ok ? uspeh() : neuspeh(); })
          .catch(neuspeh);
      } else {
        var telo = [];
        podaci.forEach(function (v, k) { if (v) telo.push(k + ': ' + v); });
        window.location.href = 'mailto:' + (obrazac.getAttribute('data-mail') || '')
          + '?subject=' + encodeURIComponent(obrazac.getAttribute('data-subject') || 'Upit')
          + '&body=' + encodeURIComponent(telo.join('\n'));
        setTimeout(uspeh, 400);
      }
    });
  }

  /* -------------------------------------------------- 9. gallery lightbox */

  var galerija = $('.galerija');

  if (galerija) {
    var slike = $$('a[data-puna]', galerija);
    if (slike.length) {
      var sloj = document.createElement('div');
      sloj.className = 'svetlo';
      sloj.setAttribute('role', 'dialog');
      sloj.setAttribute('aria-modal', 'true');
      sloj.hidden = true;
      sloj.innerHTML =
        '<button class="svetlo-zatvori" aria-label="Close">&times;</button>' +
        '<button class="svetlo-nazad" aria-label="Previous">&#8249;</button>' +
        '<img alt="">' +
        '<button class="svetlo-napred" aria-label="Next">&#8250;</button>';
      document.body.appendChild(sloj);

      var slikaEl = $('img', sloj);
      var trenutni = 0;
      var vratiFokus = null;

      function prikazi(i) {
        trenutni = (i + slike.length) % slike.length;
        var a = slike[trenutni];
        slikaEl.src = a.getAttribute('data-puna');
        slikaEl.alt = a.getAttribute('data-opis') || '';
      }

      function otvoriSvetlo(i, izvor) {
        vratiFokus = izvor;
        prikazi(i);
        sloj.hidden = false;
        document.body.style.overflow = 'hidden';
        $('.svetlo-zatvori', sloj).focus();
      }

      function zatvoriSvetlo() {
        sloj.hidden = true;
        document.body.style.overflow = '';
        if (vratiFokus) vratiFokus.focus();
      }

      slike.forEach(function (a, i) {
        a.addEventListener('click', function (e) { e.preventDefault(); otvoriSvetlo(i, a); });
      });

      $('.svetlo-zatvori', sloj).addEventListener('click', zatvoriSvetlo);
      $('.svetlo-nazad', sloj).addEventListener('click', function () { prikazi(trenutni - 1); });
      $('.svetlo-napred', sloj).addEventListener('click', function () { prikazi(trenutni + 1); });
      sloj.addEventListener('click', function (e) { if (e.target === sloj) zatvoriSvetlo(); });

      document.addEventListener('keydown', function (e) {
        if (sloj.hidden) return;
        if (e.key === 'Escape') zatvoriSvetlo();
        if (e.key === 'ArrowLeft') prikazi(trenutni - 1);
        if (e.key === 'ArrowRight') prikazi(trenutni + 1);
      });
    }
  }

  /* Prime everything that depends on scroll position on first paint. */
  requestAnimationFrame(okini);
})();
