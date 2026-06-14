from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Time, Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy import Text
from datetime import datetime
from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



class SesionChat(Base):

    __tablename__ = "sesiones_chat"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    telefono = Column(
        String,
        nullable=False
    )

    estado = Column(
        String,
        nullable=False
    )

    horarios_ofrecidos = Column(
        String,
        nullable=True
    )

    cita_id = Column(
        Integer,
        nullable=True
    )

    # NUEVOS CAMPOS

    especialidad = Column(
        String,
        nullable=True
    )

    medico_id = Column(
        Integer,
        nullable=True
    )

    fecha_objetivo = Column(
        String,
        nullable=True
    )

    fecha_seleccionada = Column(
    String,
    nullable=True
)

class DisponibilidadMedico(Base):

    __tablename__ = "disponibilidad_medico"

    id = Column(Integer, primary_key=True)

    medico_id = Column(
        Integer,
        ForeignKey("medicos.id")
    )

    dia_semana = Column(String)

    hora_inicio = Column(Time)

    hora_fin = Column(Time)

    duracion_cita = Column(Integer)

    activo = Column(
        Boolean,
        default=True
    )

class Medico(Base):
    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    especialidad = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    config_tiempo_control = Column(Integer, default=20)
    config_tiempo_procedimiento = Column(Integer, default=40)

    citas = relationship("Cita", back_populates="medico", cascade="all, delete-orphan")


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    whatsapp_id = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    registrado_en = Column(DateTime, server_default=func.now())

    citas = relationship("Cita", back_populates="paciente", cascade="all, delete-orphan")


class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)

    medico_id = Column(
        Integer,
        ForeignKey("medicos.id", ondelete="CASCADE"),
        nullable=False
    )

    paciente_id = Column(
        Integer,
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=False
    )

    fecha_hora = Column(DateTime, nullable=False)

    tipo_servicio = Column(
        String(50),
        nullable=False
    )

    estado = Column(
        String(20),
        default="programada"
    )

    creado_en = Column(
        DateTime,
        server_default=func.now()
    )

    medico = relationship(
        "Medico",
        back_populates="citas"
    )

    paciente = relationship(
        "Paciente",
        back_populates="citas"
    )

    
    __table_args__ = (
        CheckConstraint(
            "tipo_servicio IN ('control','procedimiento')",
            name="chk_tipo_servicio"
        ),
        CheckConstraint(
            "estado IN ('programada','cancelada','reagendada','completada')",
            name="chk_estado_cita"
        ),
    )

class ConfiguracionAgenda(Base):

    __tablename__ = "configuracion_agenda"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    medico_id = Column(
        Integer,
        ForeignKey("medicos.id")
    )

    dia_semana = Column(
        String
    )

    hora_inicio = Column(
        String
    )

    hora_fin = Column(
        String
    )

    duracion_cita = Column(
        Integer,
        default=20
    )

    activo = Column(
        Boolean,
        default=True
    )

class Notificacion(Base):

    __tablename__ = "notificaciones"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    paciente_id = Column(
        Integer,
        nullable=False
    )

    mensaje = Column(
        Text,
        nullable=False
    )

    fecha = Column(
        DateTime,
        default=datetime.utcnow
    )

    enviada = Column(
        Boolean,
        default=False
    )

    