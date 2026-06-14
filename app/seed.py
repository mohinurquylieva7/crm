"""
Loyiha birinchi marta run bo'lganda demo ma'lumotlar bilan to'ldiradi.
Agar bazada allaqachon User mavjud bo'lsa, qayta seed qilmaydi.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Customer, Deal, Task, Activity
from app.auth import get_password_hash


def seed_database(db: Session):
    """Bazaga demo ma'lumotlar qo'shadi (faqat baza bo'sh bo'lsa)"""

    # Agar user bor bo'lsa, seed qilingan
    if db.query(User).first():
        return

    # ═══ DEMO USER ═══
    demo_user = User(
        full_name="Admin Adminov",
        email="admin@nexuscrm.uz",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(demo_user)
    db.flush()

    # ═══ CUSTOMERS ═══
    customers_data = [
        {"name": "Alisher Karimov", "email": "alisher@techuz.com", "phone": "+998901234567", "company": "TechUZ Solutions", "status": "customer", "source": "Website"},
        {"name": "Nilufar Rahimova", "email": "nilufar@datalab.uz", "phone": "+998935551122", "company": "DataLab Analytics", "status": "customer", "source": "Referral"},
        {"name": "Bobur Toshmatov", "email": "bobur@greenlogistics.uz", "phone": "+998977778899", "company": "Green Logistics", "status": "prospect", "source": "LinkedIn"},
        {"name": "Madina Usmanova", "email": "madina@smartedu.uz", "phone": "+998911112233", "company": "SmartEdu Platform", "status": "lead", "source": "Cold Call"},
        {"name": "Sardor Nazarov", "email": "sardor@buildpro.uz", "phone": "+998944445566", "company": "BuildPro Construction", "status": "customer", "source": "Exhibition"},
        {"name": "Zulfiya Abdullayeva", "email": "zulfiya@medicore.uz", "phone": "+998903334455", "company": "MediCore Health", "status": "prospect", "source": "Website"},
        {"name": "Jamshid Olimov", "email": "jamshid@fintech.uz", "phone": "+998916667788", "company": "FinTech Solutions", "status": "lead", "source": "Partner"},
        {"name": "Dilorom Kamalova", "email": "dilorom@agritech.uz", "phone": "+998928889900", "company": "AgriTech Innovations", "status": "customer", "source": "Referral"},
        {"name": "Otabek Mirzayev", "email": "otabek@clouduz.com", "phone": "+998950001122", "company": "CloudUZ Hosting", "status": "prospect", "source": "Google Ads"},
        {"name": "Shahlo Tursunova", "email": "shahlo@designlab.uz", "phone": "+998992223344", "company": "DesignLab Studio", "status": "lead", "source": "Instagram"},
        {"name": "Rustam Qodirov", "email": "rustam@autoparts.uz", "phone": "+998933445566", "company": "AutoParts Plus", "status": "customer", "source": "Exhibition"},
        {"name": "Gulnora Azimova", "email": "gulnora@foodtech.uz", "phone": "+998945567788", "company": "FoodTech Delivery", "status": "churned", "source": "Website"},
        {"name": "Farhod Ismoilov", "email": "farhod@securenet.uz", "phone": "+998917788990", "company": "SecureNet Cyber", "status": "customer", "source": "Referral"},
        {"name": "Kamola Yusupova", "email": "kamola@beautyplus.uz", "phone": "+998909900112", "company": "BeautyPlus Cosmetics", "status": "prospect", "source": "Facebook"},
        {"name": "Ulugbek Normatov", "email": "ulugbek@solaruz.com", "phone": "+998921122334", "company": "SolarUZ Energy", "status": "lead", "source": "Cold Call"},
    ]

    customers = []
    for i, c_data in enumerate(customers_data):
        customer = Customer(
            **c_data,
            created_at=datetime.utcnow() - timedelta(days=90 - i * 5),
            updated_at=datetime.utcnow() - timedelta(days=30 - i * 2),
        )
        db.add(customer)
        customers.append(customer)

    db.flush()

    # ═══ DEALS ═══
    deals_data = [
        {"title": "TechUZ ERP tizimi", "value": 25000, "stage": "won", "probability": 100, "customer_idx": 0, "days_ago": 5},
        {"title": "DataLab ML Platform", "value": 18500, "stage": "won", "probability": 100, "customer_idx": 1, "days_ago": 12},
        {"title": "Green Logistics CRM", "value": 12000, "stage": "negotiation", "probability": 75, "customer_idx": 2, "days_ago": 8},
        {"title": "SmartEdu LMS integratsiya", "value": 8500, "stage": "proposal", "probability": 50, "customer_idx": 3, "days_ago": 3},
        {"title": "BuildPro boshqaruv tizimi", "value": 35000, "stage": "won", "probability": 100, "customer_idx": 4, "days_ago": 20},
        {"title": "MediCore HIS tizimi", "value": 42000, "stage": "negotiation", "probability": 70, "customer_idx": 5, "days_ago": 6},
        {"title": "FinTech mobile app", "value": 15000, "stage": "contacted", "probability": 30, "customer_idx": 6, "days_ago": 2},
        {"title": "AgriTech IoT monitoring", "value": 22000, "stage": "won", "probability": 100, "customer_idx": 7, "days_ago": 30},
        {"title": "CloudUZ migration", "value": 9800, "stage": "proposal", "probability": 60, "customer_idx": 8, "days_ago": 4},
        {"title": "DesignLab branding", "value": 5500, "stage": "new", "probability": 20, "customer_idx": 9, "days_ago": 1},
        {"title": "AutoParts e-commerce", "value": 28000, "stage": "won", "probability": 100, "customer_idx": 10, "days_ago": 45},
        {"title": "FoodTech delivery app", "value": 16000, "stage": "lost", "probability": 0, "customer_idx": 11, "days_ago": 25},
        {"title": "SecureNet audit tizimi", "value": 19500, "stage": "negotiation", "probability": 80, "customer_idx": 12, "days_ago": 7},
        {"title": "BeautyPlus CRM", "value": 7200, "stage": "contacted", "probability": 35, "customer_idx": 13, "days_ago": 3},
        {"title": "SolarUZ monitoring", "value": 11000, "stage": "new", "probability": 15, "customer_idx": 14, "days_ago": 1},
        {"title": "TechUZ mobile app", "value": 14000, "stage": "proposal", "probability": 55, "customer_idx": 0, "days_ago": 4},
        {"title": "DataLab Dashboard", "value": 9000, "stage": "won", "probability": 100, "customer_idx": 1, "days_ago": 60},
        {"title": "BuildPro HR tizimi", "value": 20000, "stage": "contacted", "probability": 40, "customer_idx": 4, "days_ago": 2},
    ]

    for d_data in deals_data:
        deal = Deal(
            title=d_data["title"],
            value=d_data["value"],
            stage=d_data["stage"],
            probability=d_data["probability"],
            customer_id=customers[d_data["customer_idx"]].id,
            close_date=datetime.utcnow() + timedelta(days=30 - d_data["days_ago"]),
            created_at=datetime.utcnow() - timedelta(days=d_data["days_ago"] + 10),
            updated_at=datetime.utcnow() - timedelta(days=d_data["days_ago"]),
        )
        db.add(deal)

    # ═══ TASKS ═══
    tasks_data = [
        {"title": "TechUZ bilan shartnoma imzolash", "description": "ERP tizimi uchun yakuniy shartnomani tayyorlash", "status": "done", "priority": "high", "customer_idx": 0, "days_due": -2},
        {"title": "DataLab demo o'tkazish", "description": "ML Platform demo prezentatsiya", "status": "done", "priority": "high", "customer_idx": 1, "days_due": -5},
        {"title": "Green Logistics taklif yuborish", "description": "CRM tizimi uchun narx taklifini tayyorlash", "status": "in_progress", "priority": "high", "customer_idx": 2, "days_due": 2},
        {"title": "SmartEdu bilan uchrashuv", "description": "LMS integratsiya talablarini muhokama qilish", "status": "todo", "priority": "medium", "customer_idx": 3, "days_due": 3},
        {"title": "MediCore texnik hujjat", "description": "HIS tizimi texnik spetsifikatsiyasini yozish", "status": "in_progress", "priority": "high", "customer_idx": 5, "days_due": 5},
        {"title": "FinTech qo'ng'iroq qilish", "description": "Mobile app talablarini aniqlash uchun qo'ng'iroq", "status": "todo", "priority": "medium", "customer_idx": 6, "days_due": 1},
        {"title": "CloudUZ taklif yangilash", "description": "Migration narxini qayta ko'rib chiqish", "status": "todo", "priority": "low", "customer_idx": 8, "days_due": 4},
        {"title": "SecureNet shartnoma", "description": "Audit tizimi shartnoma shartlarini kelishish", "status": "in_progress", "priority": "high", "customer_idx": 12, "days_due": 3},
        {"title": "Haftalik hisobot tayyorlash", "description": "Sales jamoasi uchun haftalik natijalar hisoboti", "status": "todo", "priority": "medium", "customer_idx": None, "days_due": 1},
        {"title": "BeautyPlus follow-up", "description": "CRM demo natijalarini so'rash", "status": "todo", "priority": "low", "customer_idx": 13, "days_due": 2},
        {"title": "SolarUZ prezentatsiya", "description": "Monitoring tizimi prezentatsiya slaydlarini tayyorlash", "status": "todo", "priority": "medium", "customer_idx": 14, "days_due": 5},
        {"title": "BuildPro HR meeting", "description": "HR tizimi modullari bo'yicha uchrashuv", "status": "todo", "priority": "high", "customer_idx": 4, "days_due": 2},
    ]

    for t_data in tasks_data:
        task = Task(
            title=t_data["title"],
            description=t_data["description"],
            status=t_data["status"],
            priority=t_data["priority"],
            customer_id=customers[t_data["customer_idx"]].id if t_data["customer_idx"] is not None else None,
            due_date=datetime.utcnow() + timedelta(days=t_data["days_due"]),
            created_at=datetime.utcnow() - timedelta(days=abs(t_data["days_due"]) + 5),
            updated_at=datetime.utcnow() - timedelta(days=1),
        )
        db.add(task)

    # ═══ ACTIVITIES ═══
    activities_data = [
        {"type": "call", "description": "TechUZ bilan shartnoma shartlari muhokama qilindi", "customer_idx": 0, "hours_ago": 2},
        {"type": "email", "description": "DataLab ga yangi ML model haqida taklif yuborildi", "customer_idx": 1, "hours_ago": 5},
        {"type": "meeting", "description": "Green Logistics jamoasi bilan CRM demo o'tkazildi", "customer_idx": 2, "hours_ago": 8},
        {"type": "call", "description": "SmartEdu texnik talablar bo'yicha qo'ng'iroq", "customer_idx": 3, "hours_ago": 12},
        {"type": "note", "description": "MediCore HIS tizimi uchun texnik hujjat boshlandi", "customer_idx": 5, "hours_ago": 18},
        {"type": "email", "description": "FinTech ga mobile app portfelini yuborildi", "customer_idx": 6, "hours_ago": 24},
        {"type": "meeting", "description": "SecureNet bilan xavfsizlik audit rejasi kelishildi", "customer_idx": 12, "hours_ago": 30},
        {"type": "call", "description": "CloudUZ migration vaqt jadvali muhokama qilindi", "customer_idx": 8, "hours_ago": 36},
        {"type": "email", "description": "BeautyPlus ga CRM demo havolasi yuborildi", "customer_idx": 13, "hours_ago": 48},
        {"type": "meeting", "description": "BuildPro bilan HR tizimi uchun kickoff uchrashuv", "customer_idx": 4, "hours_ago": 52},
        {"type": "note", "description": "SolarUZ loyihasi uchun monitoring talablari yozildi", "customer_idx": 14, "hours_ago": 60},
        {"type": "call", "description": "Dilorom bilan AgriTech IoT natijalarini muhokama qildik", "customer_idx": 7, "hours_ago": 72},
        {"type": "email", "description": "AutoParts ga e-commerce loyiha hisoboti yuborildi", "customer_idx": 10, "hours_ago": 80},
        {"type": "meeting", "description": "TechUZ bilan yangi mobile app loyihasi muhokama qilindi", "customer_idx": 0, "hours_ago": 96},
        {"type": "note", "description": "FoodTech bilan hamkorlik tugatildi — sabab: byudjet muammosi", "customer_idx": 11, "hours_ago": 120},
    ]

    for a_data in activities_data:
        activity = Activity(
            type=a_data["type"],
            description=a_data["description"],
            customer_id=customers[a_data["customer_idx"]].id,
            created_at=datetime.utcnow() - timedelta(hours=a_data["hours_ago"]),
        )
        db.add(activity)

    db.commit()
    print("✅ Demo ma'lumotlar muvaffaqiyatli qo'shildi!")
    print("📧 Login: admin@nexuscrm.uz")
    print("🔑 Parol: admin123")
