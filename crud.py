from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .models import User, Contact
from .schemas import UserCreate, ContactCreate
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db_session: Session, email: str):
    return db_session.query(User).filter(User.email == email).first()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db_session: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user

def get_user(db_session: Session, user_id: int):
    return db_session.query(User).filter(User.id == user_id).first()

def get_contact(db_session: Session, contact_id: int):
    return db_session.query(Contact).filter(Contact.id == contact_id).first()
def get_contacts(db_session: Session, user_id: int, search_query: str = None):
    query = db_session.query(Contact).filter(Contact.user_id == user_id)
    if search_query:
        query = query.filter(or_(
            Contact.first_name.ilike(f"%{search_query}%"),
            Contact.last_name.ilike(f"%{search_query}%"),
            Contact.email.ilike(f"%{search_query}%")
        ))
    return query.all()

def create_contact(db_session: Session, contact: ContactCreate):
    db_contact = Contact(**contact.dict())
    db_session.add(db_contact)
    db_session.commit()
    db_session.refresh(db_contact)
    return db_contact

def update_contact(db_session: Session, contact_id: int, contact: ContactCreate):
    db_contact = get_contact(db_session, contact_id)
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db_session.commit()
    db_session.refresh(db_contact)
    return db_contact

def delete_contact(db_session: Session, contact_id: int):
    db_contact = get_contact(db_session, contact_id)
    db_session.delete(db_contact)
    db_session.commit()
    return {"message": "Contact deleted successfully"}

def get_contacts_upcoming_birthdays(db_session: Session):
    today = datetime.today()
    end_date = today + timedelta(days=7)
    return db_session.query(Contact).filter(
        (Contact.birth_date >= today) & (Contact.birth_date <= end_date)
    ).all()