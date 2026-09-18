from database import SessionLocal
from auth import generate_invite_code, code_expiry

def create_admin_invite_code(db):
    from models import InviteCode
    admin_code = InviteCode(
        code=generate_invite_code(),
        role="admin",
        expires_at=code_expiry()
    )
    db.query(InviteCode).delete()
    db.add(admin_code)
    db.commit()
    db.refresh(admin_code)
    print(f"Admin invite code: {admin_code.code}")

if __name__ == "__main__":
    create_admin_invite_code(SessionLocal())