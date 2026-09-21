'use strict';
/* ═══════════════════════════════════════════════════════════════════
   APEX GHOST — SOLO LEVELING ENGINE v2.0
   Hooded Avatar · Radar Chart · Pixel Grid · Potion Market
   Star Background · Boot Sigil · Level-Up Cinematic
   ═══════════════════════════════════════════════════════════════════ */

const G = {
    player:      null,
    quests:      [],
    prevLevel:   0,
    mouseX:      0.5,
    mouseY:      0.5,
    radarValues: { STR:10, INT:10, AGI:10, DIS:10, FOC:10 },
    audioCtx:    null,
    currentView: 'hud',
    treasuryData:null,
    logIdx:      0,
    potionColors:['#ffd700','#00e5ff','#bb66ff'],
};

const delay = ms => new Promise(r => setTimeout(r, ms));

/* ═══════════════════════════════════════════════════════════════════
   BOOT SEQUENCE
   ═══════════════════════════════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded', async () => {
    initBgStars();
    initMouseGlow();
    await runBoot();
    initAvatar();
    initRadar();
    buildHealthGrid();
    drawPotions();
    initNavDock();
    initQuestFilters();
    initClock();
    startDataLoop();
    requestAnimationFrame(masterLoop);
});

async function runBoot() {
    const bc = document.getElementById('boot-canvas');
    if (bc) animBootSigil(bc);

    const lines = [
        '> APEX GHOST PROTOCOL v5.0...',
        '> Loading shadow attribute matrix...',
        '> Syncing quest engine...',
        '> Calibrating capital reactor...',
        '> Intel network handshake...',
        '> Hunter profile loaded.',
        '> ◈ SYSTEM AWAKENED.',
    ];
    const log = document.getElementById('boot-log');
    const bar = document.getElementById('boot-bar');
    const pct = document.getElementById('boot-pct');
    if (!log) return;

    for (let i = 0; i < lines.length; i++) {
        const d = document.createElement('div');
        d.textContent = lines[i];
        log.appendChild(d);
        log.scrollTop = log.scrollHeight;
        bar.style.width = Math.round((i+1)/lines.length*100) + '%';
        pct.textContent = Math.round((i+1)/lines.length*100) + '%';
        await delay(180 + Math.random()*120);
    }
    pct.textContent = 'ONLINE';
    await delay(500);
    playBootSound();
    const ov = document.getElementById('boot-overlay');
    ov.classList.add('fade-out');
    await delay(900);
    ov.style.display = 'none';
}

/* Boot sigil canvas */
function animBootSigil(canvas) {
    const ctx = canvas.getContext('2d');
    const cx = canvas.width/2, cy = canvas.height/2;
    let angle = 0;
    function draw() {
        ctx.clearRect(0,0,canvas.width,canvas.height);
        // Outer glow ring
        for (let r = 0; r < 3; r++) {
            const rad = 80 - r*20;
            ctx.save();
            ctx.strokeStyle = `rgba(155,51,255,${0.15 + r*0.15})`;
            ctx.lineWidth = 1.5 - r*0.4;
            ctx.shadowBlur = 15; ctx.shadowColor = '#7b00cc';
            ctx.beginPath(); ctx.arc(cx,cy,rad,0,Math.PI*2); ctx.stroke();
            ctx.restore();
        }
        // Rotating rune ring
        for (let i = 0; i < 8; i++) {
            const a = angle + (i/8)*Math.PI*2;
            const x = cx + Math.cos(a)*70, y = cy + Math.sin(a)*70;
            ctx.save();
            ctx.fillStyle = `rgba(187,102,255,${0.5+Math.sin(angle*2+i)*0.3})`;
            ctx.shadowBlur = 8; ctx.shadowColor = '#9d33ff';
            ctx.fillRect(x-2,y-2,4,4);
            ctx.restore();
        }
        // Counter ring
        for (let i = 0; i < 6; i++) {
            const a = -angle*1.5 + (i/6)*Math.PI*2;
            const x = cx + Math.cos(a)*50, y = cy + Math.sin(a)*50;
            ctx.save();
            ctx.fillStyle = `rgba(0,229,255,${0.4+Math.sin(-angle*2+i)*0.3})`;
            ctx.shadowBlur = 6; ctx.shadowColor = '#00e5ff';
            ctx.beginPath(); ctx.arc(x,y,2,0,Math.PI*2); ctx.fill();
            ctx.restore();
        }
        // Center glyph
        ctx.save();
        ctx.font = 'bold 28px Cinzel Decorative, serif';
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillStyle = '#d499ff';
        ctx.shadowBlur = 20; ctx.shadowColor = '#7b00cc';
        ctx.fillText('◈', cx, cy);
        ctx.restore();
        // Star sparks
        for (let i = 0; i < 5; i++) {
            const a = angle*0.7 + i*(Math.PI*2/5);
            const r2 = 90 + Math.sin(angle*3+i)*5;
            ctx.save();
            ctx.fillStyle = `rgba(255,215,0,${0.3+Math.sin(angle*4+i)*0.2})`;
            ctx.shadowBlur = 10; ctx.shadowColor = '#ffd700';
            ctx.beginPath();
            ctx.arc(cx+Math.cos(a)*r2, cy+Math.sin(a)*r2, 1.5,0,Math.PI*2);
            ctx.fill();
            ctx.restore();
        }
        angle += 0.025;
        if (document.getElementById('boot-overlay')?.style.display !== 'none') {
            requestAnimationFrame(draw);
        }
    }
    draw();
}

/* ═══════════════════════════════════════════════════════════════════
   BACKGROUND — STAR FIELD (Canvas 2D, no Three.js needed for bg)
   ═══════════════════════════════════════════════════════════════════ */
let bgCtx, bgStars = [], bgW, bgH, bgTime = 0;

function initBgStars() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    bgCtx = canvas.getContext('2d');
    resizeBg(canvas);
    window.addEventListener('resize', () => resizeBg(canvas));
}

function resizeBg(canvas) {
    bgW = canvas.width  = innerWidth;
    bgH = canvas.height = innerHeight;
    bgStars = Array.from({length: 220}, () => ({
        x:     Math.random() * bgW,
        y:     Math.random() * bgH,
        r:     0.3 + Math.random() * 1.4,
        speed: 0.05 + Math.random() * 0.15,
        phase: Math.random() * Math.PI * 2,
        color: Math.random() > 0.85 ? '#bb66ff' : Math.random() > 0.7 ? '#6633aa' : '#ffffff',
    }));
}

function drawBgStars(ts) {
    if (!bgCtx) return;
    bgTime = ts * 0.001;
    // Deep purple gradient base
    const grad = bgCtx.createRadialGradient(bgW*0.5,bgH*0.5,0, bgW*0.5,bgH*0.5, bgW*0.75);
    grad.addColorStop(0,   '#130020');
    grad.addColorStop(0.45,'#0d0018');
    grad.addColorStop(0.85,'#090012');
    grad.addColorStop(1,   '#070010');
    bgCtx.fillStyle = grad;
    bgCtx.fillRect(0,0,bgW,bgH);

    // Subtle central nebula glow
    const nebGrad = bgCtx.createRadialGradient(bgW*0.5,bgH*0.45,0,bgW*0.5,bgH*0.45,bgW*0.35);
    nebGrad.addColorStop(0,   'rgba(80,0,160,0.18)');
    nebGrad.addColorStop(0.5, 'rgba(50,0,100,0.08)');
    nebGrad.addColorStop(1,   'transparent');
    bgCtx.fillStyle = nebGrad;
    bgCtx.fillRect(0,0,bgW,bgH);

    // Stars
    bgStars.forEach(s => {
        const a = 0.35 + Math.sin(bgTime*s.speed + s.phase) * 0.35;
        bgCtx.save();
        bgCtx.globalAlpha = a;
        bgCtx.fillStyle = s.color;
        bgCtx.shadowBlur = s.r > 1 ? 6 : 0;
        bgCtx.shadowColor = s.color;
        bgCtx.beginPath();
        bgCtx.arc(s.x, s.y, s.r, 0, Math.PI*2);
        bgCtx.fill();
        bgCtx.restore();
    });

    // Mouse-reactive glow
    const mgx = G.mouseX * bgW, mgy = G.mouseY * bgH;
    const mg = bgCtx.createRadialGradient(mgx,mgy,0, mgx,mgy, 280);
    mg.addColorStop(0,   'rgba(100,0,200,0.1)');
    mg.addColorStop(1,   'transparent');
    bgCtx.fillStyle = mg;
    bgCtx.fillRect(0,0,bgW,bgH);
}

/* ═══════════════════════════════════════════════════════════════════
   HOODED AVATAR (Canvas 2D)
   ═══════════════════════════════════════════════════════════════════ */
let avCtx, avTime = 0, avParticles = [];

function initAvatar() {
    const canvas = document.getElementById('avatar-canvas');
    if (!canvas) return;
    avCtx = canvas.getContext('2d');
    avParticles = Array.from({length:30}, () => ({
        angle: Math.random()*Math.PI*2,
        radius: 50 + Math.random()*30,
        speed: 0.008 + Math.random()*0.012,
        size: 1 + Math.random()*2,
        phase: Math.random()*Math.PI*2,
    }));
}

function drawAvatar(ts) {
    const ctx = avCtx;
    if (!ctx) return;
    avTime = ts * 0.001;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    const cx = W/2, cy = H/2;
    ctx.clearRect(0,0,W,H);

    // Aura rings
    const pulseR = 72 + Math.sin(avTime*1.2)*5;
    for (let i = 0; i < 4; i++) {
        const r = pulseR + i*12;
        const alpha = (0.35 - i*0.07) * (1 + Math.sin(avTime*1.5)*0.2);
        ctx.save();
        ctx.strokeStyle = `rgba(${i<2?'155,51,255':'100,0,200'},${alpha})`;
        ctx.lineWidth = 2 - i*0.4;
        ctx.shadowBlur = 15; ctx.shadowColor = '#7b00cc';
        ctx.beginPath(); ctx.arc(cx, cy+12, r, 0, Math.PI*2); ctx.stroke();
        ctx.restore();
    }

    // Floor glow ellipse
    ctx.save();
    const floorGrad = ctx.createRadialGradient(cx,cy+62,0, cx,cy+62,55);
    floorGrad.addColorStop(0,'rgba(155,51,255,0.25)');
    floorGrad.addColorStop(1,'transparent');
    ctx.fillStyle = floorGrad;
    ctx.beginPath();
    ctx.ellipse(cx, cy+65, 54, 16, 0, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();

    // ── Hooded figure silhouette ──
    ctx.save();
    ctx.shadowBlur = 22; ctx.shadowColor = '#9d33ff';

    // Main body gradient fill
    const bodyGrad = ctx.createLinearGradient(cx-40, cy-70, cx+40, cy+65);
    bodyGrad.addColorStop(0,   '#1a003a');
    bodyGrad.addColorStop(0.3, '#220050');
    bodyGrad.addColorStop(0.7, '#1a003a');
    bodyGrad.addColorStop(1,   '#110025');

    // Hood (head)
    ctx.beginPath();
    ctx.arc(cx, cy-48, 28, 0, Math.PI*2);
    ctx.fillStyle = bodyGrad;
    ctx.fill();

    // Hood outer (wider at top)
    ctx.beginPath();
    ctx.ellipse(cx, cy-44, 36, 34, 0, 0, Math.PI*2);
    ctx.fill();

    // Shoulders + cloak body
    ctx.beginPath();
    ctx.moveTo(cx-52, cy+65);           // bottom-left hem
    ctx.quadraticCurveTo(cx-60, cy-10, cx-38, cy-38);  // left edge
    ctx.quadraticCurveTo(cx-22, cy-55, cx, cy-72);     // left shoulder to hood top
    ctx.quadraticCurveTo(cx+22, cy-55, cx+38, cy-38);  // right shoulder
    ctx.quadraticCurveTo(cx+60, cy-10, cx+52, cy+65);  // right edge
    ctx.closePath();
    ctx.fillStyle = bodyGrad;
    ctx.fill();

    // Cloak border glow (outline)
    ctx.strokeStyle = `rgba(155,51,255,${0.55 + Math.sin(avTime*1.8)*0.2})`;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();

    // Face shadow / void face
    ctx.save();
    const faceGrad = ctx.createRadialGradient(cx, cy-44, 2, cx, cy-44, 20);
    faceGrad.addColorStop(0, 'rgba(0,0,0,0.95)');
    faceGrad.addColorStop(0.7,'rgba(10,0,22,0.8)');
    faceGrad.addColorStop(1, 'rgba(10,0,22,0)');
    ctx.fillStyle = faceGrad;
    ctx.beginPath(); ctx.ellipse(cx, cy-42, 18, 16, 0, 0, Math.PI*2); ctx.fill();
    ctx.restore();

    // Glowing eyes
    const eyePulse = 0.7 + Math.sin(avTime*2.5)*0.3;
    [[cx-7, cy-46],[cx+7, cy-46]].forEach(([ex,ey]) => {
        ctx.save();
        ctx.fillStyle = `rgba(187,102,255,${eyePulse})`;
        ctx.shadowBlur = 12; ctx.shadowColor = '#bb66ff';
        ctx.beginPath(); ctx.ellipse(ex, ey, 3, 2, 0, 0, Math.PI*2); ctx.fill();
        ctx.restore();
    });

    // Chest rune / sigil
    ctx.save();
    ctx.font = `${14 + Math.sin(avTime*1.5)*1}px Cinzel Decorative, serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = `rgba(200,120,255,${0.5+Math.sin(avTime*2)*0.3})`;
    ctx.shadowBlur = 15; ctx.shadowColor = '#9d33ff';
    ctx.fillText('◈', cx, cy+5);
    ctx.restore();

    // Orbiting particles
    avParticles.forEach(p => {
        p.angle += p.speed;
        const x = cx + Math.cos(p.angle) * p.radius;
        const y = cy + Math.sin(p.angle) * p.radius * 0.45 + 10;
        const a = 0.4 + Math.sin(avTime*2 + p.phase)*0.35;
        ctx.save();
        ctx.fillStyle = `rgba(155,51,255,${a})`;
        ctx.shadowBlur = 8; ctx.shadowColor = '#9d33ff';
        ctx.beginPath(); ctx.arc(x,y,p.size,0,Math.PI*2); ctx.fill();
        ctx.restore();
    });
}

/* ═══════════════════════════════════════════════════════════════════
   RADAR / SPIDER CHART (around avatar)
   ═══════════════════════════════════════════════════════════════════ */
let radarCtx;
const RADAR_LABELS = ['STR','INT','AGI','DIS','FOC'];
const RADAR_COLORS = ['#ff6b6b','#44ddff','#44ff99','#ffd700','#cc88ff'];

function initRadar() {
    const canvas = document.getElementById('radar-canvas');
    if (!canvas) return;
    radarCtx = canvas.getContext('2d');
}

function drawRadar(ts) {
    const ctx = radarCtx;
    if (!ctx) return;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    const cx = W/2, cy = H/2;
    const maxR = Math.min(cx,cy) * 0.85;
    const N = RADAR_LABELS.length;
    const t = ts*0.001;

    ctx.clearRect(0,0,W,H);

    const angles = RADAR_LABELS.map((_,i) => -Math.PI/2 + (i/N)*Math.PI*2);

    // Background web rings
    for (let ring = 1; ring <= 5; ring++) {
        const r = (ring/5)*maxR;
        ctx.save();
        ctx.strokeStyle = `rgba(100,0,200,${0.12 + (ring===5?0.06:0)})`;
        ctx.lineWidth = ring===5 ? 1 : 0.6;
        ctx.setLineDash([3,5]);
        ctx.beginPath();
        angles.forEach((a,i) => {
            const x = cx + Math.cos(a)*r, y = cy + Math.sin(a)*r;
            i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
        });
        ctx.closePath(); ctx.stroke();
        ctx.restore();
    }

    // Axis lines
    angles.forEach(a => {
        ctx.save();
        ctx.strokeStyle = 'rgba(100,0,200,0.2)';
        ctx.lineWidth = 0.7;
        ctx.beginPath();
        ctx.moveTo(cx,cy);
        ctx.lineTo(cx+Math.cos(a)*maxR, cy+Math.sin(a)*maxR);
        ctx.stroke();
        ctx.restore();
    });

    // Data polygon (filled)
    const vals = RADAR_LABELS.map(l => Math.min(G.radarValues[l]||10, 100)/100);
    ctx.save();
    ctx.beginPath();
    angles.forEach((a,i) => {
        const r = vals[i]*maxR;
        const x = cx+Math.cos(a)*r, y = cy+Math.sin(a)*r;
        i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    });
    ctx.closePath();
    const fill = ctx.createRadialGradient(cx,cy,0,cx,cy,maxR);
    fill.addColorStop(0,'rgba(155,51,255,0.4)');
    fill.addColorStop(1,'rgba(100,0,200,0.1)');
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = `rgba(187,102,255,${0.7+Math.sin(t*1.5)*0.2})`;
    ctx.lineWidth = 1.5;
    ctx.shadowBlur = 10; ctx.shadowColor = '#9d33ff';
    ctx.stroke();
    ctx.restore();

    // Node dots + labels
    angles.forEach((a,i) => {
        const r = vals[i]*maxR;
        const x = cx+Math.cos(a)*r, y = cy+Math.sin(a)*r;
        // Node
        ctx.save();
        ctx.fillStyle = RADAR_COLORS[i];
        ctx.shadowBlur = 8; ctx.shadowColor = RADAR_COLORS[i];
        ctx.beginPath(); ctx.arc(x,y,4,0,Math.PI*2); ctx.fill();
        ctx.restore();
        // Label
        const lx = cx+Math.cos(a)*(maxR+14), ly = cy+Math.sin(a)*(maxR+14);
        ctx.save();
        ctx.font = 'bold 9px Share Tech Mono, monospace';
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillStyle = RADAR_COLORS[i];
        ctx.shadowBlur = 5; ctx.shadowColor = RADAR_COLORS[i];
        ctx.fillText(RADAR_LABELS[i], lx, ly);
        ctx.restore();
    });
}

/* ═══════════════════════════════════════════════════════════════════
   HEALTH GRID (pixel-style colored squares)
   ═══════════════════════════════════════════════════════════════════ */
const HEALTH_COLS = 7;
const HEALTH_ROWS = 4;
const STAT_COLORS = {
    0: '#ff6b6b', 1: '#cc88ff', 2: '#ffd700',
    3: '#44ff99', 4: '#ff6b6b', 5: '#44ddff', 6: '#cc88ff',
};

function buildHealthGrid() {
    const grid = document.getElementById('health-grid');
    if (!grid) return;
    grid.innerHTML = '';
    for (let r = 0; r < HEALTH_ROWS; r++) {
        for (let c = 0; c < HEALTH_COLS; c++) {
            const cell = document.createElement('div');
            cell.className = 'hg-cell';
            cell.id = `hg-${r}-${c}`;
            grid.appendChild(cell);
        }
    }
}

function updateHealthGrid(playerData) {
    const attrs = (playerData && playerData.attributes) ? playerData.attributes : {};
    const vals = [
        (attrs.strength     ||10)/100,
        (attrs.discipline   ||10)/100,
        (attrs.agility      ||10)/100,
        (attrs.intelligence ||10)/100,
        (attrs.strength     ||10)/100,
        (attrs.intelligence ||10)/100,
        attrs.focus ? attrs.focus/100 : (attrs.discipline||10)/100,
    ];
    for (let r = 0; r < HEALTH_ROWS; r++) {
        for (let c = 0; c < HEALTH_COLS; c++) {
            const cell = document.getElementById(`hg-${r}-${c}`);
            if (!cell) continue;
            const threshold = (HEALTH_ROWS - r) / HEALTH_ROWS;
            const lit = vals[c] >= threshold * 0.55;
            const alpha = lit ? (0.55 + vals[c]*0.45) : 0.05;
            const col = STAT_COLORS[c];
            cell.style.background = lit
                ? `rgba(${hexToRgb(col)},${alpha})`
                : 'rgba(30,0,60,0.15)';
            cell.style.borderColor = lit ? `${col}55` : 'rgba(100,0,200,0.12)';
            cell.style.color = col;
            cell.classList.toggle('lit', lit);
        }
    }
}

function hexToRgb(hex) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `${r},${g},${b}`;
}

/* ═══════════════════════════════════════════════════════════════════
   POTION BOTTLES (Market Place)
   ═══════════════════════════════════════════════════════════════════ */
function drawPotions() {
    [0,1,2].forEach(i => {
        const canvas = document.getElementById(`potion-${i}`);
        if (!canvas) return;
        drawPotion(canvas.getContext('2d'), G.potionColors[i], i);
    });
}

function drawPotion(ctx, color, idx) {
    const W = ctx.canvas.width, H = ctx.canvas.height;
    ctx.clearRect(0,0,W,H);
    const cx = W/2;
    const pulseScale = 1 + Math.sin(Date.now()*0.002 + idx)*0.03;

    ctx.save();
    ctx.translate(cx, H*0.5);
    ctx.scale(pulseScale, pulseScale);

    // Bottle body
    const bx = 0, by = 0;
    const bw = 20, bh = 36;
    const grad = ctx.createLinearGradient(-bw,0,bw,0);
    grad.addColorStop(0, 'rgba(10,0,22,0.9)');
    grad.addColorStop(0.3, color+'99');
    grad.addColorStop(0.7, color+'cc');
    grad.addColorStop(1, 'rgba(10,0,22,0.9)');
    ctx.fillStyle = grad;
    ctx.strokeStyle = color + 'aa';
    ctx.lineWidth = 1.5;
    ctx.shadowBlur = 14; ctx.shadowColor = color;

    // Rounded bottle shape
    ctx.beginPath();
    ctx.moveTo(-bw/2, -bh/2 + 6);
    ctx.quadraticCurveTo(-bw/2-6, 0, -bw/2+2, bh/2);
    ctx.quadraticCurveTo(bx, bh/2+6, bw/2-2, bh/2);
    ctx.quadraticCurveTo(bw/2+6, 0, bw/2, -bh/2+6);
    ctx.quadraticCurveTo(bw/4, -bh/2, bw/4, -bh/2-4);
    ctx.lineTo(-bw/4, -bh/2-4);
    ctx.quadraticCurveTo(-bw/4, -bh/2, -bw/2, -bh/2+6);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Cork
    ctx.fillStyle = '#aa8855';
    ctx.fillRect(-bw/4, -bh/2-10, bw/2, 7);
    ctx.strokeStyle = '#cc9966';
    ctx.lineWidth = 0.8;
    ctx.strokeRect(-bw/4, -bh/2-10, bw/2, 7);

    // Liquid level
    ctx.save();
    ctx.beginPath();
    ctx.rect(-bw/2+3, -bh/4, bw-6, bh/1.6);
    ctx.clip();
    ctx.fillStyle = color + '44';
    ctx.fillRect(-bw/2+3, -2, bw-6, bh/1.6);
    // Bubbles
    [[-4,-5,2],[3,4,1.5],[0,-10,1.8]].forEach(([bx2,by2,br]) => {
        ctx.fillStyle = color + '55';
        ctx.beginPath();
        ctx.arc(bx2, by2, br, 0, Math.PI*2);
        ctx.fill();
    });
    ctx.restore();

    // Shine
    ctx.save();
    const shine = ctx.createLinearGradient(-bw/2+4,-bh/2,bw/2-8,bh/2);
    shine.addColorStop(0,'rgba(255,255,255,0.18)');
    shine.addColorStop(0.4,'rgba(255,255,255,0.06)');
    shine.addColorStop(1,'transparent');
    ctx.fillStyle = shine;
    ctx.beginPath();
    ctx.ellipse(-bw/4, -2, 4, bh/2.5, -0.3, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();

    ctx.restore();
}

/* ═══════════════════════════════════════════════════════════════════
   CAPITAL REACTOR
   ═══════════════════════════════════════════════════════════════════ */
let reactorCtx, reactorTime = 0;

function initCapitalReactor() {
    const canvas = document.getElementById('reactor-canvas');
    if (!canvas || reactorCtx) return;
    canvas.width  = 300; canvas.height = 300;
    reactorCtx = canvas.getContext('2d');
}

function drawReactor(ts) {
    const ctx = reactorCtx;
    if (!ctx) return;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    const cx = W/2, cy = H/2;
    reactorTime = ts*0.001;
    ctx.clearRect(0,0,W,H);

    const td = G.treasuryData || {};
    const assetPct = (td.asset_pct||30)/100;
    const sustPct  = (td.sustenance_pct||40)/100;
    const liabPct  = (td.liability_pct||10)/100;
    const health   = (td.frugality_score||50)/100;

    // BG
    const bg = ctx.createRadialGradient(cx,cy,0,cx,cy,cx);
    bg.addColorStop(0, `rgba(40,0,80,${0.3+health*0.3})`);
    bg.addColorStop(1, 'rgba(7,0,16,0.95)');
    ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(cx,cy,cx,0,Math.PI*2); ctx.fill();

    // Core
    const coreR = 38 + health*22;
    const coreG = ctx.createRadialGradient(cx,cy,0,cx,cy,coreR);
    coreG.addColorStop(0, `rgba(155,51,255,${0.6+health*0.3})`);
    coreG.addColorStop(0.6,'rgba(100,0,200,0.3)');
    coreG.addColorStop(1, 'transparent');
    ctx.fillStyle = coreG;
    ctx.beginPath(); ctx.arc(cx,cy,coreR,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle = `rgba(187,102,255,${0.5+Math.sin(reactorTime*2)*0.3})`;
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(cx,cy,coreR,0,Math.PI*2); ctx.stroke();

    // Asset gold orbits
    const nAssets = Math.max(2, Math.round(assetPct*7));
    for (let i=0; i<nAssets; i++) {
        const a = (i/nAssets)*Math.PI*2 + reactorTime*0.7;
        const r = 65 + i*9;
        const x = cx+Math.cos(a)*r, y = cy+Math.sin(a)*(r*0.6);
        const g2 = ctx.createRadialGradient(x,y,0,x,y,10);
        g2.addColorStop(0,'rgba(255,215,0,0.9)'); g2.addColorStop(1,'transparent');
        ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(x,y,10,0,Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffd700'; ctx.beginPath(); ctx.arc(x,y,5,0,Math.PI*2); ctx.fill();
    }

    // Liability red dots
    for (let i=0; i<Math.round(liabPct*5); i++) {
        const a = -reactorTime*1.3 + (i/5)*Math.PI*2;
        const r = 55;
        const x = cx+Math.cos(a)*r, y = cy+Math.sin(a)*(r*0.55);
        ctx.fillStyle = 'rgba(255,34,85,0.8)';
        ctx.shadowBlur = 8; ctx.shadowColor = '#ff2255';
        ctx.beginPath(); ctx.arc(x,y,4,0,Math.PI*2); ctx.fill();
        ctx.shadowBlur = 0;
    }

    // Outer dashed ring
    ctx.save();
    ctx.strokeStyle = 'rgba(100,0,200,0.3)'; ctx.lineWidth = 1;
    ctx.setLineDash([4,8]); ctx.lineDashOffset = -reactorTime*20;
    ctx.beginPath(); ctx.arc(cx,cy,cx-5,0,Math.PI*2); ctx.stroke();
    ctx.restore();

    // Center text
    ctx.fillStyle = `rgba(200,160,255,${0.8+Math.sin(reactorTime*2)*0.2})`;
    ctx.font = 'bold 9px Cinzel, serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('CAPITAL', cx, cy-6);
    ctx.fillText('REACTOR', cx, cy+6);
}

/* ═══════════════════════════════════════════════════════════════════
   INTEL GLOBE
   ═══════════════════════════════════════════════════════════════════ */
let intelCtx, intelGlobeNodes = [], intelAngle = 0;

function initIntelGlobe() {
    const canvas = document.getElementById('intel-globe-canvas');
    if (!canvas || intelCtx) return;
    canvas.width  = canvas.offsetWidth  || 600;
    canvas.height = canvas.offsetHeight || 600;
    intelCtx = canvas.getContext('2d');
    intelGlobeNodes = Array.from({length:22}, () => ({
        phi: Math.random()*Math.PI*2,
        theta: Math.acos(2*Math.random()-1),
        active: Math.random()>0.4,
        pulse: Math.random()*Math.PI*2,
    }));
}

function drawIntelGlobe(ts) {
    const ctx = intelCtx;
    if (!ctx) return;
    const W = ctx.canvas.width, H = ctx.canvas.height;
    const cx = W/2, cy = H/2;
    const R = Math.min(cx,cy)*0.7;
    intelAngle = ts*0.0002;
    ctx.clearRect(0,0,W,H);

    ctx.strokeStyle = 'rgba(100,0,200,0.15)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(cx,cy,R,0,Math.PI*2); ctx.stroke();

    for (let i=0;i<6;i++) {
        const a = (i/6)*Math.PI + intelAngle;
        ctx.strokeStyle = 'rgba(100,0,200,0.07)'; ctx.lineWidth = 0.8;
        ctx.beginPath(); ctx.arc(cx,cy,R,a,a+Math.PI); ctx.stroke();
    }

    const vis = [];
    intelGlobeNodes.forEach(n => {
        const phi = n.phi + intelAngle;
        const x = cx + R*Math.sin(n.theta)*Math.cos(phi);
        const y = cy + R*Math.cos(n.theta);
        const depth = Math.sin(n.theta)*Math.sin(phi);
        if (depth < 0) return;
        const a = depth*0.9;
        const col = n.active ? '#bb66ff' : '#ff2255';
        ctx.fillStyle = `${col}${Math.round(a*255).toString(16).padStart(2,'0')}`;
        ctx.beginPath(); ctx.arc(x,y,n.active?5:3,0,Math.PI*2); ctx.fill();
        if (n.active) {
            const p = Math.sin(ts*0.003+n.pulse)*0.5+0.5;
            ctx.strokeStyle = `rgba(187,102,255,${a*p*0.5})`;
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.arc(x,y,5+p*8,0,Math.PI*2); ctx.stroke();
        }
        vis.push({x,y,depth,active:n.active});
    });

    for (let i=0;i<vis.length;i++) {
        for (let j=i+1;j<vis.length;j++) {
            const dx=vis[i].x-vis[j].x, dy=vis[i].y-vis[j].y;
            if (dx*dx+dy*dy<9000) {
                ctx.strokeStyle = `rgba(100,0,200,${Math.min(vis[i].depth,vis[j].depth)*0.3})`;
                ctx.lineWidth = 0.7;
                ctx.beginPath(); ctx.moveTo(vis[i].x,vis[i].y); ctx.lineTo(vis[j].x,vis[j].y); ctx.stroke();
            }
        }
    }
}

/* ═══════════════════════════════════════════════════════════════════
   LEVEL UP CINEMATIC
   ═══════════════════════════════════════════════════════════════════ */
async function triggerLevelUp(newLevel, newRank) {
    const ov = document.getElementById('levelup-overlay');
    document.getElementById('lu-level').textContent = `LEVEL ${newLevel}`;
    document.getElementById('lu-rank').textContent  = `RANK ${newRank||'?'} HUNTER`;
    ov.hidden = false;

    const lc = document.getElementById('lu-canvas');
    lc.width = innerWidth; lc.height = innerHeight;
    const lctx = lc.getContext('2d');
    const particles = Array.from({length:200},()=>({
        angle: Math.random()*Math.PI*2, speed: 3+Math.random()*7,
        r: 1+Math.random()*3, life:0, max:50+Math.random()*60,
        color: ['#9d33ff','#ffd700','#00e5ff','#ff44cc'][Math.floor(Math.random()*4)],
    }));
    const cx = innerWidth/2, cy = innerHeight/2;
    let frame = 0;
    const loop = () => {
        if (frame > 180) return;
        lctx.fillStyle = 'rgba(7,0,16,0.12)';
        lctx.fillRect(0,0,innerWidth,innerHeight);
        particles.forEach(p => {
            p.life++;
            if (p.life>p.max) { p.life=0; p.angle=Math.random()*Math.PI*2; p.speed=3+Math.random()*7; }
            const dist = p.life/p.max * 350;
            const a = 1-p.life/p.max;
            lctx.globalAlpha = a;
            lctx.fillStyle = p.color;
            lctx.shadowBlur = 6; lctx.shadowColor = p.color;
            lctx.beginPath();
            lctx.arc(cx+Math.cos(p.angle)*dist, cy+Math.sin(p.angle)*dist, p.r*a, 0, Math.PI*2);
            lctx.fill();
        });
        lctx.globalAlpha = 1;
        frame++;
        requestAnimationFrame(loop);
    };
    loop();
    playLevelUpSound();
    await delay(3200);
    ov.hidden = true;
}

/* ═══════════════════════════════════════════════════════════════════
   DATA LOOP
   ═══════════════════════════════════════════════════════════════════ */
function startDataLoop() {
    fetchAll();
    setInterval(fetchAll, 15000);
    setInterval(fetchLogs, 8000);
}

async function fetchAll() {
    await Promise.allSettled([fetchStats(), fetchTreasury()]);
    fetchLogs();
}

async function fetchStats() {
    try {
        const r = await fetch('/api/stats');
        const d = await r.json();
        if (!d || d.error) return;
        G.player = d;
        updateHUD(d);
        loadQuests(d);
        checkLevelUp(d);
    } catch(e) {}
}

async function fetchTreasury() {
    try {
        const r = await fetch('/api/treasury/summary');
        const d = await r.json();
        if (!d || d.error) return;
        G.treasuryData = d;
        updateMarket(d);
        // update reactor metrics if treasury is open
        if (G.currentView === 'treasury') updateReactorMetrics(d);
    } catch(e) {}
}

async function fetchLogs() {
    try {
        const r = await fetch(`/api/logs?last_idx=${G.logIdx}`);
        const d = await r.json();
        if (!d || !Array.isArray(d.logs)) return;
        G.logIdx = d.next_idx || G.logIdx;
        // Nothing visible on HUD for logs (could add a toast)
    } catch(e) {}
}

function checkLevelUp(d) {
    if (d.level && G.prevLevel > 0 && d.level > G.prevLevel) {
        triggerLevelUp(d.level, d.rank);
    }
    if (d.level) G.prevLevel = d.level;
}

/* ═══════════════════════════════════════════════════════════════════
   HUD UPDATE
   ═══════════════════════════════════════════════════════════════════ */
function updateHUD(d) {
    const attrs = d.attributes || {};
    const name  = d.hunter_name || 'APEX GHOST';

    setText('hunter-name',    name);
    setText('profile-name',   name);
    setText('rank-badge',     d.rank  || 'E');
    setText('level-num',      d.level || 1);
    setText('streak-val',     d.streak || 0);
    setText('streak-val2',    d.streak || 0);
    setText('gold-val',       `${d.gold||0}G`);
    setText('north-star',     d.north_star ? `"${d.north_star}"` : '"SET YOUR NORTH STAR"');

    // XP
    const xp = d.xp||0, xpMax = d.xp_threshold||1000;
    setText('xp-val', `${xp.toLocaleString()} / ${xpMax.toLocaleString()}`);
    setWidth('xp-fill', (xp/xpMax)*100);

    // Stat values (skills + attrs)
    const sMap = {
        str: attrs.strength    || 10,
        int: attrs.intelligence|| 10,
        agi: attrs.agility     || 10,
        dis: attrs.discipline  || 10,
        foc: attrs.focus || attrs.discipline || 10,
    };
    G.radarValues = {
        STR: sMap.str, INT: sMap.int, AGI: sMap.agi, DIS: sMap.dis, FOC: sMap.foc,
    };
    Object.entries(sMap).forEach(([k,v]) => {
        const val = Math.round(v);
        setText(`skv-${k}`, val);
        setWidth(`skb-${k}`, Math.min(val,100));
        setText(`av-${k}`,  val);
        setWidth(`ab-${k}`,  Math.min(val,100));
    });

    // Health grid
    updateHealthGrid(d);

    // Goal completion
    const quests = G.quests;
    const total = quests.length;
    const done  = quests.filter(q => questDone(q)).length;
    const pct   = total > 0 ? Math.round((done/total)*100) : 0;
    setText('goal-pct', `${pct}%`);
    setWidth('goal-bar', pct);
}

function updateMarket(d) {
    setText('mi-income-val', `R ${(d.monthly_income||0).toLocaleString()}`);
    setText('mi-runway-val', `${d.runway_months||0} mo`);
    setText('mi-score-val',  `${d.frugality_score||0}/100`);
    setText('tr-income',     `R ${(d.monthly_income||0).toLocaleString()}`);
    setText('tr-runway',     `${d.runway_months||0} mo`);
    setText('tr-frugality',  `${d.frugality_score||0}/100`);
    setText('tr-ratio',      `${d.kiyosaki_ratio||0}%`);
}

function updateReactorMetrics(d) { updateMarket(d); }

/* ═══════════════════════════════════════════════════════════════════
   QUEST RENDERING
   ═══════════════════════════════════════════════════════════════════ */
function questType(q) {
    const c = (q.category||q.quest_type||'').toLowerCase();
    if (c.includes('boss')) return 'boss';
    if (c.includes('habit')) return 'habit';
    return 'daily';
}
function questDone(q) {
    return q.status === 'completed' || q.completed === true;
}

function loadQuests(d) {
    G.quests = [...(d.daily_quests||[]), ...(d.weekly_quests||[])];
    renderQuestList(G.quests);
    renderQuestGrid(G.quests);
}

function renderQuestList(quests) {
    const el = document.getElementById('quest-list');
    if (!el) return;
    const active = quests.filter(q=>!questDone(q)).slice(0,5);
    el.innerHTML = '';
    if (!active.length) {
        el.innerHTML = '<div class="quest-empty">ALL CONTRACTS CLEARED ✓</div>'; return;
    }
    active.forEach(q => {
        const type = questType(q);
        const div = document.createElement('div');
        div.className = `q-item ${type==='boss'?'boss-q':type==='habit'?'habit-q':''}`;
        const safeTitle = q.title.replace(/'/g,'&#39;');
        div.innerHTML = `
            <div class="q-title">${q.title}</div>
            <span class="q-xp">+${q.xp_reward||50}XP</span>
            <button class="q-done-btn" onclick="completeQuest('${safeTitle}',event)" id="qb-${encodeURIComponent(q.title)}">✓</button>
        `;
        el.appendChild(div);
    });
}

function renderQuestGrid(quests) {
    const grid = document.getElementById('all-quest-grid');
    if (!grid) return;
    const filter = grid.dataset.filter || 'ALL';
    const filtered = filter==='ALL' ? quests : quests.filter(q=>questType(q)===filter.toLowerCase());
    grid.innerHTML = '';
    if (!filtered.length) {
        grid.innerHTML = '<div style="color:rgba(187,102,255,.3);font-family:var(--f-mono);font-size:.65rem;padding:20px">NO CONTRACTS IN THIS CATEGORY</div>';
        return;
    }
    filtered.forEach(q => {
        const type = questType(q);
        const done = questDone(q);
        const card = document.createElement('div');
        card.className = `aq-card ${type==='boss'?'boss-aq':type==='habit'?'habit-aq':''} ${done?'done-aq':''}`;
        const safeTitle = q.title.replace(/'/g,'&#39;');
        card.innerHTML = `
            <span class="aq-badge ${type}">${type.toUpperCase()}</span>
            <div class="aq-title">${q.title}</div>
            <div class="aq-desc">${q.description||'—'}</div>
            <div class="aq-footer">
                <span class="aq-xp">+${q.xp_reward||50} XP</span>
                ${!done
                    ? `<button class="aq-btn" onclick="completeQuest('${safeTitle}',event)" id="aqb-${encodeURIComponent(q.title)}">⚔ COMPLETE</button>`
                    : '<span style="color:var(--green);font-family:var(--f-mono);font-size:.6rem">✓ CLEARED</span>'}
            </div>
        `;
        grid.appendChild(card);
    });
}

async function completeQuest(title, ev) {
    ev?.stopPropagation();
    const sid = encodeURIComponent(title);
    document.querySelectorAll(`#qb-${sid}, #aqb-${sid}`).forEach(b=>{ b.disabled=true; b.textContent='...'; });
    try {
        const res = await fetch('/api/quests/toggle', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({title}),
        });
        const data = await res.json();
        if (data.status === 'success') {
            spawnXPParticles(50, ev);
            await delay(600);
            await fetchStats();
        } else {
            document.querySelectorAll(`#qb-${sid}, #aqb-${sid}`).forEach(b=>{ b.disabled=false; b.textContent='RETRY'; });
        }
    } catch(e) {
        document.querySelectorAll(`#qb-${sid}, #aqb-${sid}`).forEach(b=>{ b.disabled=false; b.textContent='RETRY'; });
    }
}

/* ═══════════════════════════════════════════════════════════════════
   TREASURY ACTIONS
   ═══════════════════════════════════════════════════════════════════ */
async function logTransaction() {
    const amount = parseFloat(document.getElementById('tr-amount')?.value);
    const desc   = document.getElementById('tr-desc')?.value||'';
    const type   = document.getElementById('tr-type')?.value||'sustenance';
    const dir    = document.getElementById('tr-direction')?.value||'expense';
    if (!amount||isNaN(amount)) return;
    const btn = document.getElementById('tr-submit-btn');
    if (btn) { btn.textContent='LOGGING...'; btn.disabled=true; }
    try {
        await fetch('/api/treasury/transactions/add',{
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({amount,description:desc,asset_type:type,direction:dir}),
        });
        document.getElementById('tr-amount').value='';
        document.getElementById('tr-desc').value='';
        await fetchTreasury();
    } catch(e) {}
    if (btn) { btn.textContent='LOG TRANSACTION'; btn.disabled=false; }
}

async function updateBudget() {
    const income = parseFloat(document.getElementById('tr-income-input')?.value);
    if (!income||isNaN(income)) return;
    try {
        await fetch('/api/treasury/budget/update',{
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({monthly_income:income,currency:'R'}),
        });
        await fetchTreasury();
    } catch(e) {}
}

async function runAudit() {
    const c = document.getElementById('audit-console');
    if (c) c.innerHTML = '<span style="color:var(--gold)">RUNNING AUDIT...<span style="animation:blink 1s step-end infinite">█</span></span>';
    try {
        const r = await fetch('/api/treasury/audit/run',{method:'POST'});
        const d = await r.json();
        if (c && d.audit) {
            c.innerHTML='';
            d.audit.split('\n').forEach((line,i)=>{
                setTimeout(()=>{
                    const div=document.createElement('div');
                    div.style.lineHeight='1.8';
                    div.innerHTML=line.replace(/\*\*(.*?)\*\*/g,'<strong style="color:var(--gold)">$1</strong>');
                    c.appendChild(div); c.scrollTop=c.scrollHeight;
                },i*35);
            });
        }
    } catch(e) { if (c) c.innerHTML='<span style="color:var(--red)">AUDIT FAILED</span>'; }
}

async function scanOpportunities() {
    const feed=document.getElementById('opp-feed');
    if (feed) feed.innerHTML='<div style="color:var(--p4);font-family:var(--f-mono);font-size:.62rem">SCANNING...</div>';
    try {
        const r=await fetch('/api/opportunities/scan',{method:'POST'});
        const d=await r.json();
        const opps=d.opportunities||[];
        if (feed) {
            feed.innerHTML='';
            opps.forEach(opp=>{
                const card=document.createElement('div'); card.className='opp-card';
                card.innerHTML=`<div class="opp-title">◎ ${opp.title||'Opportunity'}</div>
                    <div class="opp-body">${opp.service_solution||opp.loophole_summary||''}</div>
                    <button class="opp-accept" onclick="acceptOpp(${opp.id})">⚔ ACCEPT CONTRACT</button>`;
                feed.appendChild(card);
            });
            if (!opps.length) feed.innerHTML='<div class="dim-text" style="font-family:var(--f-mono);font-size:.6rem">No opportunities found — try later</div>';
        }
    } catch(e) { if (feed) feed.innerHTML='<div style="color:var(--red);font-family:var(--f-mono);font-size:.6rem">SCAN FAILED</div>'; }
}

async function acceptOpp(id) {
    try {
        const r=await fetch('/api/opportunities/accept',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({opportunity_id:id})});
        const d=await r.json();
        if (d.success) { await fetchStats(); }
    } catch(e){}
}

async function refreshIntelFeed() {
    const feed=document.getElementById('intel-feed');
    if (!feed) return;
    try {
        const r=await fetch('/api/opportunities/latest');
        const d=await r.json();
        if (!Array.isArray(d)||!d.length) { feed.innerHTML='<div class="dim-text">NO INTEL AVAILABLE</div>'; return; }
        feed.innerHTML='';
        d.forEach(item=>{
            const card=document.createElement('div'); card.className='intel-card';
            card.innerHTML=`<div class="intel-card-title">◉ ${item.title||'Record'}</div>${item.loophole_summary||item.service_solution||'—'}`;
            feed.appendChild(card);
        });
    } catch(e) { feed.innerHTML='<div class="dim-text">NETWORK UNREACHABLE</div>'; }
}

/* ═══════════════════════════════════════════════════════════════════
   NAV + OVERLAY
   ═══════════════════════════════════════════════════════════════════ */
function initNavDock() {
    document.querySelectorAll('.nav-btn').forEach(btn=>{
        btn.addEventListener('click',()=>{
            document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
            btn.classList.add('active');
            openOverlay(btn.dataset.view);
        });
    });
}

function openOverlay(view) {
    G.currentView = view;
    ['treasury','quests','intel','system'].forEach(id=>{
        const el=document.getElementById(`overlay-${id}`);
        if (el) el.hidden=true;
    });
    if (view==='hud') return;
    const ov=document.getElementById(`overlay-${view}`);
    if (ov) {
        ov.hidden=false;
        if (view==='treasury') { initCapitalReactor(); }
        if (view==='intel')    { initIntelGlobe(); refreshIntelFeed(); }
        if (view==='system')   { buildSystemGrid(); }
        if (view==='quests')   { renderQuestGrid(G.quests); }
    }
}

function closeOverlay(id) {
    const ov=document.getElementById(`overlay-${id}`);
    if (ov) ov.hidden=true;
    document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById('dock-hud')?.classList.add('active');
    G.currentView='hud';
}

function initQuestFilters() {
    document.querySelectorAll('.qf-btn').forEach(btn=>{
        btn.addEventListener('click',()=>{
            document.querySelectorAll('.qf-btn').forEach(b=>b.classList.remove('active'));
            btn.classList.add('active');
            const grid=document.getElementById('all-quest-grid');
            if (grid) grid.dataset.filter=btn.dataset.filter;
            renderQuestGrid(G.quests);
        });
    });
}

function buildSystemGrid() {
    const grid=document.getElementById('sys-grid');
    if (!grid) return;
    grid.innerHTML='';
    const mods=[
        {id:'neural',   name:'NEURAL ENGINE',   desc:'Cognitive processing core', online:true},
        {id:'voice',    name:'VOICE AI',         desc:'J.A.R.V.I.S. module', online:true},
        {id:'quest',    name:'QUEST ENGINE',     desc:'Daily contract generator', online:true},
        {id:'treasury', name:'TREASURY',         desc:'Capital reactor & finance AI', online:true},
        {id:'storage',  name:'STORAGE',          desc:'SQLite neural memory', online:true},
        {id:'scraper',  name:'INTEL SCRAPER',    desc:'Market surveillance feeds', online:true},
        {id:'auto',     name:'AUTOMATION',       desc:'OS macro scheduler', online:false},
        {id:'cloud',    name:'CLOUD SYNC',       desc:'Backup & cross-device sync', online:false},
    ];
    mods.forEach(m=>{
        const card=document.createElement('div'); card.className='sys-card';
        card.innerHTML=`
            <div class="sys-card-head">
                <div class="sys-status ${m.online?'online':'offline'}"></div>
                <div class="sys-name">${m.name}</div>
            </div>
            <div class="sys-desc">${m.desc}</div>
            <div class="sys-ping">${m.online?'● ONLINE':'○ OFFLINE'}</div>
        `;
        grid.appendChild(card);
    });
}

/* ═══════════════════════════════════════════════════════════════════
   MOUSE TRACKING
   ═══════════════════════════════════════════════════════════════════ */
function initMouseGlow() {
    window.addEventListener('mousemove', ev=>{
        G.mouseX = ev.clientX/innerWidth;
        G.mouseY = ev.clientY/innerHeight;
    });
}

/* ═══════════════════════════════════════════════════════════════════
   CLOCK
   ═══════════════════════════════════════════════════════════════════ */
function initClock() {
    const tick = ()=>{
        const n=new Date();
        setText('top-clock',`${pad(n.getHours())}:${pad(n.getMinutes())}:${pad(n.getSeconds())}`);
    };
    tick(); setInterval(tick,1000);
}
const pad = n=>String(n).padStart(2,'0');

/* ═══════════════════════════════════════════════════════════════════
   AUDIO
   ═══════════════════════════════════════════════════════════════════ */
function getAudio() {
    if (!G.audioCtx) { try { G.audioCtx=new(AudioContext||webkitAudioContext)(); }catch(e){} }
    return G.audioCtx;
}
function playBootSound() {
    const ctx=getAudio(); if(!ctx) return;
    [220,330,440,660].forEach((f,i)=>{
        const o=ctx.createOscillator(), g=ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.frequency.value=f; o.type='sine';
        const t=ctx.currentTime+i*0.12;
        g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(0.05,t+0.05); g.gain.linearRampToValueAtTime(0,t+0.35);
        o.start(t); o.stop(t+0.4);
    });
}
function playLevelUpSound() {
    const ctx=getAudio(); if(!ctx) return;
    [261,329,392,523,659,784,1047].forEach((f,i)=>{
        const o=ctx.createOscillator(), g=ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.frequency.value=f; o.type='triangle';
        const t=ctx.currentTime+i*0.09;
        g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(0.1,t+0.05); g.gain.linearRampToValueAtTime(0,t+0.4);
        o.start(t); o.stop(t+0.5);
    });
}

/* ═══════════════════════════════════════════════════════════════════
   XP PARTICLES
   ═══════════════════════════════════════════════════════════════════ */
function spawnXPParticles(xp, ev) {
    const x=ev?.clientX||innerWidth/2, y=ev?.clientY||innerHeight/2;
    for (let i=0;i<5;i++) {
        const s=document.createElement('div');
        s.className='xp-particle';
        s.textContent=`+${Math.round(xp/5)} XP`;
        s.style.left=x+(Math.random()-.5)*50+'px';
        s.style.top=y+(Math.random()-.5)*30+'px';
        s.style.setProperty('--dx',(Math.random()-.5)*80+'px');
        s.style.setProperty('--dy',-(60+Math.random()*60)+'px');
        s.style.animationDelay=i*0.08+'s';
        document.body.appendChild(s);
        setTimeout(()=>s.remove(),1500);
    }
}

/* ═══════════════════════════════════════════════════════════════════
   UTILS
   ═══════════════════════════════════════════════════════════════════ */
function setText(id,val) { const el=document.getElementById(id); if(el) el.textContent=val; }
function setWidth(id,pct) { const el=document.getElementById(id); if(el) el.style.width=Math.min(Math.max(pct,0),100)+'%'; }

/* ═══════════════════════════════════════════════════════════════════
   MASTER ANIMATION LOOP
   ═══════════════════════════════════════════════════════════════════ */
function masterLoop(ts) {
    drawBgStars(ts);
    drawAvatar(ts);
    drawRadar(ts);
    // Redraw potions with pulse
    if (Math.floor(ts/500) % 2 === 0) drawPotions();
    if (G.currentView==='treasury') drawReactor(ts);
    if (G.currentView==='intel')    drawIntelGlobe(ts);
    requestAnimationFrame(masterLoop);
}
