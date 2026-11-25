# Informe del proyecto: Simulador básico de sistema operativo

> **Proyecto académico:** simulación didáctica de mecanismos de un sistema operativo  
> **Estudiante:** ______________________________________________  
> **Curso / grupo:** ___________________________________________  
> **Docente:** ________________________________________________  
> **Institución:** _____________________________________________  
> **Fecha de entrega:** ________________________________________

## Resumen ejecutivo

Este proyecto implementa en Python un simulador de consola para explorar la administración de procesos, la planificación de CPU, la concurrencia, la sincronización, la comunicación entre hilos, la memoria y las operaciones de archivos. Presenta tres algoritmos de planificación (FCFS, SJF no expulsivo y Round Robin), resultados tabulares y diagramas de Gantt. También incluye un menú integrado, una demostración automática y pruebas unitarias con `unittest`.

El simulador es un modelo educativo: no administra procesos ni memoria reales del sistema operativo y no ejecuta comandos Linux.

---

# 1. Documento de diseño

## 1.1 Problema

Un sistema operativo administra procesos y distribuye recursos limitados, como CPU y memoria. Estos mecanismos suelen ser difíciles de observar de forma aislada: los tiempos de ejecución, la concurrencia y el acceso a recursos compartidos hacen que el comportamiento real varíe.

El proyecto aborda este problema mediante un simulador pequeño e interactivo que permite crear procesos de prueba, aplicar distintas políticas de planificación y observar resultados controlados sin modificar recursos reales del computador.

## 1.2 Objetivos

### Objetivo general

Comprender y demostrar, mediante un programa de consola en Python, mecanismos básicos de administración de recursos de un sistema operativo.

### Objetivos específicos

- Representar procesos con identificadores, estados, tiempos de CPU, llegada, prioridad y memoria requerida.
- Implementar FCFS, SJF no expulsivo y Round Robin y calcular sus métricas.
- Comparar algoritmos con tablas y diagramas de Gantt.
- Demostrar una posible condición de carrera y el efecto de `Lock` y `Semaphore`.
- Comunicar hilos mediante el patrón productor-consumidor con `queue.Queue`.
- Simular asignación y liberación de memoria RAM.
- Administrar archivos únicamente dentro de `archivos_prueba/`.
- Probar las funciones principales con pruebas automatizadas.

## 1.3 Alcance y restricciones

- Python 3.12 o superior; solo biblioteca estándar.
- Interfaz de terminal; no utiliza frameworks, bases de datos ni servicios externos.
- Los algoritmos trabajan sobre copias de procesos para mantener independientes los resultados.
- Los archivos están confinados a la carpeta de pruebas del simulador.
- La condición de carrera es ilustrativa: el resultado sin sincronización puede variar según la plataforma y la ejecución.
- No se simulan las políticas internas completas de un kernel, la paginación, los permisos reales ni el uso real de CPU.

## 1.4 Arquitectura y descripción de módulos

La aplicación separa la lógica de dominio (`core`), la presentación de consola (`utils`), las pruebas (`tests`) y el punto de entrada (`main.py`).

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Menú principal, submenús, validación de entradas e integración de módulos. |
| `core/proceso.py` | Modelo `Proceso`, estados y reinicio de métricas. |
| `core/administrador_procesos.py` | Creación con PID automático, consulta, cambio de estado, finalización, eliminación y listado. |
| `core/planificador.py` | FCFS, SJF no expulsivo, Round Robin, copias independientes y métricas de planificación. |
| `core/concurrencia.py` | Dos hilos que incrementan un contador sin bloqueo, con `Lock` o con `Semaphore`. |
| `core/comunicacion.py` | Productor-consumidor con `queue.Queue` y centinela de finalización. |
| `core/memoria.py` | Asignación y liberación de memoria, consultas y protección mediante `Lock`. |
| `core/sistema_archivos.py` | Crear, listar, leer, modificar, eliminar y consultar tamaño dentro del directorio permitido. |
| `utils/visualizacion.py` | Tablas ASCII, diagramas de Gantt y barra de uso de memoria. |
| `tests/test_simulador.py` | Pruebas unitarias de procesos, planificación, concurrencia, memoria, comunicación y archivos. |

---

# 2. Diagramas y algoritmos

## 2.1 Diagrama modular

```text
                         +----------------------+
                         |       main.py        |
                         | Menú e integración   |
                         +----------+-----------+
                                    |
                +-------------------+-------------------+
                |                   |                   |
        +-------v--------+  +-------v--------+  +-------v--------+
        | Administrador  |  | Planificador   |  | Memoria /      |
        | de procesos    |  | FCFS, SJF, RR  |  | archivos       |
        +-------+--------+  +-------+--------+  +-------+--------+
                |                   |                   |
                +-------------------+-------------------+
                                    |
                         +----------v-----------+
                         |     Proceso          |
                         | modelo y métricas    |
                         +----------------------+

       +------------------+  +-------------------+  +------------------+
       | Concurrencia     |  | Comunicación     |  | Visualización    |
       | Lock/Semaphore   |  | queue.Queue      |  | tablas y Gantt   |
       +------------------+  +-------------------+  +------------------+
                                    ^
                                    |
                         +----------+-----------+
                         | tests/test_simulador |
                         +----------------------+
```

## 2.2 Métricas utilizadas

- **Finalización:** instante en que termina el proceso.
- **Retorno:** `tiempo_finalizacion - tiempo_llegada`.
- **Espera:** `tiempo_retorno - tiempo_cpu`.
- **Promedio de espera / retorno:** promedio de cada métrica para los procesos simulados.
- **Makespan:** instante de finalización máximo medido desde el tiempo cero.

## 2.3 FCFS (First Come, First Served)

**Idea:** atender en orden de llegada. No es expulsivo. Los empates de llegada se resuelven por PID. Si la CPU está ociosa, el reloj avanza hasta la siguiente llegada.

```text
FCFS(procesos):
    ordenar procesos por (llegada, PID)
    reloj = 0
    para cada proceso:
        reloj = max(reloj, llegada del proceso)
        inicio = reloj
        reloj = reloj + CPU_requerida
        calcular finalización, retorno y espera
    devolver resultados y segmentos Gantt
```

## 2.4 SJF no expulsivo (Shortest Job First)

**Idea:** elegir el proceso disponible con menor ráfaga de CPU. En empate, se compara llegada y después PID. Una vez iniciado, el proceso continúa hasta terminar.

```text
SJF(procesos):
    ordenar pendientes por (llegada, PID)
    reloj = 0
    mientras existan pendientes o procesos listos:
        si no hay listos:
            avanzar reloj a la siguiente llegada
        agregar a listos los procesos cuya llegada <= reloj
        elegir el listo con menor (CPU_requerida, llegada, PID)
        ejecutar hasta terminar
        calcular finalización, retorno y espera
    devolver resultados y segmentos Gantt
```

## 2.5 Round Robin

**Idea:** entregar a cada proceso hasta un quantum de CPU. Si no termina, vuelve al final de la cola. Las nuevas llegadas se agregan a la cola al terminar el intervalo actual.

```text
ROUND_ROBIN(procesos, quantum):
    validar quantum > 0
    ordenar pendientes por (llegada, PID)
    reloj = 0; cola = vacía
    mientras existan pendientes o procesos en cola:
        si cola está vacía:
            avanzar reloj a la siguiente llegada
        agregar a la cola los procesos ya llegados
        proceso = retirar primero de la cola
        ejecutar min(quantum, tiempo_restante)
        actualizar reloj y tiempo_restante
        agregar a la cola los procesos que llegaron durante el intervalo
        si el proceso terminó:
            calcular finalización, retorno y espera
        si no terminó:
            agregarlo al final de la cola
    devolver resultados y segmentos Gantt
```

## 2.6 Flujo de datos de una planificación

```text
[Procesos creados]
        |
        v
[Copiar procesos de entrada]
        |
        v
[Elegir FCFS / SJF / Round Robin]
        |
        v
[Ejecutar atendiendo llegadas y CPU ociosa]
        |
        v
[Calcular finalización, retorno y espera]
        |
        v
[Mostrar tabla, promedios, makespan y Gantt]
```

---

# 3. Código fuente

## 3.1 Estructura de archivos Python

```text
proyeto_SO/
├── main.py
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

Los archivos se encuentran en la carpeta del proyecto. Las clases y funciones principales incluyen docstrings; los algoritmos y los puntos relevantes de sincronización están organizados para poder explicarse y probarse por separado.

## 3.2 Ejecución

Requisito: Python 3.12 o superior. No se requiere instalar paquetes de terceros.

Desde una terminal abierta en la raíz del proyecto:

```sh
python main.py
```

En algunos sistemas Linux, use:

```sh
python3 main.py
```

Para ejecutar las pruebas:

```sh
python -m unittest discover -s tests -v
```

**Versión de Python utilizada para la verificación de este proyecto:** Python 3.14.2  
**Versión disponible en el equipo de sustentación:** __________________________

---

# 4. Simulador: menú integrado y funcionalidades

## 4.1 Menú principal

1. Administración de procesos.
2. Planificación de CPU.
3. Simulación de concurrencia sin bloqueo.
4. Sincronización con `Lock` o `Semaphore`.
5. Comunicación productor-consumidor.
6. Administración de memoria RAM.
7. Administración de archivos.
8. Demostración integral.
9. Salir.

## 4.2 Funcionalidades mínimas operativas

- **Procesos:** crear con PID automático, listar, consultar, finalizar y eliminar.
- **Planificación:** ejecutar FCFS, SJF y Round Robin, o comparar los tres; muestra métricas y Gantt.
- **Concurrencia:** dos hilos actualizan un contador compartido; se muestra resultado esperado y obtenido.
- **Sincronización:** se puede observar el efecto de `Lock` y `Semaphore(1)`.
- **Comunicación:** productor y consumidor intercambian mensajes y terminan mediante un centinela.
- **Memoria:** asignar, consultar y liberar memoria; rechaza duplicados y falta de capacidad.
- **Archivos:** crear, listar, leer, modificar, eliminar y consultar tamaño; el menú solicita confirmación antes de sobrescribir.
- **Demostración integral:** crea cinco procesos, ejecuta los algoritmos, demuestra concurrencia y comunicación, asigna/libera memoria y crea/lee un archivo temporal de demostración.

## 4.3 Evidencia del simulador

**Captura del menú principal**

  
  
  

**Captura de la planificación y el diagrama de Gantt**

  
  
  

**Captura de la demostración integral**

  
  
  

---

# 5. Evidencias Linux

> **Completar en una terminal Linux.** Inserte aquí las capturas obtenidas en su equipo. Use procesos de prueba propios y finalícelos manualmente cuando termine. No ejecute estos comandos desde el simulador.

## 5.1 Procesos y planificación

Comandos de referencia:

```sh
ps aux
top
sleep 30 &
jobs
```

**Qué observé:**  
  
  

**Captura:**  
  
  
  

## 5.2 Prioridad y finalización de un proceso de prueba

Comandos de referencia; utilice el PID de su propio proceso de prueba:

```sh
nice -n 5 sleep 30
renice 5 -p <PID_DE_PRUEBA>
kill <PID_DE_PRUEBA>
```

**Qué observé:**  
  
  

**Captura:**  
  
  
  

## 5.3 Memoria

```sh
free -h
```

**Qué observé:**  
  
  

**Captura:**  
  
  
  

## 5.4 Archivos y permisos

Para evitar modificar archivos personales, realice la práctica en una carpeta creada para este ejercicio:

```sh
mkdir -p practica_simulador
cd practica_simulador
touch ejemplo.txt
ls -l
chmod 600 ejemplo.txt
ls -l
```

**Qué observé:**  
  
  

**Captura:**  
  
  
  

---

# 6. Comparación: simulación y Linux real

| Tema | Simulador | Linux real | Diferencia / limitación |
|---|---|---|---|
| Procesos | Objetos `Proceso` con PID interno y estados simulados. | Procesos del kernel observables con `ps aux`. | Los PID del simulador no son PID del sistema. |
| Planificación CPU | Implementa FCFS, SJF no expulsivo y Round Robin con tiempos discretos. | El kernel usa sus propias políticas, prioridades y mecanismos de planificación. | Los algoritmos del simulador no cambian la política del kernel. |
| CPU y tiempo | Ráfagas y llegadas son valores de entrada del modelo. | `top` muestra actividad y uso real, variables según carga y hardware. | El simulador no mide ciclos ni uso real de CPU. |
| Prioridad | El proceso almacena un valor de prioridad informativo. | `nice` y `renice` interactúan con la prioridad/niceness de procesos reales. | La prioridad del simulador no afecta al scheduler de Linux. |
| Concurrencia | Hilos Python incrementan un contador compartido. | El kernel planifica hilos reales y su ejecución depende del entorno. | El resultado de la carrera simulada no es idéntico en todas las ejecuciones. |
| Sincronización | `threading.Lock` y `threading.Semaphore` protegen la sección crítica del ejemplo. | Los programas usan primitivas de sincronización reales ofrecidas por el sistema/runtime. | El ejercicio solo demuestra una sección crítica sencilla. |
| Memoria | Un total configurable y asignaciones contables en MB. | `free -h` informa memoria del sistema y su uso real. | No hay memoria física reservada, paginación ni aislamiento por proceso. |
| Archivos | Operaciones confinadas a `archivos_prueba/`. | `ls -l`, `touch`, `mkdir` y `chmod` operan en el sistema de archivos real. | El simulador no reproduce propietarios ni permisos Unix. |
| Terminación | Cambia el estado de un objeto o lo elimina del registro. | `kill` envía señales a un proceso del sistema. | Finalizar en el simulador no envía señales al sistema operativo. |

---

# 7. Informe final

## 7.1 Pruebas realizadas

Se ejecutaron pruebas automatizadas con `unittest` para validar:

- Creación, consulta, finalización y eliminación de procesos.
- Resultados y métricas de FCFS, SJF y Round Robin.
- Llegadas tardías, intervalos ociosos y quantum inválido.
- Independencia de las copias usadas por los algoritmos.
- Asignación, liberación y rechazo por memoria insuficiente.
- Sincronización correcta mediante `Lock` y `Semaphore`.
- Entrega de mensajes entre productor y consumidor.
- Operaciones de archivos, rechazo de rutas externas y protección contra sobrescritura accidental.

**Resultado registrado:** 12 pruebas ejecutadas; todas aprobadas.  
**Comando:** `python -m unittest discover -s tests -v`

También se verificó la salida del menú, el flujo interactivo de sus opciones y la demostración integral.

## 7.2 Resultados de la demostración de planificación

Escenario de cinco procesos y quantum 2. Los promedios son unidades de tiempo del modelo, no mediciones del computador:

| Algoritmo | Promedio de espera | Promedio de retorno | Makespan |
|---|---:|---:|---:|
| FCFS | 4.60 | 7.60 | 15 |
| SJF no expulsivo | 3.60 | 6.60 | 15 |
| Round Robin (quantum 2) | 5.60 | 8.60 | 15 |

En este escenario, SJF obtiene el menor promedio de espera. El resultado depende del conjunto concreto de procesos; no implica que SJF siempre sea el mejor algoritmo para cualquier carga.

## 7.3 Dificultades encontradas

**Completar con las dificultades propias durante la ejecución, pruebas o comparación:**

1. ______________________________________________________________
2. ______________________________________________________________
3. ______________________________________________________________

## 7.4 Conclusiones

El simulador permite comparar políticas de planificación con métricas calculadas sobre procesos controlados. La separación de módulos facilita probar la administración de procesos, sincronización, comunicación, memoria y archivos de manera independiente. La demostración también evidencia que proteger una sección crítica evita la pérdida de actualizaciones en el ejemplo concurrente.

La comparación con Linux debe interpretarse de forma cualitativa: el proyecto representa conceptos de sistema operativo, pero no reemplaza ni modifica los servicios del kernel.

**Conclusiones personales del estudiante:**

  
  
  

---

# 8. Sustentación

## 8.1 Guion sugerido para la demostración

1. Ejecutar `python main.py` y mostrar el menú.
2. Crear un proceso y explicar PID, llegada, ráfaga, estado, prioridad y memoria requerida.
3. Ejecutar FCFS, SJF y Round Robin; describir el Gantt y comparar espera, retorno y makespan.
4. Explicar por qué cada algoritmo recibe copias independientes de los procesos.
5. Ejecutar la prueba de concurrencia sin bloqueo y luego con `Lock` o `Semaphore`.
6. Mostrar el productor-consumidor y explicar la cola y el centinela de terminación.
7. Asignar y liberar memoria; explicar las validaciones.
8. Crear, leer y eliminar un archivo de prueba; explicar cómo se restringe la ruta.
9. Ejecutar la demostración integral y comentar sus resultados.
10. Mostrar las pruebas automatizadas y explicar qué verifican.

## 8.2 Preguntas de repaso

**¿Qué diferencia a FCFS de SJF?**  
FCFS atiende según llegada. SJF elige el proceso disponible con menor ráfaga de CPU y no lo expulsa una vez iniciado.

**¿Qué hace Round Robin con el quantum?**  
Limita cuánto tiempo seguido recibe CPU cada proceso. Si queda trabajo pendiente, el proceso vuelve al final de la cola.

**¿Cómo se calculan espera y retorno?**  
Retorno = finalización − llegada. Espera = retorno − tiempo de CPU requerido.

**¿Por qué ejecutar los algoritmos sobre copias?**  
Para evitar que las métricas y estados de una ejecución alteren las entradas de la siguiente comparación.

**¿Qué es una condición de carrera?**  
Es un resultado dependiente del orden de ejecución cuando varios hilos leen y actualizan estado compartido sin sincronización adecuada.

**¿Qué protegen `Lock` y `Semaphore(1)` en el ejemplo?**  
Evitan que los dos hilos entren simultáneamente a la sección crítica que actualiza el contador.

**¿Cómo se detiene el consumidor de forma segura?**  
El productor inserta un objeto centinela en la cola después de los mensajes; al recibirlo, el consumidor termina.

**¿Qué impide que el administrador de archivos acceda fuera del directorio de pruebas?**  
Resuelve la ruta objetivo y comprueba que permanezca dentro de la raíz permitida antes de efectuar la operación.

**¿En qué se diferencia este simulador de un sistema operativo real?**  
Los recursos y procesos son datos del modelo. El programa no planifica procesos del kernel ni reserva memoria física ni cambia prioridades reales.

## 8.3 Respuestas individuales

**Pregunta adicional del docente:**  
  

**Respuesta del estudiante:**  
  
  

**Pregunta adicional del docente:**  
  

**Respuesta del estudiante:**  
  
  

## 8.4 Evidencia de sustentación

**Fecha / modalidad:** __________________________________________

**Observaciones del docente:**  
  
  

**Captura o evidencia de la presentación:**  
  
  
  

---

## Checklist de entrega

- [ ] Completar los datos de identificación.
- [ ] Ejecutar el simulador y capturar el menú y la demostración.
- [ ] Realizar las prácticas Linux y añadir las capturas.
- [ ] Completar observaciones, dificultades y conclusiones personales.
- [ ] Preparar respuestas individuales para la sustentación.
- [ ] Adjuntar la carpeta del proyecto con sus archivos `.py`, pruebas y README.
