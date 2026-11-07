"""Datos de prueba sintéticos, tomados de la Etapa 3 (sección 5). Ninguno es real."""
from datetime import datetime

from .cita import Cita
from .estados import ESTADOS
from .observadores import AvisoMedico, AvisoPaciente, BandejaDeAvisos, HistorialCambios

# Reloj de referencia de la Etapa 3: lunes 26/10/2026 08:00 (T0)
T0 = datetime(2026, 10, 26, 8, 0)

PACIENTES = {
    "PAC-02": {"nombre": "Andrés Pérez Mora", "canal": "Correo", "correo": "andres.perez@example.com", "telefono": "3000000002"},
    "PAC-03": {"nombre": "María Torres León", "canal": "SMS", "correo": "maria.torres@example.com", "telefono": "3000000003"},
}
MEDICOS = {
    "MED-01": {"nombre": "Dra. Paula Rincón", "correo": "paula.rincon@example.com"},
    "MED-02": {"nombre": "Dr. Felipe Ortiz", "correo": "felipe.ortiz@example.com"},
}
# (id, paciente, médico, fecha y hora, estado inicial)
CITAS_INICIALES = [
    ("CIT-04", "PAC-02", "MED-01", datetime(2026, 10, 27, 10, 0), "Pendiente"),
    ("CIT-05", "PAC-02", "MED-02", datetime(2026, 10, 29, 15, 0), "Pendiente"),
    ("CIT-07", "PAC-03", "MED-01", datetime(2026, 10, 27, 11, 0), "Pendiente"),
    ("CIT-01", "PAC-03", "MED-01", datetime(2026, 10, 20, 8, 0), "Atendida"),
    ("CIT-02", "PAC-03", "MED-02", datetime(2026, 10, 22, 10, 0), "Cancelada"),
]


class Sistema:
    """Arma las citas con sus suscriptores. Es el único lugar que conoce a todos."""

    def __init__(self):
        self.bandeja = BandejaDeAvisos()
        self.historial = HistorialCambios()
        self.citas = {}
        self.reiniciar()

    def reiniciar(self) -> None:
        """Vuelve los datos al estado inicial (supuesto S-05 de la Etapa 3)."""
        self.bandeja.limpiar()
        self.historial.registros.clear()
        self.citas = {}
        aviso_paciente = AvisoPaciente(self.bandeja)
        aviso_medico = AvisoMedico(self.bandeja)
        for id_cita, pac, med, fecha, estado in CITAS_INICIALES:
            cita = Cita(id_cita, PACIENTES[pac], MEDICOS[med], fecha, ESTADOS[estado]())
            # OBSERVER: aquí se apuntan los suscriptores. La clase Cita no sabe cuáles son.
            cita.suscribir(aviso_paciente)
            cita.suscribir(aviso_medico)
            cita.suscribir(self.historial)
            self.citas[id_cita] = cita
