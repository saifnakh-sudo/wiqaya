/* ============================================================
   WIQAYA — Main Application JavaScript
   ============================================================ */

let currentLanguage = "fr";
let currentScanType = "cin";
let currentScreen = "landing";
let lastScanResult = null;
let phishingScore = { correct: 0, total: 0 };

// ============================================================
// Translations
// ============================================================

const T = {
    fr: {
        scanPlaceholderCin: "Entrez votre numero CIN (ex: AB123456)",
        scanPlaceholderEmail: "Entrez votre adresse email",
        scanBtn: "Analyser",
        scanning: "Analyse en cours...",
        riskCritical: "Risque Critique",
        riskHigh: "Risque Eleve",
        riskMedium: "Risque Moyen",
        riskLow: "Risque Faible",
        score: "Score",
        breachesFound: "fuite(s) detectee(s)",
        exposedData: "Donnees exposees",
        breachSources: "Sources des fuites",
        generatePlan: "Generer mon plan de protection",
        runSimulator: "Lancer le simulateur de phishing",
        planGenerating: "L'IA analyse votre profil de risque et genere un plan personnalise...",
        phishingGenerating: "L'IA genere des scenarios de phishing personnalises...",
        notFoundTitle: "Aucune exposition detectee",
        notFoundText: "Aucune fuite n'a ete trouvee pour cet identifiant dans notre base.",
        notFoundNote: "Cela ne garantit pas que vos donnees n'ont pas ete compromises. Notre base couvre les fuites CNSS et OFPPT connues.",
        isThisScam: "Ce message est-il une arnaque ?",
        btnScam: "C'est une arnaque !",
        btnLegit: "Ca semble legitime",
        correctScam: "Correct ! C'est bien une arnaque.",
        incorrectLegit: "Attention ! C'etait une arnaque.",
        quizScore: "Score de detection",
        generalTips: "Conseils generaux de protection",
        redFlags: "Signaux d'alerte",
        technique: "Technique utilisee",
        correctAction: "Bonne reaction",
        yourRights: "Vos droits",
        resources: "Ressources utiles",
        errorTitle: "Erreur",
        errorApiKey: "Cle API OpenAI non configuree. Configurez la variable OPENAI_API_KEY.",
    },
    ar: {
        scanPlaceholderCin: "ادخل رقم البطاقة الوطنية (مثال: AB123456)",
        scanPlaceholderEmail: "ادخل بريدك الالكتروني",
        scanBtn: "تحليل",
        scanning: "جار التحليل...",
        riskCritical: "خطر حرج",
        riskHigh: "خطر مرتفع",
        riskMedium: "خطر متوسط",
        riskLow: "خطر منخفض",
        score: "النتيجة",
        breachesFound: "تسريب(ات) مكتشفة",
        exposedData: "البيانات المكشوفة",
        breachSources: "مصادر التسريب",
        generatePlan: "انشاء خطة الحماية الخاصة بي",
        runSimulator: "تشغيل محاكي التصيد",
        planGenerating: "يقوم الذكاء الاصطناعي بتحليل ملف المخاطر الخاص بك وانشاء خطة مخصصة...",
        phishingGenerating: "يقوم الذكاء الاصطناعي بانشاء سيناريوهات تصيد مخصصة...",
        notFoundTitle: "لم يتم اكتشاف اي تعرض",
        notFoundText: "لم يتم العثور على اي تسريب لهذا المعرف في قاعدة بياناتنا.",
        notFoundNote: "هذا لا يضمن ان بياناتك لم تتعرض للاختراق.",
        isThisScam: "هل هذه الرسالة احتيالية؟",
        btnScam: "هذا احتيال!",
        btnLegit: "تبدو حقيقية",
        correctScam: "صحيح! هذا فعلا احتيال.",
        incorrectLegit: "انتبه! كانت هذه رسالة احتيالية.",
        quizScore: "نتيجة الكشف",
        generalTips: "نصائح عامة للحماية",
        redFlags: "علامات التحذير",
        technique: "التقنية المستخدمة",
        correctAction: "الاجراء الصحيح",
        yourRights: "حقوقك",
        resources: "موارد مفيدة",
        errorTitle: "خطا",
        errorApiKey: "مفتاح OpenAI API غير مكون.",
    }
};

function t(key) {
    return T[currentLanguage]?.[key] || T["fr"][key] || key;
}

// ============================================================
// Navigation
// ============================================================

function showScreen(screen) {
    currentScreen = screen;
    document.querySelectorAll(".screen").forEach(function(s) { s.classList.remove("active"); });
    var target = document.getElementById("screen-" + screen);
    if (target) target.classList.add("active");
    document.querySelectorAll(".nav-link").forEach(function(link) {
        link.classList.toggle("active", link.dataset.screen === screen);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });

    if (screen === "plan" && lastScanResult && lastScanResult.found) {
        var planContent = document.getElementById("planContent");
        if (planContent.querySelector(".empty-state")) {
            generateProtectionPlan();
        }
    }
    if (screen === "phishing" && lastScanResult && lastScanResult.found) {
        var phishContent = document.getElementById("phishingContent");
        if (phishContent.querySelector(".empty-state")) {
            generatePhishingScenarios();
        }
    }
}

// ============================================================
// Language
// ============================================================

function setLanguage(lang) {
    currentLanguage = lang;
    document.documentElement.lang = lang === "ar" ? "ar" : "fr";
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.body.dir = lang === "ar" ? "rtl" : "ltr";

    document.querySelectorAll(".lang-btn").forEach(function(btn) {
        btn.classList.toggle("active",
            (lang === "fr" && btn.textContent.trim() === "FR") ||
            (lang === "ar" && btn.textContent.trim() === "عربي")
        );
    });

    var scanInput = document.getElementById("scanInput");
    if (scanInput) {
        scanInput.placeholder = currentScanType === "cin" ? t("scanPlaceholderCin") : t("scanPlaceholderEmail");
    }
}

// ============================================================
// Scanner (Module 1)
// ============================================================

function setScanType(type) {
    currentScanType = type;
    document.getElementById("tabCin").classList.toggle("active", type === "cin");
    document.getElementById("tabEmail").classList.toggle("active", type === "email");
    var input = document.getElementById("scanInput");
    input.placeholder = type === "cin" ? t("scanPlaceholderCin") : t("scanPlaceholderEmail");
    input.value = "";
    input.focus();
}

async function loadDemoCIN() {
    try {
        var res = await fetch("/api/demo-cin");
        var data = await res.json();
        if (data.cin) {
            currentScanType = "cin";
            document.getElementById("tabCin").classList.add("active");
            document.getElementById("tabEmail").classList.remove("active");
            document.getElementById("scanInput").value = data.cin;
            document.getElementById("scanInput").placeholder = t("scanPlaceholderCin");
        }
    } catch (err) {
        console.error("Failed to load demo CIN:", err);
    }
}

async function performScan() {
    var query = document.getElementById("scanInput").value.trim();
    if (!query) {
        document.getElementById("scanInput").focus();
        return;
    }

    var btn = document.getElementById("scanBtn");
    var resultsDiv = document.getElementById("scanResults");

    btn.disabled = true;
    btn.innerHTML = '<div class="spinner" style="width:18px;height:18px;border-width:2px;margin:0;display:inline-block;vertical-align:middle"></div> ' + t("scanning");

    try {
        var res = await fetch("/api/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, type: currentScanType })
        });

        var data = await res.json();
        lastScanResult = data;

        resetModule("planContent");
        resetModule("phishingContent");

        resultsDiv.classList.remove("hidden");

        if (data.found) {
            renderScanResults(data, resultsDiv);
        } else {
            renderNotFound(data, resultsDiv);
        }
    } catch (err) {
        resultsDiv.classList.remove("hidden");
        resultsDiv.innerHTML = renderError(err.message);
    }

    btn.disabled = false;
    btn.innerHTML = t("scanBtn") + ' <i class="ti ti-arrow-right"></i>';
}

function resetModule(containerId) {
    var container = document.getElementById(containerId);
    container.innerHTML = '<div class="empty-state glass-card">' +
        '<div class="empty-ic"><i class="ti ti-shield-off"></i></div>' +
        '<h3>Aucun profil de risque</h3>' +
        '<p>Effectuez d\'abord un scan pour obtenir votre profil de risque.</p>' +
        '<button class="btn-primary" onclick="showScreen(\'scanner\')">' +
        '<i class="ti ti-radar-2"></i> Aller au Scanner</button></div>';
}

function renderScanResults(data, container) {
    var risk = data.risk;
    var levelClass = risk.level.toLowerCase();
    var riskLabel = t("risk" + capitalize(levelClass));

    var html = '';

    // Risk header
    html += '<div class="risk-header ' + levelClass + '">' +
        '<div class="risk-circle" style="border-color:' + risk.color + ';color:' + risk.color + '">' +
        '<div class="risk-num">' + data.risk_score + '</div>' +
        '<div class="risk-of">/100</div></div>' +
        '<div class="risk-level" style="color:' + risk.color + '">' + riskLabel + '</div>' +
        '<div class="risk-count">' + data.total_breaches + ' ' + t("breachesFound") + '</div></div>';

    // Exposed categories
    html += '<div class="exposed-card"><h3><i class="ti ti-alert-triangle"></i> ' + t("exposedData") + '</h3>' +
        '<div class="exposed-grid">';
    data.category_details.forEach(function(cat) {
        var sev = cat.severity || "medium";
        var label = currentLanguage === "ar" ? (cat.ar || cat.fr) : cat.fr;
        html += '<div class="exp-item sev-' + sev + '">' +
            '<i class="ti ti-' + (cat.icon || 'file') + '"></i>' +
            '<span>' + label + '</span></div>';
    });
    html += '</div></div>';

    // Breach sources
    html += '<div class="exposed-card"><h3><i class="ti ti-database"></i> ' + t("breachSources") + '</h3>';
    data.breaches.forEach(function(breach) {
        var srcClass = breach.source === "CNSS" ? "cnss" : "ofppt";
        var context = currentLanguage === "ar" ? breach.context_ar : breach.context_fr;
        html += '<div class="breach-src">' +
            '<span class="bsrc-badge ' + srcClass + '">' + breach.source + '</span>' +
            '<div><div class="bsrc-info">' + context + '</div>';
        if (breach.employer) html += '<div class="bsrc-info">Employeur: ' + breach.employer + '</div>';
        if (breach.filiere) html += '<div class="bsrc-info">Filiere: ' + breach.filiere + '</div>';
        html += '</div></div>';
    });
    html += '</div>';

    // Actions
    html += '<div class="scan-actions">' +
        '<button class="btn-primary" onclick="showScreen(\'plan\')">' +
        '<i class="ti ti-shield-check"></i> ' + t("generatePlan") + '</button>' +
        '<button class="btn-secondary" onclick="showScreen(\'phishing\')">' +
        '<i class="ti ti-fish-hook"></i> ' + t("runSimulator") + '</button></div>';

    container.innerHTML = html;
}

function renderNotFound(data, container) {
    var titleKey = currentLanguage === "ar" ? "message_ar" : "message_fr";
    var noteKey = currentLanguage === "ar" ? "note_ar" : "note_fr";
    container.innerHTML = '<div class="not-found">' +
        '<i class="ti ti-shield-check"></i>' +
        '<h3>' + t("notFoundTitle") + '</h3>' +
        '<p>' + (data[titleKey] || t("notFoundText")) + '</p>' +
        '<div class="nf-note">' + (data[noteKey] || t("notFoundNote")) + '</div></div>';
}

// ============================================================
// Protection Plan (Module 2)
// ============================================================

async function generateProtectionPlan() {
    var container = document.getElementById("planContent");
    if (!lastScanResult || !lastScanResult.found) return;

    container.innerHTML = '<div class="plan-loading">' +
        '<div class="spinner"></div>' +
        '<p class="loading-text">' + t("planGenerating") + '</p></div>';

    try {
        var res = await fetch("/api/protection-plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ risk_profile: lastScanResult, language: currentLanguage })
        });
        var data = await res.json();

        if (data.error) {
            container.innerHTML = renderError(data.error.includes("API") ? t("errorApiKey") : data.error);
            return;
        }
        renderProtectionPlan(data.plan, container);
    } catch (err) {
        container.innerHTML = renderError(err.message);
    }
}

function renderProtectionPlan(plan, container) {
    var html = '<div class="plan-wrap">';

    // Header
    html += '<div class="plan-header">' +
        '<h3><i class="ti ti-shield-check"></i> Plan de protection</h3>' +
        '<p>' + (plan.summary || "") + '</p></div>';

    // Steps
    html += '<div class="plan-steps">';
    if (plan.steps && Array.isArray(plan.steps)) {
        plan.steps.forEach(function(step, i) {
            html += '<div class="plan-step">' +
                '<div class="step-num">' + (i + 1) + '</div>' +
                '<div class="step-body">' +
                '<h4>' + (step.title || "") + '</h4>' +
                '<div class="step-desc">' + (step.description || "") + '</div>';
            if (step.how) html += '<div class="step-desc"><strong>Comment:</strong> ' + step.how + '</div>';
            html += '<div class="step-tags">';
            if (step.timeline) html += '<span class="step-tag' + (step.priority <= 2 ? ' urgent' : '') + '"><i class="ti ti-clock"></i> ' + step.timeline + '</span>';
            html += '</div></div></div>';
        });
    }
    html += '</div>';

    // Resources
    if (plan.resources && Array.isArray(plan.resources) && plan.resources.length > 0) {
        html += '<div class="plan-resources"><h3>' + t("resources") + '</h3>';
        plan.resources.forEach(function(r) {
            html += '<a href="' + (r.url || '#') + '" class="res-link" target="_blank" rel="noopener">' +
                '<i class="ti ti-external-link"></i> ' +
                '<strong>' + (r.name || "") + '</strong>' +
                (r.description ? ' — ' + r.description : '') + '</a>';
        });
        html += '</div>';
    }

    // Legal
    if (plan.legal_rights) {
        html += '<div class="plan-legal"><i class="ti ti-gavel"></i>' +
            '<strong>' + t("yourRights") + ':</strong> ' + plan.legal_rights + '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
}

// ============================================================
// Phishing Simulator (Module 3)
// ============================================================

async function generatePhishingScenarios() {
    var container = document.getElementById("phishingContent");
    if (!lastScanResult || !lastScanResult.found) return;

    phishingScore = { correct: 0, total: 0 };

    container.innerHTML = '<div class="phishing-loading">' +
        '<div class="spinner"></div>' +
        '<p class="loading-text">' + t("phishingGenerating") + '</p></div>';

    try {
        var res = await fetch("/api/phishing-simulator", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ risk_profile: lastScanResult, language: currentLanguage })
        });
        var data = await res.json();

        if (data.error) {
            container.innerHTML = renderError(data.error.includes("API") ? t("errorApiKey") : data.error);
            return;
        }
        renderPhishingScenarios(data.scenarios, container);
    } catch (err) {
        container.innerHTML = renderError(err.message);
    }
}

function renderPhishingScenarios(data, container) {
    var scenarios = data.scenarios || [];
    var tips = data.general_tips || [];

    var html = '<div class="phish-score" id="phishScoreCard">' +
        '<div class="ps-val" id="phishScoreVal">0/' + scenarios.length + '</div>' +
        '<div class="ps-lbl">' + t("quizScore") + '</div></div>';

    var typeIcons = { sms: "message-2", email: "mail", call: "phone", whatsapp: "brand-whatsapp" };

    scenarios.forEach(function(scenario, idx) {
        var icon = typeIcons[scenario.type] || "message";
        html += '<div class="scenario" id="scenario-' + idx + '">' +
            '<div class="scenario-head">' +
            '<div class="sc-type ' + scenario.type + '"><i class="ti ti-' + icon + '"></i> ' +
            (scenario.type_label || scenario.type.toUpperCase()) + '</div>' +
            '<span class="sc-badge">Scenario ' + (idx + 1) + '</span></div>';

        html += '<div class="sc-message">' +
            '<div class="msg-from">' + (scenario.sender || "Inconnu") + '</div>';
        if (scenario.subject) html += '<div class="msg-subj">' + scenario.subject + '</div>';
        html += (scenario.content || "") + '</div>';

        // Quiz
        html += '<div class="quiz-bar" id="quiz-' + idx + '">' +
            '<span class="quiz-q">' + t("isThisScam") + '</span>' +
            '<div class="quiz-btns">' +
            '<button class="qbtn qbtn-scam" onclick="answerQuiz(' + idx + ',true)">' + t("btnScam") + '</button>' +
            '<button class="qbtn qbtn-legit" onclick="answerQuiz(' + idx + ',false)">' + t("btnLegit") + '</button>' +
            '</div></div>';

        // Flags (hidden)
        html += '<div class="sc-flags" id="flags-' + idx + '" style="display:none">' +
            '<h4><i class="ti ti-alert-triangle"></i> ' + t("redFlags") + '</h4>';
        (scenario.red_flags || []).forEach(function(flag, fi) {
            html += '<div class="flag"><div class="flag-n">' + (fi + 1) + '</div>' +
                '<div class="flag-body"><strong>' + (flag.flag || "") + '</strong>' +
                '<span>' + (flag.explanation || "") + '</span></div></div>';
        });
        html += '</div>';

        if (scenario.technique) {
            html += '<div class="sc-technique" id="tech-' + idx + '" style="display:none">' +
                '<strong><i class="ti ti-bulb"></i> ' + t("technique") + ':</strong> ' + scenario.technique + '</div>';
        }
        if (scenario.correct_action) {
            html += '<div class="sc-action" id="act-' + idx + '" style="display:none">' +
                '<strong><i class="ti ti-check"></i> ' + t("correctAction") + ':</strong> ' + scenario.correct_action + '</div>';
        }

        html += '</div>';
    });

    // Tips
    if (tips.length > 0) {
        html += '<div class="gen-tips"><h3><i class="ti ti-bulb"></i> ' + t("generalTips") + '</h3>';
        tips.forEach(function(tip) {
            html += '<div class="tip-row"><i class="ti ti-check"></i><span>' + tip + '</span></div>';
        });
        html += '</div>';
    }

    container.innerHTML = html;
}

function answerQuiz(idx, saidScam) {
    phishingScore.total++;
    var isCorrect = saidScam;
    if (isCorrect) phishingScore.correct++;

    var quiz = document.getElementById("quiz-" + idx);
    var flags = document.getElementById("flags-" + idx);
    var tech = document.getElementById("tech-" + idx);
    var act = document.getElementById("act-" + idx);

    if (quiz) {
        quiz.style.background = isCorrect ? "rgba(34,197,94,.15)" : "rgba(239,68,68,.15)";
        quiz.style.borderColor = isCorrect ? "rgba(34,197,94,.3)" : "rgba(239,68,68,.3)";
        quiz.innerHTML = '<span class="quiz-q" style="color:' + (isCorrect ? "#22C55E" : "#EF4444") + '">' +
            '<i class="ti ti-' + (isCorrect ? 'check' : 'x') + '"></i> ' +
            (isCorrect ? t("correctScam") : t("incorrectLegit")) + '</span>';
    }
    if (flags) flags.style.display = "block";
    if (tech) tech.style.display = "block";
    if (act) act.style.display = "block";

    var scoreEl = document.getElementById("phishScoreVal");
    if (scoreEl) {
        scoreEl.textContent = phishingScore.correct + "/" + phishingScore.total;
        scoreEl.style.color = phishingScore.correct === phishingScore.total ? "#22C55E" : "#EF4444";
    }
}

// ============================================================
// Stats
// ============================================================

async function loadStats() {
    try {
        var res = await fetch("/api/stats");
        var stats = await res.json();
        var totalEl = document.getElementById("statTotal");
        var criticalEl = document.getElementById("statCritical");
        if (totalEl) animateNumber(totalEl, stats.total_records);
        if (criticalEl) animateNumber(criticalEl, stats.critical_count);
    } catch (err) {
        console.error("Stats load failed:", err);
    }
}

function animateNumber(el, target) {
    var duration = 1200;
    var startTime = performance.now();
    function update(now) {
        var progress = Math.min((now - startTime) / duration, 1);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased).toLocaleString();
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ============================================================
// Utilities
// ============================================================

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function renderError(message) {
    return '<div class="error-state">' +
        '<i class="ti ti-alert-circle"></i>' +
        '<h3>' + t("errorTitle") + '</h3>' +
        '<p>' + message + '</p></div>';
}

// ============================================================
// Init
// ============================================================

document.addEventListener("DOMContentLoaded", function() {
    loadStats();
    var scanInput = document.getElementById("scanInput");
    if (scanInput) {
        scanInput.addEventListener("keydown", function(e) {
            if (e.key === "Enter") performScan();
        });
    }
});
