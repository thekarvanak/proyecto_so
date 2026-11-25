"""Presentación en consola sin dependencias externas."""


def mostrar_tabla(encabezados: list[str], filas: list[list[object]]) -> None:
    """Imprime filas tabulares adaptando anchos al contenido."""
    if not encabezados:
        print("(sin columnas)")
        return
    texto = [[str(valor) for valor in fila] for fila in filas]
    columnas = len(encabezados)
    if any(len(fila) != columnas for fila in texto):
        raise ValueError("Cada fila debe tener la misma cantidad de columnas.")
    anchos = [
        max([len(str(encabezados[indice]))] + [len(fila[indice]) for fila in texto])
        for indice in range(columnas)
    ]
    separador = "+-" + "-+-".join("-" * ancho for ancho in anchos) + "-+"
    print(separador)
    print("| " + " | ".join(str(valor).ljust(anchos[i]) for i, valor in enumerate(encabezados)) + " |")
    print(separador)
    for fila in texto:
        print("| " + " | ".join(valor.ljust(anchos[i]) for i, valor in enumerate(fila)) + " |")
    print(separador)


def mostrar_diagrama_gantt(segmentos: list[tuple[str, int, int]]) -> None:
    """Muestra segmentos en orden cronológico e indica los intervalos ociosos."""
    if not segmentos:
        print("(sin ejecuciones)")
        return
    print("Gantt:")
    actual = segmentos[0][1]
    partes = []
    for pid, inicio, fin in segmentos:
        if inicio > actual:
            partes.append(f"[OCIOSO {actual}-{inicio}]")
        nombre = "OCIOSO" if pid == "OCIOSO" else f"P{pid}"
        partes.append(f"[{nombre} {inicio}-{fin}]")
        actual = fin
    print(" ".join(partes))


def mostrar_barra(valor: int, total: int, ancho: int = 30) -> str:
    """Devuelve una barra textual de utilización para una cantidad y total."""
    if total <= 0 or valor < 0 or valor > total:
        raise ValueError("Se requiere 0 <= valor <= total y total positivo.")
    ocupado = round(ancho * valor / total)
    return f"[{'#' * ocupado}{'-' * (ancho - ocupado)}] {valor}/{total} MB"
