/* paras.dev: site behaviour (no dependencies). Everything here degrades to plain HTML if it fails. */
(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var root = document.documentElement;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia && matchMedia('(pointer: fine)').matches;
  var canMove = finePointer && !reduce;

  /* ------------------------------------------------ top navigation (mobile) */
  var links = $('#sidenav'), burger = $('#burger'), topbar = $('#topbar');
  function setMenu(open) {
    links.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    burger.firstElementChild.className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
  }
  burger.addEventListener('click', function () { setMenu(!links.classList.contains('open')); });
  $$('.nav-list a, .nav-cta', topbar).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && links.classList.contains('open')) { setMenu(false); burger.focus(); }
  });
  document.addEventListener('click', function (e) {
    if (links.classList.contains('open') && !e.target.closest('#topbar')) setMenu(false);
  });
  window.addEventListener('resize', function () { if (window.innerWidth >= 1050) setMenu(false); });

  /* -------------------------------------------- scroll progress, spy, words */
  var bar = $('#progress'), toTop = $('#toTop');
  var navLinks = $$('.nav-list a', links);
  var sections = navLinks.map(function (a) { return $(a.getAttribute('href')); });
  var stmt = $('#stmt'), words = [], wordsOn = 0;
  if (stmt && !reduce) {
    var raw = stmt.textContent.trim().split(/\s+/);
    stmt.textContent = '';
    raw.forEach(function (w, i) {
      var s = document.createElement('span');
      s.className = 'w';
      s.textContent = w;
      stmt.appendChild(s);
      if (i < raw.length - 1) stmt.appendChild(document.createTextNode(' '));
      words.push(s);
    });
  }

  var ticking = false;
  function onScroll() {
    ticking = false;
    var st = window.pageYOffset || root.scrollTop, h = root.scrollHeight - window.innerHeight;
    bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, st / h) : 0) + ')';
    toTop.classList.toggle('show', st > 600);
    topbar.classList.toggle('scrolled', st > 12);

    var cur = -1;
    // the section whose top is nearest the reading line (sections are not in nav order)
    var best = -Infinity;
    sections.forEach(function (s, i) {
      if (!s) return;
      var t = s.getBoundingClientRect().top;
      if (t <= window.innerHeight * 0.4 && t > best) { best = t; cur = i; }
    });
    if (h > 0 && st >= h - 4) cur = sections.length - 1;
    navLinks.forEach(function (l, i) {
      if (i === cur) l.setAttribute('aria-current', 'true'); else l.removeAttribute('aria-current');
    });

    // statement: words light up as the paragraph passes the reading line
    if (words.length && stmt) {
      var r = stmt.getBoundingClientRect();
      var p = (window.innerHeight * 0.8 - r.top) / (r.height + window.innerHeight * 0.4);
      p = Math.max(0, Math.min(1, p));
      var n = Math.round(p * words.length);
      if (n !== wordsOn) {
        for (var i = 0; i < words.length; i++) words[i].classList.toggle('on', i < n);
        wordsOn = n;
      }
    }
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();
  toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });

  // reveal on scroll (CSS path; GSAP takes over below when it loads)
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    $$('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    $$('.reveal').forEach(function (el) { el.classList.add('in'); });
  }

  document.addEventListener('visibilitychange', function () { root.classList.toggle('paused', document.hidden); });
  var yr = $('#year'); if (yr) yr.textContent = new Date().getFullYear();

  /* ------------------------------------------------------------- hero tabs */
  var tabs = $$('.tab');
  function selectTab(t) {
    tabs.forEach(function (x) {
      var on = x === t;
      x.setAttribute('aria-selected', on ? 'true' : 'false');
      x.tabIndex = on ? 0 : -1;
      $('#' + x.getAttribute('aria-controls')).hidden = !on;
    });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { selectTab(t); });
    t.addEventListener('keydown', function (e) {
      var n = null;
      if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
      if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
      if (n) { e.preventDefault(); selectTab(n); n.focus(); }
    });
  });

  /* -------------------------------------------------------------- terminal */
  var out = $('#termOut'), form = $('#termForm'), input = $('#termIn');
  var history = [], hIdx = 0;

  function line(text, cls) {
    var d = document.createElement('span');
    d.className = 'ln' + (cls ? ' ' + cls : '');
    d.textContent = text;
    out.appendChild(d);
  }
  function lines(arr, cls) { arr.forEach(function (t) { line(t, cls); }); }

  var COMMANDS = {
    help: function () {
      lines(['Available commands:',
        '  whoami           who I am',
        '  skills           what I work with',
        '  projects         my projects and their status',
        '  aura endpoints   Aura SIS API routes',
        '  aura getall      sample JSON shape from /getall/',
        '  status           availability',
        '  contact          how to reach me',
        '  clear            clear the screen']);
    },
    whoami: function () {
      lines(['Paras Patadiya', 'Python Backend Developer · Rajkot, Gujarat, India', 'B.Com (expected 2027) · Python backend training at TOPS Technologies']);
    },
    skills: function () {
      lines(['backend   : Python, Django, Django REST Framework, REST APIs',
        'database  : PostgreSQL, database fundamentals',
        'frontend  : HTML, CSS, JavaScript',
        'tools     : Git, GitHub, VS Code, API testing tools',
        'exploring : Docker, Redis, JWT auth, cloud deployment']);
    },
    projects: function () {
      lines(['[live]         Aura SIS: Django + DRF student system and API',
        '[in progress] Doctor–Patient Management System',
        '[complete]    paras.dev portfolio (this site)',
        '[upcoming]    next backend project, still in planning']);
    },
    'aura endpoints': function () {
      lines(['GET    /getall/          ?search= &course=',
        'GET    /getid/<id>/',
        'POST   /addstudent/',
        'PUT    /updateid/<id>/',
        'DELETE /deleteid/<id>/',
        'GET    /getcourse/',
        'POST   /addcourse/',
        'GET    /api/stats/']);
    },
    'aura getall': function () {
      lines(['$ curl -H "Accept: application/json" <aura-sis>/getall/', '[', '  {',
        '    "id": 1,', '    "full_name": "Sample Student",', '    "email": "student@example.com",',
        '    "phone": "…", "age": 21, "gender": "…", "city": "…", "address": "…",',
        '    "course": 1,', '    "course_details": { "course_name": "…", "course_fees": …, "student_count": … }',
        '  }', ']']);
      line('# sample shape only: field names come from serializer.py, values are placeholders', 'cmd');
    },
    status: function () { line('Open to relevant Python backend opportunities.', 'ok'); },
    contact: function () { lines(['email  : paraspatadiya6@gmail.com', 'github : github.com/paraspatadiya1', 'or use the contact form below.']); }
  };

  function run(raw) {
    var cmd = raw.trim().toLowerCase().replace(/\s+/g, ' ');
    if (!cmd) return;
    var echo = document.createElement('span');
    echo.className = 'ln cmd';
    var p = document.createElement('b'); p.textContent = 'paras@dev:~$ ';
    echo.appendChild(p); echo.appendChild(document.createTextNode(raw.trim()));
    out.appendChild(echo);
    if (cmd === 'clear') { out.textContent = ''; return; }
    if (COMMANDS[cmd]) COMMANDS[cmd]();
    else line('command not found: ' + cmd + '. Type "help".', 'hl');
    out.scrollTop = out.scrollHeight;
  }

  if (out && form) {
    lines(['Welcome. This is a small interactive terminal about me.'], 'ok');
    line('Type "help" or tap a command below.', 'cmd');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = input.value;
      if (v.trim()) { history.push(v); hIdx = history.length; }
      run(v); input.value = '';
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowUp' && history.length) { e.preventDefault(); hIdx = Math.max(0, hIdx - 1); input.value = history[hIdx]; }
      if (e.key === 'ArrowDown' && history.length) { e.preventDefault(); hIdx = Math.min(history.length, hIdx + 1); input.value = history[hIdx] || ''; }
    });
    $$('.term-chips button').forEach(function (b) {
      b.addEventListener('click', function () { run(b.getAttribute('data-cmd')); });
    });
  }

  /* ------------------------------------------- subtle 3D tilt (fine pointer) */
  if (canMove) {
    var cons = $('#console');
    if (cons) {
      cons.addEventListener('pointermove', function (e) {
        var r = cons.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        cons.style.transform = 'perspective(1100px) rotateX(' + (-y * 3).toFixed(2) + 'deg) rotateY(' + (x * 4).toFixed(2) + 'deg)';
      });
      cons.addEventListener('pointerleave', function () { cons.style.transform = ''; });
    }
    // service cards lift toward the pointer
    $$('.svc').forEach(function (el) {
      var raf = 0;
      el.addEventListener('pointermove', function (e) {
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0;
          var r = el.getBoundingClientRect();
          var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
          el.style.transform = 'perspective(900px) rotateX(' + ((0.5 - y) * 5).toFixed(2) + 'deg) rotateY(' + ((x - 0.5) * 6).toFixed(2) + 'deg) translateY(-4px)';
        });
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* ------------------------------------------------------- case-study dialogs */
  var lastTrigger = null;
  $$('[data-case]').forEach(function (b) {
    b.addEventListener('click', function () {
      var d = document.getElementById(b.getAttribute('data-case'));
      if (!d) return;
      lastTrigger = b;
      if (typeof d.showModal === 'function') d.showModal(); else d.setAttribute('open', '');
      root.style.overflow = 'hidden';
      var body = $('.case-body', d); if (body) body.scrollTop = 0;
    });
  });
  $$('dialog.case').forEach(function (d) {
    $$('[data-close]', d).forEach(function (c) {
      c.addEventListener('click', function () { if (d.close) d.close(); else d.removeAttribute('open'); });
    });
    d.addEventListener('click', function (e) { if (e.target === d && d.close) d.close(); });
    d.addEventListener('close', function () {
      root.style.overflow = '';
      if (lastTrigger) { lastTrigger.focus(); lastTrigger = null; }
    });
  });

  /* ------------------------------------------------ intro, cursor, magnetic */
  var introEl = $('#intro');
  if (introEl) {
    if (root.getAttribute('data-intro') !== 'skip') {
      try { sessionStorage.setItem('pp-intro', '1'); } catch (e) {}
      var parts = $('#introParticles');
      if (parts) {
        var pn = window.innerWidth < 720 ? 10 : 18;
        for (var pi = 0; pi < pn; pi++) {
          var sp = document.createElement('span');
          sp.style.cssText = '--s:' + (2 + Math.random() * 4).toFixed(1) + 'px;--x:' + (Math.random() * 100).toFixed(0) +
            '%;--y:' + (Math.random() * 100).toFixed(0) + '%;--dur:' + (4 + Math.random() * 4).toFixed(1) +
            's;--delay:' + (Math.random() * -4).toFixed(1) + 's';
          parts.appendChild(sp);
        }
      }
      // only the fade-out ends the intro; the root keeps intro-on so the hero's start delay stays fixed
      introEl.addEventListener('animationend', function (e) {
        if (e.target === introEl && e.animationName === 'introOut') {
          introEl.classList.add('done');
          introEl.setAttribute('aria-hidden', 'true');
        }
      });
      var skipBtn = $('#introSkip');
      if (skipBtn) skipBtn.addEventListener('click', function () {
        root.classList.remove('intro-on');   // hides the intro and starts the hero at once
        introEl.classList.add('done');
      });
    } else {
      introEl.classList.add('done');
    }
  }

  if (canMove && $('#cDot') && $('#cRing')) {
    root.classList.add('has-cursor');
    var cDot = $('#cDot'), cRing = $('#cRing');
    var mx = -100, my = -100, rx = -100, ry = -100, rafC = 0;
    var paintRing = function () {
      rx += (mx - rx) * 0.22; ry += (my - ry) * 0.22;
      cRing.style.transform = 'translate3d(' + rx.toFixed(1) + 'px,' + ry.toFixed(1) + 'px,0)';
      rafC = (Math.abs(mx - rx) > 0.3 || Math.abs(my - ry) > 0.3) ? requestAnimationFrame(paintRing) : 0;
    };
    document.addEventListener('pointermove', function (e) {
      mx = e.clientX; my = e.clientY;
      cDot.style.transform = 'translate3d(' + mx + 'px,' + my + 'px,0)';
      if (!rafC) rafC = requestAnimationFrame(paintRing);
    }, { passive: true });
    document.addEventListener('pointerover', function (e) {
      var over = e.target && e.target.closest && e.target.closest('a,button,input,textarea,.svc,.prow');
      root.classList.toggle('cursor-hover', !!over);
    }, { passive: true });
  }

  // magnetic buttons (desktop only; uses the translate property so it does not fight hover transforms)
  if (canMove) {
    $$('.btn-primary, .btn-ghost, .closing-cta').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.translate = ((e.clientX - r.left - r.width / 2) * 0.16).toFixed(1) + 'px ' +
          ((e.clientY - r.top - r.height / 2) * 0.22).toFixed(1) + 'px';
      });
      b.addEventListener('pointerleave', function () { b.style.translate = ''; });
    });
  }

  // the hero glow and the scene follow the pointer
  var heroStage = $('#heroStage');
  if (heroStage && canMove) {
    heroStage.addEventListener('pointermove', function (e) {
      var r = heroStage.getBoundingClientRect();
      heroStage.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
      heroStage.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
    }, { passive: true });
  }

  /* -------------------------------------- GSAP scroll motion (optional layer) */
  // If GSAP did not load, the CSS reveal above still works.
  if (window.gsap && window.ScrollTrigger && !reduce) {
    try {
      gsap.registerPlugin(ScrollTrigger);
      root.classList.add('gsap-on');
      $$('.reveal').forEach(function (el) { el.classList.remove('reveal'); });

      // headings reveal word by word, like the line-split titles in the reference video
      $$('.sec-title').forEach(function (h) {
        h.innerHTML = h.textContent.trim().split(/\s+/).map(function (w) {
          return '<span class="wd"><span>' + w + '</span></span>';
        }).join(' ');
        gsap.from(h.querySelectorAll('.wd > span'), {
          yPercent: 110, duration: 0.9, ease: 'power4.out', stagger: 0.05,
          scrollTrigger: { trigger: h, start: 'top 88%', once: true }
        });
      });

      // 3D entrances for each group, staggered as it reaches the viewport
      [
        ['.svc', { y: 70, rotationX: 14, opacity: 0, duration: 1 }],
        ['.prow', { y: 40, opacity: 0 }],
        ['.pillar', { y: 50, rotationX: 10, opacity: 0 }],
        ['.tl', { x: -40, rotationY: 12, opacity: 0 }],
        ['.cert', { y: 50, rotationX: 14, opacity: 0 }],
        ['.faq details', { x: -30, opacity: 0 }],
        ['.contact', { y: 60, rotationY: -10, opacity: 0, duration: 1.2 }]
      ].forEach(function (g) {
        ScrollTrigger.batch(g[0], {
          start: 'top 88%', once: true,
          onEnter: function (els) {
            gsap.from(els, Object.assign({
              transformPerspective: 1100, duration: 1, ease: 'power3.out', stagger: 0.12, clearProps: 'transform,opacity'
            }, g[1]));
          }
        });
      });

      // the flagship card rises and tilts in once
      var flag = $('.flagship');
      if (flag) gsap.from(flag, {
        y: 70, rotationX: 12, opacity: 0, duration: 1.1, ease: 'power3.out', transformPerspective: 1100,
        scrollTrigger: { trigger: flag, start: 'top 88%', once: true }
      });

      // timeline rail draws as you scroll through the experience
      var rail = $('.tl-rail');
      if (rail) gsap.from(rail, {
        scaleY: 0, ease: 'none',
        scrollTrigger: { trigger: '.timeline', start: 'top 80%', end: 'bottom 70%', scrub: 0.5 }
      });

      // decorative shapes move at different speeds (parallax)
      $$('[data-speed]').forEach(function (el) {
        var s = parseFloat(el.getAttribute('data-speed')) || 0;
        gsap.fromTo(el, { y: 0 }, {
          y: -s * 220, ease: 'none',
          scrollTrigger: { trigger: document.body, start: 'top top', end: 'bottom bottom', scrub: true }
        });
      });

      window.addEventListener('load', function () { ScrollTrigger.refresh(); });
    } catch (err) {
      root.classList.remove('gsap-on');
    }
  }

  /* ---------------------------------------------------------------- contact */
  var cForm = $('#contactForm');
  if (cForm) {
    var fields = {
      name: { el: $('#fName'), err: $('#eName'), msg: 'Please enter your name.' },
      email: { el: $('#fEmail'), err: $('#eEmail'), msg: 'Please enter a valid email address.' },
      subject: { el: $('#fSubject'), err: $('#eSubject'), msg: 'Please add a subject.' },
      message: { el: $('#fMsg'), err: $('#eMsg'), msg: 'Please write a message.' }
    };
    var submit = $('#fSubmit'), statusEl = $('#formStatus'), deliver = $('#deliverBox');

    function showStatus(text, kind) {
      statusEl.textContent = text;
      statusEl.className = 'form-status ' + (kind || '');
      statusEl.hidden = false;
    }
    function getCsrf() {
      var t = cForm.querySelector('[name=csrfmiddlewaretoken]');
      if (t && t.value) return t.value;
      var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
      return m ? decodeURIComponent(m[1]) : '';
    }
    function validate() {
      var firstBad = null;
      Object.keys(fields).forEach(function (k) {
        var f = fields[k], v = f.el.value.trim(), ok = !!v;
        if (k === 'email') ok = ok && f.el.checkValidity();
        f.el.setAttribute('aria-invalid', ok ? 'false' : 'true');
        f.err.textContent = ok ? '' : f.msg;
        if (!ok && !firstBad) firstBad = f.el;
      });
      if (firstBad) firstBad.focus();
      return !firstBad;
    }
    Object.keys(fields).forEach(function (k) {
      fields[k].el.addEventListener('input', function () {
        fields[k].el.setAttribute('aria-invalid', 'false');
        fields[k].err.textContent = '';
      });
    });

    cForm.addEventListener('submit', function (e) {
      e.preventDefault();
      statusEl.hidden = true;
      if (!validate()) return;

      var label = $('span', submit), orig = label.textContent;
      submit.disabled = true; label.textContent = 'Sending…';

      var payload = {
        name: fields.name.el.value.trim(), email: fields.email.el.value.trim(),
        subject: fields.subject.el.value.trim(), message: fields.message.el.value.trim()
      };

      fetch(cForm.getAttribute('action'), {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'X-CSRFToken': getCsrf() },
        body: JSON.stringify(payload)
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (data) { return { res: res, data: data }; });
      }).then(function (r) {
        var st = r.data && r.data.status;
        if (r.res.ok && (st === 'ok' || st === 'saved')) {
          // 'saved' = stored in the database but the email step failed (see contact_submit view)
          $('#deliverText').textContent = st === 'ok'
            ? 'Thanks, ' + payload.name + '! Your message was sent and a confirmation is on its way to your inbox.'
            : 'Thanks, ' + payload.name + '! Your message was saved, but the confirmation email could not be sent. I still have your message.';
          cForm.style.display = 'none';
          deliver.classList.add('show');
          cForm.reset();
          $('#sendAnother').focus();
        } else {
          showStatus((r.data && r.data.message) || 'Something went wrong. Please try again, or email me directly.', 'bad');
        }
      }).catch(function () {
        showStatus('Could not reach the server. Please check your connection or email me directly.', 'bad');
      }).then(function () {
        submit.disabled = false; label.textContent = orig;
      });
    });

    $('#sendAnother').addEventListener('click', function () {
      deliver.classList.remove('show');
      cForm.style.display = '';
      fields.name.el.focus();
    });

    var copy = $('#copyEmail');
    if (copy) copy.addEventListener('click', function () {
      var addr = $('#emailLink').textContent.trim();
      var done = function () { copy.textContent = 'Copied'; setTimeout(function () { copy.textContent = 'Copy'; }, 1800); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(addr).then(done, function () { copy.textContent = 'Press Ctrl+C'; });
      } else {
        var r = document.createRange(); r.selectNodeContents($('#emailLink'));
        var s = getSelection(); s.removeAllRanges(); s.addRange(r);
        copy.textContent = 'Press Ctrl+C';
      }
    });
  }
})();
