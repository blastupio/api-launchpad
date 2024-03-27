from decimal import Decimal
from sqlalchemy import Column, Text, String, DECIMAL, DateTime, func, ForeignKey

from sqlalchemy.orm import relationship

from app.base import Base, BigIntegerType


class LaunchpadProject(Base):
    __tablename__ = 'launchpad_project'

    id = Column(BigIntegerType, primary_key=True)
    name = Column(String, nullable=False)
    short_description = Column(Text(), nullable=False)

    total_raise = Column(DECIMAL, default=Decimal('0'))
    token_price = Column(DECIMAL, nullable=False)

    registration_start_at = Column(DateTime(), nullable=False)
    registration_end_at = Column(DateTime(), nullable=False)
    start_at = Column(DateTime(), nullable=False)
    end_at = Column(DateTime(), nullable=False)
    fcfs_opens_at = Column(DateTime(), nullable=False)

    created_at = Column(DateTime(), nullable=False, default=func.now())
    updated_at = Column(DateTime(), nullable=True)

    profile_images = relationship("File", back_populates="project")


class File(Base):
    __tablename__ = 'file'

    id = Column(BigIntegerType, primary_key=True)

    title = Column(String, nullable=True)
    url = Column(String, nullable=False)

    project_id = Column(BigIntegerType, ForeignKey('launchpad_project.id'))
    project = relationship("LaunchpadProject", back_populates="profile_images")

