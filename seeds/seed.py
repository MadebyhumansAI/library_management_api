import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text

from app.database import engine

with engine.connect() as conn:
    conn.execute(text(open("seeds/dataset.sql").read()))
    conn.commit()
    print("Seeded 10 books.")
