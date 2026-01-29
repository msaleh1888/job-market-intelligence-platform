from datetime import datetime

from sqlalchemy import Column, ForeignKey, Index, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


job_snapshot_skills = Table(
    "job_snapshot_skills",
    Base.metadata,
    Column("job_snapshot_id", ForeignKey("job_snapshots.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Index("ix_job_snapshot_skills_skill_id", "skill_id"),
    Index("ix_job_snapshot_skills_job_snapshot_id", "job_snapshot_id"),
)


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    jobs: Mapped[list["Job"]] = relationship(back_populates="platform")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("platform_id", "external_job_id", name="uq_jobs_platform_external_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.id"), nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(200), nullable=False)

    url: Mapped[str] = mapped_column(String(2000), nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    platform: Mapped["Platform"] = relationship(back_populates="jobs")
    snapshots: Mapped[list["JobSnapshot"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobSnapshot(Base):
    __tablename__ = "job_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)

    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    seniority: Mapped[str | None] = mapped_column(String(100), nullable=True)

    scraped_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    job: Mapped["Job"] = relationship(back_populates="snapshots")

    skills: Mapped[list["Skill"]] = relationship(
        secondary=job_snapshot_skills,
        back_populates="snapshots",
    )


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("normalized_name", name="uq_skills_normalized_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), nullable=False)

    snapshots: Mapped[list["JobSnapshot"]] = relationship(
        secondary=job_snapshot_skills,
        back_populates="skills",
    )
