# Copyright (c) 2026 Ahmed Saifeddine Nakhli / LUMIVYN LTD
# All Rights Reserved. Proprietary and Confidential.
# Unauthorized use, copying, or distribution is strictly prohibited.


import os
import json
import sqlite3
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

DB_PATH = os.path.join(os.path.dirname(__file__), "wiqaya.db")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_identifier(value):
    return hashlib.sha256(value.encode()).hexdigest()[:16]


RISK_LEVELS = {
    "CRITICAL": {"min": 75, "color": "#E24B4A", "label_fr": "Critique", "label_ar": "حرج"},
    "HIGH":     {"min": 50, "color": "#EF9F27", "label_fr": "Eleve",   "label_ar": "مرتفع"},
    "MEDIUM":   {"min": 30, "color": "#639922", "label_fr": "Moyen",   "label_ar": "متوسط"},
    "LOW":      {"min": 0,  "color": "#1D9E75", "label_fr": "Faible",  "label_ar": "منخفض"},
}

CATEGORY_LABELS = {
    "cin":             {"fr": "Numero CIN",           "ar": "رقم البطاقة الوطنية", "icon": "id-card", "severity": "high"},
    "full_name":       {"fr": "Nom complet",          "ar": "الاسم الكامل",       "icon": "user",    "severity": "medium"},
    "email":           {"fr": "Adresse email",        "ar": "البريد الإلكتروني",   "icon": "mail",    "severity": "medium"},
    "phone":           {"fr": "Numero de telephone",  "ar": "رقم الهاتف",         "icon": "phone",   "severity": "medium"},
    "employer":        {"fr": "Employeur",            "ar": "جهة العمل",          "icon": "building", "severity": "low"},
    "salary":          {"fr": "Informations salariales","ar": "معلومات الراتب",    "icon": "currency-dollar", "severity": "high"},
    "bank_account":    {"fr": "Compte bancaire (RIB)","ar": "الحساب البنكي",      "icon": "credit-card", "severity": "critical"},
    "bank_name":       {"fr": "Nom de la banque",     "ar": "اسم البنك",          "icon": "building", "severity": "medium"},
    "birth_date":      {"fr": "Date de naissance",    "ar": "تاريخ الازدياد",      "icon": "calendar", "severity": "medium"},
    "filiere":         {"fr": "Filiere de formation",  "ar": "شعبة التكوين",       "icon": "school",  "severity": "low"},
    "center":          {"fr": "Centre de formation",   "ar": "مركز التكوين",       "icon": "map-pin", "severity": "low"},
    "diploma_level":   {"fr": "Niveau de diplome",     "ar": "مستوى الشهادة",      "icon": "certificate", "severity": "low"},
    "enrollment_year": {"fr": "Annee d'inscription",   "ar": "سنة التسجيل",        "icon": "calendar", "severity": "low"},
}


def classify_risk(score):
    for level, info in RISK_LEVELS.items():
        if score >= info["min"]:
            return {"level": level, **info}
    return {"level": "LOW", **RISK_LEVELS["LOW"]}


def build_exposure_report(records):
    breaches = []
    all_categories = set()
    max_risk = 0

    for record in records:
        categories = record["exposed_categories"].split(",")
        all_categories.update(categories)
        max_risk = max(max_risk, record["risk_score"])

        breach_info = {
            "source": record["breach_source"],
            "categories": categories,
            "category_details": [
                {**CATEGORY_LABELS.get(cat, {}), "key": cat}
                for cat in categories if cat in CATEGORY_LABELS
            ],
            "risk_score": record["risk_score"],
            "city": record["city"],
        }

        if record["breach_source"] == "CNSS":
            breach_info["context_fr"] = "Fuite de la Caisse Nationale de Securite Sociale (avril 2025)"
            breach_info["context_ar"] = "تسريب الصندوق الوطني للضمان الاجتماعي (أبريل 2025)"
            if record["employer"]:
                breach_info["employer"] = record["employer"]
        elif record["breach_source"] == "OFPPT":
            breach_info["context_fr"] = "Fuite de l'OFPPT (avril 2026)"
            breach_info["context_ar"] = "تسريب مكتب التكوين المهني (أبريل 2026)"
            if record["filiere"]:
                breach_info["filiere"] = record["filiere"]

        breaches.append(breach_info)

    risk = classify_risk(max_risk)

    return {
        "found": True,
        "total_breaches": len(breaches),
        "breaches": breaches,
        "all_exposed_categories": list(all_categories),
        "category_details": [
            {**CATEGORY_LABELS.get(cat, {}), "key": cat}
            for cat in all_categories if cat in CATEGORY_LABELS
        ],
        "risk_score": max_risk,
        "risk": risk,
    }


PROTECTION_PLAN_SYSTEM_PROMPT = """Tu es WIQAYA, un assistant expert en cybersecurite et protection des donnees personnelles au Maroc. Tu generes des plans de protection personnalises pour les citoyens marocains dont les donnees ont ete exposees lors des cyberattaques contre la CNSS et l'OFPPT.

CONTEXTE JURIDIQUE MAROCAIN:
- Loi 09-08 relative a la protection des personnes physiques a l'egard du traitement des donnees a caractere personnel
- Loi 05-20 relative a la cybersecurite (promulguee en 2020)
- La CNDP (Commission Nationale de controle de la protection des Donnees a caractere Personnel) est l'autorite de regulation
- La DGSSI (Direction Generale de la Securite des Systemes d'Information) est l'autorite nationale de cybersecurite
- Le maCERT est le centre de veille, detection et reponse aux attaques informatiques

PROCEDURES CONCRETES AU MAROC:
- Plainte CNDP: formulaire en ligne sur www.cndp.ma ou par courrier au 15, Avenue Annakhil, Hay Riad, Rabat
- Signalement DGSSI: via le portail www.dgssi.gov.ma
- Depot de plainte police: Brigade Nationale de la Police Judiciaire (BNPJ) - section cybercriminalite
- Banques marocaines: procedure d'opposition carte et changement de RIB disponible en agence

INSTRUCTIONS:
1. Analyse le profil de risque fourni (categories de donnees exposees, source de la fuite, score de risque)
2. Genere un plan de protection en 5-8 etapes concretes, priorisees par urgence
3. Chaque etape doit inclure: l'action precise, pourquoi c'est important, comment le faire au Maroc
4. Utilise un langage clair et accessible, pas de jargon technique excessif
5. Adapte les recommandations aux donnees specifiquement exposees
6. IMPORTANT: Reponds en francais par defaut. Si le contexte indique l'arabe, reponds en arabe.

FORMAT DE REPONSE: JSON avec la structure suivante:
{
  "summary": "Resume de la situation en 2-3 phrases",
  "urgency": "immediate|high|medium|low",
  "steps": [
    {
      "priority": 1,
      "title": "Titre de l'action",
      "description": "Description detaillee",
      "why": "Pourquoi c'est important",
      "how": "Comment faire concretement au Maroc",
      "timeline": "Dans les 24h / Cette semaine / Ce mois"
    }
  ],
  "legal_rights": "Rappel des droits du citoyen sous la loi 09-08",
  "resources": [
    {"name": "Nom de la ressource", "url": "URL", "description": "Description"}
  ]
}"""

PHISHING_SIMULATOR_SYSTEM_PROMPT = """Tu es un expert en ingenierie sociale et en detection de phishing. Tu generes des scenarios de phishing REALISTES mais EDUCATIFS bases sur les donnees exposees d'un citoyen marocain.

CONTEXTE: Apres les fuites CNSS/OFPPT, les criminels utilisent les donnees exposees pour cibler les victimes avec des messages personnalises. Tu dois generer des exemples de ce type d'attaque pour EDUQUER l'utilisateur.

TYPES DE SCENARIOS A GENERER:
1. SMS frauduleux (smishing) - utilisant le nom reel, la banque, l'employeur
2. Email de phishing - imitant la CNSS, l'OFPPT, ou une banque marocaine
3. Appel telephonique (vishing) - script d'un faux agent bancaire
4. Message WhatsApp - fausse notification officielle

POUR CHAQUE SCENARIO:
- Genere le message tel qu'il apparaitrait (realiste et credible)
- Inclus les RED FLAGS (signaux d'alerte) numerotes
- Explique la technique utilisee par le fraudeur
- Donne le comportement correct a adopter

IMPORTANT: Les scenarios doivent etre contextualises au Maroc (banques marocaines, institutions marocaines, numeros marocains, darija parfois dans les SMS).

FORMAT JSON:
{
  "scenarios": [
    {
      "type": "sms|email|call|whatsapp",
      "type_label": "SMS frauduleux",
      "sender": "Expediteur affiche",
      "subject": "Objet (si email)",
      "content": "Le contenu du message frauduleux",
      "red_flags": [
        {"flag": "Description du signal d'alerte", "explanation": "Pourquoi c'est suspect"}
      ],
      "technique": "Nom de la technique (ex: urgence artificielle, usurpation d'identite)",
      "correct_action": "Ce qu'il faut faire face a ce message"
    }
  ],
  "general_tips": ["Conseil general 1", "Conseil general 2"]
}"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def scan_breach():
    data = request.get_json()
    query = data.get("query", "").strip()
    query_type = data.get("type", "cin")

    if not query:
        return jsonify({"error": "Veuillez fournir un identifiant"}), 400

    db = get_db()

    if query_type == "cin":
        records = db.execute(
            "SELECT * FROM breach_records WHERE UPPER(cin) = UPPER(?)", (query,)
        ).fetchall()
    elif query_type == "email":
        records = db.execute(
            "SELECT * FROM breach_records WHERE LOWER(email) = LOWER(?)", (query,)
        ).fetchall()
    else:
        return jsonify({"error": "Type de recherche invalide"}), 400

    db.close()

    if not records:
        return jsonify({
            "found": False,
            "message_fr": "Aucune exposition detectee pour cet identifiant dans nos bases.",
            "message_ar": "لم يتم اكتشاف أي تعرض لهذا المعرف في قواعد بياناتنا.",
            "note_fr": "Cela ne garantit pas que vos donnees n'ont pas ete compromises. Notre base couvre les fuites CNSS et OFPPT connues.",
            "note_ar": "هذا لا يضمن أن بياناتك لم تتعرض للاختراق. قاعدتنا تغطي التسريبات المعروفة للصندوق الوطني للضمان الاجتماعي ومكتب التكوين المهني."
        })

    report = build_exposure_report([dict(r) for r in records])
    return jsonify(report)


@app.route("/api/protection-plan", methods=["POST"])
def generate_protection_plan():
    if not OPENAI_API_KEY:
        return jsonify({"error": "Cle API OpenAI non configuree"}), 500

    data = request.get_json()
    risk_profile = data.get("risk_profile", {})
    language = data.get("language", "fr")

    user_prompt = f"""Profil de risque du citoyen:
- Score de risque: {risk_profile.get('risk_score', 'N/A')}/100
- Niveau: {risk_profile.get('risk', {}).get('level', 'N/A')}
- Sources des fuites: {', '.join(b.get('source', '') for b in risk_profile.get('breaches', []))}
- Categories de donnees exposees: {', '.join(risk_profile.get('all_exposed_categories', []))}
- Nombre de fuites: {risk_profile.get('total_breaches', 0)}

{"Reponds en arabe." if language == "ar" else "Reponds en francais."}

Genere un plan de protection personnalise pour ce citoyen."""

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PROTECTION_PLAN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        plan = json.loads(response.choices[0].message.content)
        return jsonify({"success": True, "plan": plan})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/phishing-simulator", methods=["POST"])
def generate_phishing_scenarios():
    if not OPENAI_API_KEY:
        return jsonify({"error": "Cle API OpenAI non configuree"}), 500

    data = request.get_json()
    risk_profile = data.get("risk_profile", {})
    language = data.get("language", "fr")

    breaches = risk_profile.get("breaches", [])
    exposed_cats = risk_profile.get("all_exposed_categories", [])

    context_parts = []
    for breach in breaches:
        if breach.get("employer"):
            context_parts.append(f"Employeur: {breach['employer']}")
        if breach.get("source") == "CNSS":
            context_parts.append("Victime de la fuite CNSS")
        if breach.get("source") == "OFPPT":
            context_parts.append(f"Etudiant OFPPT, filiere: {breach.get('filiere', 'N/A')}")

    user_prompt = f"""Contexte de la victime:
- Donnees exposees: {', '.join(exposed_cats)}
- {chr(10).join(context_parts)}
- Score de risque: {risk_profile.get('risk_score', 'N/A')}/100

{"Reponds en arabe." if language == "ar" else "Reponds en francais."}

Genere 3 scenarios de phishing realistes et educatifs ciblant cette personne, bases sur les donnees qui ont fuite. Chaque scenario doit utiliser les informations specifiques exposees pour montrer comment un fraudeur les exploiterait."""

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PHISHING_SIMULATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=2500,
            response_format={"type": "json_object"}
        )

        scenarios = json.loads(response.choices[0].message.content)
        return jsonify({"success": True, "scenarios": scenarios})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    db = get_db()
    stats = {
        "total_records": db.execute("SELECT COUNT(*) FROM breach_records").fetchone()[0],
        "cnss_records": db.execute("SELECT COUNT(*) FROM breach_records WHERE breach_source='CNSS'").fetchone()[0],
        "ofppt_records": db.execute("SELECT COUNT(*) FROM breach_records WHERE breach_source='OFPPT'").fetchone()[0],
        "avg_risk": round(db.execute("SELECT AVG(risk_score) FROM breach_records").fetchone()[0], 1),
        "high_risk_count": db.execute("SELECT COUNT(*) FROM breach_records WHERE risk_score >= 70").fetchone()[0],
        "critical_count": db.execute("SELECT COUNT(*) FROM breach_records WHERE risk_score >= 75").fetchone()[0],
    }
    db.close()
    return jsonify(stats)


@app.route("/api/demo-cin", methods=["GET"])
def get_demo_cin():
    db = get_db()
    record = db.execute(
        "SELECT cin, full_name, breach_source FROM breach_records WHERE risk_score >= 60 ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    db.close()
    if record:
        return jsonify({"cin": record["cin"], "name": record["full_name"], "source": record["breach_source"]})
    return jsonify({"error": "No records found"}), 404


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set. AI modules (protection plan, phishing simulator) will not work.")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print()

    print("WIQAYA -- Starting server...")
    print("   http://localhost:5000")
    print()
    app.run(debug=True, host="0.0.0.0", port=5000)
