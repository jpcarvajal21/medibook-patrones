"""
PATRÓN OBSERVER (de comportamiento)
===================================
Problema A3 del taller: cuando se cancela una cita, el paciente y el médico deben
enterarse. Si la cita llamara directamente a cada aviso, quedaría amarrada a todos.

Solución: la cita es el PUBLICADOR; solo anuncia "la cita cambió".
Los avisos son SUSCRIPTORES: se apuntan a la cita y cada uno reacciona a su manera.
Agregar un interesado nuevo (por ejemplo, el historial) es agregar un suscriptor,
sin tocar el código de la cita.
"""
from abc import ABC, abstractmethod


class Suscriptor(ABC):
    """Interfaz común: todo suscriptor sabe 'actualizarse' cuando la cita le avisa."""

    @abstractmethod
    def actualizar(self, cita, evento: str) -> None:
        ...


class Publicador:
    """Guarda la lista de suscriptores y les avisa a todos. La Cita hereda de esta clase."""

    def __init__(self):
        self._suscriptores = []

    def suscribir(self, suscriptor: Suscriptor) -> None:
        self._suscriptores.append(suscriptor)

    def desuscribir(self, suscriptor: Suscriptor) -> None:
        self._suscriptores.remove(suscriptor)

    def notificar(self, evento: str) -> None:
        # El publicador NO sabe qué hace cada suscriptor; solo les avisa.
        for suscriptor in self._suscriptores:
            suscriptor.actualizar(self, evento)


class BandejaDeAvisos:
    """Simula los envíos de SMS y correo: guarda los mensajes para mostrarlos en pantalla."""

    def __init__(self):
        self.mensajes = []

    def enviar(self, quien: str, destino: str, canal: str, texto: str) -> None:
        self.mensajes.append({"para": quien, "destino": destino, "canal": canal, "texto": texto})

    def limpiar(self) -> None:
        self.mensajes.clear()


class AvisoPaciente(Suscriptor):
    """Suscriptor 1: avisa al paciente por su canal preferido cuando se cancela su cita."""

    def __init__(self, bandeja: BandejaDeAvisos):
        self.bandeja = bandeja

    def actualizar(self, cita, evento: str) -> None:
        if evento != "cancelada":
            return  # al paciente solo le interesa la cancelación
        p = cita.paciente
        destino = p["telefono"] if p["canal"] == "SMS" else p["correo"]
        extra = " Quedó registrada como cambio tardío." if cita.tardia else ""
        self.bandeja.enviar("Paciente", destino, p["canal"],
                            f"Hola {p['nombre']}: su cita {cita.id} del {cita.fecha_texto()} "
                            f"con {cita.medico['nombre']} fue cancelada.{extra}")

class AvisoMedico(Suscriptor):
    """Suscriptor 2: avisa al médico que se liberó un horario de su agenda."""

    def __init__(self, bandeja: BandejaDeAvisos):
        self.bandeja = bandeja

    def actualizar(self, cita, evento: str) -> None:
        if evento != "cancelada":
            return
        m = cita.medico
        self.bandeja.enviar("Médico", m["correo"], "Correo",
                            f"{m['nombre']}: el paciente {cita.paciente['nombre']} canceló la cita "
                            f"{cita.id} del {cita.fecha_texto()}. El horario quedó libre.")


class HistorialCambios(Suscriptor):
    """Suscriptor 3: registra TODOS los cambios de estado (cancelada y atendida).
    Muestra que se puede agregar un interesado nuevo sin modificar la clase Cita."""

    def __init__(self):
        self.registros = []

    def actualizar(self, cita, evento: str) -> None:
        self.registros.append(f"{cita.id}: pasó a {cita.estado.nombre}")
