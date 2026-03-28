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
from data.subtopic_job_interview import SUBTOPIC_JOB_INTERVIEW
from data.subtopic_office_it_problems import SUBTOPIC_OFFICE_IT_PROBLEMS
from data.subtopic_presenting_meeting import SUBTOPIC_PRESENTING_MEETING
from data.subtopic_hr_salary_talk import SUBTOPIC_HR_SALARY_TALK
from data.subtopic_client_call import SUBTOPIC_CLIENT_CALL
from data.subtopic_onboarding_new_employee import SUBTOPIC_ONBOARDING_NEW_EMPLOYEE
from data.subtopic_working_from_home import SUBTOPIC_WORKING_FROM_HOME
from data.subtopic_bank_office import SUBTOPIC_BANK_OFFICE
from data.subtopic_construction_site import SUBTOPIC_CONSTRUCTION_SITE
from data.subtopic_restaurant_kitchen import SUBTOPIC_RESTAURANT_KITCHEN
from data.subtopic_retail_shop import SUBTOPIC_RETAIL_SHOP
from data.subtopic_warehouse_logistics import SUBTOPIC_WAREHOUSE_LOGISTICS
from data.subtopic_farming import SUBTOPIC_FARMING
from data.subtopic_hairdresser import SUBTOPIC_HAIRDRESSER
from data.subtopic_cleaning_job import SUBTOPIC_CLEANING_JOB
from data.subtopic_newborn_baby import SUBTOPIC_NEWBORN_BABY
from data.subtopic_baby_toddler import SUBTOPIC_BABY_TODDLER
from data.subtopic_kita_daycare import SUBTOPIC_KITA_DAYCARE
from data.subtopic_kindergarten import SUBTOPIC_KINDERGARTEN
from data.subtopic_primarschule import SUBTOPIC_PRIMARSCHULE
from data.subtopic_elternabend import SUBTOPIC_ELTERNABEND
from data.subtopic_homework_studying import SUBTOPIC_HOMEWORK_STUDYING
from data.subtopic_sekundarschule import SUBTOPIC_SEKUNDARSCHULE
from data.subtopic_gymnasium import SUBTOPIC_GYMNASIUM
from data.subtopic_berufslehre import SUBTOPIC_BERUFSLEHRE
from data.subtopic_schulreise import SUBTOPIC_SCHULREISE
from data.subtopic_zeugnis_day import SUBTOPIC_ZEUGNIS_DAY
from data.subtopic_spielplatz import SUBTOPIC_SPIELPLATZ
from data.subtopic_park_family import SUBTOPIC_PARK_FAMILY
from data.subtopic_pausenplatz import SUBTOPIC_PAUSENPLATZ
from data.subtopic_family_vacation import SUBTOPIC_FAMILY_VACATION
from data.subtopic_morning_routine_family import SUBTOPIC_MORNING_ROUTINE_FAMILY
from data.subtopic_bedtime_routine import SUBTOPIC_BEDTIME_ROUTINE
from data.subtopic_family_meals import SUBTOPIC_FAMILY_MEALS
from data.subtopic_weekend_family import SUBTOPIC_WEEKEND_FAMILY
from data.subtopic_kids_birthday import SUBTOPIC_KIDS_BIRTHDAY
from data.subtopic_visiting_grandparents import SUBTOPIC_VISITING_GRANDPARENTS
from data.subtopic_first_contact import SUBTOPIC_FIRST_CONTACT
from data.subtopic_breaking_the_ice import SUBTOPIC_BREAKING_THE_ICE
from data.subtopic_talking_about_yourself import SUBTOPIC_TALKING_ABOUT_YOURSELF
from data.subtopic_asking_about_others import SUBTOPIC_ASKING_ABOUT_OTHERS
from data.subtopic_reacting_naturally import SUBTOPIC_REACTING_NATURALLY
from data.subtopic_casual_opinions import SUBTOPIC_CASUAL_OPINIONS
from data.subtopic_humor_light_tone import SUBTOPIC_HUMOR_LIGHT_TONE
from data.subtopic_making_plans_social import SUBTOPIC_MAKING_PLANS_SOCIAL
from data.subtopic_invitations import SUBTOPIC_INVITATIONS
from data.subtopic_social_flow import SUBTOPIC_SOCIAL_FLOW
from data.subtopic_social_etiquette import SUBTOPIC_SOCIAL_ETIQUETTE
from data.subtopic_ending_interactions import SUBTOPIC_ENDING_INTERACTIONS
from data.subtopic_staying_in_touch import SUBTOPIC_STAYING_IN_TOUCH
from data.subtopic_shopping_local_shops import SUBTOPIC_SHOPPING_LOCAL_SHOPS
from data.subtopic_daily_services import SUBTOPIC_DAILY_SERVICES
from data.subtopic_eating_out import SUBTOPIC_EATING_OUT
from data.subtopic_public_transport import SUBTOPIC_PUBLIC_TRANSPORT
from data.subtopic_understanding_directions import SUBTOPIC_UNDERSTANDING_DIRECTIONS
from data.subtopic_appointments_scheduling import SUBTOPIC_APPOINTMENTS_SCHEDULING
from data.subtopic_time_planning import SUBTOPIC_TIME_PLANNING
from data.subtopic_housing_daily import SUBTOPIC_HOUSING_DAILY
from data.subtopic_utilities_basic_needs import SUBTOPIC_UTILITIES_BASIC_NEEDS
from data.subtopic_health_pharmacy import SUBTOPIC_HEALTH_PHARMACY
from data.subtopic_personal_errands import SUBTOPIC_PERSONAL_ERRANDS
from data.subtopic_weather_daily import SUBTOPIC_WEATHER_DAILY
from data.subtopic_handling_problems import SUBTOPIC_HANDLING_PROBLEMS
from data.subtopic_safety_urgent import SUBTOPIC_SAFETY_URGENT
from data.subtopic_greetings_goodbyes import SUBTOPIC_GREETINGS_GOODBYES
from data.subtopic_politeness_essentials import SUBTOPIC_POLITENESS_ESSENTIALS
from data.subtopic_yes_no_maybe import SUBTOPIC_YES_NO_MAYBE
from data.subtopic_basic_needs_requests import SUBTOPIC_BASIC_NEEDS_REQUESTS
from data.subtopic_understanding_misunderstanding import SUBTOPIC_UNDERSTANDING_MISUNDERSTANDING
from data.subtopic_basic_questions import SUBTOPIC_BASIC_QUESTIONS
from data.subtopic_numbers_quantities import SUBTOPIC_NUMBERS_QUANTITIES
from data.subtopic_time_basics import SUBTOPIC_TIME_BASICS
from data.subtopic_directions_basic import SUBTOPIC_DIRECTIONS_BASIC
from data.subtopic_common_verbs import SUBTOPIC_COMMON_VERBS
from data.subtopic_basic_connectors import SUBTOPIC_BASIC_CONNECTORS
from data.subtopic_simple_reactions import SUBTOPIC_SIMPLE_REACTIONS
from data.subtopic_confirming_clarifying import SUBTOPIC_CONFIRMING_CLARIFYING
from data.subtopic_closing_micro_interactions import SUBTOPIC_CLOSING_MICRO_INTERACTIONS
from data.subtopic_healthcare_insurance import SUBTOPIC_HEALTHCARE_INSURANCE
from data.subtopic_pharmacy_swiss import SUBTOPIC_PHARMACY_SWISS
from data.subtopic_appointments_formal import SUBTOPIC_APPOINTMENTS_FORMAL
from data.subtopic_gemeinde_admin import SUBTOPIC_GEMEINDE_ADMIN
from data.subtopic_permits_residency import SUBTOPIC_PERMITS_RESIDENCY
from data.subtopic_insurance_general import SUBTOPIC_INSURANCE_GENERAL
from data.subtopic_housing_swiss import SUBTOPIC_HOUSING_SWISS
from data.subtopic_mail_official_letters import SUBTOPIC_MAIL_OFFICIAL_LETTERS
from data.subtopic_banking_payments import SUBTOPIC_BANKING_PAYMENTS
from data.subtopic_taxes_basic import SUBTOPIC_TAXES_BASIC
from data.subtopic_work_admin import SUBTOPIC_WORK_ADMIN
from data.subtopic_school_childcare import SUBTOPIC_SCHOOL_CHILDCARE
from data.subtopic_waste_recycling import SUBTOPIC_WASTE_RECYCLING
from data.subtopic_transport_swiss import SUBTOPIC_TRANSPORT_SWISS
from data.subtopic_rules_compliance import SUBTOPIC_RULES_COMPLIANCE

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
    SUBTOPIC_JOB_INTERVIEW,
    SUBTOPIC_OFFICE_IT_PROBLEMS,
    SUBTOPIC_PRESENTING_MEETING,
    SUBTOPIC_HR_SALARY_TALK,
    SUBTOPIC_CLIENT_CALL,
    SUBTOPIC_ONBOARDING_NEW_EMPLOYEE,
    SUBTOPIC_WORKING_FROM_HOME,
    SUBTOPIC_BANK_OFFICE,
    SUBTOPIC_CONSTRUCTION_SITE,
    SUBTOPIC_RESTAURANT_KITCHEN,
    SUBTOPIC_RETAIL_SHOP,
    SUBTOPIC_WAREHOUSE_LOGISTICS,
    SUBTOPIC_FARMING,
    SUBTOPIC_HAIRDRESSER,
    SUBTOPIC_CLEANING_JOB,
    SUBTOPIC_NEWBORN_BABY,
    SUBTOPIC_BABY_TODDLER,
    SUBTOPIC_KITA_DAYCARE,
    SUBTOPIC_KINDERGARTEN,
    SUBTOPIC_PRIMARSCHULE,
    SUBTOPIC_ELTERNABEND,
    SUBTOPIC_HOMEWORK_STUDYING,
    SUBTOPIC_SEKUNDARSCHULE,
    SUBTOPIC_GYMNASIUM,
    SUBTOPIC_BERUFSLEHRE,
    SUBTOPIC_SCHULREISE,
    SUBTOPIC_ZEUGNIS_DAY,
    SUBTOPIC_SPIELPLATZ,
    SUBTOPIC_PARK_FAMILY,
    SUBTOPIC_PAUSENPLATZ,
    SUBTOPIC_FAMILY_VACATION,
    SUBTOPIC_MORNING_ROUTINE_FAMILY,
    SUBTOPIC_BEDTIME_ROUTINE,
    SUBTOPIC_FAMILY_MEALS,
    SUBTOPIC_WEEKEND_FAMILY,
    SUBTOPIC_KIDS_BIRTHDAY,
    SUBTOPIC_VISITING_GRANDPARENTS,
    SUBTOPIC_FIRST_CONTACT,
    SUBTOPIC_BREAKING_THE_ICE,
    SUBTOPIC_TALKING_ABOUT_YOURSELF,
    SUBTOPIC_ASKING_ABOUT_OTHERS,
    SUBTOPIC_REACTING_NATURALLY,
    SUBTOPIC_CASUAL_OPINIONS,
    SUBTOPIC_HUMOR_LIGHT_TONE,
    SUBTOPIC_MAKING_PLANS_SOCIAL,
    SUBTOPIC_INVITATIONS,
    SUBTOPIC_SOCIAL_FLOW,
    SUBTOPIC_SOCIAL_ETIQUETTE,
    SUBTOPIC_ENDING_INTERACTIONS,
    SUBTOPIC_STAYING_IN_TOUCH,
    SUBTOPIC_SHOPPING_LOCAL_SHOPS,
    SUBTOPIC_DAILY_SERVICES,
    SUBTOPIC_EATING_OUT,
    SUBTOPIC_PUBLIC_TRANSPORT,
    SUBTOPIC_UNDERSTANDING_DIRECTIONS,
    SUBTOPIC_APPOINTMENTS_SCHEDULING,
    SUBTOPIC_TIME_PLANNING,
    SUBTOPIC_HOUSING_DAILY,
    SUBTOPIC_UTILITIES_BASIC_NEEDS,
    SUBTOPIC_HEALTH_PHARMACY,
    SUBTOPIC_PERSONAL_ERRANDS,
    SUBTOPIC_WEATHER_DAILY,
    SUBTOPIC_HANDLING_PROBLEMS,
    SUBTOPIC_SAFETY_URGENT,
    SUBTOPIC_GREETINGS_GOODBYES,
    SUBTOPIC_POLITENESS_ESSENTIALS,
    SUBTOPIC_YES_NO_MAYBE,
    SUBTOPIC_BASIC_NEEDS_REQUESTS,
    SUBTOPIC_UNDERSTANDING_MISUNDERSTANDING,
    SUBTOPIC_BASIC_QUESTIONS,
    SUBTOPIC_NUMBERS_QUANTITIES,
    SUBTOPIC_TIME_BASICS,
    SUBTOPIC_DIRECTIONS_BASIC,
    SUBTOPIC_COMMON_VERBS,
    SUBTOPIC_BASIC_CONNECTORS,
    SUBTOPIC_SIMPLE_REACTIONS,
    SUBTOPIC_CONFIRMING_CLARIFYING,
    SUBTOPIC_CLOSING_MICRO_INTERACTIONS,
    SUBTOPIC_HEALTHCARE_INSURANCE,
    SUBTOPIC_PHARMACY_SWISS,
    SUBTOPIC_APPOINTMENTS_FORMAL,
    SUBTOPIC_GEMEINDE_ADMIN,
    SUBTOPIC_PERMITS_RESIDENCY,
    SUBTOPIC_INSURANCE_GENERAL,
    SUBTOPIC_HOUSING_SWISS,
    SUBTOPIC_MAIL_OFFICIAL_LETTERS,
    SUBTOPIC_BANKING_PAYMENTS,
    SUBTOPIC_TAXES_BASIC,
    SUBTOPIC_WORK_ADMIN,
    SUBTOPIC_SCHOOL_CHILDCARE,
    SUBTOPIC_WASTE_RECYCLING,
    SUBTOPIC_TRANSPORT_SWISS,
    SUBTOPIC_RULES_COMPLIANCE,
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
    # --- Greetings ---
    {"swissGerman": "Wie gaht's dir?", "german": "Wie geht es dir?", "english": "How are you?", "topic": "Greetings"},
    {"swissGerman": "Schöne Tag no!", "german": "Schönen Tag noch!", "english": "Have a nice day!", "topic": "Greetings"},
    {"swissGerman": "Merci vilmal!", "german": "Vielen Dank!", "english": "Thank you very much!", "topic": "Greetings"},
    {"swissGerman": "Grüezi mitenand!", "german": "Guten Tag zusammen!", "english": "Hello everyone!", "topic": "Greetings"},
    {"swissGerman": "Schöne Aabig!", "german": "Schönen Abend!", "english": "Have a nice evening!", "topic": "Greetings"},
    {"swissGerman": "Bis bald!", "german": "Bis bald!", "english": "See you soon!", "topic": "Greetings"},
    {"swissGerman": "Bis spöter!", "german": "Bis später!", "english": "See you later!", "topic": "Greetings"},
    {"swissGerman": "Tschau zäme!", "german": "Tschüss zusammen!", "english": "Bye everyone!", "topic": "Greetings"},
    {"swissGerman": "Mir gaht's guet, merci!", "german": "Mir geht es gut, danke!", "english": "I'm fine, thanks!", "topic": "Greetings"},
    {"swissGerman": "Sali, wie lauft's?", "german": "Hallo, wie läuft's?", "english": "Hi, how's it going?", "topic": "Greetings"},
    {"swissGerman": "Schöns Wuchenänd!", "german": "Schönes Wochenende!", "english": "Have a nice weekend!", "topic": "Greetings"},
    # --- Daily Life ---
    {"swissGerman": "Ich hätt gern en Kafi", "german": "Ich hätte gern einen Kaffee", "english": "I'd like a coffee", "topic": "Daily Life"},
    {"swissGerman": "Exgüsi, wo isch de Bahnhof?", "german": "Entschuldigung, wo ist der Bahnhof?", "english": "Excuse me, where is the train station?", "topic": "Daily Life"},
    {"swissGerman": "Was chostet das?", "german": "Was kostet das?", "english": "How much does that cost?", "topic": "Daily Life"},
    {"swissGerman": "Ich muess go poschte", "german": "Ich muss einkaufen gehen", "english": "I need to go shopping", "topic": "Daily Life"},
    {"swissGerman": "Wänn fahrt de nächscht Zug?", "german": "Wann fährt der nächste Zug?", "english": "When does the next train leave?", "topic": "Daily Life"},
    {"swissGerman": "Ich nimm es Gipfeli, bitte", "german": "Ich nehme ein Croissant, bitte", "english": "I'll have a croissant, please", "topic": "Daily Life"},
    {"swissGerman": "Chann ich mit Charte zahle?", "german": "Kann ich mit Karte zahlen?", "english": "Can I pay by card?", "topic": "Daily Life"},
    {"swissGerman": "Wo isch de nächscht Coop?", "german": "Wo ist der nächste Coop?", "english": "Where is the nearest Coop?", "topic": "Daily Life"},
    {"swissGerman": "D'Rächnig, bitte!", "german": "Die Rechnung, bitte!", "english": "The bill, please!", "topic": "Daily Life"},
    {"swissGerman": "Ich ha Hunger", "german": "Ich habe Hunger", "english": "I'm hungry", "topic": "Daily Life"},
    {"swissGerman": "Ich ha Durscht", "german": "Ich habe Durst", "english": "I'm thirsty", "topic": "Daily Life"},
    {"swissGerman": "Isch de Platz no frei?", "german": "Ist der Platz noch frei?", "english": "Is this seat still free?", "topic": "Daily Life"},
    {"swissGerman": "Händ Sie no Brot?", "german": "Haben Sie noch Brot?", "english": "Do you still have bread?", "topic": "Daily Life"},
    {"swissGerman": "En Retour uf Züri, bitte", "german": "Eine Rückfahrkarte nach Zürich, bitte", "english": "A return ticket to Zurich, please", "topic": "Daily Life"},
    {"swissGerman": "Wo muess ich umstiige?", "german": "Wo muss ich umsteigen?", "english": "Where do I need to change?", "topic": "Daily Life"},
    # --- Social ---
    {"swissGerman": "Hesch Ziit?", "german": "Hast du Zeit?", "english": "Do you have time?", "topic": "Social"},
    {"swissGerman": "Das isch mega guet!", "german": "Das ist mega gut!", "english": "That's really great!", "topic": "Social"},
    {"swissGerman": "Mir chönnted go wandere", "german": "Wir könnten wandern gehen", "english": "We could go hiking", "topic": "Social"},
    {"swissGerman": "Wämmer öppis go trinke?", "german": "Wollen wir etwas trinken gehen?", "english": "Shall we go for a drink?", "topic": "Social"},
    {"swissGerman": "Das isch luschtig!", "german": "Das ist lustig!", "english": "That's funny!", "topic": "Social"},
    {"swissGerman": "Mir händ's mega cool gha!", "german": "Wir hatten es mega cool!", "english": "We had a great time!", "topic": "Social"},
    {"swissGerman": "Woher chunsch du?", "german": "Woher kommst du?", "english": "Where are you from?", "topic": "Social"},
    {"swissGerman": "Wie lang bisch scho i de Schwiiz?", "german": "Wie lange bist du schon in der Schweiz?", "english": "How long have you been in Switzerland?", "topic": "Social"},
    {"swissGerman": "Gömmer is Kino?", "german": "Gehen wir ins Kino?", "english": "Shall we go to the cinema?", "topic": "Social"},
    {"swissGerman": "Ich find das super!", "german": "Ich finde das super!", "english": "I think that's great!", "topic": "Social"},
    {"swissGerman": "Häsch Luscht uf en Kafi?", "german": "Hast du Lust auf einen Kaffee?", "english": "Do you feel like a coffee?", "topic": "Social"},
    {"swissGerman": "Mir gsehn eus am Samschtig!", "german": "Wir sehen uns am Samstag!", "english": "See you on Saturday!", "topic": "Social"},
    {"swissGerman": "Ich freu mi druf!", "german": "Ich freue mich darauf!", "english": "I'm looking forward to it!", "topic": "Social"},
    {"swissGerman": "Was machsch am Wuchenänd?", "german": "Was machst du am Wochenende?", "english": "What are you doing on the weekend?", "topic": "Social"},
    # --- Everyday Basics ---
    {"swissGerman": "Ich verstah nöd", "german": "Ich verstehe nicht", "english": "I don't understand", "topic": "Everyday Basics"},
    {"swissGerman": "Chönd Sie das bitte wiederhole?", "german": "Können Sie das bitte wiederholen?", "english": "Can you please repeat that?", "topic": "Everyday Basics"},
    {"swissGerman": "Wie säit me das uf Schwizerdütsch?", "german": "Wie sagt man das auf Schweizerdeutsch?", "english": "How do you say that in Swiss German?", "topic": "Everyday Basics"},
    {"swissGerman": "Ich lerne Schwizerdütsch", "german": "Ich lerne Schweizerdeutsch", "english": "I'm learning Swiss German", "topic": "Everyday Basics"},
    {"swissGerman": "Chönd Sie bitte langsamer rede?", "german": "Können Sie bitte langsamer sprechen?", "english": "Can you please speak slower?", "topic": "Everyday Basics"},
    {"swissGerman": "Ja, genau!", "german": "Ja, genau!", "english": "Yes, exactly!", "topic": "Everyday Basics"},
    {"swissGerman": "Nei, danke!", "german": "Nein, danke!", "english": "No, thanks!", "topic": "Everyday Basics"},
    {"swissGerman": "Kei Ahnig!", "german": "Keine Ahnung!", "english": "No idea!", "topic": "Everyday Basics"},
    {"swissGerman": "Das isch egal", "german": "Das ist egal", "english": "It doesn't matter", "topic": "Everyday Basics"},
    {"swissGerman": "Gopfriedstutz!", "german": "Ach du meine Güte!", "english": "Oh my goodness!", "topic": "Everyday Basics"},
    # --- Family ---
    {"swissGerman": "Ich bi müed", "german": "Ich bin müde", "english": "I'm tired", "topic": "Family"},
    {"swissGerman": "D'Chind sind id Schuel", "german": "Die Kinder sind in der Schule", "english": "The kids are at school", "topic": "Family"},
    {"swissGerman": "Mir ässe zäme z'Nacht", "german": "Wir essen zusammen zu Abend", "english": "We're having dinner together", "topic": "Family"},
    {"swissGerman": "De Bueb macht Ufgabe", "german": "Der Junge macht Hausaufgaben", "english": "The boy is doing homework", "topic": "Family"},
    {"swissGerman": "Ich hol d'Chind vo de Schuel ab", "german": "Ich hole die Kinder von der Schule ab", "english": "I'm picking the kids up from school", "topic": "Family"},
    {"swissGerman": "Mir gönd am Suntig go spaziere", "german": "Wir gehen am Sonntag spazieren", "english": "We're going for a walk on Sunday", "topic": "Family"},
    {"swissGerman": "S'Meitli schlaft scho", "german": "Das Mädchen schläft schon", "english": "The girl is already sleeping", "topic": "Family"},
    # --- Work ---
    {"swissGerman": "Guete Morge, zäme!", "german": "Guten Morgen, zusammen!", "english": "Good morning, everyone!", "topic": "Work"},
    {"swissGerman": "Ich bi im Büro", "german": "Ich bin im Büro", "english": "I'm at the office", "topic": "Work"},
    {"swissGerman": "Wänn isch d'Sitzig?", "german": "Wann ist das Meeting?", "english": "When is the meeting?", "topic": "Work"},
    {"swissGerman": "Ich schick der s'Mail", "german": "Ich schicke dir die E-Mail", "english": "I'll send you the email", "topic": "Work"},
    {"swissGerman": "Ich ha hüt frei", "german": "Ich habe heute frei", "english": "I have the day off today", "topic": "Work"},
    {"swissGerman": "Ich schaff vo dihei", "german": "Ich arbeite von zu Hause", "english": "I'm working from home", "topic": "Work"},
    {"swissGerman": "De Chef isch nöd da", "german": "Der Chef ist nicht da", "english": "The boss isn't here", "topic": "Work"},
    {"swissGerman": "Mir händ viel z'tue", "german": "Wir haben viel zu tun", "english": "We have a lot to do", "topic": "Work"},
    # --- Practical Swiss Life ---
    {"swissGerman": "Ich bruuch en Termin bim Dokter", "german": "Ich brauche einen Termin beim Arzt", "english": "I need a doctor's appointment", "topic": "Practical Swiss Life"},
    {"swissGerman": "Wo isch d'Apothek?", "german": "Wo ist die Apotheke?", "english": "Where is the pharmacy?", "topic": "Practical Swiss Life"},
    {"swissGerman": "Ich ha Chopfweh", "german": "Ich habe Kopfschmerzen", "english": "I have a headache", "topic": "Practical Swiss Life"},
    {"swissGerman": "Ich muess uf d'Gmeind", "german": "Ich muss zur Gemeinde", "english": "I need to go to the municipality office", "topic": "Practical Swiss Life"},
    {"swissGerman": "Chönd Sie mir hälfe?", "german": "Können Sie mir helfen?", "english": "Can you help me?", "topic": "Practical Swiss Life"},
    {"swissGerman": "Ich ha mi aagmeldet", "german": "Ich habe mich angemeldet", "english": "I've registered", "topic": "Practical Swiss Life"},
]