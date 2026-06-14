"""
Foydalanish: python -m scripts.seed
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime, timezone
from uuid import UUID, uuid4
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.tenant import TenantSettings, SubscriptionPlan, Language
from app.models.teacher import Teacher, TeacherStatus, SalaryType
from app.models.student import Student, StudentStatus
from app.models.group import Group, GroupStatus
from app.models.student_group import StudentGroup
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.attendance import AttendanceRecord
from app.models.homework import Homework, HomeworkType
from app.models.notification import Notification, NotificationType
from app.services.auth_service import hash_password

# ─── Fixed UUIDs (mockData.ts bilan mos) ─────────────────────────────────────
ADMIN_ID     = UUID("00000000-0000-0000-0000-000000000001")

TR1 = UUID("00000000-0000-0000-0001-000000000001")
TR2 = UUID("00000000-0000-0000-0001-000000000002")
TR3 = UUID("00000000-0000-0000-0001-000000000003")
TR4 = UUID("00000000-0000-0000-0001-000000000004")

G1 = UUID("00000000-0000-0000-0002-000000000001")
G2 = UUID("00000000-0000-0000-0002-000000000002")
G3 = UUID("00000000-0000-0000-0002-000000000003")
G4 = UUID("00000000-0000-0000-0002-000000000004")
G5 = UUID("00000000-0000-0000-0002-000000000005")
G6 = UUID("00000000-0000-0000-0002-000000000006")
G7 = UUID("00000000-0000-0000-0002-000000000007")

S_IDS = [UUID(f"00000000-0000-0000-0003-{str(i).zfill(12)}") for i in range(1, 28)]


async def seed():
    async with AsyncSessionLocal() as db:
        print("🌱 Seed boshlandi...")

        # ── Admin user ────────────────────────────────────────────────────────
        admin = User(
            id=ADMIN_ID,
            email="admin@educrm.uz",
            hashed_password=hash_password("Admin1234!"),
            full_name="Tizim Admini",
            role=UserRole.superadmin,
            is_active=True,
        )
        db.add(admin)

        # ── TenantSettings ────────────────────────────────────────────────────
        tenant = TenantSettings(
            id=uuid4(),
            name="Istiqbol IELTS Markazi",
            phone="+998 91 234 56 78",
            address="Toshkent sh., Chilonzor tumani, 7-mavze, 15-uy",
            currency="UZS",
            language=Language.uz,
            working_days=["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"],
            working_hours={"start": "08:00", "end": "21:00"},
            subscription_plan=SubscriptionPlan.pro,
            subscription_expiry=date(2026, 12, 31),
        )
        db.add(tenant)

        # ── O'qituvchilar ─────────────────────────────────────────────────────
        teachers = [
            Teacher(
                id=TR1, first_name="Jasur", last_name="Toshmatov",
                phone="+998 90 111 22 33", email="jasur@educrm.uz",
                subjects=["IELTS", "General English"],
                salary=3_500_000, salary_type=SalaryType.fixed,
                joined_date=date(2022, 3, 1), status=TeacherStatus.active,
                bio="IELTS 8.0 ball egasi, 5 yillik tajriba",
            ),
            Teacher(
                id=TR2, first_name="Malika", last_name="Yusupova",
                phone="+998 90 222 33 44", email="malika@educrm.uz",
                subjects=["Speaking", "Writing"],
                salary=30, salary_type=SalaryType.percent, salary_percent=30.0,
                joined_date=date(2021, 9, 1), status=TeacherStatus.active,
                bio="Cambridge sertifikatlangan o'qituvchi",
            ),
            Teacher(
                id=TR3, first_name="Bobur", last_name="Rahimov",
                phone="+998 90 333 44 55", email="bobur@educrm.uz",
                subjects=["Matematika", "Fizika"],
                salary=4_000_000, salary_type=SalaryType.fixed,
                joined_date=date(2023, 1, 15), status=TeacherStatus.active,
                bio="Oliy matematika fani bo'yicha magistr",
            ),
            Teacher(
                id=TR4, first_name="Nilufar", last_name="Karimova",
                phone="+998 90 444 55 66", email="nilufar@educrm.uz",
                subjects=["Rus tili"],
                salary=2_800_000, salary_type=SalaryType.fixed,
                joined_date=date(2022, 6, 1), status=TeacherStatus.active,
                bio="Filologiya fanlari nomzodi",
            ),
        ]
        db.add_all(teachers)

        # ── Guruhlar ──────────────────────────────────────────────────────────
        groups = [
            Group(
                id=G1, name="IELTS Intensive A", subject="IELTS",
                teacher_id=TR1,
                days=["Dushanba", "Chorshanba", "Juma"],
                start_time="09:00", end_time="11:00", room="201",
                max_students=12, monthly_fee=600_000,
                status=GroupStatus.active, start_date=date(2024, 1, 8),
                level="B2-C1",
            ),
            Group(
                id=G2, name="IELTS Intensive B", subject="IELTS",
                teacher_id=TR1,
                days=["Seshanba", "Payshanba", "Shanba"],
                start_time="14:00", end_time="16:00", room="202",
                max_students=10, monthly_fee=600_000,
                status=GroupStatus.active, start_date=date(2024, 2, 5),
                level="B1-B2",
            ),
            Group(
                id=G3, name="Speaking Club", subject="Speaking",
                teacher_id=TR2,
                days=["Dushanba", "Chorshanba"],
                start_time="17:00", end_time="18:30", room="105",
                max_students=8, monthly_fee=400_000,
                status=GroupStatus.active, start_date=date(2024, 1, 15),
                level="A2-B1",
            ),
            Group(
                id=G4, name="Matematika Olimpiada", subject="Matematika",
                teacher_id=TR3,
                days=["Seshanba", "Payshanba"],
                start_time="10:00", end_time="12:00", room="301",
                max_students=15, monthly_fee=500_000,
                status=GroupStatus.active, start_date=date(2024, 1, 20),
                level="9-11 sinf",
            ),
            Group(
                id=G5, name="Rus tili boshlang'ich", subject="Rus tili",
                teacher_id=TR4,
                days=["Dushanba", "Chorshanba", "Juma"],
                start_time="15:00", end_time="16:30", room="104",
                max_students=12, monthly_fee=350_000,
                status=GroupStatus.active, start_date=date(2024, 3, 4),
                level="A1-A2",
            ),
            Group(
                id=G6, name="IELTS Writing Masterclass", subject="Writing",
                teacher_id=TR2,
                days=["Shanba"],
                start_time="10:00", end_time="13:00", room="201",
                max_students=8, monthly_fee=450_000,
                status=GroupStatus.active, start_date=date(2024, 2, 17),
                level="B2-C1",
            ),
            Group(
                id=G7, name="General English Beginner", subject="General English",
                teacher_id=TR1,
                days=["Seshanba", "Payshanba"],
                start_time="18:00", end_time="19:30", room="103",
                max_students=15, monthly_fee=400_000,
                status=GroupStatus.active, start_date=date(2024, 3, 12),
                level="A1-A2",
            ),
        ]
        db.add_all(groups)

        # ── O'quvchilar ───────────────────────────────────────────────────────
        students_data = [
            # (id, first, last, phone, parent_phone, parent_name, birth_date, enrolled_date, status, balance)
            (S_IDS[0],  "Akbar",    "Mirzayev",    "+998911111111", "+998911111100", "Mirzayev A.",  date(2006,5,12),  date(2024,1,8),  "active",   0),
            (S_IDS[1],  "Zulfiya",  "Rahimova",    "+998912222222", "+998912222200", "Rahimov B.",   date(2005,8,23),  date(2024,1,8),  "active",   0),
            (S_IDS[2],  "Sherzod",  "Xolmatov",    "+998913333333", "+998913333300", "Xolmatov S.",  date(2007,3,7),   date(2024,1,10), "active",   -600000),
            (S_IDS[3],  "Dilnoza",  "Nazarova",    "+998914444444", "+998914444400", "Nazarov D.",   date(2006,11,19), date(2024,1,15), "active",   0),
            (S_IDS[4],  "Jasur",    "Tursunov",    "+998915555555", "+998915555500", "Tursunova M.", date(2005,2,28),  date(2024,1,20), "active",   0),
            (S_IDS[5],  "Malika",   "Xasanova",    "+998916666666", "+998916666600", "Xasanov T.",   date(2007,7,4),   date(2024,2,1),  "active",   -400000),
            (S_IDS[6],  "Bobur",    "Qodirov",     "+998917777777", "+998917777700", "Qodirov N.",   date(2006,9,15),  date(2024,2,5),  "active",   0),
            (S_IDS[7],  "Kamola",   "Ismoilova",   "+998918888888", "+998918888800", "Ismoilov K.",  date(2005,12,3),  date(2024,2,5),  "active",   0),
            (S_IDS[8],  "Ulugbek",  "Ergashev",    "+998919999999", "+998919999900", "Ergashev U.",  date(2007,4,22),  date(2024,2,10), "active",   -600000),
            (S_IDS[9],  "Sarvinoz", "Yusupova",    "+998901010101", "+998901010100", "Yusupov S.",   date(2006,6,30),  date(2024,2,12), "active",   0),
            (S_IDS[10], "Eldor",    "Karimov",     "+998901111111", "+998901111100", "Karimova E.",  date(2005,1,17),  date(2024,2,15), "active",   0),
            (S_IDS[11], "Nozima",   "Sobirov",     "+998902222222", "+998902222200", "Sobirov N.",   date(2007,10,8),  date(2024,2,20), "active",   -350000),
            (S_IDS[12], "Humoyun",  "Aliyev",      "+998903333333", "+998903333300", "Aliyev H.",    date(2006,3,25),  date(2024,3,1),  "active",   0),
            (S_IDS[13], "Gulnora",  "Toshpulatova","+998904444444", "+998904444400", "Toshpulatov G.",date(2005,7,14), date(2024,3,4),  "active",   0),
            (S_IDS[14], "Mirzo",    "Hamidov",     "+998905555555", "+998905555500", "Hamidova M.",  date(2007,1,9),   date(2024,3,4),  "active",   -500000),
            (S_IDS[15], "Feruza",   "Razzaqova",   "+998906666666", "+998906666600", "Razzaqov F.",  date(2006,8,18),  date(2024,3,10), "active",   0),
            (S_IDS[16], "Sanjar",   "Ibragimov",   "+998907777777", "+998907777700", "Ibragimov S.", date(2005,5,27),  date(2024,3,12), "active",   0),
            (S_IDS[17], "Oydin",    "Mahmudova",   "+998908888888", "+998908888800", "Mahmudov O.",  date(2007,2,14),  date(2024,3,12), "active",   -400000),
            (S_IDS[18], "Asilbek",  "Normatov",    "+998909999999", "+998909999900", "Normatov A.",  date(2006,11,1),  date(2024,3,15), "active",   0),
            (S_IDS[19], "Mohira",   "Salimova",    "+998901020304", "+998901020300", "Salimov M.",   date(2005,4,5),   date(2024,3,18), "active",   0),
            (S_IDS[20], "Ravshan",  "Umarov",      "+998902030405", "+998902030400", "Umarov R.",    date(2007,9,20),  date(2024,3,20), "active",   -600000),
            (S_IDS[21], "Dildora",  "Xurshidova",  "+998903040506", "+998903040500", "Xurshidov D.", date(2006,12,11), date(2024,4,1),  "active",   0),
            (S_IDS[22], "Firdavs",  "Sultonov",    "+998904050607", "+998904050600", "Sultonov F.",  date(2005,6,16),  date(2024,4,1),  "inactive", 0),
            (S_IDS[23], "Muazzam",  "Baxtiyorova", "+998905060708", "+998905060700", "Baxtiyorov M.",date(2007,3,29),  date(2024,4,5),  "active",   -450000),
            (S_IDS[24], "Lochinbek","Qosimov",     "+998906070809", "+998906070800", "Qosimov L.",   date(2006,7,7),   date(2024,4,8),  "active",   0),
            (S_IDS[25], "Nafisa",   "Abdullayeva", "+998907080910", "+998907080900", "Abdullayev N.",date(2005,10,23), date(2024,4,10), "active",   0),
            (S_IDS[26], "Ibrohim",  "Qurbonov",    "+998908091011", "+998908091000", "Qurbonov I.",  date(2007,8,13),  date(2024,4,15), "graduated",0),
        ]

        students = []
        for row in students_data:
            sid, fn, ln, ph, pph, pn, bd, ed, st, bal = row
            s = Student(
                id=sid, first_name=fn, last_name=ln,
                phone=ph, parent_phone=pph, parent_name=pn,
                birth_date=bd, enrolled_date=ed,
                status=StudentStatus(st), balance=bal, total_paid=0,
            )
            students.append(s)
        db.add_all(students)

        await db.flush()

        # ── StudentGroup aloqalari ────────────────────────────────────────────
        sg_data = [
            # G1: IELTS Intensive A — 8 ta o'quvchi
            (S_IDS[0], G1), (S_IDS[1], G1), (S_IDS[3], G1), (S_IDS[4], G1),
            (S_IDS[6], G1), (S_IDS[7], G1), (S_IDS[9], G1), (S_IDS[10], G1),
            # G2: IELTS Intensive B — 7 ta
            (S_IDS[2], G2), (S_IDS[5], G2), (S_IDS[8], G2), (S_IDS[11], G2),
            (S_IDS[12], G2), (S_IDS[15], G2), (S_IDS[16], G2),
            # G3: Speaking Club — 5 ta
            (S_IDS[1], G3), (S_IDS[3], G3), (S_IDS[9], G3), (S_IDS[19], G3), (S_IDS[21], G3),
            # G4: Matematika — 6 ta
            (S_IDS[13], G4), (S_IDS[14], G4), (S_IDS[17], G4),
            (S_IDS[18], G4), (S_IDS[20], G4), (S_IDS[22], G4),
            # G5: Rus tili — 5 ta
            (S_IDS[23], G5), (S_IDS[24], G5), (S_IDS[25], G5),
            (S_IDS[26], G5), (S_IDS[0], G5),
            # G6: Writing Masterclass — 4 ta
            (S_IDS[4], G6), (S_IDS[7], G6), (S_IDS[10], G6), (S_IDS[16], G6),
            # G7: General English — 6 ta
            (S_IDS[5], G7), (S_IDS[11], G7), (S_IDS[12], G7),
            (S_IDS[15], G7), (S_IDS[18], G7), (S_IDS[25], G7),
        ]
        for sid, gid in sg_data:
            db.add(StudentGroup(student_id=sid, group_id=gid))

        await db.flush()

        # ── To'lovlar ─────────────────────────────────────────────────────────
        months = [
            ("Yanvar", 2024, 1), ("Fevral", 2024, 2), ("Mart", 2024, 3),
            ("Aprel", 2024, 4), ("May", 2024, 5),
        ]
        pay_data = []
        for idx, (mon, yr, m) in enumerate(months):
            for i, (sid, gid) in enumerate(sg_data[:15]):
                grp_fee = next(g.monthly_fee for g in groups if g.id == gid)
                pay_data.append(Payment(
                    id=uuid4(),
                    student_id=sid, group_id=gid,
                    amount=grp_fee, discount=0,
                    date=date(yr, m, 5 + (i % 10)),
                    month=mon, year=yr,
                    method=PaymentMethod.cash if i % 3 != 0 else PaymentMethod.card,
                    status=PaymentStatus.paid,
                    received_by="Tizim Admini",
                ))
        db.add_all(pay_data)

        # ── Davomat yozuvlari ─────────────────────────────────────────────────
        attendance_dates = [
            date(2024, 5, 6), date(2024, 5, 8), date(2024, 5, 13),
            date(2024, 5, 15), date(2024, 5, 20),
        ]
        g1_student_ids = [s for s, g in sg_data if g == G1]
        for att_date in attendance_dates:
            records = []
            for j, sid in enumerate(g1_student_ids):
                status = "present" if j % 5 != 3 else "absent"
                records.append({"studentId": str(sid), "status": status})
            db.add(AttendanceRecord(
                id=uuid4(), group_id=G1, date=att_date,
                taken_by="Jasur Toshmatov", records=records,
            ))

        # ── Vazifalar ─────────────────────────────────────────────────────────
        homeworks = [
            Homework(
                id=uuid4(), group_id=G1, teacher_id=TR1,
                title="IELTS Reading Test 1",
                description="Cambridge 17 — Test 1 Reading bo'limini yechib keling",
                due_date=date(2024, 5, 15), assigned_date=date(2024, 5, 8),
                type=HomeworkType.homework, max_score=40,
                results=[
                    {"studentId": str(S_IDS[0]), "score": 35, "submitted": True, "submittedDate": "2024-05-14"},
                    {"studentId": str(S_IDS[1]), "score": 28, "submitted": True, "submittedDate": "2024-05-15"},
                    {"studentId": str(S_IDS[3]), "score": 38, "submitted": True, "submittedDate": "2024-05-13"},
                ],
            ),
            Homework(
                id=uuid4(), group_id=G1, teacher_id=TR1,
                title="Writing Task 2 — Environment",
                description="'Climate change' mavzusida 250+ so'zlik essay yozing",
                due_date=date(2024, 5, 22), assigned_date=date(2024, 5, 15),
                type=HomeworkType.homework, max_score=9,
                results=[],
            ),
            Homework(
                id=uuid4(), group_id=G4, teacher_id=TR3,
                title="Algebra imtihoni",
                description="Kvadrat tenglamalar va tengsizliklar",
                due_date=date(2024, 5, 18), assigned_date=date(2024, 5, 18),
                type=HomeworkType.exam, max_score=100,
                results=[
                    {"studentId": str(S_IDS[13]), "score": 87, "submitted": True},
                    {"studentId": str(S_IDS[14]), "score": 72, "submitted": True},
                    {"studentId": str(S_IDS[17]), "score": 91, "submitted": True},
                ],
            ),
        ]
        db.add_all(homeworks)

        # ── Bildirishnomalar ──────────────────────────────────────────────────
        notifications = [
            Notification(
                id=uuid4(),
                title="Yangi o'quvchi qo'shildi",
                message="Akbar Mirzayev IELTS Intensive A guruhiga qo'shildi",
                type=NotificationType.success, is_read=False,
                user_id=ADMIN_ID,
            ),
            Notification(
                id=uuid4(),
                title="To'lov muddati o'tdi",
                message="3 nafar o'quvchining may oyi to'lovi hali amalga oshirilmagan",
                type=NotificationType.warning, is_read=False,
                user_id=None,
            ),
            Notification(
                id=uuid4(),
                title="Davomat kiritildi",
                message="IELTS Intensive A guruhining 20-may davomati kiritildi",
                type=NotificationType.info, is_read=True,
                user_id=ADMIN_ID,
            ),
        ]
        db.add_all(notifications)

        await db.commit()
        print("✅ Seed muvaffaqiyatli! Kiritilgan ma'lumotlar:")
        print(f"   👤 1 ta admin foydalanuvchi  (admin@educrm.uz / Admin1234!)")
        print(f"   🏢 1 ta markaz sozlamalari")
        print(f"   👩‍🏫 4 ta o'qituvchi")
        print(f"   📚 7 ta guruh")
        print(f"   🎓 27 ta o'quvchi")
        print(f"   💰 {len(pay_data)} ta to'lov yozuvi")
        print(f"   📋 {len(attendance_dates)} ta davomat yozuvi")
        print(f"   📝 {len(homeworks)} ta vazifa")
        print(f"   🔔 {len(notifications)} ta bildirishnoma")


if __name__ == "__main__":
    asyncio.run(seed())
