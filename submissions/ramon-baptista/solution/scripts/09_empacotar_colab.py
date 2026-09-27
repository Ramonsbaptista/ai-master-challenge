from __future__ import annotations

from pathlib import Path, PurePosixPath
import zipfile


SOLUTION = Path(__file__).resolve().parents[1]
REPOSITORY = SOLUTION.parents[2]
REQUESTED_ZIP = Path(r"C:\Users\Ramon\OneDrive\Desktop\projeto-para-colab.zip")
FALLBACK_ZIP = REPOSITORY / "projeto-para-colab.zip"
PREFIX = PurePosixPath("submissions/ramon-baptista/solution")
EXCLUDED_DIRS = {".venv", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_NAMES = {"classification_history.csv"}


def files_to_archive() -> list[Path]:
    return sorted(
        path
        for path in SOLUTION.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_DIRS for part in path.relative_to(SOLUTION).parts)
        and path.name not in EXCLUDED_NAMES
        and path.suffix.lower() != ".pyc"
    )


def write_archive(destination: Path, files: list[Path]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = PurePosixPath(*path.relative_to(SOLUTION).parts)
            archive.write(path, (PREFIX / relative).as_posix())


def verify_archive(destination: Path) -> None:
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        bad = [
            name
            for name in names
            if "\\" in name
            or "/.venv/" in f"/{name}"
            or "/__pycache__/" in f"/{name}"
            or name.endswith(".pyc")
            or name.endswith("/classification_history.csv")
        ]
        assert not bad, f"Entradas proibidas no ZIP: {bad}"
        assert all(name.startswith(PREFIX.as_posix() + "/") for name in names)
        assert archive.testzip() is None


def main() -> None:
    files = files_to_archive()
    destination = REQUESTED_ZIP
    try:
        write_archive(destination, files)
    except (OSError, PermissionError) as error:
        destination = FALLBACK_ZIP
        write_archive(destination, files)
        print(f"Destino solicitado indisponível ({error}); usado o fallback.")
    verify_archive(destination)
    print(destination)
    print(f"Arquivos: {len(files)}")


if __name__ == "__main__":
    main()
