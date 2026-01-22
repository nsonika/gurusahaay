"""
Seed script to populate database with initial concepts and synonyms.

Run with: python -m scripts.seed_data
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models import Concept, ConceptSynonym, Teacher, UploadedContent
from app.services.auth import AuthService

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Sample concepts with multilingual synonyms
CONCEPTS = [
    {
        "concept_id": "SCI_BIO_PHOTOSYNTHESIS",
        "subject": "science",
        "description_en": "Process by which plants make food using sunlight",
        "description_hi": "पौधे सूर्य की रोशनी से भोजन कैसे बनाते हैं",
        "description_kn": "ಸಸ್ಯಗಳು ಸೂರ್ಯನ ಬೆಳಕಿನಿಂದ ಆಹಾರ ತಯಾರಿಸುವ ಪ್ರಕ್ರಿಯೆ",
        "grade": "7",
        "synonyms": [
            ("en", "photosynthesis"),
            ("en", "plant food making"),
            ("en", "how plants make food"),
            ("kn", "ದ್ಯುತಿಸಂಶ್ಲೇಷಣೆ"),
            ("kn", "ಸಸ್ಯಗಳ ಆಹಾರ ತಯಾರಿಕೆ"),
            ("hi", "प्रकाश संश्लेषण"),
            ("hi", "पौधों का भोजन बनाना"),
        ]
    },
    {
        "concept_id": "MATH_FRACTIONS",
        "subject": "math",
        "description_en": "Parts of a whole number",
        "description_hi": "पूर्ण संख्या के भाग",
        "description_kn": "ಪೂರ್ಣ ಸಂಖ್ಯೆಯ ಭಾಗಗಳು",
        "grade": "5",
        "synonyms": [
            ("en", "fractions"),
            ("en", "parts of whole"),
            ("kn", "ಭಿನ್ನರಾಶಿ"),
            ("kn", "ಭಾಗಗಳು"),
            ("hi", "भिन्न"),
            ("hi", "अंश"),
        ]
    },
    {
        "concept_id": "CLASSROOM_ATTENTION",
        "subject": "pedagogy",
        "description_en": "Getting and maintaining student attention",
        "description_hi": "छात्रों का ध्यान आकर्षित करना",
        "description_kn": "ವಿದ್ಯಾರ್ಥಿಗಳ ಗಮನ ಸೆಳೆಯುವುದು",
        "grade": "all",
        "synonyms": [
            ("en", "student attention"),
            ("en", "classroom attention"),
            ("en", "students not listening"),
            ("en", "distracted students"),
            ("kn", "ವಿದ್ಯಾರ್ಥಿಗಳ ಗಮನ"),
            ("kn", "ಮಕ್ಕಳು ಕೇಳುತ್ತಿಲ್ಲ"),
            ("hi", "छात्रों का ध्यान"),
            ("hi", "बच्चे नहीं सुन रहे"),
        ]
    },
    {
        "concept_id": "CLASSROOM_DISCIPLINE",
        "subject": "pedagogy",
        "description_en": "Managing classroom behavior",
        "description_hi": "कक्षा में अनुशासन बनाए रखना",
        "description_kn": "ತರಗತಿಯಲ್ಲಿ ಶಿಸ್ತು ನಿರ್ವಹಣೆ",
        "grade": "all",
        "synonyms": [
            ("en", "discipline"),
            ("en", "classroom management"),
            ("en", "student behavior"),
            ("en", "misbehaving students"),
            ("kn", "ಶಿಸ್ತು"),
            ("kn", "ತರಗತಿ ನಿರ್ವಹಣೆ"),
            ("hi", "अनुशासन"),
            ("hi", "कक्षा प्रबंधन"),
        ]
    },
    {
        "concept_id": "SCI_PHY_MOTION",
        "subject": "science",
        "description_en": "Movement of objects and forces",
        "description_hi": "वस्तुओं की गति और बल",
        "description_kn": "ವಸ್ತುಗಳ ಚಲನೆ ಮತ್ತು ಬಲ",
        "grade": "8",
        "synonyms": [
            ("en", "motion"),
            ("en", "movement"),
            ("en", "forces and motion"),
            ("kn", "ಚಲನೆ"),
            ("kn", "ಬಲ ಮತ್ತು ಚಲನೆ"),
            ("hi", "गति"),
            ("hi", "बल और गति"),
        ]
    },
    {
        "concept_id": "LANG_READING_COMPREHENSION",
        "subject": "language",
        "description_en": "Understanding written text",
        "description_hi": "लिखित पाठ को समझना",
        "description_kn": "ಬರಹವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು",
        "grade": "all",
        "synonyms": [
            ("en", "reading comprehension"),
            ("en", "understanding text"),
            ("en", "students cant read"),
            ("kn", "ಓದುವ ಗ್ರಹಿಕೆ"),
            ("kn", "ಮಕ್ಕಳು ಓದಲು ಸಾಧ್ಯವಿಲ್ಲ"),
            ("hi", "पढ़ने की समझ"),
            ("hi", "बच्चे पढ़ नहीं सकते"),
        ]
    },
    {
        "concept_id": "MATH_MULTIPLICATION",
        "subject": "math",
        "description_en": "Multiplying numbers",
        "description_hi": "संख्याओं का गुणा",
        "description_kn": "ಸಂಖ್ಯೆಗಳ ಗುಣಾಕಾರ",
        "grade": "4",
        "synonyms": [
            ("en", "multiplication"),
            ("en", "times tables"),
            ("en", "multiply"),
            ("kn", "ಗುಣಾಕಾರ"),
            ("kn", "ಮಗ್ಗಿ"),
            ("hi", "गुणा"),
            ("hi", "पहाड़े"),
        ]
    },
    {
        "concept_id": "CLASSROOM_SLOW_LEARNERS",
        "subject": "pedagogy",
        "description_en": "Supporting students who need extra help",
        "description_hi": "कमजोर छात्रों की मदद करना",
        "description_kn": "ಹೆಚ್ಚುವರಿ ಸಹಾಯ ಬೇಕಾದ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಬೆಂಬಲ",
        "grade": "all",
        "synonyms": [
            ("en", "slow learners"),
            ("en", "struggling students"),
            ("en", "students falling behind"),
            ("en", "student engagement low"),
            ("en", "low engagement"),
            ("kn", "ನಿಧಾನ ಕಲಿಕೆ"),
            ("kn", "ಹಿಂದುಳಿದ ವಿದ್ಯಾರ್ಥಿಗಳು"),
            ("hi", "धीमी गति से सीखने वाले"),
            ("hi", "पिछड़े छात्र"),
        ]
    },
    {
        "concept_id": "SCI_PHY_TEMPERATURE",
        "subject": "science",
        "description_en": "Teaching the abstract concept of temperature and heat measurement",
        "description_hi": "तापमान और गर्मी मापना",
        "description_kn": "ತಾಪಮಾನ ಮತ್ತು ಶಾಖ ಮಾಪನ",
        "grade": "6",
        "synonyms": [
            ("en", "temperature"),
            ("en", "heat"),
            ("en", "thermometer"),
            ("en", "hot and cold"),
            ("en", "measuring temperature"),
            ("kn", "ತಾಪಮಾನ"),
            ("kn", "ಉಷ್ಣತೆ"),
            ("hi", "तापमान"),
            ("hi", "गर्मी"),
        ]
    },
    {
        "concept_id": "SCI_BIO_HUMAN_BODY",
        "subject": "science",
        "description_en": "Human body parts and systems",
        "description_hi": "मानव शरीर के अंग और तंत्र",
        "description_kn": "ಮಾನವ ದೇಹದ ಭಾಗಗಳು ಮತ್ತು ವ್ಯವಸ್ಥೆಗಳು",
        "grade": "5",
        "synonyms": [
            ("en", "human body"),
            ("en", "body parts"),
            ("en", "organs"),
            ("en", "digestive system"),
            ("en", "respiratory system"),
            ("kn", "ಮಾನವ ದೇಹ"),
            ("kn", "ದೇಹದ ಭಾಗಗಳು"),
            ("hi", "मानव शरीर"),
            ("hi", "शरीर के अंग"),
        ]
    },
    {
        "concept_id": "MATH_DIVISION",
        "subject": "math",
        "description_en": "Dividing numbers",
        "grade": "4",
        "synonyms": [
            ("en", "division"),
            ("en", "divide"),
            ("en", "sharing equally"),
            ("kn", "ಭಾಗಾಕಾರ"),
            ("hi", "भाग"),
            ("hi", "विभाजन"),
        ]
    },
    {
        "concept_id": "CLASSROOM_NOISE",
        "subject": "pedagogy",
        "description_en": "Managing classroom noise levels",
        "grade": "all",
        "synonyms": [
            ("en", "classroom noise"),
            ("en", "noisy classroom"),
            ("en", "students talking"),
            ("en", "too much noise"),
            ("kn", "ತರಗತಿಯಲ್ಲಿ ಗದ್ದಲ"),
            ("hi", "कक्षा में शोर"),
        ]
    },
    {
        "concept_id": "SCI_ENV_WATER_CYCLE",
        "subject": "science",
        "description_en": "Water cycle and evaporation",
        "grade": "5",
        "synonyms": [
            ("en", "water cycle"),
            ("en", "evaporation"),
            ("en", "rain"),
            ("en", "condensation"),
            ("kn", "ನೀರಿನ ಚಕ್ರ"),
            ("kn", "ಆವಿಯಾಗುವಿಕೆ"),
            ("hi", "जल चक्र"),
            ("hi", "वाष्पीकरण"),
        ]
    },
    {
        "concept_id": "SCI_ENV_AIR_POLLUTION",
        "subject": "science",
        "description_en": "Air pollution and its effects",
        "grade": "6",
        "synonyms": [
            ("en", "air pollution"),
            ("en", "pollution"),
            ("en", "smog"),
            ("en", "clean air"),
            ("en", "air quality"),
            ("kn", "ವಾಯು ಮಾಲಿನ್ಯ"),
            ("kn", "ಗಾಳಿ ಮಾಲಿನ್ಯ"),
            ("hi", "वायु प्रदूषण"),
            ("hi", "हवा प्रदूषण"),
            ("hi", "प्रदूषण"),
        ]
    },
    {
        "concept_id": "SCI_ENV_PLANTS",
        "subject": "science",
        "description_en": "Plants, trees and their importance",
        "grade": "4",
        "synonyms": [
            ("en", "plants"),
            ("en", "trees"),
            ("en", "gardening"),
            ("en", "plant parts"),
            ("kn", "ಸಸ್ಯಗಳು"),
            ("kn", "ಮರಗಳು"),
            ("hi", "पौधे"),
            ("hi", "पेड़"),
            ("hi", "वृक्ष"),
        ]
    },
    {
        "concept_id": "SCI_ENV_ANIMALS",
        "subject": "science",
        "description_en": "Animals and their habitats",
        "grade": "4",
        "synonyms": [
            ("en", "animals"),
            ("en", "wildlife"),
            ("en", "animal habitats"),
            ("en", "zoo animals"),
            ("kn", "ಪ್ರಾಣಿಗಳು"),
            ("kn", "ವನ್ಯಜೀವಿ"),
            ("hi", "जानवर"),
            ("hi", "पशु"),
            ("hi", "वन्यजीव"),
        ]
    },
    {
        "concept_id": "MATH_ADDITION",
        "subject": "math",
        "description_en": "Adding numbers",
        "grade": "2",
        "synonyms": [
            ("en", "addition"),
            ("en", "adding"),
            ("en", "sum"),
            ("en", "plus"),
            ("kn", "ಸಂಕಲನ"),
            ("kn", "ಕೂಡಿಸು"),
            ("hi", "जोड़"),
            ("hi", "योग"),
        ]
    },
    {
        "concept_id": "MATH_SUBTRACTION",
        "subject": "math",
        "description_en": "Subtracting numbers",
        "grade": "2",
        "synonyms": [
            ("en", "subtraction"),
            ("en", "minus"),
            ("en", "take away"),
            ("kn", "ವ್ಯವಕಲನ"),
            ("kn", "ಕಳೆಯುವುದು"),
            ("hi", "घटाव"),
            ("hi", "घटाना"),
        ]
    },
    {
        "concept_id": "LANG_HINDI_ALPHABET",
        "subject": "language",
        "description_en": "Hindi alphabet and letters",
        "grade": "1",
        "synonyms": [
            ("en", "hindi alphabet"),
            ("en", "hindi letters"),
            ("en", "devanagari"),
            ("hi", "हिंदी वर्णमाला"),
            ("hi", "अक्षर"),
            ("hi", "क ख ग"),
        ]
    },
    {
        "concept_id": "LANG_KANNADA_ALPHABET",
        "subject": "language",
        "description_en": "Kannada alphabet and letters",
        "grade": "1",
        "synonyms": [
            ("en", "kannada alphabet"),
            ("en", "kannada letters"),
            ("kn", "ಕನ್ನಡ ವರ್ಣಮಾಲೆ"),
            ("kn", "ಅಕ್ಷರಗಳು"),
            ("kn", "ಅ ಆ ಇ"),
        ]
    },
]

def seed_concepts():
    """Add concepts and synonyms to database."""
    for concept_data in CONCEPTS:
        # Check if concept exists
        existing = db.query(Concept).filter(
            Concept.concept_id == concept_data["concept_id"]
        ).first()
        
        if existing:
            print(f"Concept {concept_data['concept_id']} already exists, skipping...")
            continue
        
        # Create concept
        concept = Concept(
            concept_id=concept_data["concept_id"],
            subject=concept_data["subject"],
            description_en=concept_data["description_en"],
            description_hi=concept_data.get("description_hi"),
            description_kn=concept_data.get("description_kn"),
            grade=concept_data["grade"]
        )
        db.add(concept)
        
        # Create synonyms
        for lang, term in concept_data["synonyms"]:
            synonym = ConceptSynonym(
                concept_id=concept_data["concept_id"],
                language=lang,
                term=term
            )
            db.add(synonym)
        
        print(f"Added concept: {concept_data['concept_id']}")
    
    db.commit()
    print("Concepts seeded successfully!")


def seed_demo_teacher():
    """Create a demo teacher account."""
    existing = db.query(Teacher).filter(Teacher.phone == "9999999999").first()
    if existing:
        print("Demo teacher already exists")
        return
    
    teacher = Teacher(
        name="Demo Teacher",
        phone="9999999999",
        password_hash=AuthService.hash_password("demo123"),
        role="teacher",
        language_preference="en",
        school_name="Demo School",
        district="Bangalore Urban",
        state="Karnataka"
    )
    db.add(teacher)
    db.commit()
    print("Demo teacher created: phone=9999999999, password=demo123")


def seed_sample_content():
    """Add sample content for demo."""
    teacher = db.query(Teacher).filter(Teacher.phone == "9999999999").first()
    if not teacher:
        print("Demo teacher not found, skipping content seeding")
        return
    
    sample_content = [
        {
            "concept_id": "CLASSROOM_ATTENTION",
            "title": "5 Quick Attention Grabbers",
            "description": "Simple techniques to get students focused in 30 seconds. Clap patterns, countdown, silent signals.",
            "content_type": "tip",
            "language": "en",
            "is_verified": True,
            "content_url": "https://youtube.com/example1",
        },
        {
            "concept_id": "CLASSROOM_ATTENTION",
            "title": "ಮಕ್ಕಳ ಗಮನ ಸೆಳೆಯುವ ವಿಧಾನಗಳು",
            "description": "ತರಗತಿಯಲ್ಲಿ ಮಕ್ಕಳ ಗಮನ ಸೆಳೆಯಲು ಸರಳ ತಂತ್ರಗಳು",
            "content_type": "tip",
            "language": "kn",
            "is_verified": True,
        },
        {
            "concept_id": "SCI_BIO_PHOTOSYNTHESIS",
            "title": "Role-Play 'The Leaf Factory'",
            "description": "Assign students roles like 'Sun', 'Water', and 'CO2' to enter a circle (the leaf). Have them trade 'energy tokens' to create a 'Glucose' student, making the chemical reaction visible and fun.",
            "content_type": "activity",
            "language": "en",
            "is_verified": True,
            "content_url": "https://youtube.com/photosynthesis-roleplay",
        },
        {
            "concept_id": "SCI_BIO_PHOTOSYNTHESIS",
            "title": "Simple Leaf Breath Experiment",
            "description": "Place a leaf in water under sunlight and observe oxygen bubbles forming. Great visual demonstration of photosynthesis.",
            "content_type": "activity",
            "language": "en",
            "is_verified": True,
        },
        {
            "concept_id": "MATH_FRACTIONS",
            "title": "Teaching Fractions with Pizza",
            "description": "Use pizza slices to explain fractions visually. Cut paper pizzas into halves, quarters, eighths.",
            "content_type": "activity",
            "language": "en",
            "is_verified": True,
        },
        {
            "concept_id": "SCI_PHY_TEMPERATURE",
            "title": "Three-Bowl Water Experiment",
            "description": "Place three bowls: one with cold water, one with lukewarm, and one with warm. Have a student dip hands in cold and warm first, then both in lukewarm to show how 'feeling' temperature is relative while a thermometer gives an exact measure.",
            "content_type": "activity",
            "language": "en",
            "is_verified": True,
            "content_url": "https://youtube.com/temperature-experiment",
        },
        {
            "concept_id": "SCI_PHY_TEMPERATURE",
            "title": "DIY Thermometer Activity",
            "description": "Build a simple thermometer using a bottle, straw, and colored water. Students observe liquid rising as temperature increases.",
            "content_type": "activity",
            "language": "en",
            "is_verified": True,
        },
        {
            "concept_id": "SCI_ENV_WATER_CYCLE",
            "title": "Water Cycle Song and Actions",
            "description": "Use a catchy song with hand gestures to explain Evaporation (hands up), Condensation (hands together), and Precipitation (fingers like rain). This helps students memorize the sequence through movement and rhythm.",
            "content_type": "video",
            "language": "en",
            "is_verified": False,
            "source_type": "external",
            "content_url": "https://youtube.com/water-cycle-song",
        },
        {
            "concept_id": "SCI_ENV_WATER_CYCLE",
            "title": "Water Cycle in a Bag",
            "description": "Create a mini water cycle using a ziplock bag, water, and blue food coloring. Tape to a sunny window and watch evaporation and condensation happen!",
            "content_type": "activity",
            "language": "en",
            "is_verified": False,
            "source_type": "external",
            "content_url": "https://example.com/water-cycle-bag",
        },
        {
            "concept_id": "CLASSROOM_DISCIPLINE",
            "title": "The Quiet Signal Technique",
            "description": "Establish a silent hand signal that means 'stop and listen'. Practice it daily until it becomes automatic for students.",
            "content_type": "tip",
            "language": "en",
            "is_verified": True,
        },
        {
            "concept_id": "CLASSROOM_SLOW_LEARNERS",
            "title": "Peer Buddy System",
            "description": "Pair struggling students with helpful classmates. The buddy explains concepts in kid-friendly language and both benefit from the interaction.",
            "content_type": "tip",
            "language": "en",
            "is_verified": True,
        },
        {
            "concept_id": "SCI_PHY_MOTION",
            "title": "Toy Car Ramp Experiment",
            "description": "Use toy cars and ramps of different heights to demonstrate how gravity affects speed. Students predict and measure distances.",
            "content_type": "activity",
            "language": "en",
            "is_verified": True,
        },
    ]
    
    for content_data in sample_content:
        existing = db.query(UploadedContent).filter(
            UploadedContent.title == content_data["title"]
        ).first()
        if existing:
            continue
        
        content = UploadedContent(
            uploaded_by=teacher.id,
            concept_id=content_data["concept_id"],
            title=content_data["title"],
            description=content_data["description"],
            content_type=content_data["content_type"],
            content_url=content_data.get("content_url"),
            language=content_data["language"],
            source_type=content_data.get("source_type", "external"),
            is_verified=content_data["is_verified"],
            subject="pedagogy" if "CLASSROOM" in content_data["concept_id"] else "science",
        )
        db.add(content)
        print(f"Added content: {content_data['title']}")
    
    db.commit()
    print("Sample content seeded!")


if __name__ == "__main__":
    print("Seeding database...")
    seed_concepts()
    seed_demo_teacher()
    seed_sample_content()
    print("Done!")
    db.close()
