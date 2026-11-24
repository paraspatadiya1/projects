/* paras.dev: hero 3D backend scene.
   Three.js is loaded lazily, only when the hero stage is near the viewport.
   The render loop pauses when the stage is off-screen or the tab is hidden.
   If WebGL or the library is unavailable, the CSS fallback diagram is shown. */
(function () {
  'use strict';

  var canvas = document.getElementById('heroCanvas');
  var stage = document.getElementById('heroStage');
  if (!canvas || !stage) return;

  var THREE_URL = 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  var S = {
    THREE: null, renderer: null, scene: null, camera: null, root: null,
    col: null, paint: [], geos: [], mats: [], packets: [],
    zero: null, t0: 0, raf: 0, visible: false, started: false, dead: false,
    px: 0, py: 0, tx: 0, ty: 0
  };

  function webgl() {
    try {
      var c = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
    } catch (e) { return false; }
  }

  function cssVar(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  // Colours come from the active theme, so the scene follows the theme selector
  function refreshColors() {
    if (!S.col) return;
    S.col.brand.set(cssVar('--brand', '#7aa2ff'));
    S.col.accent.set(cssVar('--accent', '#f3b562'));
    S.col.info.set(cssVar('--info', '#7aa2ff'));
    S.paint.forEach(function (p) { p.m.color.copy(S.col[p.k]); });
  }

  function fallback() {
    S.dead = true;
    stage.classList.add('no-webgl');
  }

  function resize() {
    if (!S.renderer) return;
    var w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    S.renderer.setSize(w, h, false);
    S.camera.aspect = w / h;
    S.camera.updateProjectionMatrix();
    if (reduce) render(performance.now());
  }

  function render(now) {
    var t = (now - S.t0) / 1000;
    var root = S.root;

    // eased pointer parallax (mouse only; touch keeps native scrolling)
    S.px += (S.tx - S.px) * 0.05;
    S.py += (S.ty - S.py) * 0.05;
    root.rotation.y = Math.sin(t * 0.25) * 0.12 + S.px * 0.35;
    root.rotation.x = Math.sin(t * 0.18) * 0.05 + S.py * 0.2;
    root.position.y = Math.sin(t * 0.7) * 0.08;

    S.db.rotation.y = t * 0.3;
    S.stack.rotation.y = -t * 0.2;
    S.core.scale.setScalar(1 + Math.sin(t * 2) * 0.08);
    S.orbit1.rotation.z = t * 0.12;
    S.orbit2.rotation.z = -t * 0.08;

    // data packets travel hub -> target and loop, fading at each end
    S.packets.forEach(function (p) {
      var k = (t * 0.22 + p.off) % 1;
      p.mesh.position.lerpVectors(S.zero, p.to, k);
      p.mesh.material.opacity = Math.sin(k * Math.PI);
    });

    S.renderer.render(S.scene, S.camera);
  }

  function loop(now) {
    S.raf = 0;
    if (!S.visible || document.hidden || S.dead) return;
    render(now);
    S.raf = requestAnimationFrame(loop);
  }

  function kick() {
    if (!S.raf && S.visible && !document.hidden && !S.dead && S.renderer && !reduce) {
      S.raf = requestAnimationFrame(loop);
    }
  }

  function build(THREE) {
    S.THREE = THREE;
    var mobile = window.innerWidth < 720;

    var renderer = new THREE.WebGLRenderer({
      canvas: canvas, antialias: !mobile, alpha: true, powerPreference: 'low-power'
    });
    // cap pixel ratio on high-density displays
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.setClearColor(0x000000, 0);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
    camera.position.set(0, 0.2, 10.5);
    var root = new THREE.Group();
    scene.add(root);

    S.col = { brand: new THREE.Color(), accent: new THREE.Color(), info: new THREE.Color() };
    S.zero = new THREE.Vector3();

    // Wireframe and basic materials keep the scene cheap: no lights are needed
    function paintMat(key, opacity, wire) {
      var m = new THREE.MeshBasicMaterial({
        color: 0xffffff, wireframe: !!wire, transparent: true, opacity: opacity, depthWrite: false
      });
      S.paint.push({ m: m, k: key });
      S.mats.push(m);
      return m;
    }
    function shape(geo, key, opacity) {
      S.geos.push(geo);
      return new THREE.Mesh(geo, paintMat(key, opacity, true));
    }

    // Database cylinder with rings
    var db = new THREE.Group();
    db.position.set(-3.1, -0.1, 0);
    db.add(shape(new THREE.CylinderGeometry(0.85, 0.85, 1.6, 32, 2, true), 'brand', 0.55));
    [-0.8, 0.8].forEach(function (y) {
      var ring = shape(new THREE.TorusGeometry(0.85, 0.012, 6, 48), 'brand', 0.8);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = y;
      db.add(ring);
    });
    root.add(db);

    // Server stack
    var stack = new THREE.Group();
    stack.position.set(3.3, 0.1, 0);
    [0.95, 0.35, -0.25].forEach(function (y, i) {
      var box = shape(new THREE.BoxGeometry(1.5, 0.42, 1.0), i === 1 ? 'accent' : 'info', 0.6);
      box.position.set(0, y, 0);
      stack.add(box);
    });
    root.add(stack);

    // API hub at the centre
    var hub = new THREE.Group();
    hub.add(shape(new THREE.IcosahedronGeometry(0.55, 1), 'accent', 0.5));
    var coreGeo = new THREE.SphereGeometry(0.24, 20, 14);
    S.geos.push(coreGeo);
    var core = new THREE.Mesh(coreGeo, paintMat('accent', 0.9, false));
    hub.add(core);
    root.add(hub);

    // API nodes around the hub
    var layout = [[-1.2, 2.4], [1.4, 2.5], [3.8, 1.5], [-3.9, 1.6], [-0.9, -2.3], [2.9, -2.0]];
    var count = mobile ? 4 : layout.length;
    var targets = [];
    for (var i = 0; i < count; i++) {
      var node = shape(new THREE.IcosahedronGeometry(0.22, 0), 'accent', 0.9);
      node.position.set(layout[i][0], layout[i][1], 0);
      root.add(node);
      targets.push(node.position);
    }
    targets.push(db.position, stack.position);

    // Connection lines from the hub to every target
    var pts = [];
    targets.forEach(function (p) { pts.push(0, 0, 0, p.x, p.y, p.z); });
    var lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    var lineMat = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35 });
    S.paint.push({ m: lineMat, k: 'brand' });
    S.geos.push(lineGeo);
    S.mats.push(lineMat);
    root.add(new THREE.LineSegments(lineGeo, lineMat));

    // Animated request packets
    var packetCount = mobile ? 3 : 6;
    var packetGeo = new THREE.SphereGeometry(0.075, 8, 6);
    S.geos.push(packetGeo);
    for (var p = 0; p < packetCount; p++) {
      var pk = new THREE.Mesh(packetGeo, paintMat('accent', 1, false));
      pk.material.wireframe = false;
      root.add(pk);
      S.packets.push({ mesh: pk, to: targets[p % targets.length], off: p / packetCount });
    }

    // Two slow orbit rings
    S.orbit1 = shape(new THREE.TorusGeometry(5.1, 0.01, 4, 140), 'info', 0.25);
    S.orbit1.rotation.set(1.1, 0.2, 0.3);
    S.orbit2 = shape(new THREE.TorusGeometry(6.4, 0.01, 4, 160), 'brand', 0.18);
    S.orbit2.rotation.set(0.3, 0.7, 1.2);
    root.add(S.orbit1, S.orbit2);

    // Ambient particles
    var pCount = mobile ? 60 : 160;
    var pos = new Float32Array(pCount * 3);
    for (var j = 0; j < pos.length; j++) pos[j] = (Math.random() - 0.5) * 12;
    var pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    var pMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.05, transparent: true, opacity: 0.7, depthWrite: false });
    S.paint.push({ m: pMat, k: 'info' });
    S.geos.push(pGeo);
    S.mats.push(pMat);
    root.add(new THREE.Points(pGeo, pMat));

    S.renderer = renderer;
    S.scene = scene;
    S.camera = camera;
    S.root = root;
    S.db = db;
    S.stack = stack;
    S.core = core;

    refreshColors();
    resize();

    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); fallback(); });
    if ('ResizeObserver' in window) new ResizeObserver(resize).observe(canvas);
    else window.addEventListener('resize', resize);

    // Pause off-screen: track whether the canvas is in view
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        S.visible = entries[0].isIntersecting;
        if (S.visible) kick();
      }).observe(canvas);
    } else {
      S.visible = true;
    }
  }

  function start() {
    if (S.started) return;
    S.started = true;
    if (!webgl()) return fallback();
    import(THREE_URL).then(function (THREE) {
      try { build(THREE); } catch (e) { fallback(); return; }
      S.t0 = performance.now();
      S.visible = true;
      if (reduce) render(S.t0); // one static frame for reduced-motion users
      else kick();
    }).catch(fallback); // CDN blocked or offline: keep the CSS fallback
  }

  // Lazy start: begin loading only when the stage is near the viewport
  if ('IntersectionObserver' in window) {
    var lazy = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { lazy.disconnect(); start(); }
    }, { rootMargin: '200px' });
    lazy.observe(stage);
  } else {
    start();
  }

  stage.addEventListener('pointermove', function (e) {
    if (e.pointerType !== 'mouse') return;
    var r = stage.getBoundingClientRect();
    S.tx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    S.ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
  }, { passive: true });
  stage.addEventListener('pointerleave', function () { S.tx = 0; S.ty = 0; });

  document.addEventListener('visibilitychange', kick);
  document.addEventListener('pp-theme-change', function () {
    refreshColors();
    if (S.renderer && reduce) render(performance.now());
  });

  window.addEventListener('pagehide', function () {
    if (!S.renderer) return;
    S.geos.forEach(function (g) { g.dispose(); });
    S.mats.forEach(function (m) { m.dispose(); });
    S.renderer.dispose();
  });
})();
