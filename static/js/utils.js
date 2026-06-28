function formatINR(num) {
    if (num == null || isNaN(num)) return "₹0";
    const n = Math.round(num);
    const neg = n < 0;
    const s = Math.abs(n).toString();
    if (s.length <= 3) return "₹" + (neg ? "-" : "") + s;
    let result = s.slice(-3);
    let remaining = s.slice(0, -3);
    while (remaining.length > 2) {
        result = remaining.slice(-2) + "," + result;
        remaining = remaining.slice(0, -2);
    }
    if (remaining.length > 0) result = remaining + "," + result;
    return "₹" + (neg ? "-" : "") + result;
}

function formatLakhsCr(num) {
    if (num >= 10000000) return "₹" + (num / 10000000).toFixed(2) + " Cr";
    if (num >= 100000) return "₹" + (num / 100000).toFixed(2) + " L";
    return formatINR(num);
}

async function postCalc(url, data) {
    const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    return resp.json();
}

function showResults(containerId) {
    const el = document.getElementById(containerId);
    if (el) el.style.display = "block";
    const ph = document.getElementById("results-placeholder");
    if (ph) ph.style.display = "none";
}

function syncSlider(sliderId, inputId, prefix, suffix) {
    const slider = document.getElementById(sliderId);
    const input = document.getElementById(inputId);
    const label = document.querySelector(`label[for="${inputId}"] .field-value`);
    if (!slider || !input) return;
    function update(val) {
        slider.value = val;
        input.value = val;
        if (label) {
            const v = parseFloat(val);
            if (prefix === "₹") {
                label.textContent = formatINR(v);
            } else {
                label.textContent = (prefix || '') + val + (suffix || '');
            }
        }
    }
    slider.addEventListener("input", () => update(slider.value));
    input.addEventListener("input", () => update(input.value));
    update(input.value);
}

let _lastResult = null;
let _inflationOn = false;

function getDisplayData(result) {
    _lastResult = result;
    if (_inflationOn && result.inflation_adjusted) {
        return result.inflation_adjusted;
    }
    return result;
}

function setupInflationToggle(recalcFn) {
    const toggle = document.getElementById("inflation-toggle");
    const rateField = document.getElementById("inflation-rate-field");
    if (!toggle) return;
    toggle.addEventListener("change", () => {
        _inflationOn = toggle.checked;
        if (rateField) rateField.classList.toggle("visible", toggle.checked);
        if (recalcFn) recalcFn();
    });
    const rateInput = document.getElementById("inflation-rate");
    if (rateInput) {
        rateInput.addEventListener("change", () => {
            if (recalcFn) recalcFn();
        });
    }
}

function getInflationRate() {
    const toggle = document.getElementById("inflation-toggle");
    const rateInput = document.getElementById("inflation-rate");
    if (toggle && toggle.checked && rateInput) {
        return parseFloat(rateInput.value) || 6;
    }
    return 0;
}

// ── Calculator result storage ──
const CALC_STORE = 'calcHub_';

function saveCalcResult(key, data) {
    try { localStorage.setItem(CALC_STORE + key, JSON.stringify({ data, ts: Date.now() })); } catch(e) {}
}

function loadCalcResult(key) {
    try {
        const raw = localStorage.getItem(CALC_STORE + key);
        if (!raw) return null;
        return JSON.parse(raw).data;
    } catch(e) { return null; }
}

function prefillField(id, value) {
    if (value == null || value === undefined) return;
    const el = document.getElementById(id);
    if (!el) return;
    el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
}

// deps: [{key, name, url}, ...]
// Returns HTML for either a "prefilled" notice or a "complete X first" hint
function prereqBannerHTML(deps) {
    const missing = deps.filter(d => !loadCalcResult(d.key));
    if (missing.length === 0) {
        const names = deps.map(d => d.name).join(' & ');
        return `<div class="prefill-notice">✓ Values auto-filled from ${names} — verify before calculating.</div>`;
    }
    const links = missing.map(d => `<a href="${d.url}">${d.name}</a>`).join(' and ');
    return `<div class="prereq-hint">💡 Complete ${links} first for automatic input.</div>`;
}

// ── Primary/Derived tab setup ──
function setupSegmentTabs() {
    document.querySelectorAll('.seg-tabs').forEach(tabBar => {
        tabBar.querySelectorAll('.seg-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const parent = tab.closest('.seg-tabs');
                parent.querySelectorAll('.seg-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const paneId = 'pane-' + tab.dataset.pane;
                const container = parent.nextElementSibling;
                // walk siblings until we find the pane container
                let root = parent.parentElement;
                root.querySelectorAll('.calc-pane').forEach(p => p.classList.remove('active'));
                const pane = root.querySelector('#' + paneId);
                if (pane) pane.classList.add('active');
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', setupSegmentTabs);

function inflationHTML() {
    return `<div class="inflation-toggle">
        <label class="switch"><input type="checkbox" id="inflation-toggle"><span class="slider"></span></label>
        <span class="inf-label">Adjust for inflation</span>
        <div class="inflation-field" id="inflation-rate-field">
            <input type="number" id="inflation-rate" value="6" min="0" max="20" step="0.5">
            <span style="font-size:.7rem;color:var(--text-muted);">% p.a.</span>
        </div>
    </div>`;
}
