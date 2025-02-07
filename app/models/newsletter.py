from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

newsletter_dia_rel = Table(
    "newsletter_dia_rel",
    Base.metadata,
    Column("newsletter_id", Integer, ForeignKey("newsletters.id"), primary_key=True),
    Column("dia_id", Integer, ForeignKey("newsletters_dias.id"), primary_key=True),
)


class Newsletter(Base):
    __tablename__ = "newsletters"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, index=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, nullable=False)  # Guardamos la fecha real del email
    resumen = Column(Text, nullable=True)

    # Relación many-to-many con NewsletterDia
    dias = relationship(
        "NewsletterDia", secondary=newsletter_dia_rel, back_populates="newsletters"
    )


class NewsletterDia(Base):
    __tablename__ = "newsletters_dias"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)  # Fecha específica
    resumen = Column(Text, nullable=True)  # Resumen general del día

    # Relación many-to-many con Newsletter
    newsletters = relationship(
        "Newsletter", secondary=newsletter_dia_rel, back_populates="dias"
    )
