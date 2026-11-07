"""
PATRÓN STATE (de comportamiento)
================================
Problema C2 del taller: una cita pasa por estados (Pendiente, Cancelada, Atendida)
y cada estado permite cosas distintas. Sin el patrón, cada acción tendría muchos
"si el estado es... entonces...".

Solución: cada estado es una clase con las MISMAS acciones (cancelar y atender).
La cita no decide nada: le pasa la acción a su estado actual, y el estado decide
si la permite y a qué estado pasa la cita.
"""
from abc import ABC, abstractmethod
from datetime import datetime


class AccionNoPermitida(Exception):
    """Se lanza cuando un estado no permite una acción (por ejemplo, cancelar una cita atendida)."""


class EstadoCita(ABC):
    """Interfaz común de todos los estados. Todos tienen las mismas acciones."""

    nombre = "Sin nombre"

    @abstractmethod
    def cancelar(self, cita, ahora: datetime) -> str:
        """Intenta cancelar la cita. Devuelve un mensaje o lanza AccionNoPermitida."""

    @abstractmethod
    def atender(self, cita) -> str:
        """Intenta marcar la cita como atendida."""


class EstadoPendiente(EstadoCita):
    """La cita todavía no ocurre: se puede cancelar o atender."""

    nombre = "Pendiente"

    def cancelar(self, cita, ahora: datetime) -> str:
        # Regla de US-311 con la redacción corregida de DEF-08:
        # con 24 horas o más de anticipación no hay penalización;
        # con menos de 24 horas se permite, pero queda como "cambio tardío".
        horas_restantes = (cita.fecha_hora - ahora).total_seconds() / 3600
        if horas_restantes < 0:
            raise AccionNoPermitida("La hora de la cita ya pasó; no se puede cancelar.")
        cita.tardia = horas_restantes < 24
        cita.cambiar_estado(EstadoCancelada())          # <- el estado cambia el estado de la cita
        if cita.tardia:
            return "Cita cancelada. Quedó registrada como cambio tardío (faltaban menos de 24 horas)."
        return "Cita cancelada sin penalización (faltaban 24 horas o más)."

    def atender(self, cita) -> str:
        cita.cambiar_estado(EstadoAtendida())
        return "Cita marcada como atendida."


class EstadoCancelada(EstadoCita):
    """La cita ya se canceló: no se puede volver a cancelar ni atender."""

    nombre = "Cancelada"

    def cancelar(self, cita, ahora: datetime) -> str:
        raise AccionNoPermitida("Esta cita ya está cancelada.")

    def atender(self, cita) -> str:
        raise AccionNoPermitida("Una cita cancelada no se puede atender.")


class EstadoAtendida(EstadoCita):
    """La cita ya ocurrió: no se puede cancelar (CP-311-04)."""

    nombre = "Atendida"

    def cancelar(self, cita, ahora: datetime) -> str:
        raise AccionNoPermitida("Una cita atendida no se puede cancelar.")

    def atender(self, cita) -> str:
        raise AccionNoPermitida("Esta cita ya fue atendida.")


# Para crear una cita a partir de un texto ("Pendiente", "Cancelada", "Atendida").
ESTADOS = {e.nombre: e for e in (EstadoPendiente, EstadoCancelada, EstadoAtendida)}
