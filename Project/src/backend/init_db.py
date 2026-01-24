"""
Initialize the CabbageMeet database.

Run this script once to create the database tables.
"""

from src.backend.database import init_db

if __name__ == "__main__":
    print("Initializing CabbageMeet database...")
    init_db()
    print("Database initialized successfully!")

