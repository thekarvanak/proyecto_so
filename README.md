# Simulador básico de sistema operativo

Proyecto académico interactivo en Python que representa, de manera experimental, la administración de procesos, planificación de CPU, sincronización, comunicación entre hilos, memoria y archivos. No modifica procesos, memoria ni archivos del sistema operativo real.

## Objetivos

**General:** comprender los mecanismos básicos que un sistema operativo usa para administrar recursos y ejecutar procesos.

**Específicos:**

- Crear, consultar y cambiar el estado de procesos simulados.
- Comparar FCFS, SJF no expulsivo y Round Robin mediante métricas y diagramas de Gantt.
- Observar una condición de carrera y el efecto de Lock y Semaphore.
- Intercambiar mensajes entre productor y consumidor mediante una cola segura.
- Controlar asignaciones de memoria y confinar operaciones de archivos a un directorio de pruebas.

## Requisitos y ejecución

- Python 3.12 o superior.
- No requiere paquetes de terceros.

Desde la carpeta del proyecto:

```powershell
python main.py
```

En Linux o macOS:

```sh
python3 main.py
```

Para ejecutar las pruebas:

```sh
python -m unittest discover -s tests -v
```

El menú principal permite acceder a cada módulo. En la demostración integral se utiliza quantum 2, sin solicitar entradas intermedias. Las operaciones de archivos se limitan a `archivos_prueba/`.

## Estructura

```text
sistema_operativo/
├── main.py
├── README.md
├── core/
│   ├── __init__.py
│   ├── proceso.py
│   ├── administrador_procesos.py
│   ├── planificador.py
│   ├── concurrencia.py
│   ├── comunicacion.py
│   ├── memoria.py
│   └── sistema_archivos.py
├── utils/
│   ├── __init__.py
│   └── visualizacion.py
├── tests/
│   └── test_simulador.py
└── archivos_prueba/
```

## Módulos

- `core/proceso.py`: modelo de proceso, estados y métricas.
- `core/administrador_procesos.py`: asignación automática de PID, consulta, actualización de estado y eliminación.
- `core/planificador.py`: algoritmos de CPU y resultados independientes para cada ejecución.
- `core/concurrencia.py`: dos hilos que incrementan un contador, con y sin sincronización.
- `core/comunicacion.py`: productor-consumidor mediante `queue.Queue` y un centinela para terminar el consumidor.
- `core/memoria.py`: asignación/liberación de memoria protegida con `threading.Lock`.
- `core/sistema_archivos.py`: operaciones con `pathlib`, confinadas a `archivos_prueba/`.
- `utils/visualizacion.py`: tablas, diagrama de Gantt y barra de memoria, sin dependencias externas.
- `main.py`: menú interactivo y escenario integral.

## Planificación de CPU

- **FCFS:** ejecuta procesos en orden de llegada. No es expulsivo. Ante llegadas simultáneas, usa PID como desempate.
- **SJF no expulsivo:** entre los procesos ya llegados elige el de menor ráfaga de CPU; el empate se resuelve por llegada y PID. Cada proceso se ejecuta hasta el final.
- **Round Robin:** distribuye la CPU en intervalos de hasta el quantum indicado. Los procesos que llegan mientras otro se ejecuta se incorporan a la cola al terminar ese intervalo.

Para cada proceso se calcula finalización, retorno (`finalización - llegada`) y espera (`retorno - CPU requerida`). Se muestran los promedios, el makespan (tiempo de finalización máximo desde el instante cero) y los segmentos del diagrama de Gantt, incluidos intervalos ociosos. Los algoritmos operan sobre copias: no alteran los procesos administrados por el menú.

## Concurrencia y sincronización

La opción sin bloqueo separa la lectura y escritura del contador con un cambio de hilo, haciendo visible una posible condición de carrera. `Lock` y `Semaphore(1)` serializan la sección crítica. El sistema operativo real puede planificar hilos de formas diferentes, por lo que la ejecución sin bloqueo ilustra el riesgo y no garantiza un resultado incorrecto en cada plataforma o ejecución.

La cola del productor-consumidor es segura para acceso concurrente. Un objeto centinela indica al consumidor que no habrá más mensajes y evita depender de un tiempo de espera arbitrario.

## Administración de memoria

La capacidad predeterminada es 1024 MB. Se rechazan cantidades inválidas, asignaciones duplicadas por PID y solicitudes que exceden la memoria disponible. Liberar un PID sin asignación produce un error explícito. Las consultas informan memoria total, utilizada y disponible.

## Sistema de archivos

La raíz predeterminada es `archivos_prueba/`. La ruta resultante se resuelve y verifica antes de cada operación para impedir el acceso fuera de esa carpeta. Crear un archivo existente falla por defecto; el menú solicita confirmación explícita antes de sobrescribir. Las pruebas usan directorios temporales aislados.

## Comparación educativa con Linux

Ejecute los comandos manualmente en una terminal Linux; el simulador no los invoca ni ejecuta comandos destructivos:

| Comando | Observación en Linux | Módulo relacionado |
|---|---|---|
| `ps aux` | Lista procesos, propietarios y consumo reportado. | Administración de procesos |
| `top` o `htop` | Observa procesos y utilización dinámica de CPU. | Planificación y procesos |
| `nice -n 5 sleep 30` | Inicia un proceso de prueba con un valor de niceness. | Prioridad y procesos |
| `renice 5 -p <PID>` | Cambia niceness de un proceso existente; use solo un proceso de prueba propio. | Estados/prioridad de procesos |
| `sleep 2` | Mantiene un proceso activo durante un periodo. | Procesos y tiempo de CPU |
| `sleep 30 &` y `jobs` | Inicia y consulta un trabajo en segundo plano de la sesión. | Concurrencia y planificación |
| `kill <PID>` | Envía una señal a un proceso; solo use el PID de su proceso de prueba. | Finalización de procesos |
| `free -h` | Muestra memoria utilizada y disponible. | Administración de memoria |
| `ls -l` | Lista archivos con permisos, propietario y tamaño. | Sistema de archivos |
| `chmod` | Cambia permisos de archivos. | Sistema de archivos (permisos no simulados) |
| `mkdir` y `touch` | Crean un directorio y un archivo vacío. | Sistema de archivos |

El simulador no reproduce el kernel Linux, los estados de proceso reales, políticas de prioridad del kernel, paginación, permisos Unix ni mediciones reales de CPU. Sus modelos son deliberadamente pequeños para hacer visibles los conceptos.

## Pruebas

Las pruebas con `unittest` validan el ciclo de vida de procesos; tiempos de FCFS, SJF y Round Robin, incluidas llegadas tardías; aislamiento entre ejecuciones; memoria y sincronización; mensajes; y operaciones y confinamiento de archivos. No requieren red, bases de datos ni recursos externos.
