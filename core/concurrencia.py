"""Demostraciones prácticas de condición de carrera y sincronización."""

from threading import Barrier, Lock, Semaphore, Thread
from time import sleep


def ejecutar_incrementos(mecanismo: str = "ninguno", iteraciones: int = 5000) -> tuple[int, int]:
    """Ejecuta dos trabajadores y devuelve (esperado, obtenido)."""
    if mecanismo not in {"ninguno", "lock", "semaphore"}:
        raise ValueError("El mecanismo debe ser ninguno, lock o semaphore.")
    if isinstance(iteraciones, bool) or not isinstance(iteraciones, int) or iteraciones <= 0:
        raise ValueError("Las iteraciones deben ser un entero positivo.")

    contador = [0]
    barrera = Barrier(2)
    bloqueo = Lock() if mecanismo == "lock" else None
    semaforo = Semaphore(1) if mecanismo == "semaphore" else None

    def trabajador(numero: int) -> None:
        print(f"Hilo {numero}: listo para iniciar.")
        barrera.wait()
        for indice in range(iteraciones):
            if bloqueo is not None:
                with bloqueo:
                    if indice == 0:
                        print(f"Hilo {numero}: ingresa a la sección crítica (Lock).")
                    contador[0] += 1
                    if indice == 0:
                        print(f"Hilo {numero}: sale de la sección crítica (Lock).")
            elif semaforo is not None:
                with semaforo:
                    if indice == 0:
                        print(f"Hilo {numero}: ingresa a la sección crítica (Semaphore).")
                    contador[0] += 1
                    if indice == 0:
                        print(f"Hilo {numero}: sale de la sección crítica (Semaphore).")
            else:
                anterior = contador[0]
                if indice == 0:
                    print(f"Hilo {numero}: ingresa a la sección crítica sin bloqueo.")
                sleep(0)
                contador[0] = anterior + 1
                if indice == 0:
                    print(f"Hilo {numero}: sale de la sección crítica sin bloqueo.")
        print(f"Hilo {numero}: terminó.")

    hilos = [Thread(target=trabajador, args=(numero,), name=f"Trabajador-{numero}") for numero in (1, 2)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    esperado = iteraciones * len(hilos)
    return esperado, contador[0]


def mostrar_resultado_concurrencia(mecanismo: str, iteraciones: int = 5000) -> tuple[int, int]:
    """Imprime los valores de referencia y el resultado medido."""
    esperado, obtenido = ejecutar_incrementos(mecanismo, iteraciones)
    print(f"Mecanismo: {mecanismo}; resultado esperado: {esperado}; obtenido: {obtenido}")
    return esperado, obtenido
