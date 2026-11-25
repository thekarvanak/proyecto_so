"""Punto de entrada del simulador de sistema operativo."""

import tempfile

from core.administrador_procesos import AdministradorProcesos
from core.comunicacion import ejecutar_productor_consumidor
from core.concurrencia import mostrar_resultado_concurrencia
from core.memoria import AdministradorMemoria
from core.planificador import Planificador
from core.proceso import EstadoProceso
from core.sistema_archivos import AdministradorArchivos
from utils.visualizacion import mostrar_barra, mostrar_tabla


class AplicacionSimulador:
    """Coordina los menús y servicios del simulador."""

    def __init__(self) -> None:
        self.procesos = AdministradorProcesos()
        self.memoria = AdministradorMemoria()
        self.archivos = AdministradorArchivos()

    def ejecutar(self) -> None:
        while True:
            print(
                "\n=== Simulador básico de sistema operativo ===\n"
                "1. Administración de procesos\n"
                "2. Planificación de CPU\n"
                "3. Simulación de concurrencia\n"
                "4. Sincronización de procesos\n"
                "5. Comunicación entre procesos\n"
                "6. Administración de memoria RAM\n"
                "7. Administración de archivos\n"
                "8. Ejecutar demostración integral\n"
                "9. Salir"
            )
            opcion = self._leer_entero("Seleccione una opción: ")
            acciones = {
                1: self._menu_procesos,
                2: self._menu_planificacion,
                3: lambda: self._menu_concurrencia(solo_sin_bloqueo=True),
                4: lambda: self._menu_concurrencia(solo_sin_bloqueo=False),
                5: self._menu_comunicacion,
                6: self._menu_memoria,
                7: self._menu_archivos,
                8: self.demostracion_integral,
            }
            if opcion == 9:
                print("Simulador finalizado.")
                return
            accion = acciones.get(opcion)
            if accion is None:
                print("Opción no válida.")
            else:
                accion()

    def _menu_procesos(self) -> None:
        while True:
            print(
                "\n--- Administración de procesos ---\n"
                "1. Crear proceso\n2. Listar procesos\n3. Consultar proceso\n"
                "4. Finalizar proceso\n5. Eliminar proceso\n6. Regresar"
            )
            opcion = self._leer_entero("Opción: ")
            if opcion == 1:
                nombre = input("Nombre: ").strip()
                llegada = self._leer_entero("Tiempo de llegada: ", 0)
                cpu = self._leer_entero("Tiempo de CPU: ", 1)
                prioridad = self._leer_entero("Prioridad (menor número = más alta): ", 0)
                memoria = self._leer_entero("Memoria requerida (MB): ", 0)
                try:
                    proceso = self.procesos.crear_proceso(nombre, llegada, cpu, prioridad, memoria)
                    print(f"Proceso creado con PID {proceso.pid}.")
                except ValueError as error:
                    print(f"No se pudo crear el proceso: {error}")
            elif opcion == 2:
                self.procesos.mostrar_procesos()
            elif opcion == 3:
                pid = self._leer_entero("PID: ", 1)
                try:
                    self.procesos.mostrar_procesos_individual(pid)
                except ValueError as error:
                    print(error)
            elif opcion == 4:
                self._cambiar_estado_proceso(EstadoProceso.TERMINADO)
            elif opcion == 5:
                pid = self._leer_entero("PID: ", 1)
                try:
                    self.procesos.eliminar_proceso(pid)
                    print(f"Proceso {pid} eliminado.")
                except ValueError as error:
                    print(error)
            elif opcion == 6:
                return
            else:
                print("Opción no válida.")

    def _cambiar_estado_proceso(self, estado: EstadoProceso) -> None:
        pid = self._leer_entero("PID: ", 1)
        try:
            self.procesos.cambiar_estado(pid, estado)
            print(f"Proceso {pid}: estado {estado.value}.")
        except ValueError as error:
            print(error)

    def _menu_planificacion(self) -> None:
        while True:
            print(
                "\n--- Planificación de CPU ---\n"
                "1. Ejecutar FCFS\n2. Ejecutar SJF no expulsivo\n"
                "3. Ejecutar Round Robin\n4. Comparar los tres algoritmos\n5. Regresar"
            )
            opcion = self._leer_entero("Opción: ")
            planificador = Planificador(self.procesos.consultar_todos())
            if opcion == 1:
                planificador.mostrar_resultado(planificador.ejecutar_fcfs())
            elif opcion == 2:
                planificador.mostrar_resultado(planificador.ejecutar_sjf())
            elif opcion in (3, 4):
                quantum = self._leer_entero("Quantum: ", 1)
                resultados = (
                    [planificador.ejecutar_round_robin(quantum)]
                    if opcion == 3
                    else planificador.ejecutar_todos(quantum)
                )
                for resultado in resultados:
                    planificador.mostrar_resultado(resultado)
                if opcion == 4:
                    mostrar_tabla(
                        ["Algoritmo", "Prom. espera", "Prom. retorno", "Makespan"],
                        [
                            [r.algoritmo, f"{r.promedio_espera:.2f}", f"{r.promedio_retorno:.2f}", r.makespan]
                            for r in resultados
                        ],
                    )
            elif opcion == 5:
                return
            else:
                print("Opción no válida.")

    def _menu_concurrencia(self, solo_sin_bloqueo: bool) -> None:
        opciones = (
            [(1, "ninguno", "sin bloqueo")]
            if solo_sin_bloqueo
            else [(1, "lock", "con Lock"), (2, "semaphore", "con Semaphore")]
        )
        while True:
            titulo = "Concurrencia" if solo_sin_bloqueo else "Sincronización"
            print(f"\n--- {titulo} ---")
            for numero, _, etiqueta in opciones:
                print(f"{numero}. Ejecutar {etiqueta}")
            regresar = len(opciones) + 1
            print(f"{regresar}. Regresar")
            opcion = self._leer_entero("Opción: ")
            if opcion == regresar:
                return
            mecanismo = next((clave for numero, clave, _ in opciones if numero == opcion), None)
            if mecanismo is None:
                print("Opción no válida.")
            else:
                mostrar_resultado_concurrencia(mecanismo)

    @staticmethod
    def _menu_comunicacion() -> None:
        while True:
            print("\n--- Comunicación entre procesos ---\n1. Ejecutar productor-consumidor\n2. Regresar")
            opcion = AplicacionSimulador._leer_entero("Opción: ")
            if opcion == 1:
                enviados, recibidos = ejecutar_productor_consumidor()
                print(f"Mensajes enviados: {len(enviados)} | recibidos: {len(recibidos)} | cola final: vacía")
            elif opcion == 2:
                return
            else:
                print("Opción no válida.")

    def _menu_memoria(self) -> None:
        while True:
            print(
                "\n--- Administración de memoria ---\n"
                "1. Consultar memoria\n2. Asignar memoria\n3. Liberar memoria\n"
                "4. Mostrar asignaciones\n5. Regresar"
            )
            opcion = self._leer_entero("Opción: ")
            if opcion == 1:
                self._mostrar_memoria()
            elif opcion == 2:
                pid = self._leer_entero("PID: ", 1)
                cantidad = self._leer_entero("Cantidad (MB): ", 1)
                try:
                    self.memoria.asignar_memoria(pid, cantidad)
                    print(f"Asignados {cantidad} MB al PID {pid}.")
                except (ValueError, MemoryError) as error:
                    print(f"No se pudo asignar memoria: {error}")
            elif opcion == 3:
                pid = self._leer_entero("PID: ", 1)
                try:
                    print(f"Se liberaron {self.memoria.liberar_memoria(pid)} MB del PID {pid}.")
                except ValueError as error:
                    print(error)
            elif opcion == 4:
                mostrar_tabla(
                    ["PID", "Memoria (MB)"],
                    [[pid, cantidad] for pid, cantidad in self.memoria.mostrar_asignaciones().items()],
                )
                self._mostrar_memoria()
            elif opcion == 5:
                return
            else:
                print("Opción no válida.")

    def _mostrar_memoria(self) -> None:
        total, utilizada, disponible = self.memoria.consultar_memoria()
        print(f"Total: {total} MB | Utilizada: {utilizada} MB | Disponible: {disponible} MB")
        print(mostrar_barra(utilizada, total))

    def _menu_archivos(self) -> None:
        while True:
            print(
                "\n--- Administración de archivos ---\n"
                "1. Crear archivo\n2. Listar archivos\n3. Leer archivo\n"
                "4. Modificar archivo\n5. Eliminar archivo\n6. Consultar tamaño\n7. Regresar"
            )
            opcion = self._leer_entero("Opción: ")
            try:
                if opcion == 1:
                    nombre = input("Nombre (ruta relativa): ").strip()
                    contenido = input("Contenido: ")
                    try:
                        self.archivos.crear_archivo(nombre, contenido)
                    except FileExistsError:
                        confirmar = input("Ya existe. ¿Sobrescribir? (s/N): ").strip().lower()
                        if confirmar != "s":
                            print("Operación cancelada.")
                            continue
                        self.archivos.crear_archivo(nombre, contenido, sobrescribir=True)
                    print("Archivo creado.")
                elif opcion == 2:
                    archivos = self.archivos.listar_archivos()
                    for archivo in archivos:
                        print(archivo.relative_to(self.archivos.raiz))
                    if not archivos:
                        print("(no hay archivos)")
                elif opcion == 3:
                    print(self.archivos.leer_archivo(input("Nombre: ").strip()))
                elif opcion == 4:
                    nombre = input("Nombre: ").strip()
                    contenido = input("Nuevo contenido: ")
                    self.archivos.modificar_archivo(nombre, contenido)
                    print("Archivo modificado.")
                elif opcion == 5:
                    nombre = input("Nombre: ").strip()
                    if input(f"¿Eliminar {nombre}? (s/N): ").strip().lower() == "s":
                        self.archivos.eliminar_archivo(nombre)
                        print("Archivo eliminado.")
                    else:
                        print("Operación cancelada.")
                elif opcion == 6:
                    nombre = input("Nombre: ").strip()
                    print(f"Tamaño: {self.archivos.consultar_tamano(nombre)} bytes.")
                elif opcion == 7:
                    return
                else:
                    print("Opción no válida.")
            except (OSError, ValueError) as error:
                print(f"Operación de archivo fallida: {error}")

    def demostracion_integral(self) -> None:
        """Ejecuta un escenario autónomo que integra todos los módulos."""
        print("\n=== Demostración integral ===")
        self.procesos = AdministradorProcesos()
        self.memoria = AdministradorMemoria()
        datos = [
            ("Procesamiento", 0, 5, 2, 256),
            ("Almacenamiento", 1, 3, 1, 128),
            ("Comunicación", 2, 1, 3, 96),
            ("Reportes", 4, 4, 2, 192),
            ("Respaldo", 5, 2, 4, 160),
        ]
        for nombre, llegada, cpu, prioridad, memoria in datos:
            self.procesos.crear_proceso(nombre, llegada, cpu, prioridad, memoria)
        print("\nProcesos iniciales:")
        self.procesos.mostrar_procesos()

        planificador = Planificador(self.procesos.consultar_todos())
        resultados = planificador.ejecutar_todos(quantum=2)
        for resultado in resultados:
            planificador.mostrar_resultado(resultado)
        mostrar_tabla(
            ["Algoritmo", "Prom. espera", "Prom. retorno", "Makespan"],
            [[r.algoritmo, f"{r.promedio_espera:.2f}", f"{r.promedio_retorno:.2f}", r.makespan] for r in resultados],
        )

        print("\nConcurrencia y sincronización:")
        mostrar_resultado_concurrencia("ninguno", iteraciones=2000)
        mostrar_resultado_concurrencia("lock", iteraciones=2000)
        print("\nComunicación:")
        enviados, recibidos = ejecutar_productor_consumidor()

        print("\nMemoria:")
        for proceso in self.procesos.consultar_todos():
            self.memoria.asignar_memoria(proceso.pid, proceso.memoria_requerida)
        self._mostrar_memoria()
        liberado = self.procesos.consultar_todos()[0].pid
        self.memoria.liberar_memoria(liberado)
        print(f"Memoria liberada para PID {liberado}.")
        self._mostrar_memoria()

        print("\nArchivos:")
        with tempfile.TemporaryDirectory(prefix="demostracion_", dir=self.archivos.raiz) as directorio:
            archivos_demo = AdministradorArchivos(directorio)
            ruta_demo = "demostracion_integral.txt"
            archivos_demo.crear_archivo(
                ruta_demo,
                "Archivo creado por la demostración integral del simulador.\n",
            )
            print(f"Contenido: {archivos_demo.leer_archivo(ruta_demo).strip()}")
            print(f"Tamaño: {archivos_demo.consultar_tamano(ruta_demo)} bytes.")
        print(
            "\nResumen: 5 procesos planificados con 3 algoritmos; "
            f"{len(enviados)} mensajes enviados y {len(recibidos)} recibidos; "
            f"{len(self.memoria.mostrar_asignaciones())} asignaciones de memoria activas."
        )

    @staticmethod
    def _leer_entero(mensaje: str, minimo: int | None = None) -> int:
        while True:
            try:
                valor = int(input(mensaje))
                if minimo is not None and valor < minimo:
                    print(f"El valor debe ser al menos {minimo}.")
                    continue
                return valor
            except ValueError:
                print("Ingrese un número entero válido.")


if __name__ == "__main__":
    AplicacionSimulador().ejecutar()
