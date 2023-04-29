import datetime
from typing import Optional, Type

from sqlalchemy import Date, create_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session

DATABASE_NAME = "gods.db"

conn = create_engine(f"sqlite:///../{DATABASE_NAME}")


class Base(DeclarativeBase):
    pass


class Meeting(Base):
    __tablename__ = "meeting"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(Date())
    leader: Mapped[str] = Mapped[Optional[str]]
    topic: Mapped[str] = Mapped[Optional[str]]
    notes: Mapped[str] = Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"Meeting(id={self.id!r}, date={self.date!r}, leader={self.leader!r})"


def add_meeting(submitted_date, leader, topic, notes) -> bool:
    try:
        meeting_date = datetime.datetime.strptime(submitted_date, "%d/%m/%y").date()
    except ValueError:
        return False

    with Session(conn) as session:
        meeting = Meeting(date=meeting_date, leader=leader, topic=topic, notes=notes)
        session.add(meeting)
        session.commit()

    return True


def get_all_meetings() -> list[Type[Meeting]]:
    with Session(conn) as session:
        meetings = session.query(Meeting).all()

    return meetings


def get_all_meetings_formatted() -> str:
    meetings = get_all_meetings()

    result = ""
    for meeting in meetings:
        result += f'{meeting.date}: Meeting will be led by {meeting.leader} and the topic will be {meeting.topic}\n'

    return result
