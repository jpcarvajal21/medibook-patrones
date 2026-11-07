"""
La clase Cita une los dos patrones:
- Para STATE es el "contexto": guarda su estado actual y le pasa las acciones.
- Para OBSERVER es el "publicador": cuando cambia de estado, avisa a sus suscriptores.
"""
from datetime import datetime

from .estados import EstadoCita
from .observadores import Publicador


class Cita(Publicador):
    def __init__(self, id_cita: str, paciente: dict, medico: dict, fecha_hora: datetime, estado: EstadoCita):
        super().__init__()
        self.id = id_cita
        self.paciente = paciente
        self.medico = medico
        self.fecha_hora = fecha_hora
        self.estado = estado          # STATE: el estado actual es un objeto
        self.tardia = False
    #DELEGAN
    # ---------- Acciones: la cita NO decide, le pasa la acción a su estado ----------
    def cancelar(self, ahora: datetime) -> str:
        return self.estado.cancelar(self, ahora)

    def atender(self) -> str:
        return self.estado.atender(self)

    # ---------- Lo llaman los estados cuando la cita debe cambiar ----------
    def cambiar_estado(self, nuevo_estado: EstadoCita) -> None:
        self.estado = nuevo_estado
        # OBSERVER: después de cambiar, la cita solo anuncia el evento.
        self.notificar(nuevo_estado.nombre.lower())

    # ---------- Utilidades ----------
    def fecha_texto(self) -> str:
        return self.fecha_hora.strftime("%d/%m/%Y %H:%M")

    def a_dict(self) -> dict:
        return {
            "id": self.id,
            "paciente": self.paciente["nombre"],
            "canal": self.paciente["canal"],
            "medico": self.medico["nombre"],
            "fecha": self.fecha_texto(),
            "estado": self.estado.nombre,
            "tardia": self.tardia,
        }
