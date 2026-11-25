"""Administrador de memoria RAM con operaciones atómicas bajo Lock."""

from threading import Lock


class AdministradorMemoria:
    """Controla asignaciones de memoria por PID."""

    def __init__(self, capacidad_total: int = 1024) -> None:
        if isinstance(capacidad_total, bool) or not isinstance(capacidad_total, int) or capacidad_total <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")
        self.capacidad_total = capacidad_total
        self._asignaciones: dict[int, int] = {}
        self._lock = Lock()

    @property
    def memoria_utilizada(self) -> int:
        with self._lock:
            return sum(self._asignaciones.values())

    @property
    def memoria_disponible(self) -> int:
        return self.capacidad_total - self.memoria_utilizada

    def validar_disponibilidad(self, cantidad: int) -> bool:
        self._validar_cantidad(cantidad)
        return cantidad <= self.memoria_disponible

    def asignar_memoria(self, pid: int, cantidad: int) -> None:
        """Asigna memoria si hay capacidad y el PID no tiene asignación."""
        self._validar_pid(pid)
        self._validar_cantidad(cantidad)
        with self._lock:
            if pid in self._asignaciones:
                raise ValueError(f"El PID {pid} ya tiene memoria asignada.")
            if cantidad > self.capacidad_total - sum(self._asignaciones.values()):
                raise MemoryError("Memoria insuficiente para realizar la asignación.")
            self._asignaciones[pid] = cantidad

    def liberar_memoria(self, pid: int) -> int:
        """Libera memoria de un PID y devuelve la cantidad liberada."""
        self._validar_pid(pid)
        with self._lock:
            if pid not in self._asignaciones:
                raise ValueError(f"No hay memoria asignada al PID {pid}.")
            return self._asignaciones.pop(pid)

    def mostrar_asignaciones(self) -> dict[int, int]:
        """Devuelve una copia de las asignaciones activas."""
        with self._lock:
            return dict(self._asignaciones)

    def consultar_memoria(self) -> tuple[int, int, int]:
        """Devuelve capacidad, uso y disponibilidad en MB."""
        with self._lock:
            utilizada = sum(self._asignaciones.values())
            disponible = self.capacidad_total - utilizada
        return self.capacidad_total, utilizada, disponible

    @staticmethod
    def _validar_pid(pid: int) -> None:
        if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
            raise ValueError("El PID debe ser un entero positivo.")

    @staticmethod
    def _validar_cantidad(cantidad: int) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("La cantidad de memoria debe ser un entero positivo.")
