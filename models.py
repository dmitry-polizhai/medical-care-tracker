from sqlalchemy import Column, Integer, String, Date
from database import Base


class VisitDB(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    visit_date = Column(Date)
    doctor = Column(String)
    clinic = Column(String)
    reason = Column(String)
    treatment = Column(String)
    next_visit = Column(String)