import uuid

from sqlalchemy import Column, UUID, String, Boolean, Table, ForeignKey, Text
from sqlalchemy.orm import relationship

from config.database import Base
trip_member_association_table = Table(
    "trip_member_association_table",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("trip_id", ForeignKey("trips.id"), primary_key=True)
)


class Trip(Base):
    __tablename__ = 'trips'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100))
    description = Column(Text())
    is_public = Column(Boolean())
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="trips_owned",
        lazy="selectin"
    )

    members = relationship(
        "User",
        secondary=trip_member_association_table,
        back_populates="trips_joined",
        lazy="selectin"
    )
