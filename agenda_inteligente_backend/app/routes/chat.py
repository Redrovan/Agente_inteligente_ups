import unicodedata
from datetime import date, timedelta, datetime
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Medico
from app.services.disponibilidad_service import (
    obtener_horarios_disponibles
)
from app.services.cita_service import (
    registrar_cita_desde_chat
)
from app.services.chat_service import (
    obtener_sesion,
    guardar_sesion,
    eliminar_sesion
)

from app.models.models import (
    Medico,
    Cita
)

from app.services.gemini_service import interpretar_mensaje


def normalizar(texto: str):
    texto = texto.lower().strip()
    return "".join(
        c
        for c in unicodedata.normalize(
            "NFD",
            texto
        )
        if unicodedata.category(c) != "Mn"
    )


router = APIRouter(
    prefix="/api/v1",
    tags=["Agente IA Demo"]
)


@router.post("/chat")
def chat(
    mensaje: dict,
    db: Session = Depends(get_db)
):
    print("===ENTRE AL CHAT ===")

    telefono = mensaje["telefono"]
    texto = mensaje["mensaje"].strip()

    sesion = obtener_sesion(
        db,
        telefono
    )

    print("SESION:", sesion)

    if sesion:
        print("ESTADO:", sesion.estado)

    # =====================================
    # GEMINI SOLO SI NO HAY SESION ACTIVA
    # =====================================

    if not sesion:

        try:

            print("MENSAJE:", texto)

            texto_lower = texto.lower()

            if (
                "mis citas" in texto_lower
                or "mostrar citas" in texto_lower
                or "muestrame mis citas" in texto_lower
            ):
                citas = (
                    db.query(Cita)
                    .filter(
                        Cita.paciente_id == 1,
                        Cita.estado != "cancelada"
                    )
                    .all()
                
                )
                
                return {
                    
                    "citas": [
                        {
                            "id": c.id,
                            "fecha": c.fecha_hora.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "estado": c.estado
                        }
                        for c in citas
                    ]
                }
            
            datos_ia = interpretar_mensaje(texto)
            
            print("GEMINI:", datos_ia)

            if (
                datos_ia.get("intencion")
                == "consultar_citas"
            ):
                
                citas = (
                    db.query(Cita)
                    .filter(
                        Cita.paciente_id == 1,
                        Cita.estado != "cancelada"
                    )
                    .all()
                )

                return {
                    "citas":[
                        {
                            "id": c.id,
                            "fecha": c.fecha_hora.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "estado": c.estado
                        }
                        for c in citas
                    ]
                }
            
            if(
                datos_ia.get("intencion")
                == "cancelar_cita"
            ):
                
                
                
                print("ENTRO A CANCELAR")
                
                citas = (
                    db.query(Cita)
                    .filter(
                        Cita.paciente_id == 1,
                        Cita.estado.in_(["programada","reagendada"])
                    )
                    .all()
                )

                if not citas:

                    return {
                        "respuesta":
                        "No tiene citas programadas"
                    }
                
                guardar_sesion(
                    db,
                    telefono,
                    estado="esperando_cancelacion"
                )

                return {
                    "respuesta":
                    "Seleccione el ID de la cita a cancelar.",
                    "citas": [
                        {
                            "id": c.id,
                            "fecha": c.fecha_hora.strftime(
                                "%Y-%m-%d %H:%M"
                            )
                        }
                        for c in citas
                    ]
                }
            
            if (
                datos_ia.get("intencion")
                == "reagendar_cita"
            ):
                
                citas = (
                    db.query(Cita)
                    .filter(
                        Cita.paciente_id == 1,
                        Cita.estado.in_(["programa","reagendada"])
                    )
                    .all()
                )

                if not citas:

                    return {
                        "respuesta":
                        "No tiene citas para reagendar."
                    }
                
                guardar_sesion(
                    db,
                    telefono,
                    estado="esperando_reagendar_id"
                )

                return {
                    "respuesta":
                    "seleccione el ID de la cita a reagendar.",
                    "citas": [
                        {
                            "id":c.id,
                            "fecha": c.fecha_hora.strftime("%Y-%m-%d %H:%M"
                            ),
                            "estado": c.estado
                        }
                        for c in citas
                    ]
                }

            if (
                datos_ia.get("intencion") == "agendar_cita"
                and datos_ia.get("especialidad")
            ):

                especialidad_buscada = datos_ia["especialidad"]

                print(
                    "ESPECIALIDAD:",
                    especialidad_buscada
                )

                medicos = db.query(Medico).all()

                medico = None

                for m in medicos:

                    if (
                        normalizar(m.especialidad)
                        ==
                        normalizar(especialidad_buscada)
                    ):

                        medico = m
                        break

                print(
                    "MEDICO ENCONTRADO:",
                    medico
                )

                if medico:

                    fecha_texto = (
                        datos_ia.get(
                            "fecha",
                            ""
                        )
                        .lower()
                        .strip()
                    )

                    if fecha_texto in [
                        "mañana",
                        "manana"
                    ]:

                        fecha_consulta = (
                            date.today()
                            + timedelta(days=1)
                        )

                    elif fecha_texto == "hoy":

                        fecha_consulta = (
                            date.today()
                        )

                    else:

                        fecha_consulta = (
                            date.today()
                        )

                    horarios = []

                    for _ in range(14):

                        horarios = (
                            obtener_horarios_disponibles(
                                db,
                                medico.id,
                                fecha_consulta
                            )
                        )

                        if horarios:
                            break

                        fecha_consulta += timedelta(
                            days=1
                        )

                    print(
                        "FECHA FINAL:",
                        fecha_consulta
                    )

                    print(
                        "HORARIOS:",
                        horarios
                    )

                    if horarios:

                        guardar_sesion(
                            db,
                            telefono,
                            estado="esperando_horario",
                            especialidad=medico.especialidad,
                            medico_id=medico.id,
                            fecha_seleccionada=str(
                                fecha_consulta
                            ),
                            horarios=horarios[:5]
                        )

                        return {
                            "respuesta":
                            f"Encontré disponibilidad para {medico.especialidad}. Seleccione un horario.",
                            "fecha":
                            str(fecha_consulta),
                            "horarios":
                            horarios[:5]
                        }

                    return {
                        "respuesta":
                        "No encontré horarios disponibles para las próximas dos semanas."
                    }

        except Exception as e:

            print(
                "ERROR GEMINI:",
                e
            )

            if "citas" in texto.lower():

                citas = (
                    db.query(Cita)
                    .filter(
                        Cita.paciente_id == 1,
                        Cita.estado != "cancelado"
                    )
                    .all
                )

                return{
                    "citas": [
                        {
                            "id": c.id,
                            "fecha": c.fecha_hora.strftyime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "estado": c.estado
                        }

                        for c in citas
                    ]
                }

# =====================================
# CANCELAR CITA
# =====================================


    if (
        sesion and
        sesion.estado == "esperando_cancelacion"
    ):
        
        print ("Entro a cancelacion")
                
        if not texto.isdigit():

            return {
                "respuesta":
                "Ingrese un ID valido."
            }
                
        cita = (
            db.query(Cita)
            .filter(
                Cita.id == int(texto)
            )
            .first()  
        )

        if not cita:
            
            return {
                "respuesta":
                "cita no encontrada."
            }
                
        cita.estado = "cancelada"
                
        db.commit()

        eliminar_sesion(
            db,
            telefono
        )

        return {
            "respuesta":
            f"cita {cita.id} cancelada correctamente."
        }
    
    
    if (
        sesion and
        sesion.estado == "esperando_reagendar_id"
    
    ):
        
        if not texto.isdigit():
            
            return {
                "respuesta":
                "Ingrese un ID válido."
            }
        
        cita = (
            db.query(Cita)
            .filter(
                Cita.id == int(texto)
            )
            .first()
        )
        
        if not cita:
            
            return {
                "respuesta":
                "Cita no encontrada."
            }
        guardar_sesion(
            db,
            telefono,
            estado="esperando_reagendar_fecha",
            especialidad=str(cita.id),
            medico_id=cita.medico_id
        )
        
        return {
            "respuesta":
            "Ingrese la nueva fecha (YYYY-MM-DD)."
        }

    # =====================================
    # PASO 1
    # ESPECIALIDAD
    # =====================================

    if texto.lower() == "quiero una cita":

        especialidades = (
            db.query(Medico.especialidad)
            .distinct()
            .all()
        )

        lista = [
            e[0]
            for e in especialidades
        ]

        print("GUARDANDO SESION CANCELACION")

        guardar_sesion(
            db,
            telefono,
            "esperando_especialidad"
        )

        print("SESION GUARDADA")

        return {
            "especialidades": lista,
            "respuesta":
            "Seleccione una especialidad."
        }

    # =====================================
    # PASO 2
    # USUARIO SELECCIONA ESPECIALIDAD
    # =====================================

    if (
        sesion and
        sesion.estado == "esperando_especialidad"
    ):

        medicos = (
            db.query(Medico)
            .all()
        )

        especialidades = list(
            set(
                [
                    m.especialidad
                    for m in medicos
                ]
            )
        )

        especialidad_seleccionada = None

        if texto.isdigit():

            indice = int(texto) - 1

            if 0 <= indice < len(especialidades):

                especialidad_seleccionada = (
                    especialidades[indice]
                )

        else:

            for esp in especialidades:

                if (
                    normalizar(esp)
                    ==
                    normalizar(texto)
                ):

                    especialidad_seleccionada = esp
                    break

        if not especialidad_seleccionada:

            return {
                "respuesta":
                "Especialidad no encontrada."
            }

        medico = (
            db.query(Medico)
            .filter(
                Medico.especialidad ==
                especialidad_seleccionada
            )
            .first()
        )

        guardar_sesion(
            db,
            telefono,
            estado="esperando_fecha",
            especialidad=especialidad_seleccionada,
            medico_id=medico.id
        )

        return {
            "respuesta":
            "Ingrese la fecha (YYYY-MM-DD) o escriba HOY o MAÑANA."
        }
    
    
    # =====================================
# REAGENDAR - FECHA
# =====================================

    if (
        sesion and
        sesion.estado == "esperando_reagendar_fecha"
    ):
        
        try:
            
            fecha_consulta = datetime.strptime(
                texto,
                "%Y-%m-%d"
            ).date()
            
        except:
            
            return {
                "respuesta":
                "Fecha inválida."
            }
        
        horarios = obtener_horarios_disponibles(
            db,
            sesion.medico_id,
            fecha_consulta
        )
        
        if not horarios:
            
            return {
                "respuesta":
                "No existen horarios disponibles."
            }
        
        guardar_sesion(
            db,
            telefono,
            estado="esperando_reagendar_hora",
            especialidad=sesion.especialidad,
            medico_id=sesion.medico_id,
            fecha_seleccionada=str(fecha_consulta),
            horarios=horarios[:5]
        )

        return {
            "fecha": str(fecha_consulta),
            "horarios": horarios[:5],
            "respuesta":
            "Seleccione un horario."
        }

    # =====================================
    # PASO 3
    # FECHA
    # =====================================

    if (
        sesion and
        sesion.estado == "esperando_fecha"
    ):

        try:

            if normalizar(texto) == "hoy":

                fecha_consulta = date.today()

            elif normalizar(texto) == "manana":

                fecha_consulta = (
                    date.today()
                    + timedelta(days=1)
                )

            else:

                fecha_consulta = datetime.strptime(
                    texto,
                    "%Y-%m-%d"
                ).date()

        except:

            return {
                "respuesta":
                "Fecha inválida. Use YYYY-MM-DD, HOY o MAÑANA."
            }
        
        print("Medico:", sesion.medico_id)
        print("Fecha Inicial:", fecha_consulta)
        
        horarios = []
        
        for _ in range(14):

            horarios = obtener_horarios_disponibles(
            db,
            sesion.medico_id,
            fecha_consulta
        )
            print(
                "Buscando:",
                fecha_consulta,
                horarios
            )
            if horarios:
                break

            fecha_consulta +=  timedelta(days=1)

        print("FECHA FINAL:", fecha_consulta)
        print("HORARIOS PASO 3:", horarios)

        if not horarios:

            return {
                "respuesta":
                "No existen horarios disponibles para las próximas dos semanas."
            }

        guardar_sesion(
            db,
            telefono,
            estado="esperando_horario",
            especialidad=sesion.especialidad,
            medico_id=sesion.medico_id,
            fecha_seleccionada=str(fecha_consulta),
            horarios=horarios[:5]
        )

        return {
            "fecha":
            str(fecha_consulta),
            "horarios":
            horarios[:5],
            "respuesta":
            f"Encontre disponibilidad para el dia {fecha_consulta}. Seleccione un horario."
        }
    
    # =====================================
# REAGENDAR - HORARIO
# =====================================

    if (
        sesion and
        sesion.estado == "esperando_reagendar_hora"
    ):
        
        horarios = (
            sesion.horarios_ofrecidos
            .split(",")
        )
        
        if texto not in horarios:
            
            return {
                "respuesta":
                "Seleccione un horario válido."
            }
        
        cita_id = int(
            sesion.especialidad
        )

        cita = (
            db.query(Cita)
            .filter(
                Cita.id == cita_id
            )
            .first()
        )
        
        nueva_fecha_hora = datetime.strptime(
            f"{sesion.fecha_seleccionada} {texto}",
            "%Y-%m-%d %H:%M"
        )

        cita.fecha_hora = nueva_fecha_hora
        cita.estado = "reagendada"

        db.commit()

        eliminar_sesion(
            db,
            telefono
        )
        
        return {
            "respuesta":
            f"Cita reagendada correctamente para {nueva_fecha_hora.strftime('%Y-%m-%d %H:%M')}"
        }

    # =====================================
    # PASO 4
    # HORARIO
    # =====================================

    if (
        sesion and
        sesion.estado == "esperando_horario"
    ):

        horarios = (
            sesion.horarios_ofrecidos
            .split(",")
        )

        indice = None

        if texto.isdigit():

            pos = int(texto) - 1

            if 0 <= pos < len(horarios):

                indice = pos

        if indice is not None:

            hora = horarios[indice]

        else:

            hora = texto

        if hora not in horarios:

            return {
                "respuesta":
                "Seleccione uno de los horarios mostrados."
            }

        cita = registrar_cita_desde_chat(
            db=db,
            fecha=sesion.fecha_seleccionada,
            hora=hora,
            medico_id=sesion.medico_id,
            paciente_id=1
        )

        eliminar_sesion(
            db,
            telefono
        )

        return {
            "respuesta":
            f"Cita agendada correctamente para {sesion.fecha_seleccionada} a las {hora}"
        }

    return {
        "respuesta":
        "Escriba: quiero una cita"
    }