Digital Library Management System Project Report
Prepared By: Abdul Rehman
Batch: 17 - Saylani
Date: December 18, 2025

1. Introduction
This project is a Python-based digital library system using OOP concepts. It manages books, allowing add, search, borrow, and return operations. It includes CLI for console and Streamlit for web interface, with JSON data storage.

2. Objective
To apply Python and OOP for a real-world library simulation, handling user interactions and data management.

3. Tools Used

Python 3.x
Libraries: json, os, datetime, pandas, streamlit
Interfaces: CLI (console menu), Streamlit (web GUI)
Storage: books.json, borrowed.json

4. Key Concepts

Classes: Book, Library
OOP: Encapsulation, objects
Data: Dicts/lists for books/borrows
File I/O: JSON persistence
Advanced: Dates/fines, categories, admin login

5. Features

Add Book (admin only)
Search by Title/Author/Category
Borrow/Return Book (with due dates/fines)
View All Books/Borrowed Records

6. Code Structure

Book Class: Holds book details
Library Class: Manages operations, load/save data
run_cli(): Console menu loop
run_streamlit(): Web interface with tables
Main: Detects CLI or Streamlit mode

7. How to Run

Install: pip install streamlit pandas
CLI: python digital_library_management_system.py
Streamlit: streamlit run digital_library_management_system.py
Admin: "admin"/"password"

8. Screenshots
(Insert here: CLI menu, Streamlit view, borrow example, etc.)
9. Learning Outcomes

Mastered OOP in Python
Handled user inputs and data persistence
Built CLI/GUI apps

10. Conclusion
This system demonstrates Python skills effectively. Future: User auth, database integration.