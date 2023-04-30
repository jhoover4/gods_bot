import datetime
import traceback
from typing import Optional, Type

from sqlalchemy import Date, create_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session

DATABASE_NAME = "gods.db"


class Base(DeclarativeBase):
    pass


class Meeting(Base):
    __tablename__ = "meeting"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(Date())
    leader: Mapped[Optional[str]]
    topic: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"Meeting(id={self.id!r}, date={self.date!r}, leader={self.leader!r}, topic={self.topic!r}," \
               f"notes={self.notes!r})"


class Database:
    """Holds logic for dealing with the database. Is a singleton so that the database connection is only instantiated
    once."""

    def __init__(self):
        self.engine = create_engine(f"sqlite:///{DATABASE_NAME}")
        Base.metadata.create_all(self.engine)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def insert_meeting(self, submitted_date, leader, topic, notes) -> bool:
        try:
            meeting_date = datetime.datetime.strptime(submitted_date, "%m/%d/%y")
        except ValueError as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            return False

        with Session(self.engine) as session:
            meeting = Meeting(date=meeting_date, leader=leader, topic=topic, notes=notes)
            session.add(meeting)
            session.commit()

        return True

    def get_all_meetings(self) -> list[Type[Meeting]]:
        with Session(self.engine) as session:
            meetings = session.query(Meeting).all()

        return meetings

    def get_all_meetings_formatted(self) -> str:
        meetings = self.get_all_meetings()

        result = ""
        for meeting in meetings:
            result += f"**{meeting.date}**: Meeting will be led by {meeting.leader.title()} and the topic will be " \
                      f"{meeting.topic}\n"

        return result
