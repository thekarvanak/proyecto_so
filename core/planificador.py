"""Algoritmos FCFS, SJF no expulsivo y Round Robin."""

from collections import deque
from dataclasses import dataclass

from core.proceso import EstadoProceso, Proceso
from utils.visualizacion import mostrar_diagrama_gantt, mostrar_tabla


@dataclass
class ResultadoPlanificacion:
    """Resultado aislado de una ejecución de planificación."""

    algoritmo: str
    procesos: list[Proceso]
    segmentos: list[tuple[str, int, int]]

    @property
    def promedio_espera(self) -> float:
        if not self.procesos:
            return 0.0
        return sum(p.tiempo_espera or 0 for p in self.procesos) / len(self.procesos)

    @property
    def promedio_retorno(self) -> float:
        if not self.procesos:
            return 0.0
        return sum(p.tiempo_retorno or 0 for p in self.procesos) / len(self.procesos)

    @property
    def makespan(self) -> int:
        if not self.procesos:
            return 0
        return max(p.tiempo_finalizacion or 0 for p in self.procesos)

    @property
    def cantidad_procesos(self) -> int:
        return len(self.procesos)


class Planificador:
    """Ejecuta cada algoritmo sobre copias independientes."""

    def __init__(self, procesos: list[Proceso]) -> None:
        self.procesos = procesos

    def ejecutar_fcfs(self) -> ResultadoPlanificacion:
        """Ejecuta FCFS, respetando llegada y tiempo ocioso de CPU."""
        copias = self._copiar_procesos()
        tiempo = 0
        segmentos: list[tuple[str, int, int]] = []
        for proceso in sorted(copias, key=lambda p: (p.tiempo_llegada, p.pid)):
            tiempo = max(tiempo, proceso.tiempo_llegada)
            inicio = tiempo
            fin_previo = segmentos[-1][2] if segmentos else 0
            if inicio > fin_previo:
                segmentos.append(("OCIOSO", fin_previo, inicio))
            tiempo += proceso.tiempo_cpu
            self._completar(proceso, inicio, tiempo)
            segmentos.append((str(proceso.pid), inicio, tiempo))
        return ResultadoPlanificacion("FCFS", copias, segmentos)

    def ejecutar_sjf(self) -> ResultadoPlanificacion:
        """Selecciona el trabajo disponible más corto sin expulsión."""
        copias = self._copiar_procesos()
        pendientes = sorted(copias, key=lambda p: (p.tiempo_llegada, p.pid))
        listos: list[Proceso] = []
        segmentos: list[tuple[str, int, int]] = []
        tiempo = 0
        indice = 0
        while indice < len(pendientes) or listos:
            if not listos and indice < len(pendientes):
                tiempo = max(tiempo, pendientes[indice].tiempo_llegada)
            while indice < len(pendientes) and pendientes[indice].tiempo_llegada <= tiempo:
                listos.append(pendientes[indice])
                indice += 1
            proceso = min(listos, key=lambda p: (p.tiempo_cpu, p.tiempo_llegada, p.pid))
            listos.remove(proceso)
            inicio = tiempo
            fin_previo = segmentos[-1][2] if segmentos else 0
            if inicio > fin_previo:
                segmentos.append(("OCIOSO", fin_previo, inicio))
            tiempo += proceso.tiempo_cpu
            self._completar(proceso, inicio, tiempo)
            segmentos.append((str(proceso.pid), inicio, tiempo))
        return ResultadoPlanificacion("SJF no expulsivo", copias, segmentos)

    def ejecutar_round_robin(self, quantum: int) -> ResultadoPlanificacion:
        """Ejecuta Round Robin incorporando procesos al llegar."""
        if isinstance(quantum, bool) or not isinstance(quantum, int) or quantum <= 0:
            raise ValueError("El quantum debe ser un entero positivo.")
        copias = self._copiar_procesos()
        pendientes = sorted(copias, key=lambda p: (p.tiempo_llegada, p.pid))
        cola: deque[Proceso] = deque()
        segmentos: list[tuple[str, int, int]] = []
        tiempo = 0
        indice = 0
        while indice < len(pendientes) or cola:
            if not cola and indice < len(pendientes):
                tiempo = max(tiempo, pendientes[indice].tiempo_llegada)
            while indice < len(pendientes) and pendientes[indice].tiempo_llegada <= tiempo:
                cola.append(pendientes[indice])
                indice += 1
            proceso = cola.popleft()
            proceso.estado = EstadoProceso.EJECUTANDO
            if proceso.tiempo_inicio is None:
                proceso.tiempo_inicio = tiempo
            inicio = tiempo
            fin_previo = segmentos[-1][2] if segmentos else 0
            if inicio > fin_previo:
                segmentos.append(("OCIOSO", fin_previo, inicio))
            ejecucion = min(quantum, proceso.tiempo_restante or 0)
            tiempo += ejecucion
            proceso.tiempo_restante = (proceso.tiempo_restante or 0) - ejecucion
            segmentos.append((str(proceso.pid), inicio, tiempo))
            while indice < len(pendientes) and pendientes[indice].tiempo_llegada <= tiempo:
                cola.append(pendientes[indice])
                indice += 1
            if proceso.tiempo_restante == 0:
                self._completar(proceso, proceso.tiempo_inicio or inicio, tiempo)
            else:
                proceso.estado = EstadoProceso.LISTO
                cola.append(proceso)
        return ResultadoPlanificacion("Round Robin", copias, segmentos)

    def ejecutar_todos(self, quantum: int) -> list[ResultadoPlanificacion]:
        """Compara los tres algoritmos sin compartir estado mutable."""
        return [
            self.ejecutar_fcfs(),
            self.ejecutar_sjf(),
            self.ejecutar_round_robin(quantum),
        ]

    @staticmethod
    def mostrar_resultado(resultado: ResultadoPlanificacion) -> None:
        """Muestra tabla, estadísticas y Gantt de un algoritmo."""
        print(f"\nResultados: {resultado.algoritmo}")
        mostrar_tabla(
            ["PID", "Nombre", "Llegada", "CPU", "Finalización", "Retorno", "Espera"],
            [
                [
                    p.pid, p.nombre, p.tiempo_llegada, p.tiempo_cpu,
                    p.tiempo_finalizacion, p.tiempo_retorno, p.tiempo_espera,
                ]
                for p in sorted(resultado.procesos, key=lambda p: p.pid)
            ],
        )
        print(
            f"Promedio espera: {resultado.promedio_espera:.2f} | "
            f"promedio retorno: {resultado.promedio_retorno:.2f} | "
            f"makespan: {resultado.makespan} | procesos: {resultado.cantidad_procesos}"
        )
        mostrar_diagrama_gantt(resultado.segmentos)

    def _copiar_procesos(self) -> list[Proceso]:
        copias = []
        for original in self.procesos:
            copia = Proceso(
                pid=original.pid,
                nombre=original.nombre,
                tiempo_llegada=original.tiempo_llegada,
                tiempo_cpu=original.tiempo_cpu,
                prioridad=original.prioridad,
                memoria_requerida=original.memoria_requerida,
            )
            copia.estado = EstadoProceso.LISTO
            copias.append(copia)
        return copias

    @staticmethod
    def _completar(proceso: Proceso, inicio: int, fin: int) -> None:
        proceso.estado = EstadoProceso.TERMINADO
        proceso.tiempo_inicio = inicio
        proceso.tiempo_finalizacion = fin
        proceso.tiempo_restante = 0
        proceso.tiempo_retorno = fin - proceso.tiempo_llegada
        proceso.tiempo_espera = proceso.tiempo_retorno - proceso.tiempo_cpu
