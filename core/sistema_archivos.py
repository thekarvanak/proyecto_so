from pathlib import Path


class AdministradorArchivos:
    """Realiza operaciones seguras bajo un directorio raíz permitido."""

    def __init__(self, directorio_pruebas: str | Path | None = None) -> None:
        raiz = Path(directorio_pruebas) if directorio_pruebas is not None else (
            Path(__file__).resolve().parent.parent / "archivos_prueba"
        )
        raiz.mkdir(parents=True, exist_ok=True)
        self.raiz = raiz.resolve()

    def crear_archivo(self, nombre: str, contenido: str = "", sobrescribir: bool = False) -> Path:
        ruta = self._resolver(nombre)
        if ruta.exists() and not sobrescribir:
            raise FileExistsError(f"El archivo {nombre!r} ya existe; confirme antes de sobrescribir.")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")
        return ruta

    def listar_archivos(self) -> list[Path]:
        """Lista archivos regulares sin seguir enlaces fuera de la raíz."""
        return sorted(
            (ruta for ruta in self.raiz.rglob("*") if ruta.is_file() and self._dentro_de_raiz(ruta)),
            key=lambda ruta: str(ruta.relative_to(self.raiz)).casefold(),
        )

    def leer_archivo(self, nombre: str) -> str:
        ruta = self._resolver_existente(nombre)
        return ruta.read_text(encoding="utf-8")

    def modificar_archivo(self, nombre: str, contenido: str) -> None:
        self._resolver_existente(nombre).write_text(contenido, encoding="utf-8")

    def eliminar_archivo(self, nombre: str) -> None:
        ruta = self._resolver_existente(nombre)
        if not ruta.is_file():
            raise IsADirectoryError(f"{nombre!r} no es un archivo.")
        ruta.unlink()

    def consultar_tamano(self, nombre: str) -> int:
        """Devuelve el tamaño del archivo en bytes."""
        return self._resolver_existente(nombre).stat().st_size

    def _resolver_existente(self, nombre: str) -> Path:
        ruta = self._resolver(nombre)
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe el archivo {nombre!r}.")
        return ruta

    def _resolver(self, nombre: str) -> Path:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Debe indicar un nombre de archivo.")
        ruta = (self.raiz / nombre).resolve()
        if not self._dentro_de_raiz(ruta):
            raise ValueError("La ruta debe permanecer dentro de archivos_prueba/.")
        return ruta

    def _dentro_de_raiz(self, ruta: Path) -> bool:
        try:
            ruta.resolve().relative_to(self.raiz)
            return True
        except ValueError:
            return False
