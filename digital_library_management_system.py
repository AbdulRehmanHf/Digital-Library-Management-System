import json
import os
import sys
import pandas as pd  # For Streamlit tables
from datetime import datetime, timedelta

try:
    import streamlit as st
except ImportError:
    st = None

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"
DUE_DAYS = 14  # Books due after 14 days
FINE_PER_DAY = 1  # $1 per day overdue

class Book:
    def __init__(self, title, author, book_id, total_copies, category):
        self.title = title
        self.author = author
        self.book_id = book_id
        self.total_copies = total_copies
        self.available_copies = total_copies
        self.category = category

    def __str__(self):
        return f"ID: {self.book_id}, Title: {self.title}, Author: {self.author}, Category: {self.category}, Available: {self.available_copies}/{self.total_copies}"

class Library:
    def __init__(self):
        self.books = {}
        self.borrowed = {}  # book_id: [{"user": user_name, "borrow_date": datetime, "due_date": datetime}]
        self.load_data()

    def load_data(self):
        if os.path.exists('books.json'):
            with open('books.json', 'r') as f:
                data = json.load(f)
                for book_id, info in data.items():
                    book = Book(info['title'], info['author'], book_id, info['total'], info['category'])
                    book.available_copies = info['available']
                    self.books[book_id] = book
        if os.path.exists('borrowed.json'):
            with open('borrowed.json', 'r') as f:
                borrowed_data = json.load(f)
                for book_id, records in borrowed_data.items():
                    self.borrowed[book_id] = []
                    for rec in records:
                        self.borrowed[book_id].append({
                            "user": rec["user"],
                            "borrow_date": datetime.fromisoformat(rec["borrow_date"]),
                            "due_date": datetime.fromisoformat(rec["due_date"])
                        })

    def save_data(self):
        data = {}
        for book_id, book in self.books.items():
            data[book_id] = {
                'title': book.title,
                'author': book.author,
                'total': book.total_copies,
                'available': book.available_copies,
                'category': book.category
            }
        with open('books.json', 'w') as f:
            json.dump(data, f)

        borrowed_data = {}
        for book_id, records in self.borrowed.items():
            borrowed_data[book_id] = []
            for rec in records:
                borrowed_data[book_id].append({
                    "user": rec["user"],
                    "borrow_date": rec["borrow_date"].isoformat(),
                    "due_date": rec["due_date"].isoformat()
                })
        with open('borrowed.json', 'w') as f:
            json.dump(borrowed_data, f)

    def add_book(self, title, author, book_id, total_copies, category):
        if book_id in self.books:
            return "Book ID already exists."
        try:
            total_copies = int(total_copies)
            if total_copies <= 0:
                return "Total copies must be positive."
            book = Book(title, author, book_id, total_copies, category)
            self.books[book_id] = book
            self.save_data()
            return "Book added successfully."
        except ValueError:
            return "Total copies must be a number."

    def search_by_title(self, title):
        return [book for book in self.books.values() if title.lower() in book.title.lower()]

    def search_by_author(self, author):
        return [book for book in self.books.values() if author.lower() in book.author.lower()]

    def search_by_category(self, category):
        return [book for book in self.books.values() if category.lower() in book.category.lower()]

    def borrow_book(self, book_id, user_name):
        if book_id not in self.books:
            return "Book not found."
        book = self.books[book_id]
        if book.available_copies > 0:
            book.available_copies -= 1
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=DUE_DAYS)
            if book_id not in self.borrowed:
                self.borrowed[book_id] = []
            self.borrowed[book_id].append({
                "user": user_name,
                "borrow_date": borrow_date,
                "due_date": due_date
            })
            self.save_data()
            return f"Book borrowed successfully by {user_name}. Due date: {due_date.strftime('%Y-%m-%d')}"
        else:
            return "No copies available."

    def return_book(self, book_id, user_name):
        if book_id not in self.books:
            return "Book not found."
        if book_id in self.borrowed:
            for rec in self.borrowed[book_id]:
                if rec["user"] == user_name:
                    self.books[book_id].available_copies += 1
                    return_date = datetime.now()
                    due_date = rec["due_date"]
                    self.borrowed[book_id].remove(rec)
                    if not self.borrowed[book_id]:
                        del self.borrowed[book_id]
                    self.save_data()
                    if return_date > due_date:
                        overdue_days = (return_date - due_date).days
                        fine = overdue_days * FINE_PER_DAY
                        return f"Book returned successfully by {user_name}. Overdue by {overdue_days} days. Fine: ${fine}"
                    else:
                        return f"Book returned successfully by {user_name}. No fine."
        return "No record of this borrowing."

    def view_all_books(self):
        return list(self.books.values())

    def view_borrowed_records(self):
        records = []
        for book_id, recs in self.borrowed.items():
            book = self.books.get(book_id)
            if book:
                for rec in recs:
                    records.append(f"Book ID: {book_id}, Title: {book.title}, Borrowed by: {rec['user']}, Borrow Date: {rec['borrow_date'].strftime('%Y-%m-%d')}, Due Date: {rec['due_date'].strftime('%Y-%m-%d')}")
        return records

def admin_login_cli():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def run_cli(library):
    is_admin = False
    while True:
        print("\nWelcome to Digital Library System")
        if not is_admin:
            print("0. Admin Login")
        print("1. Add Book" if is_admin else "1. (Admin Only) Add Book")
        print("2. Search by Title")
        print("3. Search by Author")
        print("4. Search by Category")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. View All Books")
        print("8. View Borrowed Records")
        print("9. Exit")
        choice = input("Enter your choice: ")

        if choice == '0' and not is_admin:
            if admin_login_cli():
                is_admin = True
                print("Admin login successful.")
            else:
                print("Invalid credentials.")
            continue

        if choice == '1':
            if not is_admin:
                print("Admin access required.")
                continue
            title = input("Enter Title: ")
            author = input("Enter Author: ")
            book_id = input("Enter Book ID: ")
            total_copies = input("Enter Total Copies: ")
            category = input("Enter Category: ")
            result = library.add_book(title, author, book_id, total_copies, category)
            print(result)

        elif choice == '2':
            title = input("Enter Title to search: ")
            results = library.search_by_title(title)
            if results:
                for book in results:
                    print(book)
            else:
                print("No books found.")

        elif choice == '3':
            author = input("Enter Author to search: ")
            results = library.search_by_author(author)
            if results:
                for book in results:
                    print(book)
            else:
                print("No books found.")

        elif choice == '4':
            category = input("Enter Category to search: ")
            results = library.search_by_category(category)
            if results:
                for book in results:
                    print(book)
            else:
                print("No books found.")

        elif choice == '5':
            book_id = input("Enter Book ID: ")
            user_name = input("Enter Your Name: ")
            result = library.borrow_book(book_id, user_name)
            print(result)

        elif choice == '6':
            book_id = input("Enter Book ID: ")
            user_name = input("Enter Your Name: ")
            result = library.return_book(book_id, user_name)
            print(result)

        elif choice == '7':
            books = library.view_all_books()
            if books:
                for book in books:
                    print(book)
            else:
                print("No books in library.")

        elif choice == '8':
            records = library.view_borrowed_records()
            if records:
                for record in records:
                    print(record)
            else:
                print("No borrowed books.")

        elif choice == '9':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

def is_running_with_streamlit():
    if st is None:
        return False
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        return ctx is not None
    except ImportError:
        return False

def run_streamlit(library):
    st.title("Digital Library Management System")

    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

    if not st.session_state.is_admin:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.write("Login successful.")
            else:
                st.write("Invalid credentials.")
        return  # Stop here if not logged in

    menu = st.sidebar.selectbox("Menu", [
        "Add Book",
        "Search by Title",
        "Search by Author",
        "Search by Category",
        "Borrow Book",
        "Return Book",
        "View All Books",
        "View Borrowed Records"
    ])

    if menu == "Add Book":
        if not st.session_state.is_admin:
            st.write("Admin access required.")
            return
        st.subheader("Add New Book")
        title = st.text_input("Title")
        author = st.text_input("Author")
        book_id = st.text_input("Book ID")
        total_copies = st.text_input("Total Copies")
        category = st.text_input("Category")
        if st.button("Add"):
            result = library.add_book(title, author, book_id, total_copies, category)
            st.write(result)

    elif menu == "Search by Title":
        st.subheader("Search by Title")
        title = st.text_input("Enter Title")
        if st.button("Search"):
            results = library.search_by_title(title)
            if results:
                search_data = [
                    {
                        "ID": book.book_id,
                        "Title": book.title,
                        "Author": book.author,
                        "Category": book.category,
                        "Available": f"{book.available_copies}/{book.total_copies}"
                    } for book in results
                ]
                st.dataframe(pd.DataFrame(search_data))
            else:
                st.write("No books found.")

    elif menu == "Search by Author":
        st.subheader("Search by Author")
        author = st.text_input("Enter Author")
        if st.button("Search"):
            results = library.search_by_author(author)
            if results:
                search_data = [
                    {
                        "ID": book.book_id,
                        "Title": book.title,
                        "Author": book.author,
                        "Category": book.category,
                        "Available": f"{book.available_copies}/{book.total_copies}"
                    } for book in results
                ]
                st.dataframe(pd.DataFrame(search_data))
            else:
                st.write("No books found.")

    elif menu == "Search by Category":
        st.subheader("Search by Category")
        category = st.text_input("Enter Category")
        if st.button("Search"):
            results = library.search_by_category(category)
            if results:
                search_data = [
                    {
                        "ID": book.book_id,
                        "Title": book.title,
                        "Author": book.author,
                        "Category": book.category,
                        "Available": f"{book.available_copies}/{book.total_copies}"
                    } for book in results
                ]
                st.dataframe(pd.DataFrame(search_data))
            else:
                st.write("No books found.")

    elif menu == "Borrow Book":
        st.subheader("Borrow Book")
        book_id = st.text_input("Book ID")
        user_name = st.text_input("Your Name")
        if st.button("Borrow"):
            result = library.borrow_book(book_id, user_name)
            st.write(result)

    elif menu == "Return Book":
        st.subheader("Return Book")
        book_id = st.text_input("Book ID")
        user_name = st.text_input("Your Name")
        if st.button("Return"):
            result = library.return_book(book_id, user_name)
            st.write(result)

    elif menu == "View All Books":
        st.subheader("All Books")
        books = library.view_all_books()
        if books:
            books_data = [
                {
                    "ID": book.book_id,
                    "Title": book.title,
                    "Author": book.author,
                    "Category": book.category,
                    "Available": f"{book.available_copies}/{book.total_copies}"
                } for book in books
            ]
            st.dataframe(pd.DataFrame(books_data))
        else:
            st.write("No books in library.")

    elif menu == "View Borrowed Records":
        st.subheader("Borrowed Records")
        records = library.view_borrowed_records()
        if records:
            records_data = []
            for record in records:
                parts = record.split(", ")
                book_id = parts[0].split(": ")[1]
                title = parts[1].split(": ")[1]
                borrowed_by = parts[2].split(": ")[1]
                borrow_date = parts[3].split(": ")[1]
                due_date = parts[4].split(": ")[1]
                records_data.append({
                    "Book ID": book_id,
                    "Title": title,
                    "Borrowed by": borrowed_by,
                    "Borrow Date": borrow_date,
                    "Due Date": due_date
                })
            st.dataframe(pd.DataFrame(records_data))
        else:
            st.write("No borrowed books.")

if __name__ == "__main__":
    library = Library()
    if is_running_with_streamlit() or (len(sys.argv) > 1 and sys.argv[1] == '--streamlit'):
        run_streamlit(library)
    else:
        run_cli(library)