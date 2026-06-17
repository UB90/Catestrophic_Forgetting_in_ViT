// ==========================================================================
//  Global State & Templates
// ==========================================================================
let projectData = null;

const TEMPLATES = {
    default: `// Preprocessing script for Office-31
count dataset "Office-31"

detail dataset "Office-31" output "office31_details.csv"

verify dataset "Office-31" corrupt

resize dataset "Office-31" to 32x32, 96x96 outdir "office31_resized"

convert dataset "Office-31" to rgb outdir "office31_rgb"`,

    count: `// Count domains and categories in Office-31
count dataset "Office-31"`,

    verify: `// Verify integrity of all images (checks for truncations and corrupt pixels)
verify dataset "Office-31" corrupt`,

    resize: `// Resize the dataset to target input sizes for ViT models
resize dataset "Office-31" to 32x32, 96x96 outdir "office31_resized"`,

    convert: `// Convert all images to RGB (strips grayscale or CMYK anomalies)
convert dataset "Office-31" to rgb outdir "office31_rgb"`
};

// ==========================================================================
//  App Lifecycle
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    loadProjectInfo();
    loadGitTimeline();
    
    // Set active tab to overview initially
    switchTab('overview');
});

// ==========================================================================
//  Theme Toggling
// ==========================================================================
function initTheme() {
    const themeBtn = document.getElementById("theme-toggle-btn");
    themeBtn.addEventListener("click", () => {
        const body = document.body;
        if (body.classList.contains("dark-theme")) {
            body.classList.replace("dark-theme", "light-theme");
            localStorage.setItem("theme", "light-theme");
        } else {
            body.classList.replace("light-theme", "dark-theme");
            localStorage.setItem("theme", "dark-theme");
        }
    });

    // Restore preference
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light-theme") {
        document.body.classList.replace("dark-theme", "light-theme");
    }
}

// ==========================================================================
//  Tab Navigation
// ==========================================================================
function switchTab(tabId) {
    // Update active nav item
    const navButtons = document.querySelectorAll(".nav-item");
    navButtons.forEach(btn => btn.classList.remove("active"));
    
    const activeBtn = document.getElementById(`btn-tab-${tabId}`);
    if (activeBtn) activeBtn.classList.add("active");
    
    // Update active panel
    const panels = document.querySelectorAll(".tab-panel");
    panels.forEach(panel => panel.classList.remove("active"));
    
    const activePanel = document.getElementById(`tab-overview`);
    const targetPanel = document.getElementById(`tab-${tabId}`);
    if (targetPanel) {
        targetPanel.classList.add("active");
    }

    // Dynamic Headers
    const titleEl = document.getElementById("page-title");
    const subEl = document.getElementById("page-subtitle");
    
    switch(tabId) {
        case "overview":
            titleEl.textContent = "Research Overview";
            subEl.textContent = "Continual domain adaptation status and theoretical background";
            break;
        case "dsl":
            titleEl.textContent = "ImgPrep DSL Studio";
            subEl.textContent = "Write, compile, and execute declarative preprocessing scripts";
            break;
        case "timeline":
            titleEl.textContent = "Git History Timeline";
            subEl.textContent = "Chronological code development and commits log";
            break;
        case "research":
            titleEl.textContent = "Continual Learning Primer";
            subEl.textContent = "Why Vision Transformers experience forgetting and candidate strategies";
            break;
    }
}

function switchOutputTab(subtabId) {
    const buttons = document.querySelectorAll(".panel-tabs .tab-btn");
    buttons.forEach(btn => btn.classList.remove("active"));
    document.getElementById(`btn-out-${subtabId}`).classList.add("active");

    const panels = document.querySelectorAll(".output-subpanel");
    panels.forEach(p => p.classList.remove("active"));
    document.getElementById(`out-tab-${subtabId}`).classList.add("active");
}

// ==========================================================================
//  Data Fetchers
// ==========================================================================
async function loadProjectInfo() {
    try {
        const response = await fetch("/api/project-info");
        const data = await response.json();
        projectData = data;
        
        // Update statuses
        const statusModeEl = document.getElementById("backend-status-mode");
        const datasetBadgeEl = document.getElementById("dataset-status-badge");
        const modeBadgeEl = document.getElementById("mode-badge");

        if (data.datasetExists) {
            statusModeEl.textContent = "Live mode (Office-31 connected)";
            datasetBadgeEl.textContent = "Connected (Live)";
            datasetBadgeEl.parentElement.querySelector(".metric-sub").textContent = "Found folder locally";
            modeBadgeEl.textContent = "Live Execution Mode";
            modeBadgeEl.className = "badge emerald-badge";
        } else {
            statusModeEl.textContent = "Simulation Mode (No dataset)";
            datasetBadgeEl.textContent = "Missing (Simulated)";
            datasetBadgeEl.parentElement.querySelector(".metric-sub").textContent = "Path: " + data.datasetPath;
            modeBadgeEl.textContent = "Simulation Mode";
        }
    } catch(err) {
        console.error("Error fetching project info:", err);
    }
}

async function loadGitTimeline() {
    const container = document.getElementById("git-timeline-list");
    try {
        const response = await fetch("/api/git-log");
        const data = await response.json();
        
        if (data.success && data.commits.length > 0) {
            container.innerHTML = "";
            data.commits.forEach(commit => {
                const item = document.createElement("div");
                item.className = "timeline-item";
                item.innerHTML = `
                    <div class="timeline-badge"></div>
                    <div class="timeline-card">
                        <div class="timeline-meta">
                            <span class="timeline-hash">commit ${commit.hash}</span>
                            <span class="timeline-date">${commit.date}</span>
                        </div>
                        <div class="timeline-subject">${commit.subject}</div>
                        <div class="timeline-author">Author: ${commit.author}</div>
                    </div>
                `;
                container.appendChild(item);
            });
        } else {
            container.innerHTML = `<div class="placeholder-text">No commits found or error loading log: ${data.error || 'Empty'}</div>`;
        }
    } catch(err) {
        container.innerHTML = `<div class="placeholder-text">Error connecting to git backend API.</div>`;
    }
}

// ==========================================================================
//  DSL Studio Script Templates
// ==========================================================================
function loadTemplate() {
    const select = document.getElementById("template-select");
    const val = select.value;
    const input = document.getElementById("dsl-code-input");
    if (TEMPLATES[val]) {
        input.value = TEMPLATES[val];
    }
}

// ==========================================================================
//  Lark AST Tree Renderer
// ==========================================================================
function renderAST(node, container) {
    container.innerHTML = "";
    if (!node) {
        container.innerHTML = '<div class="placeholder-text">Lark AST not generated yet.</div>';
        return;
    }
    
    function buildNodeEl(n) {
        const el = document.createElement("div");
        el.className = "ast-node";
        
        const header = document.createElement("div");
        header.className = "ast-node-header";
        
        if (n.type === "rule") {
            const toggle = document.createElement("span");
            toggle.className = "ast-icon-toggle";
            toggle.textContent = "▼";
            header.appendChild(toggle);
            
            const ruleName = document.createElement("span");
            ruleName.className = "ast-rule";
            ruleName.textContent = n.rule_name;
            header.appendChild(ruleName);
            
            el.appendChild(header);
            
            const childrenContainer = document.createElement("div");
            childrenContainer.className = "ast-children";
            
            n.children.forEach(c => {
                childrenContainer.appendChild(buildNodeEl(c));
            });
            el.appendChild(childrenContainer);
            
            header.onclick = (e) => {
                e.stopPropagation();
                toggle.classList.toggle("collapsed");
                childrenContainer.classList.toggle("collapsed");
                if (toggle.classList.contains("collapsed")) {
                    toggle.textContent = "▶";
                } else {
                    toggle.textContent = "▼";
                }
            };
        } else if (n.type === "token") {
            const tokenType = document.createElement("span");
            tokenType.className = "ast-token";
            tokenType.textContent = n.token_type + ": ";
            header.appendChild(tokenType);
            
            const tokenVal = document.createElement("span");
            tokenVal.className = "ast-token-val";
            tokenVal.textContent = `"${n.value}"`;
            header.appendChild(tokenVal);
            
            el.appendChild(header);
        } else {
            const litVal = document.createElement("span");
            litVal.className = "ast-literal";
            litVal.textContent = n.value;
            header.appendChild(litVal);
            el.appendChild(header);
        }
        
        return el;
    }
    
    container.appendChild(buildNodeEl(node));
}

// ==========================================================================
//  Terminal Utilities & DSL Runs
// ==========================================================================
function printTerminal(text, type = "normal") {
    const stdout = document.getElementById("terminal-stdout");
    const line = document.createElement("div");
    line.className = `terminal-line text-${type}`;
    line.textContent = text;
    stdout.appendChild(line);
    stdout.scrollTop = stdout.scrollHeight;
}

function clearConsole() {
    const stdout = document.getElementById("terminal-stdout");
    stdout.innerHTML = '<div class="terminal-line text-system">Terminal cleared. Waiting for actions...</div>';
}

async function parseDSL() {
    const script = document.getElementById("dsl-code-input").value;
    switchOutputTab("ast");
    
    printTerminal("\n$ imgprep --compile-only script.imgprep", "cmd");
    
    try {
        const response = await fetch("/api/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ script })
        });
        const data = await response.json();
        
        if (data.success) {
            printTerminal("[SUCCESS] Compilation completed without warnings.", "success");
            printTerminal(`[INFO] Abstract Syntax Tree successfully generated with Lark (lalr).`, "system");
            printTerminal(`[INFO] Found ${data.actions.length} action statement(s).`, "system");
            
            // Render AST
            renderAST(data.ast, document.getElementById("ast-tree-root"));
            
            // Render JSON Actions
            document.getElementById("actions-json-code").querySelector("code").textContent = JSON.stringify(data.actions, null, 4);
        } else {
            printTerminal(`[ERROR] Parsing failed:`, "error");
            printTerminal(data.error, "error");
            
            // Reset visualizers
            document.getElementById("ast-tree-root").innerHTML = `<div class="placeholder-text text-error">Syntax Error: ${data.error.split('\n')[0]}</div>`;
            document.getElementById("actions-json-code").querySelector("code").textContent = "[]";
        }
    } catch(err) {
        printTerminal("[ERROR] Failed to communicate with compiler backend API.", "error");
    }
}

async function runDSL() {
    const script = document.getElementById("dsl-code-input").value;
    switchOutputTab("terminal");
    
    printTerminal("\n$ python main.py script.imgprep", "cmd");
    
    try {
        // First compile & retrieve actions
        const parseRes = await fetch("/api/parse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ script })
        });
        const parseData = await parseRes.json();
        
        if (!parseData.success) {
            printTerminal(`[ERROR] Parsing failed. Cannot execute script.`, "error");
            printTerminal(parseData.error, "error");
            return;
        }

        // Trigger execution endpoint
        const isSimulated = !projectData || !projectData.datasetExists;
        const response = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                script,
                mode: isSimulated ? "simulated" : "real"
            })
        });
        const data = await response.json();
        
        if (!data.success) {
            printTerminal(`[ERROR] Execution aborted: ${data.error}`, "error");
            return;
        }

        if (data.mode === "real") {
            // Live run - print captured stdout returned by server
            const lines = data.stdout.split("\n");
            for (let line of lines) {
                if (line.trim()) {
                    let type = "normal";
                    if (line.includes("COUNT") || line.includes("RESIZE") || line.includes("CONVERT") || line.includes("VERIFY") || line.includes("DETAIL")) {
                        type = "cmd";
                    } else if (line.includes("[ERROR]")) {
                        type = "error";
                    } else if (line.includes("[WARN]")) {
                        type = "warn";
                    } else if (line.includes("TOTAL") || line.includes("Wrote") || line.includes("valid")) {
                        type = "success";
                    }
                    printTerminal(line, type);
                    await new Promise(r => setTimeout(r, 60)); // short delay for visual satisfaction
                }
            }
            if (data.error) {
                printTerminal(`[RUNTIME ERROR] ${data.error}`, "error");
            }
        } else {
            // Simulated run - execute detailed step-by-step console animations
            printTerminal("[SIMULATOR] Initiating simulation runner...", "system");
            await new Promise(r => setTimeout(r, 600));

            for (let action of data.actions) {
                await simulateAction(action);
            }
            
            printTerminal("============================================================", "success");
            printTerminal("  SIMULATION COMPLETED SUCCESSFULLY (DRY RUN)", "success");
            printTerminal("============================================================", "success");
        }
    } catch(err) {
        printTerminal("[ERROR] Execution request failed.", "error");
        console.error(err);
    }
}

// Helper to simulate action sequences visually in terminal
async function simulateAction(action) {
    const act = action.action.toUpperCase();
    const dataset = action.dataset;
    
    printTerminal("\n============================================================", "normal");
    printTerminal(`  ${act}  –  ${dataset}`, "normal");
    printTerminal("============================================================", "normal");
    await new Promise(r => setTimeout(r, 400));

    if (action.action === "count") {
        printTerminal("  Domain: amazon  (2817 images)", "normal");
        printTerminal("    back_pack..................... 100\n    bike.......................... 82\n    calculator.................... 94\n    [truncated 28 classes]", "system");
        await new Promise(r => setTimeout(r, 450));
        
        printTerminal("  Domain: dslr  (498 images)", "normal");
        printTerminal("    back_pack..................... 18\n    bike.......................... 14\n    [truncated 29 classes]", "system");
        await new Promise(r => setTimeout(r, 350));
        
        printTerminal("  Domain: webcam  (795 images)", "normal");
        printTerminal("    back_pack..................... 22\n    bike.......................... 19\n    [truncated 29 classes]", "system");
        await new Promise(r => setTimeout(r, 350));

        printTerminal("  TOTAL images: 4110\n", "success");
    } 
    
    else if (action.action === "detail") {
        printTerminal(`  Exporting shape and channel mode details to CSV...`, "system");
        await new Promise(r => setTimeout(r, 500));
        printTerminal(`  Scanning: Amazon/back_pack/image_0001.jpg (800x800, RGB)...`, "system");
        await new Promise(r => setTimeout(r, 300));
        printTerminal(`  Scanning: DSLR/keyboard/image_0012.png (1200x900, RGB)...`, "system");
        await new Promise(r => setTimeout(r, 300));
        
        printTerminal(`  Wrote 4110 rows to ${action.output}`, "success");
    } 
    
    else if (action.action === "verify") {
        printTerminal(`  Checking for corrupt files and Pillow format compatibility...`, "system");
        await new Promise(r => setTimeout(r, 200));
        
        // Progress bar simulation
        const stdout = document.getElementById("terminal-stdout");
        const progressLine = document.createElement("div");
        progressLine.className = "terminal-line";
        progressLine.innerHTML = `  Verifying: <div class="terminal-progress-bar"><div class="terminal-progress-fill" style="width: 0%"></div></div> <span class="progress-pct">0%</span>`;
        stdout.appendChild(progressLine);
        
        const fill = progressLine.querySelector(".terminal-progress-fill");
        const pctText = progressLine.querySelector(".progress-pct");
        
        for (let i = 10; i <= 100; i += 15) {
            let pct = Math.min(i, 100);
            fill.style.width = pct + "%";
            pctText.textContent = `${pct}% [${Math.floor(4110 * pct / 100)}/4110]`;
            stdout.scrollTop = stdout.scrollHeight;
            await new Promise(r => setTimeout(r, 150));
        }
        
        printTerminal("  All 4110 images are valid ✓", "success");
    } 
    
    else if (action.action === "resize") {
        const resolutions = action.resolutions;
        const outdir = action.outdir;
        printTerminal(`  Resolutions: ${resolutions.map(r => r.join('x')).join(', ')}`, "system");
        printTerminal(`  Output directory: ${outdir}`, "system");
        
        for (let res of resolutions) {
            let rStr = res.join('x');
            printTerminal(`  Creating folder ${outdir}/${rStr}...`, "system");
            await new Promise(r => setTimeout(r, 300));
            printTerminal(`    [Resize] Processing amazon domain...`, "system");
            await new Promise(r => setTimeout(r, 200));
            printTerminal(`    [Resize] Processing dslr domain...`, "system");
            await new Promise(r => setTimeout(r, 200));
            printTerminal(`    [Resize] Processing webcam domain...`, "system");
            await new Promise(r => setTimeout(r, 200));
            printTerminal(`  ✓ ${rStr}: resized 4110 images → ${outdir}/${rStr}`, "success");
        }
    } 
    
    else if (action.action === "convert") {
        const fmt = action.format;
        const outdir = action.outdir;
        printTerminal(`  Target color mode: ${fmt.toUpperCase()}`, "system");
        printTerminal(`  Output directory: ${outdir}`, "system");
        await new Promise(r => setTimeout(r, 400));
        
        printTerminal(`  Converting channels...`, "system");
        await new Promise(r => setTimeout(r, 500));
        printTerminal(`  ✓ Converted 4110 images to ${fmt} → ${outdir}`, "success");
    }
}
