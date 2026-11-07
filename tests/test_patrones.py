"""
Pruebas automáticas del prototipo. Usan los casos de la Etapa 3 de MediBook+.
Ejecutar desde la carpeta del proyecto:  python -m unittest -v
"""
import unittest
from datetime import datetime

from dominio.datos import T0, Sistema
from dominio.estados import AccionNoPermitida
from dominio.observadores import Suscriptor


class PruebasState(unittest.TestCase):
    def setUp(self):
        self.sistema = Sistema()          # datos en su estado inicial (S-05)
        self.cita04 = self.sistema.citas["CIT-04"]   # pendiente, 27/10/2026 10:00

    def test_cp_311_01_cancelar_con_24_h_01_min(self):
        mensaje = self.cita04.cancelar(datetime(2026, 10, 26, 9, 59))
        self.assertEqual(self.cita04.estado.nombre, "Cancelada")
        self.assertFalse(self.cita04.tardia)
        self.assertIn("sin penalización", mensaje)

    def test_cp_311_02_cancelar_con_24_h_exactas(self):
        self.cita04.cancelar(datetime(2026, 10, 26, 10, 0))
        self.assertFalse(self.cita04.tardia)

    def test_cp_311_03_cancelar_con_23_h_59_min(self):
        mensaje = self.cita04.cancelar(datetime(2026, 10, 26, 10, 1))
        self.assertTrue(self.cita04.tardia)
        self.assertIn("cambio tardío", mensaje)

    def test_cp_311_04_no_se_cancela_una_cita_atendida(self):
        cita01 = self.sistema.citas["CIT-01"]
        with self.assertRaises(AccionNoPermitida):
            cita01.cancelar(T0)
        self.assertEqual(cita01.estado.nombre, "Atendida")

    def test_no_se_cancela_dos_veces(self):
        self.cita04.cancelar(T0)
        with self.assertRaises(AccionNoPermitida):
            self.cita04.cancelar(T0)


class PruebasObserver(unittest.TestCase):
    def setUp(self):
        self.sistema = Sistema()

    def test_cancelar_avisa_al_paciente_y_al_medico(self):
        self.sistema.citas["CIT-04"].cancelar(T0)
        para = [m["para"] for m in self.sistema.bandeja.mensajes]
        self.assertEqual(para, ["Paciente", "Médico"])
        # PAC-02 prefiere correo, así que el aviso va a su correo
        self.assertEqual(self.sistema.bandeja.mensajes[0]["destino"], "andres.perez@example.com")

    def test_paciente_con_sms_recibe_por_sms(self):
        self.sistema.citas["CIT-07"].cancelar(T0)
        self.assertEqual(self.sistema.bandeja.mensajes[0]["canal"], "SMS")
        self.assertEqual(self.sistema.bandeja.mensajes[0]["destino"], "3000000003")

    def test_si_state_rechaza_no_hay_avisos(self):
        with self.assertRaises(AccionNoPermitida):
            self.sistema.citas["CIT-01"].cancelar(T0)
        self.assertEqual(self.sistema.bandeja.mensajes, [])

    def test_historial_registra_todos_los_cambios(self):
        self.sistema.citas["CIT-05"].atender()
        self.assertEqual(self.sistema.historial.registros, ["CIT-05: pasó a Atendida"])
        self.assertEqual(self.sistema.bandeja.mensajes, [])   # atender no genera avisos

    def test_agregar_un_suscriptor_nuevo_sin_tocar_la_cita(self):
        class Contador(Suscriptor):
            def __init__(self):
                self.veces = 0

            def actualizar(self, cita, evento):
                self.veces += 1

        contador = Contador()
        cita = self.sistema.citas["CIT-05"]
        cita.suscribir(contador)
        cita.cancelar(T0)
        self.assertEqual(contador.veces, 1)


if __name__ == "__main__":
    unittest.main()
