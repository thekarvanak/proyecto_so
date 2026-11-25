"""Representación de un proceso administrado por el simulador."""

from dataclasses import dataclass
from enum import Enum


class EstadoProceso(str, Enum):
    NUEVO = "NUEVO"
    LISTO = "LISTO"
    EJECUTANDO = "EJECUTANDO"
    BLOQUEADO = "BLOQUEADO"
    TERMINADO = "TERMINADO"


@dataclass
class Proceso:
    """Estado y métricas de un proceso simulado."""

    pid: int
    nombre: str
    tiempo_llegada: int
    tiempo_cpu: int
    prioridad: int = 0
    memoria_requerida: int = 0
    estado: EstadoProceso = EstadoProceso.NUEVO
    tiempo_restante: int | None = None
    tiempo_inicio: int | None = None
    tiempo_finalizacion: int | None = None
    tiempo_retorno: int | None = None
    tiempo_espera: int | None = None

    def __post_init__(self) -> None:
        if self.pid <= 0:
            raise ValueError("El PID debe ser un entero positivo.")
        if not self.nombre.strip():
            raise ValueError("El nombre del proceso no puede estar vacío.")
        if self.tiempo_llegada < 0:
            raise ValueError("El tiempo de llegada no puede ser negativo.")
        if self.tiempo_cpu <= 0:
            raise ValueError("El tiempo de CPU debe ser mayor que cero.")
        if self.prioridad < 0:
            raise ValueError("La prioridad no puede ser negativa.")
        if self.memoria_requerida < 0:
            raise ValueError("La memoria requerida no puede ser negativa.")
        if self.tiempo_restante is None:
            self.tiempo_restante = self.tiempo_cpu

    @property
    def tiempo_cpu_requerido(self) -> int:
        """Alias descriptivo del tiempo de CPU original."""
        return self.tiempo_cpu

    def reiniciar(self) -> None:
        """Restaura métricas y estado para una nueva simulación."""
        self.estado = EstadoProceso.NUEVO
        self.tiempo_restante = self.tiempo_cpu
        self.tiempo_inicio = None
        self.tiempo_finalizacion = None
        self.tiempo_retorno = None
        self.tiempo_espera = None
