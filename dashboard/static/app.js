// Global parameters
let focusActive = false;
let terminalLogs = null;
let lastLogIndex = 0;

// Goals setup builder array
let builderGoals = [];

document.addEventListener("DOMContentLoaded", () => {
    // Preload the high-fidelity hologram image for 2D Canvas fallback
    window.characterHoloImg = new Image();
    window.characterHoloImg.onload = () => console.log("Hologram image loaded successfully");
    window.characterHoloImg.onerror = (e) => console.error("Hologram image failed to load", e);
    window.characterHoloImg.src = 'jinwoo.jpg?v=' + Date.now();

    terminalLogs = document.getElementById("terminal-logs");
    
    // 1. Initial REST fetch
    fetchStats();
    setInterval(fetchStats, 5000); // Poll stats every 5s

    // 2. Poll real-time logs from backend console redirect
    fetchLogs();
    setInterval(fetchLogs, 1000); // Poll logs every 1s

    // 3. Start J.A.R.V.I.S. Hologram Canvas Animations
    initAnimations();

    // 4. Bind Control Center Triggers
    initControlCenter();
});

// ==========================================
// TAB SWITCHING NAVIGATION
// ==========================================

function switchTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
    });
    // Remove active state from all tab headers
    document.querySelectorAll(".tab-link").forEach(link => {
        link.classList.remove("active");
        if (link.getAttribute("onclick").includes(`'${tabId}'`)) {
            link.classList.add("active");
        }
    });
    // Activate target pane
    document.getElementById(`pane-${tabId}`).classList.add("active");
    
    // Dispatch tab data loads
    if (tabId === "plan") {
        loadExecutionPlan();
    } else if (tabId === "intel") {
        loadLatestIntelligence();
    } else if (tabId === "goals") {
        loadGoalsFormDefaults();
    }
}

// ==========================================
// REST API DATA LOGIC (STATS & LOGS)
// ==========================================

async function fetchStats() {
    try {
        const response = await fetch("/api/stats");
        if (!response.ok) return;
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error("Error fetching stats:", error);
    }
}

function updateUI(data) {
    document.getElementById("hunter_name").textContent = data.hunter_name;
    document.getElementById("north-star").textContent = data.north_star || "NO ACTIVE YEARLY OBJECTIVES";
    document.getElementById("streak-val").textContent = data.streak;
    document.getElementById("gold-val").textContent = data.gold;

    if (data.attributes) {
        document.getElementById("hud-attributes").textContent = 
            `STR: ${data.attributes.strength} // INT: ${data.attributes.intelligence} // AGI: ${data.attributes.agility} // DIS: ${data.attributes.discipline}`;
    }
    
    const rankBadge = document.getElementById("rank-badge");
    rankBadge.textContent = data.rank;
    rankBadge.className = "rank-badge";
    if (data.rank === "S") {
        rankBadge.classList.add("rank-S");
    } else if (data.rank === "A" || data.rank === "B") {
        rankBadge.classList.add("rank-A");
    }

    document.getElementById("level-label").textContent = `LEVEL ${data.level} - HUNTER`;
    document.getElementById("xp-ratio").textContent = `${data.xp} / ${data.xp_threshold} XP`;
    const pct = Math.min((data.xp / data.xp_threshold) * 100, 100);
    document.getElementById("xp-bar-fill").style.width = `${pct}%`;

    focusActive = data.focus_active;
    const focusBtn = document.getElementById("btn-focus");
    const focusText = document.getElementById("btn-focus-text");
    if (focusActive) {
        focusBtn.classList.add("active-session");
        focusText.textContent = "DEACTIVATE FOCUS SESSION";
    } else {
        focusBtn.classList.remove("active-session");
        focusText.textContent = "INITIATE FOCUS SESSION";
    }

    const dailyContainer = document.getElementById("daily-quest-list");
    dailyContainer.innerHTML = "";
    if (data.daily_quests.length === 0) {
        dailyContainer.innerHTML = '<div class="quest-item"><span class="quest-title-text" style="color: var(--text-secondary);">No daily quests active.</span></div>';
    } else {
        data.daily_quests.forEach(q => {
            const isCompleted = q.status === "COMPLETED";
            const item = document.createElement("div");
            item.className = `quest-item ${isCompleted ? 'completed' : ''}`;
            item.innerHTML = `
                <div class="quest-checkbox"><span class="quest-checkmark">✓</span></div>
                <div class="quest-details">
                    <span class="quest-title-text">${q.title}</span>
                    <span class="quest-reward">+${q.xp_reward} XP</span>
                </div>
            `;
            item.addEventListener("click", () => toggleQuest(q.title, q.evidence_required, isCompleted));
            dailyContainer.appendChild(item);
        });
    }

    const focusContainer = document.getElementById("focus-history-list");
    focusContainer.innerHTML = "";
    if (data.focus_history.length === 0) {
        focusContainer.innerHTML = '<div class="focus-item"><span class="focus-time" style="color: var(--text-secondary);">No focus history recorded.</span></div>';
    } else {
        data.focus_history.forEach(session => {
            const dateStr = formatDate(new Date(session.start_time));
            const duration = calculateDuration(session.start_time, session.end_time);
            const isSuccess = session.completed === 1;

            const item = document.createElement("div");
            item.className = "focus-item";
            item.innerHTML = `
                <div class="focus-meta">
                    <span class="focus-time">${dateStr}</span>
                    <span class="focus-duration">${duration} deep work block</span>
                </div>
                <span class="focus-badge ${isSuccess ? 'badge-success' : 'badge-pending'}">
                    ${isSuccess ? 'COMPLETED' : 'INCOMPLETE'}
                </span>
            `;
            focusContainer.appendChild(item);
        });
    }
}

async function toggleQuest(title, evidence_required = false, isCompleted = false) {
    let evidence = "";
    if (evidence_required && !isCompleted) {
        evidence = prompt(`[Evidence Required]\nPlease provide proof for completing '${title}' (e.g., GitHub link, Strava URL, transaction ID):`);
        if (evidence === null || evidence.trim() === "") {
            logToTerminal(`[QUEST] Evidence submission cancelled for "${title}".`);
            return;
        }
    }
    
    try {
        const response = await fetch("/api/quests/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: title, evidence: evidence })
        });
        const respData = await response.json();
        
        if (response.ok) {
            logToTerminal(`[QUEST] ${respData.message}`);
            fetchStats();
        } else {
            logToTerminal(`[ERROR] ${respData.error}`);
            alert(`Evidence Rejected:\n${respData.error}`);
        }
    } catch (e) {
        logToTerminal(`[ERROR] Failed to toggle quest: ${e}`);
    }
}

// ==========================================
// CONTROL CENTER TRIGGERS
// ==========================================

function initControlCenter() {
    const focusBtn = document.getElementById("btn-focus");
    focusBtn.addEventListener("click", () => {
        if (focusActive) {
            triggerAction("stop_private_mode");
        } else {
            triggerAction("start_private_mode");
        }
    });
}

async function triggerAction(actionName) {
    logToTerminal(`[SYSTEM] Initializing command procedure: "${actionName.toUpperCase()}"...`);
    try {
        const response = await fetch("/api/actions/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: actionName })
        });
        const data = await response.json();
        
        if (data.status === "success") {
            logToTerminal(`[J.A.R.V.I.S.] ${data.message}`);
            fetchStats();
            // If triggering scraper, switch to intelligence tab after brief delay to let user see logs start
            if (actionName === "intelligence_brief") {
                setTimeout(() => {
                    switchTab("intel");
                }, 2000);
            }
        } else {
            logToTerminal(`[WARNING] Procedure aborted: ${data.message}`);
        }
    } catch (e) {
        logToTerminal(`[ERROR] Command protocol failed: ${e}`);
    }
}

// ==========================================
// EXECUTION PLAN DATA RETRIEVAL
// ==========================================

async function loadExecutionPlan() {
    try {
        const response = await fetch("/api/goals/plan");
        if (!response.ok) return;
        const data = await response.json();
        
        if (!data.active) {
            document.getElementById("plan-north-star").textContent = "NO YEARLY PLAN CREATED. Pls configure yearly goals wizard first.";
            document.getElementById("plan-hunter-name").textContent = "---";
            return;
        }

        document.getElementById("plan-hunter-name").textContent = data.profile_name;
        document.getElementById("plan-quarter").textContent = data.current_quarter;
        document.getElementById("plan-week").textContent = data.week_number;
        document.getElementById("plan-north-star").textContent = data.north_star;

        // Render monthly focus list
        const mList = document.getElementById("plan-monthly-focus-list");
        mList.innerHTML = data.monthly_focus.map(item => `<li>${item}</li>`).join("") || "<li>No focus points mapped.</li>";
        
        // Render weekly targets list
        const wList = document.getElementById("plan-weekly-targets-list");
        wList.innerHTML = data.weekly_targets.map(item => `<li>${item}</li>`).join("") || "<li>No weekly targets mapped.</li>";
        
        // Render today actions list
        const tList = document.getElementById("plan-today-actions-list");
        tList.innerHTML = data.today_actions.map(item => `<li>${item}</li>`).join("") || "<li>No today actions mapped.</li>";

        // Render detailed Yearly Goals backlog card blocks
        const backlogContainer = document.getElementById("plan-goals-backlog");
        backlogContainer.innerHTML = "";
        
        data.yearly_goals.forEach(goal => {
            const card = document.createElement("div");
            card.className = "goal-card-detail";
            
            // Map subitems
            const milestonesLi = goal.milestones.map(m => `<li>${m}</li>`).join("") || "<li>None decomposed yet</li>";
            const habitsLi = goal.daily_habits.map(h => `<li>${h}</li>`).join("") || "<li>None mapped</li>";

            card.innerHTML = `
                <div class="goal-card-header">
                    <span class="goal-card-title">${goal.title}</span>
                    <span class="goal-category-tag">${goal.category}</span>
                </div>
                <div class="goal-card-body">
                    <p>${goal.description || 'No description provided.'}</p>
                    <div class="goal-meta-grid">
                        <div class="goal-meta-field">
                            <span>METRIC OUTCOME</span>
                            ${goal.success_metric || '---'}
                        </div>
                        <div class="goal-meta-field">
                            <span>DEADLINE</span>
                            ${goal.deadline} (Priority: ${goal.priority})
                        </div>
                    </div>
                    <div class="goal-decomposed-sublists">
                        <div>
                            <span>📍 Quarterly Milestones:</span>
                            <ul>${milestonesLi}</ul>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span>⚡ Core Daily Habits:</span>
                            <ul>${habitsLi}</ul>
                        </div>
                    </div>
                </div>
            `;
            backlogContainer.appendChild(card);
        });

        // Query shadow journal captures list
        try {
            const jRes = await fetch("/api/journal/latest");
            if (jRes.ok) {
                const jData = await jRes.json();
                const jList = document.getElementById("plan-journal-captures-list");
                jList.innerHTML = jData.map(item => {
                    const label = item.category === "bug_fix" ? "BUG" : "NOTE";
                    const color = item.category === "bug_fix" ? "var(--rose)" : "var(--cyan)";
                    return `<li style="margin-bottom: 0.35rem; font-family: 'Consolas', monospace; font-size: 0.8rem;">
                        <span style="color: ${color}; font-weight: bold;">[${label}]</span> ${item.content}
                    </li>`;
                }).join("") || "<li>No quick captures recorded. Press Win+J to add.</li>";
            }
        } catch (je) {
            console.error("Error loading journal captures:", je);
        }

    } catch (e) {
        console.error("Failed to load execution plan:", e);
    }
}

// ==========================================
// GOALS WIZARD BUILDER FORM LOGIC
// ==========================================

async function loadGoalsFormDefaults() {
    // Fill in defaults automatically
    document.getElementById("input-target-year").value = new Date().getFullYear();
    document.getElementById("build-deadline").value = new Date(new Date().getFullYear(), 11, 31).toISOString().split("T")[0]; // Dec 31
    
    // Fetch stats to fill name
    try {
        const r = await fetch("/api/stats");
        if (r.ok) {
            const d = await r.json();
            document.getElementById("input-hunter-name").value = d.hunter_name || "Hunter";
            document.getElementById("input-north-star").value = d.north_star || "";
        }
    } catch(e){}
}

function addGoalToBuilder() {
    const title = document.getElementById("build-title").value.trim();
    const category = document.getElementById("build-category").value;
    const description = document.getElementById("build-desc").value.trim();
    const successMetric = document.getElementById("build-metric").value.trim();
    const priority = document.getElementById("build-priority").value;
    const deadline = document.getElementById("build-deadline").value;

    if (!title) {
        alert("Objective Title is required!");
        return;
    }
    if (!deadline) {
        alert("Target Deadline date is required!");
        return;
    }

    const goalObj = {
        title: title,
        category: category,
        description: description,
        success_metric: successMetric,
        priority: priority,
        deadline: deadline
    };

    builderGoals.push(goalObj);
    renderBuilderList();

    // Clear builder inputs for next entry
    document.getElementById("build-title").value = "";
    document.getElementById("build-desc").value = "";
    document.getElementById("build-metric").value = "";
    document.getElementById("build-priority").value = "3";
}

function removeGoalFromBuilder(index) {
    builderGoals.splice(index, 1);
    renderBuilderList();
}

function renderBuilderList() {
    document.getElementById("builder-count").textContent = builderGoals.length;
    const container = document.getElementById("added-goals-list");
    container.innerHTML = "";

    builderGoals.forEach((goal, idx) => {
        const row = document.createElement("div");
        row.className = "added-goal-row";
        row.innerHTML = `
            <div class="added-goal-meta">
                <span class="added-goal-title">${goal.title}</span>
                <span class="added-goal-category">${goal.category} // Priority ${goal.priority} // Target: ${goal.deadline}</span>
            </div>
            <button type="button" class="btn-remove-goal" onclick="removeGoalFromBuilder(${idx})">REMOVE</button>
        `;
        container.appendChild(row);
    });
}

async function submitGoalsConfig(event) {
    event.preventDefault();
    
    if (builderGoals.length === 0) {
        alert("You must add at least one yearly objective before syncing!");
        return;
    }

    const payload = {
        hunter_name: document.getElementById("input-hunter-name").value.trim(),
        target_year: document.getElementById("input-target-year").value,
        north_star: document.getElementById("input-north-star").value.trim(),
        goals: builderGoals
    };

    try {
        logToTerminal("[SYSTEM] Sending goals configuration mapping to database...");
        const response = await fetch("/api/goals/setup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (data.status === "success") {
            logToTerminal(`[J.A.R.V.I.S.] Goals tree synced. Profile: ${payload.hunter_name}`);
            // Clear builder list
            builderGoals = [];
            renderBuilderList();
            
            // Re-poll stats and navigate to plan view
            fetchStats();
            switchTab("plan");
        } else {
            logToTerminal(`[WARNING] Goals sync failed: ${data.error}`);
        }
    } catch(e) {
        logToTerminal(`[ERROR] Connection error during goals setup: ${e}`);
    }
}

// ==========================================
// INTELLIGENCE BRIEF DATA LOADER
// ==========================================

async function loadLatestIntelligence() {
    const metaBox = document.getElementById("intel-brief-meta");
    const dataGrid = document.getElementById("intel-brief-data");

    try {
        const response = await fetch("/api/intelligence/latest");
        if (!response.ok) return;
        const data = await response.json();

        if (!data.active) {
            metaBox.style.display = "block";
            dataGrid.style.display = "none";
            metaBox.textContent = 'Intelligence brief compilation not yet completed in this runtime. Go to STATS HUD and click "SCRAPE INTEL BRIEF" to run scanner feeds.';
            return;
        }

        // Show brief details
        metaBox.style.display = "block";
        dataGrid.style.display = "grid";

        metaBox.innerHTML = `REPORT LEVEL: SECURE // COMPILED AT: ${data.brief.generated_at} // DISCOVERED FEED TARGETS: ${data.brief.total_items}`;
        
        // Renders trends summary content
        document.getElementById("intel-trend-summary-text").textContent = data.brief.trend_summary;

        // Renders security findings list
        const secContainer = document.getElementById("intel-security-findings-list");
        secContainer.innerHTML = "";

        if (data.brief.security_findings.length === 0) {
            secContainer.innerHTML = '<div class="intel-security-item" style="background: rgba(16,185,129,0.05); border-color: rgba(16,185,129,0.15);"><span class="security-item-title" style="color: var(--emerald);">NO SYSTEM THREAT THRESHOLDS EXCEEDED</span></div>';
        } else {
            data.brief.security_findings.forEach(f => {
                const card = document.createElement("div");
                card.className = "intel-security-item";
                card.innerHTML = `
                    <div class="security-item-header">
                        <span class="security-item-title">${f.title}</span>
                        <span class="security-sentiment-badge">ALERT</span>
                    </div>
                    <span class="security-item-source">Source: ${f.source}</span>
                    <a href="${f.url}" target="_blank" class="security-item-link">Open thread targets &gt;&gt;</a>
                `;
                secContainer.appendChild(card);
            });
        }

    } catch (e) {
        console.error("Failed to load latest intelligence:", e);
    }
}

// ==========================================
// THREE.JS OPEN SOURCE WEBGL 3D CHARACTER ENGINE
// ==========================================

function initThreeJSCharacter() {
    const canvas = document.getElementById("canvas-character-3d");
    if (!canvas || typeof THREE === "undefined") return false;

    try {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, canvas.width / canvas.height, 0.1, 1000);
        camera.position.set(0, 1.1, 8.2);

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(canvas.width, canvas.height);
        renderer.setPixelRatio(window.devicePixelRatio || 1);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xa855f7, 0.9);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xc084fc, 1.8);
        dirLight.position.set(5, 10, 7);
        scene.add(dirLight);

        const pointLight = new THREE.PointLight(0xffffff, 2.5, 12);
        pointLight.position.set(0, 2.5, 3);
        scene.add(pointLight);

        // Parent Character Group for 360 Rotation
        const characterGroup = new THREE.Group();
        scene.add(characterGroup);

        // Materials
        const wireframeMat = new THREE.MeshBasicMaterial({ color: 0xc084fc, wireframe: true });
        const solidArmorMat = new THREE.MeshPhongMaterial({ 
            color: 0x3b0764, 
            emissive: 0x6b21a8,
            wireframe: true,
            transparent: true,
            opacity: 0.8
        });
        const glowEyeMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const daggerMat = new THREE.MeshPhongMaterial({ color: 0xffffff, emissive: 0xc084fc, wireframe: true });

        // 1. High-Fidelity Character Illustration (Hologram Plane)
        const textureLoader = new THREE.TextureLoader();
        const characterTex = textureLoader.load('jinwoo.png');
        
        const planeGeo = new THREE.PlaneGeometry(6.5, 6.5);
        const planeMat = new THREE.MeshBasicMaterial({ 
            map: characterTex, 
            color: 0xffffff,
            transparent: true,
            blending: THREE.AdditiveBlending,
            side: THREE.DoubleSide
        });
        
        // Use two intersecting planes (a cross) so it never completely disappears when viewed edge-on!
        const characterPlane1 = new THREE.Mesh(planeGeo, planeMat);
        const characterPlane2 = new THREE.Mesh(planeGeo, planeMat);
        characterPlane2.rotation.y = Math.PI / 2; // Intersecting at 90 degrees
        
        // Group them to apply bobbing easily
        const characterSprite = new THREE.Group();
        characterSprite.add(characterPlane1);
        characterSprite.add(characterPlane2);
        
        characterSprite.position.y = 1.2;
        
        // Add to characterGroup so it rotates 360 degrees!
        characterGroup.add(characterSprite);

        // 6. Concentric Floor Rings
        const ringGeo1 = new THREE.RingGeometry(1.5, 1.55, 32);
        const ringGeo2 = new THREE.RingGeometry(2.2, 2.25, 32);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xa855f7, side: THREE.DoubleSide });
        const ring1 = new THREE.Mesh(ringGeo1, ringMat);
        const ring2 = new THREE.Mesh(ringGeo2, ringMat);
        ring1.rotation.x = Math.PI / 2;
        ring2.rotation.x = Math.PI / 2;
        ring1.position.y = -1.15;
        ring2.position.y = -1.15;
        characterGroup.add(ring1);
        characterGroup.add(ring2);

        // 7. Rising Shadow Monarch Particle Aura
        const particleCount = 200;
        const particleGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 3.5;
            positions[i + 1] = (Math.random() - 0.5) * 4.0;
            positions[i + 2] = (Math.random() - 0.5) * 3.5;
        }
        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particleMat = new THREE.PointsMaterial({ color: 0xc084fc, size: 0.09, transparent: true, opacity: 0.85 });
        const particleSystem = new THREE.Points(particleGeo, particleMat);
        characterGroup.add(particleSystem);

        // 60 FPS WebGL Render Loop
        let bobTime = 0;
        function animate() {
            requestAnimationFrame(animate);
            characterGroup.rotation.y += 0.012;
            
            // Character floating bob animation
            bobTime += 0.03;
            characterSprite.position.y = 1.2 + Math.sin(bobTime) * 0.15;
            
            // Particles drift upwards
            const pos = particleGeo.attributes.position.array;
            for (let i = 1; i < particleCount * 3; i += 3) {
                pos[i] += 0.015;
                if (pos[i] > 3.0) pos[i] = -1.2;
            }
            particleGeo.attributes.position.needsUpdate = true;

            renderer.render(scene, camera);
        }
        animate();
        return true;
    } catch (err) {
        console.error("Three.js init error:", err);
        return false;
    }
}

// ==========================================
// HOLOGRAPHIC CANVAS ANIMATIONS
// ==========================================

function initAnimations() {
    const characterCanvas = document.getElementById("canvas-character-3d");
    const characterCtx = characterCanvas ? characterCanvas.getContext("2d") : null;
    
    const hexRadarCanvas = document.getElementById("canvas-radar-hex");
    const hexRadarCtx = hexRadarCanvas ? hexRadarCanvas.getContext("2d") : null;

    const globeCanvas = document.getElementById("canvas-globe");
    const globeCtx = globeCanvas ? globeCanvas.getContext("2d") : null;
    
    const radarCanvas = document.getElementById("canvas-radar");
    const radarCtx = radarCanvas ? radarCanvas.getContext("2d") : null;
    
    const waveCanvas = document.getElementById("canvas-waveform");
    const waveCtx = waveCanvas ? waveCanvas.getContext("2d") : null;

    let rotation = 0;
    let sweepAngle = 0;

    const blips = [
        { r: 75, angle: 1.2, size: 4, label: "IDE", opacity: 0 },
        { r: 120, angle: 3.5, size: 5, label: "GUARD", opacity: 0 },
        { r: 50, angle: 5.1, size: 3, label: "DB", opacity: 0 }
    ];

    // Shadow Monarch particles for 3D character
    const auraParticles = Array.from({ length: 35 }, () => ({
        x: (Math.random() - 0.5) * 80,
        y: -130 + Math.random() * 260,
        z: (Math.random() - 0.5) * 80,
        speed: 0.8 + Math.random() * 1.2,
        size: 1.5 + Math.random() * 2.5,
        opacity: Math.random()
    }));

    // Initialize Three.js WebGL 3D Hunter Model
    const threeSuccess = initThreeJSCharacter();

    function drawLoop() {
        rotation += 0.012;
        sweepAngle = (sweepAngle + 0.02) % (2 * Math.PI);
        
        if (!threeSuccess && characterCtx) {
            draw3DCharacterHologram(characterCtx, characterCanvas.width, characterCanvas.height, rotation, auraParticles);
        }
        
        if (hexRadarCtx) {
            drawHexAttributeRadar(hexRadarCtx, hexRadarCanvas.width, hexRadarCanvas.height);
        }

        if (globeCtx) {
            drawHologlobe(globeCtx, globeCanvas.width, globeCanvas.height, rotation);
        }

        if (radarCtx) {
            drawHoloRadar(radarCtx, radarCanvas.width, radarCanvas.height, sweepAngle, blips);
        }

        if (waveCtx) {
            drawHoloWaveform(waveCtx, waveCanvas.width, waveCanvas.height);
        }
        
        updateCoordinates();
        requestAnimationFrame(drawLoop);
    }
    requestAnimationFrame(drawLoop);
}

// ----------------------------------------------------
// 360° 3D SHADOW MONARCH CHARACTER HOLOGRAM RENDERER
// ----------------------------------------------------
function project3D(x, y, z, rotY, cx, cy) {
    const cos = Math.cos(rotY);
    const sin = Math.sin(rotY);
    
    // Rotate around Y axis
    const xRot = x * cos - z * sin;
    const zRot = x * sin + z * cos;
    const yRot = y;
    
    // Perspective projection
    const fov = 350;
    const scale = fov / (fov - zRot);
    const screenX = cx + xRot * scale;
    const screenY = cy - yRot * scale;
    
    return { x: screenX, y: screenY, z: zRot, scale: scale };
}

function draw3DCharacterHologram(ctx, width, height, rot, auraParticles) {
    ctx.clearRect(0, 0, width, height);
    const cx = width / 2;
    const cy = height / 2 + 10;
    
    // 1. Draw Rising Shadow Monarch Aura Particles
    auraParticles.forEach(p => {
        p.y += p.speed;
        if (p.y > 130) {
            p.y = -130;
            p.x = (Math.random() - 0.5) * 80;
            p.z = (Math.random() - 0.5) * 80;
        }
        const pt = project3D(p.x, p.y, p.z, rot, cx, cy);
        const alpha = Math.sin((p.y + 130) / 260 * Math.PI) * 0.7;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, Math.max(0.5, p.size * pt.scale), 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(168, 85, 247, ${alpha})`;
        ctx.shadowColor = "#a855f7";
        ctx.shadowBlur = 8;
        ctx.fill();
    });
    ctx.shadowBlur = 0;

    // 2. Draw Floor Concentric 3D Rings & Solo Leveling Runes
    for (let r of [90, 65, 40]) {
        ctx.beginPath();
        for (let a = 0; a <= 2 * Math.PI; a += 0.15) {
            const rx = r * Math.cos(a);
            const rz = r * Math.sin(a);
            const pt = project3D(rx, -135, rz, rot * 0.5, cx, cy);
            if (a === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.closePath();
        ctx.strokeStyle = "rgba(168, 85, 247, 0.35)";
        ctx.lineWidth = 1.4;
        ctx.stroke();
    }

    // 3. Draw Holographic Character Illustration (instead of manual lines)
    if (window.characterHoloImg && window.characterHoloImg.complete && window.characterHoloImg.naturalWidth !== 0) {
        // Calculate a simulated 3D rotation scale (Y-axis rotation) for 360 spin
        const scaleX = Math.cos(rot);
        
        ctx.save();
        ctx.translate(cx, cy - 30);
        
        // Apply the 360 degree spin rotation
        ctx.scale(scaleX, 1);
        
        const imgW = 300; 
        const imgH = 300; 
        
        // Add a floating bob effect
        const bob = Math.sin(Date.now() / 400) * 8;
        
        // Normal blending to ensure image is visible regardless of background color
        ctx.globalCompositeOperation = "source-over"; 
        ctx.globalAlpha = 0.95;
        ctx.drawImage(window.characterHoloImg, -imgW/2, -imgH/2 + bob, imgW, imgH);
        
        ctx.restore();
    }
}

// ----------------------------------------------------
// SOLO LEVELING HEXAGONAL ATTRIBUTE RADAR CHART
// ----------------------------------------------------
function drawHexAttributeRadar(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    const cx = width / 2;
    const cy = height / 2;
    const radius = 75;

    const attributes = [
        { name: "STRENGTH", val: 88, max: 100 },
        { name: "INTELLIGENCE", val: 30, max: 100 },
        { name: "AGILITY", val: 40, max: 100 },
        { name: "PERCEPTION", val: 10, max: 100 },
        { name: "ENDURANCE", val: 10, max: 100 },
        { name: "FOCUS", val: 10, max: 100 }
    ];

    const numAxes = attributes.length;

    // 1. Concentric Grid Hexagons
    for (let level = 0.25; level <= 1.0; level += 0.25) {
        ctx.beginPath();
        for (let i = 0; i < numAxes; i++) {
            const angle = (i * 2 * Math.PI / numAxes) - Math.PI / 2;
            const x = cx + radius * level * Math.cos(angle);
            const y = cy + radius * level * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.strokeStyle = "rgba(168, 85, 247, 0.18)";
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // 2. Axes Lines
    for (let i = 0; i < numAxes; i++) {
        const angle = (i * 2 * Math.PI / numAxes) - Math.PI / 2;
        const x = cx + radius * Math.cos(angle);
        const y = cy + radius * Math.sin(angle);
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(x, y);
        ctx.strokeStyle = "rgba(168, 85, 247, 0.3)";
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // 3. Attribute Value Polygon
    ctx.beginPath();
    const polyPoints = [];
    for (let i = 0; i < numAxes; i++) {
        const angle = (i * 2 * Math.PI / numAxes) - Math.PI / 2;
        const ratio = attributes[i].val / attributes[i].max;
        const x = cx + radius * ratio * Math.cos(angle);
        const y = cy + radius * ratio * Math.sin(angle);
        polyPoints.push({ x, y });
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();

    // Purple Gradient Fill
    const grad = ctx.createRadialGradient(cx, cy, 5, cx, cy, radius);
    grad.addColorStop(0, "rgba(192, 132, 252, 0.55)");
    grad.addColorStop(1, "rgba(168, 85, 247, 0.2)");
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.strokeStyle = "#c084fc";
    ctx.lineWidth = 2.5;
    ctx.shadowColor = "#a855f7";
    ctx.shadowBlur = 10;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // 4. Vertex Points & Labels
    polyPoints.forEach((pt, i) => {
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = "#ffffff";
        ctx.shadowColor = "#c084fc";
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;

        const angle = (i * 2 * Math.PI / numAxes) - Math.PI / 2;
        const labelR = radius + 22;
        const lx = cx + labelR * Math.cos(angle);
        const ly = cy + labelR * Math.sin(angle);

        ctx.font = "bold 9px 'Rajdhani', sans-serif";
        ctx.fillStyle = "#e9d5ff";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(attributes[i].name, lx, ly - 6);
        
        ctx.font = "bold 12px 'Rajdhani', sans-serif";
        ctx.fillStyle = "#a855f7";
        ctx.fillText(attributes[i].val.toString(), lx, ly + 6);
    });
}

function drawHologlobe(ctx, width, height, rot) {
    ctx.clearRect(0, 0, width, height);
    const cx = width / 2;
    const cy = height / 2;
    const radius = 130;
    
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = "rgba(0, 242, 254, 0.08)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    for (let lat = -Math.PI/2 + 0.3; lat < Math.PI/2; lat += 0.35) {
        const yOffset = radius * Math.sin(lat);
        const ellipseRadius = radius * Math.cos(lat);
        ctx.beginPath();
        ctx.ellipse(cx, cy + yOffset, ellipseRadius, ellipseRadius * 0.2, 0, 0, 2 * Math.PI);
        ctx.strokeStyle = "rgba(0, 242, 254, 0.15)";
        ctx.lineWidth = 1;
        ctx.stroke();
    }
    
    for (let lon = 0; lon < Math.PI; lon += Math.PI/6) {
        const offsetAngle = lon + rot;
        const ellipseWidth = radius * Math.sin(offsetAngle);
        ctx.beginPath();
        ctx.ellipse(cx, cy, Math.abs(ellipseWidth), radius, 0, 0, 2 * Math.PI);
        const isFront = Math.cos(offsetAngle) >= 0;
        ctx.strokeStyle = isFront ? "rgba(0, 242, 254, 0.25)" : "rgba(0, 242, 254, 0.06)";
        ctx.lineWidth = isFront ? 1.2 : 0.8;
        ctx.stroke();
    }
    
    ctx.beginPath();
    ctx.moveTo(cx, cy - radius - 15);
    ctx.lineTo(cx, cy + radius + 15);
    ctx.strokeStyle = "rgba(0, 242, 254, 0.25)";
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.stroke();
    ctx.setLineDash([]);
    
    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, 2 * Math.PI);
    ctx.fillStyle = "rgba(0, 242, 254, 0.12)";
    ctx.fill();
    ctx.strokeStyle = "var(--cyan)";
    ctx.stroke();
}

function drawHoloRadar(ctx, width, height, sweep, blips) {
    ctx.clearRect(0, 0, width, height);
    const cx = width / 2;
    const cy = height / 2;
    const maxRadius = 100;
    
    ctx.beginPath();
    ctx.rect(cx - maxRadius - 10, cy - maxRadius - 10, (maxRadius + 10)*2, (maxRadius + 10)*2);
    ctx.strokeStyle = "rgba(0, 242, 254, 0.04)";
    ctx.stroke();
    
    for (let r = 25; r <= maxRadius; r += 25) {
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, 2 * Math.PI);
        ctx.strokeStyle = "rgba(0, 242, 254, 0.08)";
        ctx.stroke();
    }
    
    ctx.beginPath();
    ctx.moveTo(cx - maxRadius, cy);
    ctx.lineTo(cx + maxRadius, cy);
    ctx.moveTo(cx, cy - maxRadius);
    ctx.lineTo(cx, cy + maxRadius);
    ctx.strokeStyle = "rgba(0, 242, 254, 0.08)";
    ctx.stroke();
    
    const sx = cx + maxRadius * Math.cos(sweep);
    const sy = cy + maxRadius * Math.sin(sweep);
    
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, maxRadius, sweep, sweep - 0.35, true);
    ctx.closePath();
    ctx.fillStyle = "rgba(0, 242, 254, 0.06)";
    ctx.fill();
    
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(sx, sy);
    ctx.strokeStyle = "var(--cyan)";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    
    blips.forEach(blip => {
        const bx = cx + blip.r * Math.cos(blip.angle);
        const by = cy + blip.r * Math.sin(blip.angle);
        let diff = sweep - blip.angle;
        if (diff < 0) diff += 2 * Math.PI;
        
        if (diff < 0.15) {
            blip.opacity = 1.0;
        } else {
            blip.opacity = Math.max(0, blip.opacity - 0.005);
        }
        
        if (blip.opacity > 0) {
            ctx.beginPath();
            ctx.arc(bx, by, blip.size, 0, 2 * Math.PI);
            ctx.fillStyle = `rgba(0, 242, 254, ${blip.opacity})`;
            ctx.fill();
            
            ctx.beginPath();
            ctx.arc(bx, by, blip.size + 4, 0, 2 * Math.PI);
            ctx.strokeStyle = `rgba(0, 242, 254, ${blip.opacity * 0.35})`;
            ctx.stroke();
            
            ctx.font = "8px Consolas";
            ctx.fillStyle = `rgba(242, 201, 76, ${blip.opacity * 0.85})`;
            ctx.fillText(blip.label, bx + 8, by + 3);
        }
    });
}

function drawHoloWaveform(ctx, width, height) {
    ctx.clearRect(0, 0, width, height);
    const centerY = height / 2;
    const time = Date.now() * 0.004;
    ctx.lineWidth = 1.5;
    
    ctx.beginPath();
    ctx.strokeStyle = "rgba(0, 242, 254, 0.4)";
    for (let x = 0; x < width; x++) {
        const y = centerY + Math.sin(x * 0.02 + time) * 12 * Math.sin(x * 0.005);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
    
    ctx.beginPath();
    ctx.strokeStyle = "rgba(0, 242, 254, 0.15)";
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x++) {
        const y = centerY + Math.sin(x * 0.035 - time * 0.8) * 8 * Math.sin(x * 0.003);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
}

function updateCoordinates() {
    const lat = (34.0522 + (Math.random() - 0.5) * 0.0002).toFixed(6);
    const lon = (-118.2437 + (Math.random() - 0.5) * 0.0002).toFixed(6);
    document.getElementById("hud-coordinates").textContent = `LAT: ${lat} // LON: ${lon} // CHNL: SECURE_F3`;
}

// ==========================================
// CONSOLE LOG CONVERTER
// ==========================================

async function fetchLogs() {
    try {
        const response = await fetch(`/api/logs?last_idx=${lastLogIndex}`);
        if (!response.ok) return;
        const data = await response.json();
        if (data.logs && data.logs.length > 0) {
            data.logs.forEach(logLine => {
                appendLogLine(logLine);
            });
            lastLogIndex = data.next_idx;
        }
    } catch (error) {
        console.error("Error fetching logs:", error);
    }
}

function appendLogLine(logLine) {
    if (!terminalLogs) return;
    
    let timeStr = "";
    let message = logLine;
    
    if (logLine.startsWith("[")) {
        const closeBracketIdx = logLine.indexOf("]");
        if (closeBracketIdx !== -1) {
            timeStr = logLine.substring(1, closeBracketIdx);
            message = logLine.substring(closeBracketIdx + 1).trim();
        }
    }
    
    const div = document.createElement("div");
    if (timeStr) {
        div.innerHTML = `<span class="log-time">[${timeStr}]</span> ${message}`;
    } else {
        div.textContent = message;
    }
    
    terminalLogs.appendChild(div);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
}

function logToTerminal(text) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour12: false });
    appendLogLine(`[${timeStr}] ${text}`);
}

// ==========================================
// UTILITIES
// ==========================================

function formatDate(dateObj) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    if (dateObj.toDateString() === today.toDateString()) {
        return `Today, ${timeStr}`;
    } else if (dateObj.toDateString() === yesterday.toDateString()) {
        return `Yesterday, ${timeStr}`;
    } else {
        return `${dateObj.toLocaleDateString([], { month: 'short', day: 'numeric' })}, ${timeStr}`;
    }
}

function calculateDuration(startStr, endStr) {
    if (!endStr) return "Active...";
    const start = new Date(startStr);
    const end = new Date(endStr);
    const diffMins = Math.floor((end - start) / 60000);
    return diffMins < 1 ? "Under a minute" : `${diffMins} min`;
}
