from fastapi import FastAPI
from Backend.app.db.session import Base, engine
import Backend.app.models

Base.metadata.create_all(bind=engine)
