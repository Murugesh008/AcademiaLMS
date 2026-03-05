"""
Seed script: creates departments, courses, and users.
Must be run from the project root:  python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
import app.models  # noqa — registers all models

from app.models.department import Department
from app.models.course import Course
from app.models.user import User
from app.auth import hash_password

# Ensure tables exist (safe even if already created by Alembic)
Base.metadata.create_all(bind=engine)

DEPARTMENTS = [
    {"name": "Computer Science",      "code": "CS",   "description": "Computing, algorithms and software systems."},
    {"name": "Mathematics",            "code": "MATH", "description": "Pure and applied mathematics."},
    {"name": "Physics",                "code": "PHY",  "description": "Classical and modern physics."},
    {"name": "Business Administration","code": "BUS",  "description": "Management, finance and entrepreneurship."},
]

COURSES = [
    # CS
    {"name": "Intro to Computer Science",   "code": "CS101",   "dept": "CS",   "description": "Foundations of computation and programming."},
    {"name": "Data Structures & Algorithms","code": "CS201",   "dept": "CS",   "description": "Arrays, trees, graphs and algorithm design."},
    {"name": "Database Systems",            "code": "CS301",   "dept": "CS",   "description": "Relational databases, SQL and NoSQL."},
    {"name": "Operating Systems",           "code": "CS401",   "dept": "CS",   "description": "Processes, memory and file systems."},
    # MATH
    {"name": "Calculus I",                  "code": "MATH101", "dept": "MATH", "description": "Limits, derivatives and integrals."},
    {"name": "Linear Algebra",              "code": "MATH201", "dept": "MATH", "description": "Vectors, matrices and linear transformations."},
    {"name": "Discrete Mathematics",        "code": "MATH301", "dept": "MATH", "description": "Logic, sets, combinatorics and graph theory."},
    # PHY
    {"name": "Classical Mechanics",         "code": "PHY101",  "dept": "PHY",  "description": "Newton's laws, energy and momentum."},
    {"name": "Electromagnetism",            "code": "PHY201",  "dept": "PHY",  "description": "Electric and magnetic fields, Maxwell's equations."},
    # BUS
    {"name": "Principles of Management",    "code": "BUS101",  "dept": "BUS",  "description": "Planning, organising, leading and controlling."},
    {"name": "Financial Accounting",        "code": "BUS201",  "dept": "BUS",  "description": "Balance sheets, income statements and cash flows."},
]

USERS = [
    # Professors
    {"email": "prof.smith@uni.edu",    "password": "Professor123!", "full_name": "Dr. Alice Smith",   "role": "professor", "dept": "CS"},
    {"email": "prof.johnson@uni.edu",  "password": "Professor123!", "full_name": "Dr. Bob Johnson",   "role": "professor", "dept": "CS"},
    {"email": "prof.williams@uni.edu", "password": "Professor123!", "full_name": "Dr. Carol Williams","role": "professor", "dept": "MATH"},
    {"email": "prof.brown@uni.edu",    "password": "Professor123!", "full_name": "Dr. David Brown",   "role": "professor", "dept": "PHY"},
    {"email": "prof.jones@uni.edu",    "password": "Professor123!", "full_name": "Dr. Emma Jones",    "role": "professor", "dept": "BUS"},
    # Students
    {"email": "student.alice@uni.edu", "password": "Student123!",   "full_name": "Alice Chen",        "role": "student",   "dept": "CS"},
    {"email": "student.bob@uni.edu",   "password": "Student123!",   "full_name": "Bob Patel",         "role": "student",   "dept": "CS"},
    {"email": "student.carol@uni.edu", "password": "Student123!",   "full_name": "Carol Lee",         "role": "student",   "dept": "MATH"},
    {"email": "student.dave@uni.edu",  "password": "Student123!",   "full_name": "Dave Nguyen",       "role": "student",   "dept": "PHY"},
    {"email": "student.emma@uni.edu",  "password": "Student123!",   "full_name": "Emma Garcia",       "role": "student",   "dept": "BUS"},
]


def seed():
    db = SessionLocal()
    try:
        print("── Seeding departments ──────────────────────")
        dept_map: dict[str, Department] = {}
        for d in DEPARTMENTS:
            obj = db.execute(
                __import__("sqlalchemy").select(Department).where(Department.code == d["code"])
            ).scalar_one_or_none()
            if not obj:
                obj = Department(**d)
                db.add(obj)
                db.flush()
                print(f"  + {d['name']}")
            else:
                print(f"  ~ {d['name']} (already exists)")
            dept_map[d["code"]] = obj
        db.commit()

        print("── Seeding courses ──────────────────────────")
        for c in COURSES:
            dept = dept_map[c["dept"]]
            obj = db.execute(
                __import__("sqlalchemy").select(Course).where(
                    Course.code == c["code"], Course.department_id == dept.id
                )
            ).scalar_one_or_none()
            if not obj:
                db.add(Course(name=c["name"], code=c["code"],
                              description=c.get("description"), department_id=dept.id))
                print(f"  + {c['code']} — {c['name']}")
            else:
                print(f"  ~ {c['code']} (already exists)")
        db.commit()

        print("── Seeding users ────────────────────────────")
        for u in USERS:
            obj = db.execute(
                __import__("sqlalchemy").select(User).where(User.email == u["email"])
            ).scalar_one_or_none()
            if not obj:
                db.add(User(
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"],
                    department_id=dept_map[u["dept"]].id,
                ))
                print(f"  + {u['email']} ({u['role']} / {u['dept']})")
            else:
                print(f"  ~ {u['email']} (already exists)")
        db.commit()

        print("\n✅  Done!\n")
        print("  PROFESSOR logins  (password: Professor123!)")
        for u in USERS:
            if u["role"] == "professor":
                print(f"    {u['email']}")
        print("\n  STUDENT logins  (password: Student123!)")
        for u in USERS:
            if u["role"] == "student":
                print(f"    {u['email']}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
