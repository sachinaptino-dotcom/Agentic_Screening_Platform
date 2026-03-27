from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from database import Base


class RecruiterAuth(Base):
    __tablename__ = "recruiter_auth"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, server_default="recruiter")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login = Column(DateTime(timezone=True))

    performance = relationship("RecruiterPerformance", back_populates="auth", uselist=False, cascade="all, delete")


class RecruiterPerformance(Base):
    __tablename__ = "recruiter_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    auth_id = Column(UUID(as_uuid=True), ForeignKey("recruiter_auth.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_name = Column(String(150), nullable=False)
    department = Column(String(100))
    total_resumes_uploaded = Column(Integer, nullable=False, server_default="0")
    total_jds_processed = Column(Integer, nullable=False, server_default="0")
    total_shortlisted = Column(Integer, nullable=False, server_default="0")
    total_rejected = Column(Integer, nullable=False, server_default="0")
    avg_ats_score_given = Column(Numeric(5, 2), nullable=False, server_default="0.00")
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    auth = relationship("RecruiterAuth", back_populates="performance")
    candidates = relationship("Candidate", back_populates="recruiter", cascade="all, delete")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("recruiter_performance.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255))
    phone = Column(String(30))
    location = Column(String(150))
    job_applied = Column(String(200))
    job_title = Column(String(200))
    ats_score = Column(SmallInteger, nullable=False, server_default="0")
    rank = Column(SmallInteger, index=True)
    skills_matched = Column(ARRAY(Text), nullable=False, server_default="{}")
    skills_not_matched = Column(ARRAY(Text), nullable=False, server_default="{}")
    main_summary = Column(Text)
    keyword_score = Column(Numeric(5, 2))
    semantic_score = Column(Numeric(5, 2))
    authenticity_score = Column(Numeric(5, 2))
    authenticity_flag = Column(String(20))
    authenticity_notes = Column(Text)
    linkedin_flag = Column(String(10))
    linkedin_summary = Column(Text)
    pros = Column(ARRAY(Text), nullable=False, server_default="{}")
    cons = Column(ARRAY(Text), nullable=False, server_default="{}")
    resume_path = Column(Text)
    linkedin_path = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    recruiter = relationship("RecruiterPerformance", back_populates="candidates")

    __table_args__ = (
        CheckConstraint("ats_score BETWEEN 0 AND 100", name="ck_candidates_ats_score"),
        CheckConstraint("authenticity_flag IN ('pass', 'fail', 'no_linkedin')", name="ck_candidates_authenticity_flag"),
        CheckConstraint("linkedin_flag IN ('green', 'red', 'none')", name="ck_candidates_linkedin_flag"),
        Index("idx_candidates_score", "ats_score"),
        Index("idx_candidates_rank", "rank"),
    )
