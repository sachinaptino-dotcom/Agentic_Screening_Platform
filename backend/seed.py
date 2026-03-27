from database import SessionLocal
from auth import hash_password
from models import RecruiterAuth, RecruiterPerformance


def upsert_recruiter(db, email: str, password: str, name: str, department: str):
    auth = db.query(RecruiterAuth).filter(RecruiterAuth.email == email).first()
    if not auth:
        auth = RecruiterAuth(email=email, password_hash=hash_password(password), role="recruiter", is_active=True)
        db.add(auth)
        db.flush()
    perf = db.query(RecruiterPerformance).filter(RecruiterPerformance.auth_id == auth.id).first()
    if not perf:
        perf = RecruiterPerformance(auth_id=auth.id, user_name=name, department=department)
        db.add(perf)


def seed():
    db = SessionLocal()
    try:
        upsert_recruiter(db, "recruiter1@test.com", "Test@1234", "Recruiter One", "Engineering")
        upsert_recruiter(db, "recruiter2@test.com", "Test@1234", "Recruiter Two", "Product")
        db.commit()
        print("Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
