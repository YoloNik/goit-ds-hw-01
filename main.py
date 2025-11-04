from address_book import (
    AddressBook,
    add_contact,
    change_contact,
    show_phones,
    show_all,
    add_birthday,
    show_birthday,
    birthdays,
)

EXIT_COMMANDS = {"exit", "close"}


def handle_add_cmd(book: AddressBook, args: list[str]) -> str:
    """
    add <name> <phone>
    Name can be multi-word; last token is phone (10 digits).
    """
    if len(args) < 2:
        return "Error: Usage -> add <name> <phone>"
    name = " ".join(args[:-1])
    phone = args[-1]
    return add_contact([name, phone], book)

def handle_change_cmd(book: AddressBook, args: list[str]) -> str:
    """
    change <name> <old_phone> <new_phone>
    Name can be multi-word; last two tokens are phones.
    """
    if len(args) < 3:
        return "Error: Usage -> change <name> <old_phone> <new_phone>"
    name = " ".join(args[:-2])
    old_phone = args[-2]
    new_phone = args[-1]
    return change_contact([name, old_phone, new_phone], book)

def handle_phone_cmd(book: AddressBook, args: list[str]) -> str:
    """
    phone <name>
    Name can be multi-word.
    """
    if not args:
        return "Error: Usage -> phone <name>"
    name = " ".join(args)
    return show_phones([name], book)

def handle_all_cmd(book: AddressBook, args: list[str]) -> str:
    """
    all
    """
    if args:
        return "Error: Usage -> all"
    return show_all(book)

def handle_add_birthday_cmd(book: AddressBook, args: list[str]) -> str:
    """
    add-birthday <name> <DD.MM.YYYY>
    Name can be multi-word; last token is date.
    """
    if len(args) < 2:
        return "Error: Usage -> add-birthday <name> <DD.MM.YYYY>"
    name = " ".join(args[:-1])
    date_str = args[-1]
    return add_birthday([name, date_str], book)

def handle_show_birthday_cmd(book: AddressBook, args: list[str]) -> str:
    """
    show-birthday <name>
    """
    if not args:
        return "Error: Usage -> show-birthday <name>"
    name = " ".join(args)
    return show_birthday([name], book)

def handle_birthdays_cmd(book: AddressBook, args: list[str]) -> str:
    """
    birthdays
    """
    if args:
        return "Error: Usage -> birthdays"
    return birthdays([], book)

def handle_delete_cmd(book: AddressBook, args: list[str]) -> str:
    """
    delete <name>
    """
    if not args:
        return "Error: Usage -> delete <name>"
    name = " ".join(args)
    if book.find(name):
        book.delete(name)
        return "Contact deleted."
    return "Error: Contact not found."

def handle_help_cmd(book: AddressBook, args: list[str]) -> str:
    """
    help
    """
    if args:
        return "Error: Usage -> help"
    return (
        "Available commands:\n"
        "  add <name> <phone>                    - Add a contact or add another phone (10 digits).\n"
        "  change <name> <old_phone> <new_phone> - Replace a phone (10 digits).\n"
        "  phone <name>                          - Show all phones for a contact.\n"
        "  all                                   - Show all contacts.\n"
        "  add-birthday <name> <DD.MM.YYYY>      - Add a birthday to a contact.\n"
        "  show-birthday <name>                  - Show a contact's birthday.\n"
        "  birthdays                             - Show upcoming birthdays (7 days; weekend -> Monday).\n"
        "  delete <name>                         - Delete a contact.\n"
        "  help                                  - Show this help.\n"
        "  exit | close                          - Exit the program.\n"
    )


def route_command(book: AddressBook, cmd: str, args: list[str]) -> str:
    """
    Routes command to the corresponding handler function.
    """
    if cmd in EXIT_COMMANDS:
        return "__EXIT__"

    handlers = {
        "add": handle_add_cmd,
        "change": handle_change_cmd,
        "phone": handle_phone_cmd,
        "all": handle_all_cmd,
        "add-birthday": handle_add_birthday_cmd,
        "show-birthday": handle_show_birthday_cmd,
        "birthdays": handle_birthdays_cmd,
        "delete": handle_delete_cmd,
        "help": handle_help_cmd,
    }

    handler = handlers.get(cmd)
    if handler is None:
        return "Unknown command. Type 'help' to see available commands."
    return handler(book, args)

def parse_input(line: str) -> tuple[str, list[str]]:
    """
    Splits raw line into (command, args_list).
    """
    line = line.strip()
    if not line:
        return "", []
    parts = line.split()
    return parts[0].lower(), parts[1:]

def main():
    book = AddressBook()
    book.load_data()
    print("Welcome to Address Book!")
    print(handle_help_cmd(book, []))

    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            book.save_data()
            break

        cmd, args = parse_input(line)
        if not cmd:
            continue

        result = route_command(book, cmd, args)
        if result == "__EXIT__":
            print("Goodbye!")
            book.save_data()
            break
        print(result)

if __name__ == "__main__":
    main()

    