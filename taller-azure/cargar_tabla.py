"""Punto 4: carga datos a la tabla `sensores` de Azure Table Storage."""
from datetime import datetime, timezone
from getpass import getpass

from azure.data.tables import TableServiceClient

LECTURAS = [
    {"gas": 436, "temperatura": 26.50, "humedad": 42.3, "riesgo": "Medium"},
    {"gas": 465, "temperatura": 26.25, "humedad": 42.0, "riesgo": "Medium"},
    {"gas": 320, "temperatura": 22.25, "humedad": 35.5, "riesgo": "Low"},
]


def crear_entidad(numero, lectura):
    return {
        "PartitionKey": "esp32-sala",       # agrupa las filas (por dispositivo)
        "RowKey": f"lectura-{numero:04d}",  # ID unico dentro de la particion
        "Fecha": datetime.now(timezone.utc).isoformat(),
        **lectura,
    }


def main():
    # getpass no muestra lo que pegas ni lo guarda en ningun archivo
    conexion = getpass("Pega tu connection string (no se ve) y Enter: ").strip()
    servicio = TableServiceClient.from_connection_string(conexion)
    tabla = servicio.create_table_if_not_exists("sensores")

    for numero, lectura in enumerate(LECTURAS, start=1):
        entidad = crear_entidad(numero, lectura)
        tabla.upsert_entity(entidad)  # inserta, o actualiza si ya existe
        print("Subida:", entidad["RowKey"])

    print("\nContenido de la tabla:")
    for e in tabla.list_entities():
        print(e["RowKey"], e["gas"], e["temperatura"], e["humedad"], e["riesgo"])


if __name__ == "__main__":
    main()
