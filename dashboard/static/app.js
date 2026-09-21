'use strict';

// ═══════════════════════════════════════════════════
// APEX GHOST — NEURAL ENGINE v4.2.1
// ═══════════════════════════════════════════════════

// ── GLOBAL STATE ──
let focusActive = false;
let lastLogIdx  = 0;
let allQuests   = [];
let activeFilter = 'ALL';
let builderGoals = [];
let prevLevel = 1;
let audioCtx  = null;

// Canvas animation state
let bgScene, bgCamera, bgRenderer, bgUniforms;
let avScene, avCamera, avRenderer;
let avParticles, avParticlePos;
let runeAngle = 0;
let miniRuneAngle = 0;
let dataStreamCtx, dataStreamCols = [];

// XP animation
let xpDisplayed = 0, xpTarget = 0, xpMax = 1000;
let xpShimmerX = -1, shimmerDir = 1;

// Radar animation
let radarDisplayed = [0,0,0,0,0];
let radarTarget    = [30,40,25,20,35];
const RADAR_LABELS = ['Physical','Mental','Financial','Spiritual','Emotional'];
const RADAR_COLORS = ['#ff6b6b','#4ecdc4','#FFD700','#a8e6cf','#EE82EE'];

// Stat arcs animation
let attrDisplayed = { str:0, int:0, agi:0, dis:0 };
let attrTarget    = { str:10, int:10, agi:10, dis:10 };

// Mouse tracking
let mouseX = 0.5, mouseY = 0.5;

// ═══════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════
window.addEventListener('DOMContentLoaded', () => {
    initBgShader();
    initAvatarCanvas();
    initDataStream();
    runBootSequence().then(() => {
        startLiveData();
        requestAnimationFrame(masterLoop);
        initControlCenter();
        initMouseGlow();
        initClock();
        renderCalendar();
        initNavButtons();
    });
});

async function runBootSequence() {
    const lines = [
        '> APEX GHOST NEURAL OS v4.2.1...',
        '> Loading cognitive modules...',
        '> Syncing memory stack...',
        '> Authenticating hunter profile...',
        '> Neural interface established.',
        '> SYSTEM ONLINE.',
    ];
    const container = document.getElementById('boot-lines');
    const bar = document.getElementById('boot-progress');

    for (let i = 0; i < lines.length; i++) {
        await typeBootLine(container, lines[i], 22);
        bar.style.width = `${((i + 1) / lines.length) * 100}%`;
        await delay(120);
    }
    await delay(500);
    const overlay = document.getElementById('boot-overlay');
    overlay.classList.add('fade-out');
    await delay(900);
    overlay.style.display = 'none';
    playUISound('boot');
}

function typeBootLine(container, text, speed) {
    return new Promise(resolve => {
        const div = document.createElement('div');
        div.className = 'boot-line boot-cursor';
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        let i = 0;
        const t = setInterval(() => {
            div.textContent = text.slice(0, ++i);
            if (i >= text.length) {
                clearInterval(t);
                div.classList.remove('boot-cursor');
                resolve();
            }
        }, speed);
    });
}

const delay = ms => new Promise(r => setTimeout(r, ms));

// ═══════════════════════════════════════════════════
// MASTER 60 FPS LOOP
// ═══════════════════════════════════════════════════
let lastTs = 0;
function masterLoop(ts) {
    const dt = Math.min(ts - lastTs, 50);
    lastTs = ts;

    updateBgShader(ts);
    updateAvatarCanvas(ts);
    updateRuneRing(ts);
    updateMiniRuneRing(ts);
    updateDataStream(ts);
    animXP(dt);
    animRadar(dt);
    animStatArcs(dt);

    requestAnimationFrame(masterLoop);
}

// ═══════════════════════════════════════════════════
// BACKGROUND — SWIRLING VOID PORTAL (Three.js WebGL)
// ═══════════════════════════════════════════════════
function initBgShader() {
    const canvas = document.getElementById('bg-canvas');
    bgRenderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false });
    bgRenderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    resizeBgRenderer();

    bgScene  = new THREE.Scene();
    bgCamera = new THREE.OrthographicCamera(-1,1,1,-1,0,1);

    bgUniforms = {
        time:       { value: 0 },
        resolution: { value: new THREE.Vector2(innerWidth, innerHeight) },
        mouse:      { value: new THREE.Vector2(0.5, 0.5) }
    };

    const frag = `
        precision mediump float;
        uniform float time;
        uniform vec2 resolution;
        uniform vec2 mouse;
        varying vec2 vUv;

        float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5); }
        float noise(vec2 p) {
            vec2 i = floor(p), f = fract(p);
            f = f*f*(3.0-2.0*f);
            return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),
                       mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
        }

        void main() {
            vec2 uv = vUv;
            vec2 center = vec2(0.5) + (mouse - 0.5) * 0.08;
            vec2 p = uv - center;
            float dist = length(p);
            float angle = atan(p.y, p.x);
            float t = time * 0.12;

            // Swirling vortex
            float swirl = angle + dist * 4.0 - t * 1.5;
            float vortex = sin(swirl * 4.0) * 0.5 + 0.5;
            vortex *= 1.0 - smoothstep(0.0, 0.7, dist);

            // Nebula noise
            float n1 = noise(uv * 3.0 + vec2(t, t * 0.6)) * 0.6;
            float n2 = noise(uv * 6.0 + vec2(-t * 1.2, t * 0.4)) * 0.4;
            float nebula = (n1 + n2) * (1.0 - smoothstep(0.2, 0.9, dist));

            vec3 base    = vec3(0.012, 0.0, 0.027);
            vec3 vortexC = vec3(0.34, 0.0, 0.66) * vortex * 0.55;
            vec3 nebulaC = vec3(0.10, 0.0, 0.25) * nebula * 0.5;
            vec3 iceCore = vec3(0.0, 0.38, 0.5) * (1.0 - smoothstep(0.0, 0.25, dist)) * 0.12;

            // Subtle grid
            vec2 grid = fract(uv * 28.0);
            float gLine = max(step(0.97, grid.x), step(0.97, grid.y));
            vec3 gridC = vec3(0.13, 0.0, 0.26) * gLine * 0.25;

            vec3 col = base + vortexC + nebulaC + iceCore + gridC;
            float vignette = 1.0 - smoothstep(0.35, 1.1, dist * 1.2);
            col *= vignette;

            gl_FragColor = vec4(col, 1.0);
        }
    `;
    const vert = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position,1.0); }`;
    const geo = new THREE.PlaneGeometry(2,2);
    const mat = new THREE.ShaderMaterial({ uniforms: bgUniforms, vertexShader: vert, fragmentShader: frag });
    bgScene.add(new THREE.Mesh(geo, mat));

    window.addEventListener('resize', resizeBgRenderer);
}

function resizeBgRenderer() {
    if (!bgRenderer) return;
    bgRenderer.setSize(innerWidth, innerHeight);
    if (bgUniforms) bgUniforms.resolution.value.set(innerWidth, innerHeight);
}

function updateBgShader(ts) {
    if (!bgRenderer) return;
    bgUniforms.time.value = ts * 0.001;
    bgUniforms.mouse.value.set(mouseX, mouseY);
    bgRenderer.render(bgScene, bgCamera);
}

// ═══════════════════════════════════════════════════
// AVATAR (Three.js — hologram + particles + rune)
// ═══════════════════════════════════════════════════
function initAvatarCanvas() {
    const canvas = document.getElementById('avatar-canvas');
    if (!canvas) return;

    avRenderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    avRenderer.setClearColor(0x000000, 0);
    avRenderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    const W = canvas.clientWidth || 290, H = canvas.clientHeight || 400;
    avRenderer.setSize(W, H);

    avScene  = new THREE.Scene();
    avCamera = new THREE.PerspectiveCamera(55, W/H, 0.1, 100);
    avCamera.position.set(0, 0.2, 4);

    // Hologram plane — character display
    const vShad = `
        uniform float time;
        varying vec2 vUv;
        varying float vEdge;
        void main() {
            vUv = uv;
            vec3 pos = position;
            pos.z += sin(pos.x * 5.0 + time) * 0.025 + sin(pos.y * 8.0 + time*1.3) * 0.018;
            vEdge = pow(abs(uv.x - 0.5) * 2.0, 3.0);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
    `;
    const fShad = `
        uniform float time;
        uniform float focusBoost;
        varying vec2 vUv;
        varying float vEdge;
        void main() {
            float pulse = sin(time * 2.0) * 0.5 + 0.5;
            float scanY  = mod(vUv.y * 60.0 + time * 4.0, 1.0);
            float scan   = step(0.92, scanY) * 0.12;
            float flicker = sin(time * 30.0) * 0.02;
            float holo    = vEdge * (0.7 + pulse * 0.3) + 0.06 + scan + flicker;
            vec3 evColor  = vec3(0.54, 0.0, 1.0);
            vec3 iceColor = vec3(0.0, 0.96, 1.0);
            vec3 col = mix(evColor, iceColor, vEdge * 0.4) * (vEdge * 1.6 + 0.25);
            col += evColor * pulse * (0.25 + focusBoost * 0.4);
            gl_FragColor = vec4(col, holo * (0.75 + focusBoost * 0.2));
        }
    `;
    const planeGeo = new THREE.PlaneGeometry(2.6, 3.8, 40, 60);
    const planeMat = new THREE.ShaderMaterial({
        uniforms: { time: {value:0}, focusBoost: {value:0} },
        vertexShader: vShad, fragmentShader: fShad,
        transparent: true, side: THREE.DoubleSide, depthWrite: false
    });
    const holoMesh = new THREE.Mesh(planeGeo, planeMat);
    holoMesh.name = 'holo';
    holoMesh.position.y = 0.15;
    avScene.add(holoMesh);

    // Rune rings
    const mkTorus = (r, tube, col, opacity) => {
        const m = new THREE.Mesh(
            new THREE.TorusGeometry(r, tube, 8, 80),
            new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity })
        );
        avScene.add(m); return m;
    };
    mkTorus(1.5, 0.018, 0x8B00FF, 0.75).name = 'ring1';
    mkTorus(1.15, 0.01, 0x00F5FF, 0.45).name = 'ring2';
    mkTorus(0.85, 0.008, 0x8B00FF, 0.3).name = 'ring3';

    // Particles
    const N = 180;
    avParticlePos = new Float32Array(N * 3);
    const pColors = new Float32Array(N * 3), pVels = [];
    for (let i = 0; i < N; i++) {
        const a = Math.random() * Math.PI * 2;
        const r = 0.7 + Math.random() * 1.1;
        avParticlePos[i*3]   = Math.cos(a) * r;
        avParticlePos[i*3+1] = (Math.random() - 0.5) * 4.0;
        avParticlePos[i*3+2] = Math.sin(a) * r;
        const c = new THREE.Color().setHSL(0.76 + (Math.random()-0.5)*0.08, 1, 0.62);
        pColors[i*3]=c.r; pColors[i*3+1]=c.g; pColors[i*3+2]=c.b;
        pVels.push({ vy: 0.004 + Math.random()*0.007, vx: (Math.random()-0.5)*0.002 });
    }
    const pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(avParticlePos, 3));
    pGeo.setAttribute('color', new THREE.BufferAttribute(pColors, 3));
    avParticles = new THREE.Points(pGeo, new THREE.PointsMaterial({ size: 0.05, vertexColors: true, transparent: true, opacity: 0.9, depthWrite: false }));
    avParticles._vels = pVels;
    avScene.add(avParticles);

    canvas.addEventListener('mouseenter', () => { const h = avScene.getObjectByName('holo'); if(h) h.material.uniforms.focusBoost.value = 0.6; });
    canvas.addEventListener('mouseleave', () => { const h = avScene.getObjectByName('holo'); if(h) h.material.uniforms.focusBoost.value = focusActive ? 0.4 : 0; });
}

function updateAvatarCanvas(ts) {
    if (!avRenderer) return;
    const t = ts * 0.001;

    const holo = avScene.getObjectByName('holo');
    if (holo) { holo.material.uniforms.time.value = t; holo.material.uniforms.focusBoost.value = focusActive ? 0.45 : 0; }

    const r1 = avScene.getObjectByName('ring1'); if(r1) r1.rotation.z += 0.004;
    const r2 = avScene.getObjectByName('ring2'); if(r2) { r2.rotation.z -= 0.006; r2.rotation.x = Math.sin(t*0.4)*0.3; }
    const r3 = avScene.getObjectByName('ring3'); if(r3) r3.rotation.y += 0.008;

    if (avParticles) {
        for (let i = 0; i < avParticles._vels.length; i++) {
            avParticlePos[i*3+1] += avParticles._vels[i].vy;
            avParticlePos[i*3]   += avParticles._vels[i].vx;
            if (avParticlePos[i*3+1] > 2.2) {
                avParticlePos[i*3+1] = -2.2;
                const a = Math.random()*Math.PI*2, r = 0.7+Math.random()*1.1;
                avParticlePos[i*3] = Math.cos(a)*r;
                avParticlePos[i*3+2] = Math.sin(a)*r;
            }
        }
        avParticles.geometry.attributes.position.needsUpdate = true;
    }

    // Parallax from mouse
    avCamera.position.x = (mouseX - 0.5) * 0.4;
    avCamera.position.y = (mouseY - 0.5) * -0.2 + 0.2;
    avCamera.lookAt(0, 0.1, 0);

    avRenderer.render(avScene, avCamera);
}

// ═══════════════════════════════════════════════════
// RUNE RING CANVAS (sidebar overlay)
// ═══════════════════════════════════════════════════
const RUNES = ['ᚠ','ᚢ','ᚦ','ᚨ','ᚱ','ᚲ','ᚷ','ᚹ','ᚺ','ᚾ','ᛁ','ᛃ','ᛇ','ᛈ'];

function updateRuneRing(ts) {
    const canvas = document.getElementById('rune-canvas');
    if (!canvas) return;
    const parent = canvas.parentElement;
    const W = parent.clientWidth * 0.8, H = parent.clientHeight * 0.8;
    if (canvas.width !== Math.round(W)) { canvas.width = Math.round(W); canvas.height = Math.round(H); }
    const ctx = canvas.getContext('2d');
    const cx = W/2, cy = H/2, r = Math.min(W,H) * 0.44;
    runeAngle += 0.003;
    ctx.clearRect(0,0,W,H);

    const pulse = Math.sin(ts * 0.0018) * 0.5 + 0.5;

    // Outer ring
    ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.strokeStyle = `rgba(139,0,255,${0.4 + pulse*0.3})`; ctx.lineWidth = 1.5; ctx.stroke();

    // Energy ring
    const grad = ctx.createLinearGradient(cx-r,cy,cx+r,cy);
    grad.addColorStop(0,'rgba(139,0,255,0)');
    grad.addColorStop(0.5,'rgba(0,245,255,0.15)');
    grad.addColorStop(1,'rgba(139,0,255,0)');
    ctx.strokeStyle = grad; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(cx,cy,r*0.88,runeAngle,runeAngle+Math.PI*0.8); ctx.stroke();

    // Inner ring
    ctx.beginPath(); ctx.arc(cx,cy,r*0.72,0,Math.PI*2);
    ctx.strokeStyle = `rgba(0,245,255,${0.15 + pulse*0.15})`; ctx.lineWidth = 0.8; ctx.stroke();

    // Rune symbols
    const fsize = Math.round(Math.min(W,H)*0.09);
    ctx.font = `${fsize}px serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    RUNES.slice(0,10).forEach((rune, i) => {
        const a = runeAngle + (i/10)*Math.PI*2;
        const rx = cx + Math.cos(a)*r*1.05, ry = cy + Math.sin(a)*r*1.05;
        const alpha = 0.35 + pulse * 0.45;
        ctx.fillStyle = `rgba(160,32,240,${alpha.toFixed(2)})`;
        ctx.fillText(rune, rx, ry);
    });
    RUNES.slice(0,6).forEach((rune,i) => {
        const a = -runeAngle * 1.5 + (i/6)*Math.PI*2;
        const rx = cx+Math.cos(a)*r*0.6, ry = cy+Math.sin(a)*r*0.6;
        ctx.fillStyle = `rgba(0,245,255,${(0.2+pulse*0.2).toFixed(2)})`;
        ctx.font = `${Math.round(fsize*0.6)}px serif`;
        ctx.fillText(rune, rx, ry);
    });
}

// ── Mini rune ring in header
function updateMiniRuneRing(ts) {
    const c = document.getElementById('rune-ring-mini');
    if (!c) return;
    const ctx = c.getContext('2d');
    const W=c.width, H=c.height, cx=W/2, cy=H/2, r=W*0.36;
    miniRuneAngle += 0.004;
    ctx.clearRect(0,0,W,H);
    const pulse = Math.sin(ts*0.002)*0.5+0.5;
    ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.strokeStyle=`rgba(139,0,255,${0.5+pulse*0.3})`; ctx.lineWidth=1.2; ctx.stroke();
    ctx.font = `${Math.round(W*0.18)}px serif`;
    ctx.textAlign='center'; ctx.textBaseline='middle';
    RUNES.slice(0,6).forEach((rune,i) => {
        const a = miniRuneAngle + (i/6)*Math.PI*2;
        const alpha = 0.4 + pulse*0.4;
        ctx.fillStyle = `rgba(160,32,240,${alpha.toFixed(2)})`;
        ctx.fillText(rune, cx+Math.cos(a)*r, cy+Math.sin(a)*r);
    });
    ctx.beginPath(); ctx.arc(cx,cy,3,0,Math.PI*2);
    ctx.fillStyle = `rgba(0,245,255,${(0.7+pulse*0.3).toFixed(2)})`; ctx.fill();
}

// ═══════════════════════════════════════════════════
// DATA STREAM CANVAS (sidebar background)
// ═══════════════════════════════════════════════════
function initDataStream() {
    const c = document.getElementById('data-stream-canvas');
    if (!c) return;
    c.width  = c.offsetWidth  || 290;
    c.height = c.offsetHeight || 800;
    dataStreamCtx = c.getContext('2d');
    const cols = Math.floor(c.width / 12);
    for (let i=0; i<cols; i++) {
        dataStreamCols.push({ x: i*12, y: Math.random()*c.height, speed: 0.5+Math.random()*1.5 });
    }
}

let dsLastTs = 0;
function updateDataStream(ts) {
    const c = document.getElementById('data-stream-canvas');
    if (!c || !dataStreamCtx) return;
    if (ts - dsLastTs < 60) return;
    dsLastTs = ts;
    const W=c.width, H=c.height;
    dataStreamCtx.fillStyle = 'rgba(3,0,7,0.12)';
    dataStreamCtx.fillRect(0,0,W,H);
    dataStreamCtx.font = '11px Share Tech Mono, monospace';
    dataStreamCtx.fillStyle = 'rgba(139,0,255,0.9)';
    dataStreamCols.forEach(col => {
        const char = Math.random() > 0.5
            ? String.fromCharCode(0x30A0 + Math.floor(Math.random()*96))
            : Math.floor(Math.random()*16).toString(16).toUpperCase();
        dataStreamCtx.fillText(char, col.x, col.y);
        col.y += col.speed * 12;
        if (col.y > H) { col.y = 0; col.speed = 0.5 + Math.random()*1.5; }
    });
}

// ═══════════════════════════════════════════════════
// XP BAR CANVAS — 60 FPS shimmer + particle burst
// ═══════════════════════════════════════════════════
function animXP(dt) {
    const c = document.getElementById('xp-canvas');
    if (!c) return;
    if (!c.width || c.width !== c.clientWidth) c.width = c.clientWidth || 400;
    const ctx = c.getContext('2d');
    const W=c.width, H=c.height;

    // Ease toward target
    const diff = xpTarget - xpDisplayed;
    if (Math.abs(diff) > 0.05) xpDisplayed += diff * 0.05;

    const fillW = W * Math.min(xpDisplayed / xpMax, 1.0);
    ctx.clearRect(0,0,W,H);

    // Track
    ctx.fillStyle='rgba(139,0,255,0.08)';
    ctx.beginPath(); ctx.roundRect(0,0,W,H,4); ctx.fill();

    // Fill
    if (fillW > 2) {
        const g = ctx.createLinearGradient(0,0,W,0);
        g.addColorStop(0,'#3D0070');
        g.addColorStop(0.4,'#8B00FF');
        g.addColorStop(0.8,'#A020F0');
        g.addColorStop(1,'#00F5FF');
        ctx.fillStyle = g;
        ctx.shadowColor = '#8B00FF'; ctx.shadowBlur = 12;
        ctx.beginPath(); ctx.roundRect(0,0,fillW,H,4); ctx.fill();
        ctx.shadowBlur = 0;

        // Ice tip glow
        const tipG = ctx.createLinearGradient(fillW-20,0,fillW+5,0);
        tipG.addColorStop(0,'rgba(0,245,255,0)');
        tipG.addColorStop(1,'rgba(0,245,255,0.8)');
        ctx.fillStyle = tipG;
        ctx.beginPath(); ctx.roundRect(Math.max(0,fillW-22),0,22,H,4); ctx.fill();
    }

    // Shimmer sweep
    xpShimmerX += dt * 0.22 * shimmerDir;
    if (xpShimmerX > W+80) { xpShimmerX = -80; }
    if (xpShimmerX > -80 && xpShimmerX < fillW) {
        const sg = ctx.createLinearGradient(xpShimmerX-40,0,xpShimmerX+40,0);
        sg.addColorStop(0,'rgba(255,255,255,0)');
        sg.addColorStop(0.5,'rgba(255,255,255,0.22)');
        sg.addColorStop(1,'rgba(255,255,255,0)');
        ctx.fillStyle = sg;
        ctx.beginPath(); ctx.roundRect(0,0,fillW,H,4); ctx.fill();
    }

    // Milestone ticks
    [0.25,0.5,0.75].forEach(m => {
        ctx.strokeStyle='rgba(0,245,255,0.35)'; ctx.lineWidth=1;
        ctx.beginPath(); ctx.moveTo(W*m,0); ctx.lineTo(W*m,H); ctx.stroke();
    });

    // Border
    ctx.strokeStyle='rgba(139,0,255,0.5)'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.roundRect(0,0,W,H,4); ctx.stroke();
}

// ═══════════════════════════════════════════════════
// STAT ARCS — Circular arc gauges for STR/INT/AGI/DIS
// ═══════════════════════════════════════════════════
function animStatArcs(dt) {
    const c = document.getElementById('stat-arcs-canvas');
    if (!c) return;
    if (c.width !== c.clientWidth) { c.width = c.clientWidth || 280; c.height = Math.round(c.width * 0.5); }
    const ctx = c.getContext('2d');
    const W=c.width, H=c.height;
    ctx.clearRect(0,0,W,H);

    // Interpolate
    ['str','int','agi','dis'].forEach(k => {
        const d = attrTarget[k] - attrDisplayed[k];
        if (Math.abs(d) > 0.05) attrDisplayed[k] += d * 0.06;
    });

    const arcs = [
        { key:'str', label:'STR', color:'#C77DFF', glow:'rgba(199,125,255,0.6)', cx:W*0.15, cy:H*0.5 },
        { key:'int', label:'INT', color:'#00BFFF', glow:'rgba(0,191,255,0.6)',   cx:W*0.38, cy:H*0.5 },
        { key:'agi', label:'AGI', color:'#00FF88', glow:'rgba(0,255,136,0.6)',   cx:W*0.62, cy:H*0.5 },
        { key:'dis', label:'DIS', color:'#FF6B6B', glow:'rgba(255,107,107,0.6)', cx:W*0.85, cy:H*0.5 },
    ];
    const arcR = W * 0.09;

    arcs.forEach(a => {
        const val = attrDisplayed[a.key];
        const maxVal = 100;
        const startA = -Math.PI * 0.8;
        const endA   =  Math.PI * 0.8;
        const prog   = startA + (val/maxVal)*(endA-startA);

        // Track
        ctx.beginPath(); ctx.arc(a.cx,a.cy,arcR,startA,endA);
        ctx.strokeStyle='rgba(255,255,255,0.06)'; ctx.lineWidth=arcR*0.22; ctx.lineCap='round'; ctx.stroke();

        // Fill
        if (val > 0) {
            ctx.beginPath(); ctx.arc(a.cx,a.cy,arcR,startA,prog);
            ctx.strokeStyle=a.color; ctx.lineWidth=arcR*0.22; ctx.lineCap='round';
            ctx.shadowColor=a.glow; ctx.shadowBlur=12; ctx.stroke(); ctx.shadowBlur=0;
        }

        // Value
        ctx.fillStyle='#F0E8FF'; ctx.textAlign='center'; ctx.textBaseline='middle';
        ctx.font = `bold ${Math.round(arcR*0.65)}px Rajdhani,sans-serif`;
        ctx.fillText(Math.round(val), a.cx, a.cy - arcR*0.08);

        // Label
        ctx.fillStyle='#8B6BB0'; ctx.font = `${Math.round(arcR*0.42)}px Rajdhani,sans-serif`;
        ctx.fillText(a.label, a.cx, a.cy + arcR*0.55);
    });
}

// ═══════════════════════════════════════════════════
// RADAR CHART CANVAS
// ═══════════════════════════════════════════════════
function animRadar(dt) {
    const c = document.getElementById('radar-canvas');
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const sz = Math.min(rect.width||200, rect.height||200);
    if (Math.abs(c.width-sz) > 2) { c.width=sz; c.height=sz; }
    const ctx = c.getContext('2d');
    const W=c.width, H=c.height;
    const cx=W/2, cy=H/2, maxR=Math.min(W,H)*0.34;

    for (let i=0;i<5;i++) {
        const d=radarTarget[i]-radarDisplayed[i];
        if (Math.abs(d)>0.05) radarDisplayed[i]+=d*0.05;
    }

    ctx.clearRect(0,0,W,H);

    // Grid rings
    [1,0.67,0.33].forEach((s,ri) => {
        ctx.beginPath();
        for(let i=0;i<5;i++) {
            const a=(i/5)*Math.PI*2-Math.PI/2;
            i===0?ctx.moveTo(cx+Math.cos(a)*maxR*s, cy+Math.sin(a)*maxR*s):ctx.lineTo(cx+Math.cos(a)*maxR*s, cy+Math.sin(a)*maxR*s);
        }
        ctx.closePath();
        ctx.strokeStyle=ri===0?'rgba(139,0,255,0.45)':'rgba(139,0,255,0.18)';
        ctx.lineWidth=ri===0?1:0.6; ctx.stroke();
    });

    // Axis lines
    for(let i=0;i<5;i++) {
        const a=(i/5)*Math.PI*2-Math.PI/2;
        ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+Math.cos(a)*maxR, cy+Math.sin(a)*maxR);
        ctx.strokeStyle='rgba(139,0,255,0.3)'; ctx.lineWidth=0.6; ctx.stroke();
    }

    // Filled polygon
    ctx.beginPath();
    for(let i=0;i<5;i++) {
        const a=(i/5)*Math.PI*2-Math.PI/2;
        const v=(radarDisplayed[i]/100)*maxR;
        i===0?ctx.moveTo(cx+Math.cos(a)*v,cy+Math.sin(a)*v):ctx.lineTo(cx+Math.cos(a)*v,cy+Math.sin(a)*v);
    }
    ctx.closePath();
    ctx.fillStyle='rgba(139,0,255,0.2)'; ctx.fill();
    ctx.strokeStyle='rgba(139,0,255,0.8)'; ctx.lineWidth=1.5;
    ctx.shadowColor='rgba(139,0,255,0.5)'; ctx.shadowBlur=8; ctx.stroke(); ctx.shadowBlur=0;

    // Vertex dots + labels
    for(let i=0;i<5;i++) {
        const a=(i/5)*Math.PI*2-Math.PI/2;
        const v=(radarDisplayed[i]/100)*maxR;
        ctx.beginPath(); ctx.arc(cx+Math.cos(a)*v, cy+Math.sin(a)*v, 4, 0, Math.PI*2);
        ctx.fillStyle=RADAR_COLORS[i]; ctx.shadowColor=RADAR_COLORS[i]; ctx.shadowBlur=8; ctx.fill(); ctx.shadowBlur=0;
        const lx=cx+Math.cos(a)*(maxR+18), ly=cy+Math.sin(a)*(maxR+14);
        ctx.font=`10px Rajdhani,sans-serif`; ctx.textAlign='center'; ctx.textBaseline='middle';
        ctx.fillStyle='rgba(139,107,176,0.8)'; ctx.shadowBlur=0;
        ctx.fillText(RADAR_LABELS[i],lx,ly);
    }
}

// ═══════════════════════════════════════════════════
// CALENDAR
// ═══════════════════════════════════════════════════
function renderCalendar(streakDays=[]) {
    const grid = document.getElementById('cal-grid');
    const lbl  = document.getElementById('cal-month');
    if (!grid) return;
    const now=new Date(), yr=now.getFullYear(), mo=now.getMonth(), td=now.getDate();
    const MONTHS=['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER'];
    lbl.textContent = `${MONTHS[mo]} ${yr}`;
    const firstDay = new Date(yr,mo,1).getDay();
    const offset = firstDay===0?6:firstDay-1;
    const daysInMo = new Date(yr,mo+1,0).getDate();
    grid.innerHTML='';
    for(let e=0;e<offset;e++) { const d=document.createElement('div'); d.className='cal-day empty'; grid.appendChild(d); }
    for(let d=1;d<=daysInMo;d++) {
        const cell=document.createElement('div');
        const isToday=d===td, isPast=d<td, isDone=streakDays.includes(d);
        const isMile=[7,14,21,30].includes(d) && isDone;
        let cls='cal-day ';
        if(isToday) cls+='today'; else if(isDone) cls+='completed'; else if(isPast) cls+='missed'; else cls+='future';
        if(isMile) cls+=' milestone';
        cell.className=cls; cell.textContent=d;
        grid.appendChild(cell);
    }
}

// ═══════════════════════════════════════════════════
// LIVE DATA (REST API polling)
// ═══════════════════════════════════════════════════
function startLiveData() {
    fetchStats();
    fetchLogs();
    setInterval(fetchStats, 5000);
    setInterval(fetchLogs, 1500);
}

async function fetchStats() {
    try {
        const r = await fetch('/api/stats');
        if (!r.ok) return;
        updateUI(await r.json());
    } catch(e) {}
}

function updateUI(d) {
    const name = d.hunter_name || 'HUNTER';

    // Identity sidebar
    document.getElementById('hunter-name').textContent = name.toUpperCase();
    const rb = document.getElementById('rank-badge');
    rb.textContent = d.rank || 'E';
    rb.className = 'hunter-rank-badge' + (['S'].includes(d.rank)?' rank-S':'');
    document.getElementById('rank-label').textContent = d.rank || 'E';

    // HP
    const hp=d.hp||500, hpMax=d.hp_max||500;
    const hb = document.getElementById('hp-bar-fill');
    if(hb) hb.style.width = `${Math.max(0,Math.min((hp/hpMax)*100,100))}%`;
    const hd = document.getElementById('hp-display'); if(hd) hd.textContent=`${hp}/${hpMax}`;

    // Gold / streak
    document.getElementById('gold-val').textContent   = d.gold || 0;
    document.getElementById('streak-val').textContent = d.streak || 0;
    document.getElementById('gold-display').textContent  = `${d.gold||0}G`;
    document.getElementById('streak-display').textContent = `${d.streak||0} DAYS`;
    const cs = document.getElementById('cal-streak'); if(cs) cs.textContent=d.streak||0;

    // North star
    const ns = document.getElementById('north-star-sidebar');
    if(ns) ns.textContent = `"${(d.north_star||'SET YOUR NORTH STAR').toUpperCase()}"`;

    // Level + XP
    const nl = d.level||1;
    document.getElementById('level-num').textContent = nl;
    const lt = document.getElementById('level-tag'); if(lt) lt.textContent='HUNTER';
    const xr = document.getElementById('xp-ratio'); if(xr) xr.textContent=`${d.xp||0} / ${d.xp_threshold||1000} XP`;
    xpTarget=d.xp||0; xpMax=d.xp_threshold||1000;
    const nrv=document.getElementById('next-rank-val');
    const ranks=['E','D','C','B','A','S'];
    const ri=ranks.indexOf(d.rank||'E');
    if(nrv) nrv.textContent=ri<ranks.length-1?ranks[ri+1]:'MAX';

    // Level up check
    if (nl > prevLevel) { triggerLevelUp(nl); }
    prevLevel = nl;

    // Attributes
    if (d.attributes) {
        const a=d.attributes;
        attrTarget.str=a.strength||a.str||10;
        attrTarget.int=a.intelligence||a.int||10;
        attrTarget.agi=a.agility||a.agi||10;
        attrTarget.dis=a.discipline||a.dis||10;
        const attrs = document.getElementById('hud-attributes');
        if(attrs) attrs.textContent=`STR:${attrTarget.str} // INT:${attrTarget.int} // AGI:${attrTarget.agi} // DIS:${attrTarget.dis}`;
    }

    // Focus
    focusActive = d.focus_active||false;
    const fs=document.getElementById('focus-status'), ft=document.getElementById('focus-txt');
    if(focusActive) { fs?.classList.add('active'); if(ft) ft.textContent='FOCUS ACTIVE'; }
    else            { fs?.classList.remove('active'); if(ft) ft.textContent='SYSTEM STANDBY'; }
    const fb=document.getElementById('btn-focus'), fbt=document.getElementById('focus-btn-text');
    if(focusActive) { fb?.classList.add('active-focus'); if(fbt) fbt.textContent='DEACTIVATE FOCUS'; }
    else            { fb?.classList.remove('active-focus'); if(fbt) fbt.textContent='INITIATE FOCUS SESSION'; }

    // Quests
    allQuests = d.daily_quests||[];
    renderDailyQuests(allQuests);
    renderAllQuests(allQuests);

    // Radar from quests
    const map={FITNESS:0,PHYSICAL:0,MENTAL:1,CAREER:1,SKILLS:1,FINANCIAL:2,FINANCE:2,SPIRITUAL:3,MINDSET:3,EMOTIONAL:4,SOCIAL:4};
    const tot=[0,0,0,0,0], cnt=[0,0,0,0,0];
    allQuests.forEach(q=>{const idx=map[(q.category||'').toUpperCase()]; if(idx!==undefined){tot[idx]+=(q.status==='COMPLETED'?100:25);cnt[idx]++;}});
    for(let i=0;i<5;i++) radarTarget[i]=cnt[i]>0?Math.min(tot[i]/cnt[i],100):radarTarget[i];

    // Achievements
    checkAchievements(d);
}

// ═══════════════════════════════════════════════════
// QUEST RENDERING
// ═══════════════════════════════════════════════════
function renderDailyQuests(quests) {
    const list=document.getElementById('daily-quest-list');
    if(!list) return;
    list.innerHTML='';
    if(!quests||!quests.length) { list.innerHTML='<div class="quest-empty">Run Daily Protocol to populate quests.</div>'; return; }
    quests.slice(0,10).forEach((q,i)=>{
        const done=q.status==='COMPLETED';
        const el=document.createElement('div');
        el.className=`quest-item ${done?'completed':''}`;
        el.style.animationDelay=`${i*60}ms`;
        el.innerHTML=`
            <div class="qi-check">${done?'✓':''}</div>
            <div class="qi-body">
                <span class="qi-title">${q.title}</span>
                <span class="qi-xp">+${q.xp_reward||0} XP</span>
            </div>
            <span class="qi-badge badge-${q.category||'DAILY'}">${q.category||'DAILY'}</span>
        `;
        el.addEventListener('click',()=>{toggleQuest(q.title,q.evidence_required,done);playUISound('click');});
        list.appendChild(el);
    });
}

function renderAllQuests(quests) {
    const g=document.getElementById('all-quests-grid');
    if(!g) return;
    const filtered=activeFilter==='ALL'?quests:quests.filter(q=>(q.category||'').toUpperCase()===activeFilter);
    g.innerHTML='';
    if(!filtered.length){g.innerHTML='<div class="quest-empty" style="grid-column:1/-1">No quests in this category.</div>';return;}
    filtered.forEach(q=>{
        const done=q.status==='COMPLETED', boss=(q.category||'').toUpperCase()==='BOSS';
        const dc=done?'done':q.status==='IN_PROGRESS'?'act':'pend';
        const card=document.createElement('div');
        card.className=`qcard ${boss?'boss':''} ${done?'completed':''}`;
        card.innerHTML=`
            <div class="qc-head"><span class="qc-title">${q.title}</span><span class="qi-badge badge-${q.category||'DAILY'}">${q.category||'DAILY'}</span></div>
            <div class="qc-desc">${q.description||'Complete this mission.'}</div>
            <div class="qc-foot"><span class="qc-xp">+${q.xp_reward||0} XP${boss?' ☠':''}</span><span class="status-ring ${dc}"></span></div>
        `;
        card.addEventListener('click',()=>{toggleQuest(q.title,q.evidence_required,done);playUISound('click');});
        g.appendChild(card);
    });
}

function setQuestFilter(cat) {
    activeFilter=cat;
    document.querySelectorAll('.qfbtn').forEach(b=>b.classList.toggle('active',b.dataset.f===cat));
    renderAllQuests(allQuests);
}
document.addEventListener('click',e=>{if(e.target.classList.contains('qfbtn'))setQuestFilter(e.target.dataset.f);});

async function toggleQuest(title,evidence_required=false,isCompleted=false) {
    let evidence='';
    if(evidence_required&&!isCompleted){
        evidence=prompt(`[EVIDENCE REQUIRED]\nProof for: "${title}"\n(GitHub link, Strava URL, etc.)`);
        if(evidence===null||!evidence.trim()){logMsg('[QUEST] Evidence cancelled.','sys');return;}
    }
    try {
        const r=await fetch('/api/quests/toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,evidence})});
        const d=await r.json();
        if(r.ok){logMsg(`[QUEST] ${d.message}`,'sys');if(!isCompleted)playUISound('complete');fetchStats();}
        else logMsg(`[ERROR] ${d.error}`,'error');
    } catch(e){logMsg(`[ERROR] ${e}`,'error');}
}

// ═══════════════════════════════════════════════════
// CONTROL CENTER
// ═══════════════════════════════════════════════════
function initControlCenter() {
    const fb=document.getElementById('btn-focus');
    if(fb) fb.addEventListener('click',()=>{triggerAction(focusActive?'stop_private_mode':'start_private_mode');});
}

async function triggerAction(name) {
    logMsg(`[SYSTEM] Executing: ${name.toUpperCase()}...`,'sys');
    playUISound('click');
    try {
        const r=await fetch('/api/actions/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action:name})});
        const d=await r.json();
        if(d.status==='success'){logMsg(`[J.A.R.V.I.S.] ${d.message}`,'jarvis');fetchStats();if(name==='intelligence_brief')setTimeout(()=>switchTab('intel'),2000);}
        else logMsg(`[WARNING] ${d.message}`,'error');
    } catch(e){logMsg(`[ERROR] ${e}`,'error');}
}

// ═══════════════════════════════════════════════════
// LOG POLLING
// ═══════════════════════════════════════════════════
async function fetchLogs() {
    try {
        const r=await fetch(`/api/logs?since=${lastLogIdx}`);
        if(!r.ok) return;
        const data=await r.json();
        if(Array.isArray(data)&&data.length){data.forEach(e=>appendLog(e));lastLogIdx+=data.length;}
    } catch(e){}
}
function appendLog(e){logMsg(typeof e==='string'?e:(e.message||JSON.stringify(e)));}

function logMsg(msg,type='info') {
    ['terminal-logs','terminal-sys'].forEach(id=>{
        const el=document.getElementById(id); if(!el)return;
        const line=document.createElement('div');
        const now=new Date();
        const ts=`[${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}]`;
        const m=String(msg);
        const t=type!=='info'?type:m.includes('[ERROR]')?'error':m.includes('J.A.R.V.I.S.')||m.includes('JARVIS')?'jarvis':m.includes('[SYSTEM]')||m.includes('[QUEST]')||m.includes('[CLOUD]')?'sys':'info';
        line.className=`log-${t}`;
        line.textContent=`${ts} ${m}`;
        el.appendChild(line);
        el.scrollTop=el.scrollHeight;
        while(el.children.length>250)el.removeChild(el.firstChild);
    });
}

// ═══════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════
const TABS=['core','quests','goals','intel','system'];
function initNavButtons() {
    document.querySelectorAll('.nav-btn').forEach(btn=>{
        btn.addEventListener('click',()=>switchTab(btn.dataset.tab));
    });
}
function switchTab(id) {
    TABS.forEach(t=>{
        const p=document.getElementById(`pane-${t}`), b=document.getElementById(`nav-${t}`);
        if(p) p.style.display=t===id?'flex':'none';
        if(b) b.classList.toggle('active',t===id);
    });
    if(id==='goals')  loadPlan();
    if(id==='intel')  loadIntel();
    if(id==='system') loadJournal();
    playUISound('click');
}

// ═══════════════════════════════════════════════════
// PLAN / GOALS
// ═══════════════════════════════════════════════════
async function loadPlan() {
    try {
        const r=await fetch('/api/goals/plan'); if(!r.ok)return;
        const d=await r.json(); if(!d.active){document.getElementById('plan-north-star').textContent='No plan deployed. Use the wizard.';return;}
        document.getElementById('plan-hunter').textContent=d.profile_name||'---';
        document.getElementById('plan-quarter').textContent=d.current_quarter||'---';
        document.getElementById('plan-week').textContent=d.week_number||'---';
        document.getElementById('plan-north-star').textContent=d.north_star||'---';
        const ml=document.getElementById('plan-monthly');if(ml)ml.innerHTML=(d.monthly_focus||[]).map(i=>`<li>${i}</li>`).join('')||'<li>---</li>';
        const wl=document.getElementById('plan-weekly');if(wl)wl.innerHTML=(d.weekly_targets||[]).map(i=>`<li>${i}</li>`).join('')||'<li>---</li>';
        const tl=document.getElementById('plan-today');if(tl)tl.innerHTML=(d.today_actions||[]).map(i=>`<li>${i}</li>`).join('')||'<li>---</li>';
        const bl=document.getElementById('goals-backlog');if(bl){bl.innerHTML='';(d.yearly_goals||[]).forEach(g=>{const c=document.createElement('div');c.className='goal-detail-card';c.innerHTML=`<div class="gdc-head"><span class="gdc-title">${g.title}</span><span class="gdc-cat">${g.category}</span></div><div class="gdc-body">${g.description||'No description.'}<br><small style="color:var(--ev-bright)">Deadline: ${g.deadline} — P${g.priority}</small></div>`;bl.appendChild(c);});}
    } catch(e){}
}

function addGoal() {
    const t=document.getElementById('b-title')?.value.trim();
    const cat=document.getElementById('b-cat')?.value;
    const desc=document.getElementById('b-desc')?.value.trim();
    const met=document.getElementById('b-metric')?.value.trim();
    const pri=document.getElementById('b-priority')?.value;
    const dl=document.getElementById('b-deadline')?.value;
    if(!t||!dl){alert('Title and deadline required!');return;}
    builderGoals.push({title:t,category:cat,description:desc,success_metric:met,priority:pri,deadline:dl});
    renderBuilderList(); ['b-title','b-desc','b-metric'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});
    playUISound('complete');
}

function removeGoal(i){builderGoals.splice(i,1);renderBuilderList();}

function renderBuilderList() {
    const cnt=document.getElementById('b-count');if(cnt)cnt.textContent=builderGoals.length;
    const list=document.getElementById('b-list');if(!list)return;
    list.innerHTML='';
    builderGoals.forEach((g,i)=>{
        const r=document.createElement('div');r.className='b-row';
        r.innerHTML=`<span style="font-size:0.75rem;color:var(--tw)">${g.title} <span style="color:var(--tm)">(${g.category})</span></span><button class="b-rm" onclick="removeGoal(${i})">✕</button>`;
        list.appendChild(r);
    });
}

async function deployPlan() {
    const name=document.getElementById('inp-name')?.value.trim();
    const year=document.getElementById('inp-year')?.value;
    const ns=document.getElementById('inp-northstar')?.value.trim();
    if(!name||!ns||!builderGoals.length){alert('Fill name, north star and at least 1 goal.');return;}
    try {
        const r=await fetch('/api/goals/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({profile_name:name,target_year:year,north_star:ns,yearly_goals:builderGoals})});
        const d=await r.json();
        logMsg(r.ok?`[SYSTEM] Plan deployed: ${d.message||'OK'}`:`[ERROR] ${d.error}`);
        if(r.ok){builderGoals=[];renderBuilderList();loadPlan();playUISound('complete');}
    } catch(e){logMsg(`[ERROR] ${e}`,'error');}
}

async function loadGoalsDefaults() {
    document.getElementById('inp-year').value=new Date().getFullYear();
    document.getElementById('b-deadline').value=new Date(new Date().getFullYear(),11,31).toISOString().split('T')[0];
    try{const r=await fetch('/api/stats');if(r.ok){const d=await r.json();document.getElementById('inp-name').value=d.hunter_name||'Hunter';document.getElementById('inp-northstar').value=d.north_star||'';}}catch(e){}
}

// ═══════════════════════════════════════════════════
// INTEL
// ═══════════════════════════════════════════════════
async function loadIntel() {
    const el=document.getElementById('intel-content'); if(!el)return;
    try {
        const r=await fetch('/api/intelligence/latest'); if(!r.ok){el.innerHTML='<div class="empty-state">No brief available. Trigger from System tab.</div>';return;}
        const d=await r.json();
        let html='';
        if(d.summary) html+=`<div class="intel-summary">${d.summary}</div>`;
        if(d.findings?.length){html+='<div class="intel-grid">';d.findings.forEach(f=>{html+=`<div class="intel-card"><div class="intel-card-title">${f.title||'Finding'}</div>${f.source?`<a href="${f.source}" target="_blank" rel="noopener">↗ Source</a>`:''}<p style="font-size:0.73rem;color:var(--tm);margin-top:0.3rem;line-height:1.5">${f.summary||''}</p></div>`;});html+='</div>';}
        el.innerHTML=html||'<div class="empty-state">Brief is empty.</div>';
    } catch(e){el.innerHTML=`<div class="empty-state">Load failed: ${e}</div>`;}
}

// ═══════════════════════════════════════════════════
// JOURNAL
// ═══════════════════════════════════════════════════
async function submitJournal() {
    const txt=document.getElementById('journal-text')?.value.trim();
    const mood=document.getElementById('journal-mood')?.value;
    if(!txt){alert('Write something first!');return;}
    try {
        const r=await fetch('/api/journal/entry',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content:txt,mood})});
        const d=await r.json();
        if(r.ok){logMsg(`[JOURNAL] Entry logged. Mood: ${mood}`,'sys');document.getElementById('journal-text').value='';loadJournal();playUISound('complete');}
        else logMsg(`[ERROR] ${d.error}`,'error');
    } catch(e){logMsg(`[ERROR] ${e}`,'error');}
}

async function loadJournal() {
    const list=document.getElementById('journal-list'); if(!list)return;
    try {
        const r=await fetch('/api/journal/latest'); if(!r.ok)return;
        const data=await r.json();
        if(!Array.isArray(data)||!data.length){list.innerHTML='<div class="quest-empty">No entries yet.</div>';return;}
        list.innerHTML='';
        data.slice(-8).reverse().forEach(e=>{
            const el=document.createElement('div');el.className='journal-entry';
            const ts=new Date(e.timestamp||e.created_at||Date.now());
            const tsStr=`${ts.getDate()}/${ts.getMonth()+1} ${String(ts.getHours()).padStart(2,'0')}:${String(ts.getMinutes()).padStart(2,'0')}`;
            el.innerHTML=`<div class="je-head"><span class="je-time">${tsStr}</span><span class="je-mood">${e.mood||'NEUTRAL'}</span></div><div class="je-text">${e.content}</div>`;
            list.appendChild(el);
        });
    }catch(e){}
}

// ═══════════════════════════════════════════════════
// ACHIEVEMENTS
// ═══════════════════════════════════════════════════
function checkAchievements(d) {
    const completed=(d.daily_quests||[]).filter(q=>q.status==='COMPLETED').length;
    const hasBoss=(d.daily_quests||[]).some(q=>(q.category||'').toUpperCase()==='BOSS'&&q.status==='COMPLETED');
    if(completed>=5)  unlock('ach-firstblood');
    if((d.streak||0)>=7)  unlock('ach-scholar');
    if((d.streak||0)>=30) unlock('ach-iron');
    if(hasBoss)            unlock('ach-boss');
    if(d.rank==='S')       unlock('ach-apex');
}
function unlock(id){const c=document.getElementById(id);if(c?.classList.contains('locked')){c.classList.remove('locked');c.style.borderColor='var(--gold)';c.style.boxShadow='0 0 12px var(--gold-glow)';playUISound('complete');}}

// ═══════════════════════════════════════════════════
// LEVEL UP CINEMATIC
// ═══════════════════════════════════════════════════
function triggerLevelUp(lvl) {
    const ov=document.getElementById('levelup-overlay');
    const ln=document.getElementById('lu-new-level');
    if(!ov||!ln)return;
    ln.textContent=`LEVEL ${lvl} ACHIEVED`;
    ov.removeAttribute('hidden');
    playUISound('levelup');
    setTimeout(()=>ov.setAttribute('hidden',''),4000);
}

// ═══════════════════════════════════════════════════
// MOUSE GLOW + PARALLAX
// ═══════════════════════════════════════════════════
function initMouseGlow() {
    const glow=document.getElementById('mouse-glow');
    document.addEventListener('mousemove',e=>{
        mouseX=e.clientX/innerWidth;
        mouseY=e.clientY/innerHeight;
        if(glow){ glow.style.left=e.clientX+'px'; glow.style.top=e.clientY+'px'; }
        // Update avatar parallax (done in updateAvatarCanvas via mouseX/Y)
    });
}

// ═══════════════════════════════════════════════════
// LIVE CLOCK
// ═══════════════════════════════════════════════════
function initClock() {
    const el=document.getElementById('sys-clock');
    const tick=()=>{
        if(!el)return;
        const n=new Date();
        el.textContent=[n.getHours(),n.getMinutes(),n.getSeconds()].map(x=>String(x).padStart(2,'0')).join(':');
    };
    tick(); setInterval(tick,1000);
}

// ═══════════════════════════════════════════════════
// WEB AUDIO API
// ═══════════════════════════════════════════════════
function getACtx(){if(!audioCtx)try{audioCtx=new(window.AudioContext||window.webkitAudioContext)();}catch(e){return null;}return audioCtx;}

function playUISound(type){
    const ctx=getACtx(); if(!ctx)return;
    const now=ctx.currentTime;
    const mg=ctx.createGain(); mg.gain.setValueAtTime(0.05,now); mg.connect(ctx.destination);
    const mk=(freq,wave,dur,gain=0.05)=>{
        const o=ctx.createOscillator(),g=ctx.createGain();
        o.type=wave; o.frequency.setValueAtTime(freq,now);
        g.gain.setValueAtTime(gain,now); g.gain.exponentialRampToValueAtTime(0.001,now+dur);
        o.connect(g); g.connect(ctx.destination); o.start(now); o.stop(now+dur+0.01);
    };
    if(type==='click'){mk(900,'square',0.05);}
    else if(type==='complete'){[440,554,659].forEach((f,i)=>{setTimeout(()=>mk(f,'sine',0.28,0.07),i*110);});}
    else if(type==='levelup'){
        const o=ctx.createOscillator(),g=ctx.createGain();
        o.type='sawtooth'; o.frequency.setValueAtTime(110,now); o.frequency.exponentialRampToValueAtTime(880,now+0.9);
        g.gain.setValueAtTime(0.07,now); g.gain.exponentialRampToValueAtTime(0.001,now+1.1);
        o.connect(g); g.connect(ctx.destination); o.start(now); o.stop(now+1.1);
        mk(55,'sine',0.5,0.12);
    }
    else if(type==='error'){mk(300,'sawtooth',0.25);}
    else if(type==='boot'){[100,200,300,250,450].forEach((f,i)=>{setTimeout(()=>mk(f,'sine',0.12,0.05),i*90);});}
}

// ═══════════════════════════════════════════════════
// RESIZE
// ═══════════════════════════════════════════════════
window.addEventListener('resize',()=>{
    resizeBgRenderer();
    const av=document.getElementById('avatar-canvas');
    if(av&&avRenderer){avRenderer.setSize(av.clientWidth,av.clientHeight);avCamera.aspect=av.clientWidth/av.clientHeight;avCamera.updateProjectionMatrix();}
    const xp=document.getElementById('xp-canvas'); if(xp) xp.width=xp.clientWidth||400;
    const ds=document.getElementById('data-stream-canvas'); if(ds){ds.width=ds.offsetWidth||290;ds.height=ds.offsetHeight||800;}
});
window.addEventListener('load',()=>{
    const xp=document.getElementById('xp-canvas'); if(xp) xp.width=xp.clientWidth||400;
});
