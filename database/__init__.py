from .models import Base
from .sqlite.vars import sqlite_engine as engine

# Create table
Base.metadata.create_all(engine)