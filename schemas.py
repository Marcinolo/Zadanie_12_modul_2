from pydantic import BaseModel

# Model do przesyłania danych kontaktu przy tworzeniu
class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: str
    extra_data: str = None

# Model do przesyłania danych kontaktu z ID
class ContactOut(ContactCreate):
    id: int

# Model tokena
class Token(BaseModel):
    access_token: str
    token_type: str