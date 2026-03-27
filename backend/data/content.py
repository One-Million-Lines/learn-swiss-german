"""
MVP Data — Topics → Subtopics → Dialogues (beginner / intermediate)
"""

TOPICS = [
    {
        "id": "everyday-basics",
        "title": "Everyday Basics",
        "description": "Essential greetings, polite phrases, and basic expressions for daily life",
        "icon": "wave",
        "color": "from-red-500 to-orange-500",
    },
    {
        "id": "daily-life",
        "title": "Daily Life",
        "description": "Shopping, transport, eating out, and navigating your day in Switzerland",
        "icon": "home",
        "color": "from-blue-500 to-cyan-500",
    },
    {
        "id": "social",
        "title": "Social",
        "description": "Meeting people, small talk, making plans, and socializing",
        "icon": "handshake",
        "color": "from-purple-500 to-pink-500",
    },
    {
        "id": "work",
        "title": "Work",
        "description": "Office conversations, meetings, and professional Swiss German",
        "icon": "briefcase",
        "color": "from-emerald-500 to-teal-500",
    },
    {
        "id": "family-school",
        "title": "Family & School",
        "description": "Talking about family, school life, and everyday routines at home",
        "icon": "users",
        "color": "from-amber-500 to-yellow-500",
    },
    {
        "id": "practical-swiss-life",
        "title": "Practical Swiss Life",
        "description": "Doctor visits, appointments, bureaucracy, and Swiss-specific situations",
        "icon": "flag",
        "color": "from-rose-500 to-red-500",
    },
]


# ---------------------------------------------------------------------------
# SUBTOPICS  –  imported from individual subtopic files
# ---------------------------------------------------------------------------

from data.subtopic_saying_hello import SUBTOPIC_SAYING_HELLO
from data.subtopic_small_talk_neighbors import SUBTOPIC_SMALL_TALK_NEIGHBORS
from data.subtopic_buying_bread_coffee import SUBTOPIC_BUYING_BREAD_COFFEE
from data.subtopic_supermarket_checkout import SUBTOPIC_SUPERMARKET_CHECKOUT
from data.subtopic_asking_directions import SUBTOPIC_ASKING_DIRECTIONS
from data.subtopic_train_station import SUBTOPIC_TRAIN_STATION
from data.subtopic_making_plans_after_work import SUBTOPIC_MAKING_PLANS_AFTER_WORK
from data.subtopic_work_informal_chat import SUBTOPIC_WORK_INFORMAL_CHAT
from data.subtopic_talking_to_parents import SUBTOPIC_TALKING_TO_PARENTS
from data.subtopic_at_the_doctor import SUBTOPIC_AT_THE_DOCTOR
from data.subtopic_making_appointment import SUBTOPIC_MAKING_APPOINTMENT
from data.subtopic_landlord_repair import SUBTOPIC_LANDLORD_REPAIR

SUBTOPICS = [
    SUBTOPIC_SAYING_HELLO,
    SUBTOPIC_SMALL_TALK_NEIGHBORS,
    SUBTOPIC_BUYING_BREAD_COFFEE,
    SUBTOPIC_SUPERMARKET_CHECKOUT,
    SUBTOPIC_ASKING_DIRECTIONS,
    SUBTOPIC_TRAIN_STATION,
    SUBTOPIC_MAKING_PLANS_AFTER_WORK,
    SUBTOPIC_WORK_INFORMAL_CHAT,
    SUBTOPIC_TALKING_TO_PARENTS,
    SUBTOPIC_AT_THE_DOCTOR,
    SUBTOPIC_MAKING_APPOINTMENT,
    SUBTOPIC_LANDLORD_REPAIR,
]


# ---------------------------------------------------------------------------
# PATTERNS, VOCABULARY, DAILY_PHRASES  –  unchanged from previous version
# ---------------------------------------------------------------------------

PATTERNS = [
    {
        "id": "k-to-ch",
        "title": "K → Ch Shift",
        "description": "One of the most distinctive features of Swiss German. Initial 'k' becomes 'ch'.",
        "examples": [
            {"german": "Kopf", "swissGerman": "Chopf", "english": "head"},
            {"german": "Kind", "swissGerman": "Chind", "english": "child"},
            {"german": "kaufen", "swissGerman": "chaufe", "english": "to buy"},
            {"german": "kochen", "swissGerman": "choche", "english": "to cook"},
            {"german": "kalt", "swissGerman": "chalt", "english": "cold"},
        ],
    },
    {
        "id": "verb-pronoun-fusion",
        "title": "Verb + Pronoun Fusion",
        "description": "In Swiss German, subject pronouns commonly fuse with the verb ending.",
        "examples": [
            {"german": "hast du", "swissGerman": "hesch", "english": "have you / do you have"},
            {"german": "machst du", "swissGerman": "machsch", "english": "do you make/do"},
            {"german": "kommst du", "swissGerman": "chunsch", "english": "do you come"},
            {"german": "habe ich", "swissGerman": "hani", "english": "I have"},
            {"german": "wollen wir", "swissGerman": "wämmer", "english": "shall we"},
        ],
    },
    {
        "id": "diminutive-li",
        "title": "The -li Diminutive",
        "description": "Swiss German uses '-li' where standard German uses '-chen' or '-lein' for diminutives.",
        "examples": [
            {"german": "Brötchen", "swissGerman": "Weggli", "english": "bread roll"},
            {"german": "Mädchen", "swissGerman": "Meitli", "english": "girl"},
            {"german": "Croissant", "swissGerman": "Gipfeli", "english": "croissant"},
            {"german": "Päckchen", "swissGerman": "Päckli", "english": "package"},
        ],
    },
    {
        "id": "no-simple-past",
        "title": "No Simple Past Tense",
        "description": "Swiss German never uses the Präteritum (simple past). Everything uses Perfekt (have + participle).",
        "examples": [
            {"german": "Ich war müde", "swissGerman": "Ich bi müed gsi", "english": "I was tired"},
            {"german": "Ich ging", "swissGerman": "Ich bi gange", "english": "I went"},
            {"german": "Er sagte", "swissGerman": "Er hät gsäit", "english": "He said"},
            {"german": "Wir machten", "swissGerman": "Mir händ gmacht", "english": "We made/did"},
        ],
    },
    {
        "id": "go-particle",
        "title": "The 'go' Motion Particle",
        "description": "Swiss German adds 'go' before an infinitive to indicate motion toward an activity.",
        "examples": [
            {"german": "einkaufen gehen", "swissGerman": "go poschte", "english": "to go shopping"},
            {"german": "essen gehen", "swissGerman": "go esse", "english": "to go eat"},
            {"german": "schwimmen gehen", "swissGerman": "go schwümme", "english": "to go swimming"},
            {"german": "schauen gehen", "swissGerman": "go luege", "english": "to go look"},
        ],
    },
    {
        "id": "french-loanwords",
        "title": "French Loanwords",
        "description": "Swiss German borrows many words from French due to proximity to French-speaking Switzerland.",
        "examples": [
            {"german": "Danke", "swissGerman": "Merci", "english": "thank you"},
            {"german": "Entschuldigung", "swissGerman": "Exgüsi", "english": "excuse me"},
            {"german": "Fahrrad", "swissGerman": "Velo", "english": "bicycle"},
            {"german": "Fahrkarte", "swissGerman": "Billett", "english": "ticket"},
            {"german": "Bürgersteig", "swissGerman": "Trottoir", "english": "sidewalk"},
        ],
    },
    {
        "id": "infinitive-drop-n",
        "title": "Infinitive Drops -n",
        "description": "Swiss German infinitives typically drop the final '-n' or '-en'.",
        "examples": [
            {"german": "machen", "swissGerman": "mache", "english": "to make/do"},
            {"german": "schreiben", "swissGerman": "schriibe", "english": "to write"},
            {"german": "kaufen", "swissGerman": "chaufe", "english": "to buy"},
            {"german": "laufen", "swissGerman": "laufe", "english": "to walk/run"},
        ],
    },
]


VOCABULARY = [
    {
        "id": "greetings-farewells",
        "topicId": "everyday-basics",
        "title": "Greetings & Farewells",
        "words": [
            {"swissGerman": "Grüezi", "german": "Guten Tag", "english": "Hello (formal)"},
            {"swissGerman": "Hoi / Sali", "german": "Hallo", "english": "Hi (informal)"},
            {"swissGerman": "Guete Morge", "german": "Guten Morgen", "english": "Good morning"},
            {"swissGerman": "Guete Aabig", "german": "Guten Abend", "english": "Good evening"},
            {"swissGerman": "Guet Nacht", "german": "Gute Nacht", "english": "Good night"},
            {"swissGerman": "Tschau / Tschüss", "german": "Tschüss", "english": "Bye"},
            {"swissGerman": "Uf Wiedersee", "german": "Auf Wiedersehen", "english": "Goodbye (formal)"},
            {"swissGerman": "Bis morn", "german": "Bis morgen", "english": "See you tomorrow"},
        ],
    },
    {
        "id": "polite-expressions",
        "topicId": "everyday-basics",
        "title": "Polite Expressions",
        "words": [
            {"swissGerman": "Merci / Danke", "german": "Danke", "english": "Thank you"},
            {"swissGerman": "Merci vilmal", "german": "Vielen Dank", "english": "Thank you very much"},
            {"swissGerman": "Bitte", "german": "Bitte", "english": "Please / You're welcome"},
            {"swissGerman": "Exgüsi", "german": "Entschuldigung", "english": "Excuse me"},
            {"swissGerman": "Kei Problem", "german": "Kein Problem", "english": "No problem"},
        ],
    },
    {
        "id": "food-drink",
        "topicId": "daily-life",
        "title": "Food & Drink",
        "words": [
            {"swissGerman": "Kafi", "german": "Kaffee", "english": "coffee"},
            {"swissGerman": "Gipfeli", "german": "Croissant", "english": "croissant"},
            {"swissGerman": "Weggli", "german": "Brötchen", "english": "bread roll"},
            {"swissGerman": "Znüni", "german": "Vormittagssnack", "english": "morning snack"},
            {"swissGerman": "Zmittag", "german": "Mittagessen", "english": "lunch"},
            {"swissGerman": "Zvieri", "german": "Nachmittagssnack", "english": "afternoon snack"},
            {"swissGerman": "Znacht", "german": "Abendessen", "english": "dinner"},
        ],
    },
    {
        "id": "transport",
        "topicId": "daily-life",
        "title": "Transport & Getting Around",
        "words": [
            {"swissGerman": "Zug", "german": "Zug", "english": "train"},
            {"swissGerman": "Tram", "german": "Straßenbahn", "english": "tram"},
            {"swissGerman": "Velo", "german": "Fahrrad", "english": "bicycle"},
            {"swissGerman": "Billett", "german": "Fahrkarte", "english": "ticket"},
            {"swissGerman": "Gleis", "german": "Gleis", "english": "platform/track"},
            {"swissGerman": "Bahnhof", "german": "Bahnhof", "english": "train station"},
        ],
    },
    {
        "id": "family-people",
        "topicId": "family-school",
        "title": "Family & People",
        "words": [
            {"swissGerman": "Muetter / Mami", "german": "Mutter / Mama", "english": "mother / mom"},
            {"swissGerman": "Vatter / Papi", "german": "Vater / Papa", "english": "father / dad"},
            {"swissGerman": "Chind", "german": "Kind/Kinder", "english": "child/children"},
            {"swissGerman": "Bueb", "german": "Junge", "english": "boy"},
            {"swissGerman": "Meitli", "german": "Mädchen", "english": "girl"},
            {"swissGerman": "Gschwiister", "german": "Geschwister", "english": "siblings"},
        ],
    },
    {
        "id": "work-office",
        "topicId": "work",
        "title": "Work & Office",
        "words": [
            {"swissGerman": "schaffe", "german": "arbeiten", "english": "to work"},
            {"swissGerman": "Büro", "german": "Büro", "english": "office"},
            {"swissGerman": "Sitzig", "german": "Sitzung/Meeting", "english": "meeting"},
            {"swissGerman": "Bricht", "german": "Bericht", "english": "report"},
            {"swissGerman": "Chef/Chefin", "german": "Chef/Chefin", "english": "boss"},
            {"swissGerman": "Ferie", "german": "Urlaub/Ferien", "english": "vacation"},
        ],
    },
    {
        "id": "health",
        "topicId": "practical-swiss-life",
        "title": "Health & Body",
        "words": [
            {"swissGerman": "Chopfweh", "german": "Kopfschmerzen", "english": "headache"},
            {"swissGerman": "Buuchweh", "german": "Bauchschmerzen", "english": "stomachache"},
            {"swissGerman": "Halsschmerze", "german": "Halsschmerzen", "english": "sore throat"},
            {"swissGerman": "Fieber", "german": "Fieber", "english": "fever"},
            {"swissGerman": "Dokter / Arzt", "german": "Arzt", "english": "doctor"},
            {"swissGerman": "Apothek", "german": "Apotheke", "english": "pharmacy"},
        ],
    },
    {
        "id": "numbers-time",
        "topicId": "everyday-basics",
        "title": "Numbers & Time",
        "words": [
            {"swissGerman": "eis", "german": "eins", "english": "one"},
            {"swissGerman": "zwöi", "german": "zwei", "english": "two"},
            {"swissGerman": "drü", "german": "drei", "english": "three"},
            {"swissGerman": "vier", "german": "vier", "english": "four"},
            {"swissGerman": "föif", "german": "fünf", "english": "five"},
            {"swissGerman": "hüt", "german": "heute", "english": "today"},
            {"swissGerman": "morn", "german": "morgen", "english": "tomorrow"},
            {"swissGerman": "geschter", "german": "gestern", "english": "yesterday"},
        ],
    },
]


DAILY_PHRASES = [
    {"swissGerman": "Wie gaht's dir?", "german": "Wie geht es dir?", "english": "How are you?", "topic": "Greetings"},
    {"swissGerman": "Ich hätt gern en Kafi", "german": "Ich hätte gern einen Kaffee", "english": "I'd like a coffee", "topic": "Daily Life"},
    {"swissGerman": "Hesch Ziit?", "german": "Hast du Zeit?", "english": "Do you have time?", "topic": "Social"},
    {"swissGerman": "Das isch mega guet!", "german": "Das ist mega gut!", "english": "That's really great!", "topic": "Social"},
    {"swissGerman": "Exgüsi, wo isch de Bahnhof?", "german": "Entschuldigung, wo ist der Bahnhof?", "english": "Excuse me, where is the train station?", "topic": "Daily Life"},
    {"swissGerman": "Schöne Tag no!", "german": "Schönen Tag noch!", "english": "Have a nice day!", "topic": "Greetings"},
    {"swissGerman": "Was chostet das?", "german": "Was kostet das?", "english": "How much does that cost?", "topic": "Daily Life"},
    {"swissGerman": "Merci vilmal!", "german": "Vielen Dank!", "english": "Thank you very much!", "topic": "Greetings"},
    {"swissGerman": "Ich verstah nöd", "german": "Ich verstehe nicht", "english": "I don't understand", "topic": "Everyday Basics"},
    {"swissGerman": "Mir chönnted go wandere", "german": "Wir könnten wandern gehen", "english": "We could go hiking", "topic": "Social"},
    {"swissGerman": "Ich bi müed", "german": "Ich bin müde", "english": "I'm tired", "topic": "Family"},
    {"swissGerman": "Guete Morge, zäme!", "german": "Guten Morgen, zusammen!", "english": "Good morning, everyone!", "topic": "Work"},
]