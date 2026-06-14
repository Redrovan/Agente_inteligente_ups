from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from typing import List
from datetime import time

# =====================================================
# SCHEMAS WHATSAPP WEBHOOK
# =====================================================

class TextMessage(BaseModel):
    body: str


class MessageItem(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    text: Optional[TextMessage] = None
    type: str


class ContactItem(BaseModel):
    profile: dict
    wa_id: str


class MetadataItem(BaseModel):
    display_phone_number: str
    phone_number_id: str


class ValueItem(BaseModel):
    messaging_product: str
    metadata: MetadataItem
    contacts: Optional[List[ContactItem]] = None
    messages: Optional[List[MessageItem]] = None


class ChangeItem(BaseModel):
    value: ValueItem
    field: str


class EntryItem(BaseModel):
    id: str
    changes: List[ChangeItem]


class WebhookWhatsAppPayload(BaseModel):
    object: str
    entry: List[EntryItem]

    class Config:
        populate_by_name = True


# =====================================================
# MEDICOS
# =====================================================

class MedicoBase(BaseModel):
    nombre: str
    especialidad: str
    email: str


class MedicoCreate(MedicoBase):
    config_tiempo_control: int = 20
    config_tiempo_procedimiento: int = 40


class MedicoResponse(MedicoBase):
    id: int
    config_tiempo_control: int
    config_tiempo_procedimiento: int

    class Config:
        from_attributes = True


# =====================================================
# PACIENTES
# =====================================================

class PacienteBase(BaseModel):
    nombre: str
    whatsapp_id: str
    email: Optional[str] = None


class PacienteCreate(PacienteBase):
    pass


class PacienteResponse(PacienteBase):
    id: int

    class Config:
        from_attributes = True


# =====================================================
# CITAS
# =====================================================

class CitaCreate(BaseModel):
    medico_id: int
    paciente_id: int
    fecha_hora: datetime
    tipo_servicio: str


class CitaResponse(BaseModel):
    id: int
    medico_id: int
    paciente_id: int
    fecha_hora: datetime
    tipo_servicio: str
    estado: str

    class Config:
        from_attributes = True


class DisponibilidadRequest(BaseModel):
    medico_id: int
    fecha: date


class DisponibilidadResponse(BaseModel):
    medico_id: int
    fecha: date
    horarios_disponibles: List[str]


# =====================================================
# CANCELACION DE CITAS
# =====================================================

class CancelarCitaResponse(BaseModel):
    mensaje: str
    cita_id: int
    estado: str


# =====================================================
# REAGENDAR CITAS
# =====================================================

class ReagendarCitaRequest(BaseModel):
    nueva_fecha_hora: datetime


class ReagendarCitaResponse(BaseModel):
    mensaje: str
    cita_id: int
    fecha_hora: datetime
    estado: str


# =====================================================
# PREDICCION DE DEMANDA
# =====================================================

class PrediccionDemandaResponse(BaseModel):
    hora_pico: str | None
    cantidad_citas: int
    recomendacion: str


# =====================================================
# DASHBOARD
# =====================================================

class DashboardResponse(BaseModel):
    total_medicos: int
    total_pacientes: int
    total_citas: int
    citas_programadas: int
    citas_canceladas: int
    citas_reagendadas: int
    hora_pico: str | None

# =====================================================
# DISPONIBILIDAD CONFIGURABLE
# =====================================================

class DisponibilidadMedicoCreate(BaseModel):

    medico_id: int

    dia_semana: str

    hora_inicio: time

    hora_fin: time

    duracion_cita: int


class DisponibilidadMedicoResponse(BaseModel):

    id: int

    medico_id: int

    dia_semana: str

    hora_inicio: time

    hora_fin: time

    duracion_cita: int

    activo: bool

    class Config:
        from_attributes = True


    # =====================================================
# AGENDA SEMANAL
# =====================================================

class SlotAgenda(BaseModel):
    hora: str
    estado: str


class AgendaDia(BaseModel):
    dia: str
    slots: List[SlotAgenda]


class ConfiguracionAgendaCreate(
    BaseModel
):
    medico_id: int
    dia_semana: str
    hora_inicio: str
    hora_fin: str
    duracion_cita: int