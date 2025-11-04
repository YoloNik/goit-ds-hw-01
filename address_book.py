from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError, KeyError) as e:
            return f"Error: {str(e)}"
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        s = str(value)
        if not s.isdigit() or len(s) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(s)

class Birthday(Field):
    def __init__(self, value: str):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self.value = value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_str):
        phone = Phone(phone_str)
        self.phones.append(phone)

    def remove_phone(self, phone_str):
        phone = self.find_phone(phone_str)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError(f"Phone number {phone_str} not found.")

    def edit_phone(self, old_phone_str, new_phone_str):
        phone = self.find_phone(old_phone_str)
        if not phone:
            raise ValueError(f"Phone number {old_phone_str} not found.")
        new_phone = Phone(new_phone_str)
        self.remove_phone(old_phone_str)
        self.phones.append(new_phone)

    def change_phone(self, old, new):
        for i, p in enumerate(self.phones):
            if p.value == old:
                self.phones[i] = Phone(new)
                return True
        return False

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_str):
        for phone in self.phones:
            if phone.value == phone_str:
                return phone
        return None

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        bday = self.birthday.value if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {bday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                # Convert string -> date
                bday_obj = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday_obj.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                delta = (bday_this_year - today).days
                if 0 <= delta <= 7:
                    # Move weekend birthdays to mon
                    if bday_this_year.weekday() == 5:
                        bday_this_year += timedelta(days=2)
                    elif bday_this_year.weekday() == 6:
                        bday_this_year += timedelta(days=1)
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": bday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming

    def __str__(self):
        if not self.data:
            return "AddressBook: <empty>"
        return "\n".join(str(record) for record in self.data.values())
    
    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)
    
    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            return AddressBook() 

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.change_phone(old_phone, new_phone):
        return "Phone number updated."
    return "Contact or phone not found."

@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join(p.value for p in record.phones) if record.phones else "No phones saved."
    return "Contact not found."

@input_error
def show_all(book):
    return str(book)

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if record:
        record.add_birthday(bday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value 
    return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join([f"{item['name']}: {item['birthday']}" for item in upcoming])

