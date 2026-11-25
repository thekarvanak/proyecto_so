"""Operaciones de creación, consulta y ciclo de vida de procesos."""

from core.proceso import EstadoProceso, Proceso
from utils.visualizacion import mostrar_tabla


class AdministradorProcesos:
    """Mantiene procesos y genera identificadores PID únicos."""

    def __init__(self) -> None:
        self._procesos: dict[int, Proceso] = {}
        self._siguiente_pid = 1

    def crear_proceso(
        self,
        nombre: str,
        tiempo_llegada: int,
        tiempo_cpu: int,
        prioridad: int = 0,
        memoria_requerida: int = 0,
    ) -> Proceso:
        """Valida y registra un proceso con PID automático."""
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del proceso no puede estar vacío.")
        for campo, valor in (
            ("tiempo_llegada", tiempo_llegada),
            ("tiempo_cpu", tiempo_cpu),
            ("prioridad", prioridad),
            ("memoria_requerida", memoria_requerida),
        ):
            if isinstance(valor, bool) or not isinstance(valor, int):
                raise ValueError(f"{campo} debe ser un entero.")
        proceso = Proceso(
            pid=self._siguiente_pid,
            nombre=nombre.strip(),
            tiempo_llegada=tiempo_llegada,
            tiempo_cpu=tiempo_cpu,
            prioridad=prioridad,
            memoria_requerida=memoria_requerida,
        )
        self._procesos[proceso.pid] = proceso
        self._siguiente_pid += 1
        return proceso

    def consultar_todos(self) -> list[Proceso]:
        """Devuelve los procesos ordenados por PID."""
        return [self._procesos[pid] for pid in sorted(self._procesos)]

    def consultar_proceso(self, pid: int) -> Proceso:
        """Devuelve un proceso o informa que el PID no existe."""
        try:
            return self._procesos[pid]
        except KeyError as error:
            raise ValueError(f"No existe un proceso con PID {pid}.") from error

    def cambiar_estado(self, pid: int, estado: EstadoProceso) -> None:
        """Actualiza el estado de un proceso existente."""
        proceso = self.consultar_proceso(pid)
        try:
            proceso.estado = EstadoProceso(estado)
        except ValueError as error:
            raise ValueError(f"Estado de proceso no válido: {estado}.") from error

    def finalizar_proceso(self, pid: int) -> None:
        """Marca un proceso como terminado."""
        self.cambiar_estado(pid, EstadoProceso.TERMINADO)

    def eliminar_proceso(self, pid: int) -> Proceso:
        """Elimina y devuelve un proceso registrado."""
        proceso = self.consultar_proceso(pid)
        del self._procesos[pid]
        return proceso

    def mostrar_procesos(self) -> None:
        """Imprime una tabla con datos y estado de cada proceso."""
        procesos = self.consultar_todos()
        mostrar_tabla(
            ["PID", "Nombre", "Llegada", "CPU", "Prioridad", "Memoria (MB)", "Estado"],
            [
                [
                    p.pid, p.nombre, p.tiempo_llegada, p.tiempo_cpu,
                    p.prioridad, p.memoria_requerida, p.estado.value,
                ]
                for p in procesos
            ],
        )

    def mostrar_procesos_individual(self, pid: int) -> None:
        """Muestra una fila para un proceso solicitado por PID."""
        proceso = self.consultar_proceso(pid)
        mostrar_tabla(
            ["PID", "Nombre", "Llegada", "CPU", "Prioridad", "Memoria (MB)", "Estado"],
            [[
                proceso.pid, proceso.nombre, proceso.tiempo_llegada, proceso.tiempo_cpu,
                proceso.prioridad, proceso.memoria_requerida, proceso.estado.value,
            ]],
        )
