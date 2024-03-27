from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User
from .crud import (
    get_contact,
    get_contacts,
    create_contact,
    update_contact,
    delete_contact,
    get_contacts_upcoming_birthdays,
    authenticate_user,
    create_access_token,
)
from .schemas import ContactCreate, ContactOut, Token

# Tworzenie instancji aplikacji FastAPI
app = FastAPI()

# Tworzenie bazy danych SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tworzenie tabel w bazie danych
Base.metadata.create_all(bind=engine)

# Dependency to get the current user based on the provided token
def get_current_user(token: str = Depends(create_access_token)):
    user = authenticate_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Routes
@app.post("/contacts/", response_model=ContactOut)
def create_new_contact(contact: ContactCreate, db_session=SessionLocal(), current_user: User = Depends(get_current_user)):
    return create_contact(db_session, contact)

@app.get("/contacts/", response_model=list[ContactOut])
def read_all_contacts(search_query: str = None, db_session=SessionLocal(), current_user: User = Depends(get_current_user)):
    return get_contacts(db_session, search_query)

@app.get("/contacts/{contact_id}", response_model=ContactOut)
def read_contact(contact_id: int, db_session=SessionLocal(), current_user: User = Depends(get_current_user)):
    return get_contact(db_session, contact_id)

@app.put("/contacts/{contact_id}", response_model=ContactOut)
def update_existing_contact(contact_id: int, contact: ContactCreate, db_session=SessionLocal(), current_user: User = Depends(get_current_user)):
    return update_contact(db_session, contact_id, contact)

@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_contact(contact_id: int, db_session=SessionLocal(), current_user: User = Depends(get_current_user)):
    return delete_contact(db_session, contact_id)

@app.get("/contacts/upcoming_birthdays", response_model=list[ContactOut])
def get_upcoming_birthdays(db_session=SessionLocal(), current_user: User = Depends(get_current_user)):
    return get_contacts_upcoming_birthdays(db_session)

@app.post("/login", response_model=Token)
def login_for_access_token(email: str, password: str, db_session=SessionLocal()):
    user = authenticate_user(email, password, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}