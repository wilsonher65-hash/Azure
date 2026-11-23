"""Punto 3: sube lo que haya en la carpeta `archivos` al share `multimedia`."""
from getpass import getpass
from pathlib import Path

from azure.core.exceptions import ResourceExistsError
from azure.storage.fileshare import ShareClient

CARPETA_LOCAL = Path(__file__).resolve().parent / "archivos"
TIPOS = {
    "fotos": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"},
    "videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "documentos": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"},
}


def carpeta_para(archivo):
    for carpeta, extensiones in TIPOS.items():
        if archivo.suffix.lower() in extensiones:
            return carpeta
    return None


def main():
    archivos = [a for a in sorted(CARPETA_LOCAL.iterdir()) if a.is_file()]
    if not archivos:
        raise SystemExit(f"Pon primero tus archivos en: {CARPETA_LOCAL}")

    conexion = getpass("Pega tu connection string (no se ve) y Enter: ").strip()
    share = ShareClient.from_connection_string(conexion, share_name="multimedia")

    for carpeta in TIPOS:
        try:
            share.create_directory(carpeta)
        except ResourceExistsError:
            pass  # ya estaba creada

    for archivo in archivos:
        carpeta = carpeta_para(archivo)
        if carpeta is None:
            print("Omitido (tipo no reconocido):", archivo.name)
            continue
        with archivo.open("rb") as datos:
            share.get_file_client(f"{carpeta}/{archivo.name}").upload_file(datos)
        print(f"Subido: {carpeta}/{archivo.name}")


if __name__ == "__main__":
    main()
