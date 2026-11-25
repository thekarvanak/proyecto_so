"""Comunicación productor-consumidor mediante queue.Queue."""

from queue import Queue
from threading import Thread


def ejecutar_productor_consumidor(mensajes: list[str] | None = None) -> tuple[list[str], list[str]]:
    """Envía mensajes a un consumidor y finaliza con un centinela seguro."""
    if mensajes is None:
        mensajes = ["Solicitud de procesamiento", "Guardar reporte", "Cerrar conexión"]
    if any(not isinstance(mensaje, str) for mensaje in mensajes):
        raise ValueError("Todos los mensajes deben ser cadenas de texto.")

    cola: Queue[object] = Queue()
    centinela = object()
    recibidos: list[str] = []

    def productor() -> None:
        for mensaje in mensajes:
            print(f"Productor envía: {mensaje}")
            cola.put(mensaje)
        cola.put(centinela)

    def consumidor() -> None:
        while True:
            mensaje = cola.get()
            try:
                if mensaje is centinela:
                    return
                texto = str(mensaje)
                recibidos.append(texto)
                print(f"Consumidor recibe: {texto}")
            finally:
                cola.task_done()

    hilo_consumidor = Thread(target=consumidor, name="Consumidor")
    hilo_productor = Thread(target=productor, name="Productor")
    hilo_consumidor.start()
    hilo_productor.start()
    hilo_productor.join()
    cola.join()
    hilo_consumidor.join()
    return list(mensajes), recibidos
