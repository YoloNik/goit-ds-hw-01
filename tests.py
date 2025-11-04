#used AI for generate tests
import unittest
from datetime import datetime, timedelta

from address_book import (
    AddressBook, Record, Phone, Birthday,
    add_contact, change_contact, show_phones, show_all,
    add_birthday, show_birthday, birthdays
)

class AddressBookTests(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    # --- 1. add_contact ---
    def test_add_contact_new(self):
        msg = add_contact(["Alice", "0123456789"], self.book)
        self.assertEqual(msg, "Contact added.")
        rec = self.book.find("Alice")
        self.assertIsNotNone(rec)
        self.assertEqual([p.value for p in rec.phones], ["0123456789"])

    def test_add_contact_existing_additional_phone(self):
        add_contact(["Bob", "0123456789"], self.book)
        msg = add_contact(["Bob", "1234567890"], self.book)
        self.assertEqual(msg, "Contact updated.")
        phones = [p.value for p in self.book.find("Bob").phones]
        self.assertCountEqual(phones, ["0123456789", "1234567890"])

    def test_add_contact_invalid_phone(self):
        msg = add_contact(["Eve", "12345"], self.book)
        self.assertTrue(msg.startswith("Error:"))
        self.assertIn("Phone number must contain exactly 10 digits", msg)

	# --- 2. change_contact ---
    def test_change_contact_success(self):
        add_contact(["Carl", "1111111111"], self.book)
        msg = change_contact(["Carl", "1111111111", "2222222222"], self.book)
        self.assertEqual(msg, "Phone number updated.")
        rec = self.book.find("Carl")
        self.assertEqual([p.value for p in rec.phones], ["2222222222"])

    def test_change_contact_not_found(self):
        msg = change_contact(["Nope", "1111111111", "2222222222"], self.book)
        self.assertEqual(msg, "Contact or phone not found.")

    def test_change_contact_invalid_new_phone(self):
        add_contact(["Don", "3333333333"], self.book)
        msg = change_contact(["Don", "3333333333", "abc"], self.book)
        self.assertTrue(msg.startswith("Error:"))
        self.assertIn("Phone number must contain exactly 10 digits", msg)

    # --- 3. show_phones ---
    def test_show_phones_success(self):
        add_contact(["Didi", "3333333333"], self.book)
        result = show_phones(["Didi"], self.book)
        self.assertEqual(result, "3333333333")

    def test_show_phones_contact_not_found(self):
        result = show_phones(["Unknown"], self.book)
        self.assertEqual(result, "Contact not found.")

    def test_show_phones_missing_arg_indexerror(self):
        result = show_phones([], self.book)
        self.assertTrue(result.startswith("Error:"))

    # --- 4. show_all / __str__ ---
    def test_show_all_empty(self):
        output = show_all(self.book)
        self.assertIn("<empty>", output)

    def test_show_all_with_contact_and_birthday_format(self):
        add_contact(["Eva", "4444444444"], self.book)
        out = show_all(self.book)
        self.assertIn("Contact name: Eva", out)
        self.assertIn("phones: 4444444444", out)
        self.assertIn("birthday: N/A", out)

    # --- 5. add_birthday / show_birthday / walidacje ---
    def test_add_and_show_birthday_success(self):
        add_contact(["Fred", "5555555555"], self.book)
        msg = add_birthday(["Fred", "01.01.2000"], self.book)
        self.assertEqual(msg, "Birthday added.")
        shown = show_birthday(["Fred"], self.book)
        self.assertEqual(shown, "01.01.2000")

    def test_add_birthday_invalid_format(self):
        add_contact(["Gina", "6666666666"], self.book)
        msg = add_birthday(["Gina", "2000-01-01"], self.book)
        self.assertTrue(msg.startswith("Error:"))
        self.assertIn("Invalid date format. Use DD.MM.YYYY", msg)

    def test_show_birthday_not_found(self):
        self.assertEqual(show_birthday(["Unknown"], self.book), "Birthday not found.")

    # --- 6. get_upcoming_birthdays + weekend shift ---
    def test_birthdays_upcoming_within_7_days(self):
        today = datetime.today().date()
        def fmt(d): return d.strftime("%d.%m.%Y")
        add_contact(["Sally", "7777777777"], self.book)
        target = today + timedelta(days=3)
        add_birthday(["Sally", target.strftime("%d.%m.%Y")], self.book)
        res = birthdays([], self.book)
        self.assertIn(f"Sally: {fmt(target)}", res)

    def test_birthdays_weekend_shift_to_monday(self):
        today = datetime.today().date()
        saturday = None
        for d in range(1, 8):
            cand = today + timedelta(days=d)
            if cand.weekday() == 5:
                saturday = cand
                break

        if not saturday:
            self.skipTest("No Saturday within next 7 days to test weekend shift")

        add_contact(["Sam", "8888888888"], self.book)
        add_birthday(["Sam", saturday.strftime("%d.%m.%Y")], self.book)
        res = birthdays([], self.book)
        monday = saturday + timedelta(days=2)
        self.assertIn(f"Sam: {monday.strftime('%d.%m.%Y')}", res)

    def test_birthdays_none(self):
        book2 = AddressBook()
        add_contact(["Later", "9999999999"], book2)
        far = (datetime.today().date() + timedelta(days=10)).strftime("%d.%m.%Y")
        add_birthday(["Later", far], book2)
        res = birthdays([], book2)
        self.assertEqual(res, "No upcoming birthdays.")

    # --- 7. Testy metod Record i AddressBook bezpośrednio ---
    def test_record_add_remove_edit_phone(self):
        r = Record("X")
        r.add_phone("1111111111")
        self.assertEqual([p.value for p in r.phones], ["1111111111"])

        r.remove_phone("1111111111")
        self.assertEqual(len(r.phones), 0)
        with self.assertRaises(ValueError):
            r.remove_phone("2222222222")
        # add + edit_phone
        r.add_phone("3333333333")
        r.edit_phone("3333333333", "4444444444")
        self.assertEqual([p.value for p in r.phones], ["4444444444"])
        with self.assertRaises(ValueError):
            r.edit_phone("5555555555", "6666666666")
    def test_address_book_add_find_delete(self):
        r = Record("Y")
        r.add_phone("0000000000")
        self.book.add_record(r)
        self.assertIsNotNone(self.book.find("Y"))
        self.book.delete("Y")
        self.assertIsNone(self.book.find("Y"))

    # --- 8. Dekorator input_error: KeyError/IndexError/ValueError ---
    def test_input_error_catches_index_error(self):
        result = show_phones([], self.book)
        self.assertTrue(result.startswith("Error:"))

    def test_input_error_catches_value_error_on_birthday(self):
        add_contact(["V", "1010101010"], self.book)
        result = add_birthday(["V", "bad_date"], self.book)
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("Invalid date format", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)


