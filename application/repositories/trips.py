from sqlalchemy.orm import Session

from models.trips import Trip


class TripRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, trip: Trip):
        self.db.add(trip)
        self.db.commit()

    def update(self, trip: Trip):
        self.db.query(Trip).update(trip)
        self.db.commit()

    def get_trip_by_id(self, trip_id: str):
        return self.db.query(Trip).filter(Trip.id == trip_id).first()

    def get_all(self):
        return self.db.query(Trip).all()
    