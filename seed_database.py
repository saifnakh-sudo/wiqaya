import sqlite3
import random
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "wiqaya.db")

FIRST_NAMES_M = [
    "Mohammed", "Ahmed", "Youssef", "Amine", "Omar", "Hassan", "Rachid",
    "Khalid", "Samir", "Karim", "Mehdi", "Hamza", "Bilal", "Zakaria",
    "Nabil", "Adil", "Mustapha", "Abdellatif", "Driss", "Brahim",
    "Taha", "Imad", "Issam", "Reda", "Soufiane", "Othmane", "Ayoub",
    "Anass", "Walid", "Jawad", "Hicham", "Fouad", "Aziz", "Tarik"
]

FIRST_NAMES_F = [
    "Fatima", "Khadija", "Aicha", "Meryem", "Salma", "Nadia", "Houda",
    "Sanae", "Laila", "Zineb", "Hajar", "Amina", "Sara", "Imane",
    "Nawal", "Soukaina", "Ghita", "Oumaima", "Hanane", "Mouna",
    "Wafae", "Loubna", "Asmae", "Karima", "Samira", "Rajae", "Ikram"
]

LAST_NAMES = [
    "Bennani", "Alaoui", "Tazi", "El Idrissi", "Berrada", "Chraibi",
    "Fassi Fihri", "El Amrani", "Bouchta", "Kettani", "Sqalli",
    "Benkirane", "El Ouazzani", "Mansouri", "Lahlou", "Cherkaoui",
    "El Harti", "Benjelloun", "Mernissi", "Filali", "Bouzid",
    "Tahiri", "Naciri", "Andaloussi", "Senhaji", "Ziani", "Ouahbi",
    "Bouazza", "Haddaoui", "Rhazi", "Amzazi", "El Malki", "Kabbaj",
    "Bensouda", "Guedira", "El Fassi", "Benamour", "Slaoui"
]

CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Fes", "Tanger", "Agadir",
    "Meknes", "Oujda", "Kenitra", "Tetouan", "Safi", "El Jadida",
    "Nador", "Beni Mellal", "Mohammedia", "Khouribga", "Settat",
    "Berrechid", "Sale", "Temara", "Larache", "Khemisset"
]

EMPLOYERS = [
    "OCP Group", "Maroc Telecom", "Bank Al-Maghrib", "ONCF",
    "Attijariwafa Bank", "BMCE Bank", "Banque Populaire", "Royal Air Maroc",
    "Managem Group", "Lydec", "ONEE", "Marsa Maroc", "LafargeHolcim Maroc",
    "Renault Maroc", "Groupe Addoha", "Cosumar", "Centrale Danone",
    "Inwi", "Orange Maroc", "Societe Generale Maroc", "CDG",
    "TMSA", "Tanger Med", "OFPPT", "CHU Ibn Sina", "CNSS",
    "Ministere de la Sante", "Ministere de l'Education", "ANAPEC",
    "Auto Hall", "Label'Vie", "Marjane Holding", "Kitea",
    "Stroc Industrie", "Menara Holding", "Palmeraie Holding",
    "Akwa Group", "Ynna Holding", "Saham Group", "Wafa Assurance"
]

BANKS = [
    "Attijariwafa Bank", "BMCE Bank of Africa", "Banque Populaire",
    "Societe Generale Maroc", "CIH Bank", "Credit du Maroc",
    "BMCI", "CDM", "Al Barid Bank", "CFG Bank", "Bank Assafa",
    "Credit Agricole du Maroc"
]

OFPPT_FILIERES = [
    "Developpement Digital", "Infrastructure Digitale",
    "Technicien Specialise en Electricite",
    "Technicien en Maintenance Industrielle",
    "Gestion des Entreprises", "Commerce",
    "Technicien Comptable d'Entreprises",
    "Cuisine", "Hotellerie", "Tourisme",
    "Mecanique Auto", "Electromecanique",
    "Dessin de Batiment", "Construction Metallique",
    "Secretariat de Direction", "Logistique"
]

OFPPT_CENTERS = [
    "ISTA Hay Riad Rabat", "ISTA NTIC Casablanca", "ISTA Kenitra",
    "ISTA Tanger", "ISTA Fes", "ISTA Marrakech", "ISTA Agadir",
    "ISTA Meknes", "ISTA Oujda", "ISTA Tetouan", "ISTA Safi",
    "CFP Casablanca", "CFP Rabat", "CFP Tanger", "CFP Marrakech"
]

BREACH_CNSS = "CNSS"
BREACH_OFPPT = "OFPPT"

DATA_CATEGORIES = {
    BREACH_CNSS: [
        "cin", "full_name", "email", "phone", "employer",
        "salary", "bank_account", "bank_name", "birth_date"
    ],
    BREACH_OFPPT: [
        "cin", "full_name", "email", "phone", "filiere",
        "center", "diploma_level", "enrollment_year"
    ]
}


def generate_cin():
    letters = random.choice(["A", "B", "BE", "BH", "BJ", "BK", "C", "D",
                              "DA", "E", "EE", "F", "G", "H", "I", "J",
                              "K", "L", "M", "N", "P", "Q", "R", "S", "T",
                              "U", "V", "W", "X", "Z"])
    numbers = random.randint(100000, 999999)
    return f"{letters}{numbers}"


def generate_phone():
    prefixes = ["0661", "0662", "0668", "0670", "0671", "0672",
                "0700", "0708", "0610", "0611", "0612", "0613"]
    return f"{random.choice(prefixes)}{random.randint(100000, 999999)}"


def generate_email(first, last):
    domains = ["gmail.com", "yahoo.fr", "hotmail.com", "outlook.com",
               "live.fr", "hotmail.fr", "yahoo.com"]
    sep = random.choice([".", "_", ""])
    num = random.choice(["", str(random.randint(1, 99)), str(random.randint(1990, 2005))])
    first_clean = first.lower().replace(" ", "")
    last_clean = last.lower().replace(" ", "")
    return f"{first_clean}{sep}{last_clean}{num}@{random.choice(domains)}"


def generate_bank_account():
    return f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000000000, 9999999999)}{random.randint(10, 99)}"


def generate_salary():
    brackets = [
        (2800, 4000, 0.25),
        (4000, 7000, 0.30),
        (7000, 15000, 0.25),
        (15000, 30000, 0.12),
        (30000, 80000, 0.06),
        (80000, 200000, 0.02),
    ]
    r = random.random()
    cumulative = 0
    for low, high, prob in brackets:
        cumulative += prob
        if r <= cumulative:
            return round(random.uniform(low, high), 2)
    return round(random.uniform(2800, 4000), 2)


def hash_identifier(value):
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def create_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS breach_records")
    c.execute("DROP TABLE IF EXISTS breach_lookup")

    c.execute("""
        CREATE TABLE breach_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            breach_source TEXT NOT NULL,
            cin TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            city TEXT,
            employer TEXT,
            salary REAL,
            bank_account TEXT,
            bank_name TEXT,
            birth_date TEXT,
            filiere TEXT,
            center TEXT,
            diploma_level TEXT,
            enrollment_year INTEGER,
            exposed_categories TEXT,
            risk_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE breach_lookup (
            lookup_hash TEXT NOT NULL,
            lookup_type TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            FOREIGN KEY (record_id) REFERENCES breach_records(id)
        )
    """)

    c.execute("CREATE INDEX idx_lookup_hash ON breach_lookup(lookup_hash)")
    c.execute("CREATE INDEX idx_cin ON breach_records(cin)")
    c.execute("CREATE INDEX idx_email ON breach_records(email)")

    conn.commit()
    return conn


def calculate_risk_score(categories):
    weights = {
        "cin": 20, "full_name": 5, "email": 8, "phone": 10,
        "employer": 5, "salary": 15, "bank_account": 25,
        "bank_name": 8, "birth_date": 10, "filiere": 3,
        "center": 3, "diploma_level": 3, "enrollment_year": 2
    }
    score = sum(weights.get(cat, 0) for cat in categories)
    return min(score, 100)


def seed_cnss_records(conn, count=3000):
    c = conn.cursor()
    records = []

    for _ in range(count):
        is_female = random.random() < 0.35
        first = random.choice(FIRST_NAMES_F if is_female else FIRST_NAMES_M)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        cin = generate_cin()
        email = generate_email(first, last)
        phone = generate_phone()
        city = random.choice(CITIES)
        employer = random.choice(EMPLOYERS)
        salary = generate_salary()
        bank_account = generate_bank_account()
        bank_name = random.choice(BANKS)
        birth_year = random.randint(1960, 2000)
        birth_date = f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{birth_year}"

        all_cats = DATA_CATEGORIES[BREACH_CNSS].copy()
        num_exposed = random.randint(5, len(all_cats))
        exposed = random.sample(all_cats, num_exposed)
        if "cin" not in exposed:
            exposed.append("cin")
        if "full_name" not in exposed:
            exposed.append("full_name")

        risk = calculate_risk_score(exposed)
        exposed_str = ",".join(exposed)

        records.append((
            BREACH_CNSS, cin, full_name, email, phone, city,
            employer, salary, bank_account, bank_name, birth_date,
            None, None, None, None,
            exposed_str, risk
        ))

    c.executemany("""
        INSERT INTO breach_records (
            breach_source, cin, full_name, email, phone, city,
            employer, salary, bank_account, bank_name, birth_date,
            filiere, center, diploma_level, enrollment_year,
            exposed_categories, risk_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    print(f"  [OK] {count} CNSS records generated")
    return records


def seed_ofppt_records(conn, count=2000):
    c = conn.cursor()
    records = []

    for _ in range(count):
        is_female = random.random() < 0.45
        first = random.choice(FIRST_NAMES_F if is_female else FIRST_NAMES_M)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        cin = generate_cin()
        email = generate_email(first, last)
        phone = generate_phone()
        city = random.choice(CITIES)
        filiere = random.choice(OFPPT_FILIERES)
        center = random.choice(OFPPT_CENTERS)
        diploma_level = random.choice(["Technicien", "Technicien Specialise", "Qualification", "Specialisation"])
        enrollment_year = random.randint(2018, 2026)

        all_cats = DATA_CATEGORIES[BREACH_OFPPT].copy()
        num_exposed = random.randint(4, len(all_cats))
        exposed = random.sample(all_cats, num_exposed)
        if "cin" not in exposed:
            exposed.append("cin")
        if "full_name" not in exposed:
            exposed.append("full_name")

        risk = calculate_risk_score(exposed)
        exposed_str = ",".join(exposed)

        records.append((
            BREACH_OFPPT, cin, full_name, email, phone, city,
            None, None, None, None, None,
            filiere, center, diploma_level, enrollment_year,
            exposed_str, risk
        ))

    c.executemany("""
        INSERT INTO breach_records (
            breach_source, cin, full_name, email, phone, city,
            employer, salary, bank_account, bank_name, birth_date,
            filiere, center, diploma_level, enrollment_year,
            exposed_categories, risk_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    print(f"  [OK] {count} OFPPT records generated")


def build_lookup_index(conn):
    c = conn.cursor()
    c.execute("SELECT id, cin, email FROM breach_records")
    rows = c.fetchall()

    lookups = []
    for row_id, cin, email in rows:
        lookups.append((hash_identifier(cin.upper()), "cin", row_id))
        if email:
            lookups.append((hash_identifier(email.lower()), "email", row_id))

    c.executemany("INSERT INTO breach_lookup (lookup_hash, lookup_type, record_id) VALUES (?, ?, ?)", lookups)
    conn.commit()
    print(f"  [OK] Lookup index built ({len(lookups)} entries)")


def main():
    print("WIQAYA -- Seeding synthetic breach database...")
    print()
    conn = create_database()
    seed_cnss_records(conn, count=3000)
    seed_ofppt_records(conn, count=2000)
    build_lookup_index(conn)
    print()

    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM breach_records")
    total = c.fetchone()[0]
    c.execute("SELECT AVG(risk_score) FROM breach_records")
    avg_risk = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM breach_records WHERE risk_score >= 70")
    high_risk = c.fetchone()[0]

    print(f"Database ready: {total} records")
    print(f"   Average risk score: {avg_risk:.1f}/100")
    print(f"   High risk (>=70): {high_risk} records")
    print(f"   File: {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
