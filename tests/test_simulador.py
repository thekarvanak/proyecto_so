"""Pruebas unitarias del simulador; los archivos usan directorios temporales."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from core.administrador_procesos import AdministradorProcesos
from core.comunicacion import ejecutar_productor_consumidor
from core.concurrencia import ejecutar_incrementos
from core.memoria import AdministradorMemoria
from core.planificador import Planificador
from core.proceso import EstadoProceso
from core.sistema_archivos import AdministradorArchivos


class PruebasProcesos(unittest.TestCase):
    def setUp(self) -> None:
        self.administrador = AdministradorProcesos()

    def test_crear_consultar_y_validar_proceso(self) -> None:
        proceso = self.administrador.crear_proceso("Editor", 0, 4, 1, 128)
        self.assertEqual(proceso.pid, 1)
        self.assertIs(self.administrador.consultar_proceso(1), proceso)
        self.assertEqual(self.administrador.consultar_todos(), [proceso])
        with self.assertRaises(ValueError):
            self.administrador.crear_proceso(" ", 0, 2)

    def test_finalizar_y_eliminar_proceso(self) -> None:
        proceso = self.administrador.crear_proceso("Worker", 0, 2)
        self.administrador.finalizar_proceso(proceso.pid)
        self.assertEqual(proceso.estado, EstadoProceso.TERMINADO)
        self.assertIs(self.administrador.eliminar_proceso(proceso.pid), proceso)
        with self.assertRaises(ValueError):
            self.administrador.consultar_proceso(proceso.pid)


class PruebasPlanificacion(unittest.TestCase):
    def setUp(self) -> None:
        administrador = AdministradorProcesos()
        administrador.crear_proceso("P1", 0, 5)
        administrador.crear_proceso("P2", 1, 3)
        administrador.crear_proceso("P3", 2, 1)
        self.procesos = administrador.consultar_todos()
        self.planificador = Planificador(self.procesos)

    def test_fcfs_y_metricas(self) -> None:
        resultado = self.planificador.ejecutar_fcfs()
        por_pid = {p.pid: p for p in resultado.procesos}
        self.assertEqual([por_pid[i].tiempo_finalizacion for i in (1, 2, 3)], [5, 8, 9])
        self.assertEqual([por_pid[i].tiempo_retorno for i in (1, 2, 3)], [5, 7, 7])
        self.assertEqual([por_pid[i].tiempo_espera for i in (1, 2, 3)], [0, 4, 6])
        self.assertEqual(resultado.promedio_espera, 10 / 3)
        self.assertEqual(resultado.makespan, 9)

    def test_sjf_no_expulsivo(self) -> None:
        resultado = self.planificador.ejecutar_sjf()
        por_pid = {p.pid: p for p in resultado.procesos}
        self.assertEqual([por_pid[i].tiempo_finalizacion for i in (1, 2, 3)], [5, 9, 6])
        self.assertEqual([por_pid[i].tiempo_espera for i in (1, 2, 3)], [0, 5, 3])

    def test_round_robin(self) -> None:
        resultado = self.planificador.ejecutar_round_robin(2)
        por_pid = {p.pid: p for p in resultado.procesos}
        self.assertEqual([por_pid[i].tiempo_finalizacion for i in (1, 2, 3)], [9, 8, 5])
        self.assertEqual([por_pid[i].tiempo_espera for i in (1, 2, 3)], [4, 4, 2])
        self.assertEqual([p.estado for p in resultado.procesos], [EstadoProceso.TERMINADO] * 3)

    def test_llegadas_tardias_e_intervalo_ocioso(self) -> None:
        administrador = AdministradorProcesos()
        administrador.crear_proceso("Tardio", 5, 2)
        resultado = Planificador(administrador.consultar_todos()).ejecutar_fcfs()
        self.assertEqual(resultado.makespan, 7)
        self.assertEqual(resultado.segmentos[0], ("OCIOSO", 0, 5))
        self.assertEqual(resultado.procesos[0].tiempo_espera, 0)

    def test_algoritmos_no_modifican_procesos_originales(self) -> None:
        original = self.procesos[0]
        self.planificador.ejecutar_todos(2)
        self.assertEqual(original.estado, EstadoProceso.NUEVO)
        self.assertEqual(original.tiempo_restante, original.tiempo_cpu)
        self.assertIsNone(original.tiempo_finalizacion)

    def test_quantum_invalido(self) -> None:
        with self.assertRaises(ValueError):
            self.planificador.ejecutar_round_robin(0)


class PruebasMemoria(unittest.TestCase):
    def test_asignar_liberar_y_rechazar_exceso(self) -> None:
        memoria = AdministradorMemoria(100)
        memoria.asignar_memoria(1, 40)
        self.assertEqual(memoria.consultar_memoria(), (100, 40, 60))
        with self.assertRaises(ValueError):
            memoria.asignar_memoria(1, 10)
        with self.assertRaises(MemoryError):
            memoria.asignar_memoria(2, 61)
        self.assertEqual(memoria.liberar_memoria(1), 40)
        self.assertEqual(memoria.consultar_memoria(), (100, 0, 100))
        with self.assertRaises(ValueError):
            memoria.liberar_memoria(1)


class PruebasConcurrencia(unittest.TestCase):
    def test_lock_y_semaphore_protegen_el_contador(self) -> None:
        for mecanismo in ("lock", "semaphore"):
            with contextlib.redirect_stdout(io.StringIO()):
                esperado, obtenido = ejecutar_incrementos(mecanismo, iteraciones=1000)
            self.assertEqual(obtenido, esperado)

    def test_productor_consumidor_entrega_todos_los_mensajes(self) -> None:
        mensajes = ["uno", "dos", "tres"]
        with contextlib.redirect_stdout(io.StringIO()):
            enviados, recibidos = ejecutar_productor_consumidor(mensajes)
        self.assertEqual(enviados, mensajes)
        self.assertEqual(recibidos, mensajes)


class PruebasArchivos(unittest.TestCase):
    def test_operaciones_y_restricciones_de_ruta(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal) / "archivos_prueba"
            archivos = AdministradorArchivos(raiz)
            archivos.crear_archivo("nota.txt", "hola")
            self.assertEqual(archivos.leer_archivo("nota.txt"), "hola")
            self.assertEqual(archivos.consultar_tamano("nota.txt"), 4)
            with self.assertRaises(FileExistsError):
                archivos.crear_archivo("nota.txt", "no sobrescribir")
            archivos.modificar_archivo("nota.txt", "actualizado")
            self.assertEqual(archivos.leer_archivo("nota.txt"), "actualizado")
            self.assertEqual(len(archivos.listar_archivos()), 1)
            with self.assertRaises(ValueError):
                archivos.crear_archivo("../fuera.txt", "no permitido")
            archivos.eliminar_archivo("nota.txt")
            with self.assertRaises(FileNotFoundError):
                archivos.leer_archivo("nota.txt")


if __name__ == "__main__":
    unittest.main()
