import sqlite3
import datetime

DATABASE_NAME = "gods.db"


class Database:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS meetings
                     (id INTEGER PRIMARY KEY,
                     date TEXT NOT NULL)"""
        )

    def get_all_meetings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT date FROM meetings ORDER BY date ASC")
        result = cursor.fetchone()
        if result:
            # TODO: List all meetings
            for meeting in result:
                response += "The next meeting is in {} days on {}.".format(
                    days_until, meeting_date.strftime("%A, %B %d")
                )
        else:
            response = "There are no meetings scheduled."

        return response

    def add_meeting(self, date):
        # TODO: Evaluate date, if bad error
        meeting_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        try:
            self.conn.execute("INSERT INTO meetings (date) VALUES (?)", (meeting_date,))
            self.conn.commit()
            response = "Meeting scheduled for {}.".format(
                meeting_date.strftime("%A, %B %d")
            )
        except (IndexError, ValueError):
            response = "Invalid date format. Please use YYYY-MM-DD."

        return response
