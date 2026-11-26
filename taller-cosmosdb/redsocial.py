"""
RedSocial en Azure Cosmos DB (API NoSQL) con Python.

Qué hace:
  1. Se conecta a tu cuenta de Cosmos DB.
  2. Crea (si no existen) la base de datos "RedSocial" y el contenedor "Mensajes".
  3. Agrega varios mensajes de ejemplo.
  4. Consulta los mensajes por diferentes criterios: usuario, fechas, texto, etc.

Cada mensaje es un documento JSON como este:
  {
    "id": "msg-001",                      <- Id de mensaje
    "idUsuario": "usuario-ana",           <- Id de usuario (también es la clave de partición)
    "fechaHora": "2026-11-20T08:15:00Z",  <- fecha-hora de envío (ISO 8601, UTC)
    "texto": "Hola a todos",
    "url": "https://ejemplo.com/foto1.jpg"
  }

Antes de ejecutarlo, pon tus datos de conexión en variables de entorno
(o el programa te los pide al arrancar):
  COSMOS_URL  -> el "URI" de tu cuenta (Azure Portal > tu cuenta > Claves)
  COSMOS_KEY  -> la "CLAVE PRINCIPAL" de esa misma página

Uso:
  python redsocial.py
"""

import base64
import binascii
import os
from datetime import datetime, timezone
from getpass import getpass

from azure.cosmos import CosmosClient, PartitionKey, exceptions

NOMBRE_BD = "RedSocial"
NOMBRE_CONTENEDOR = "Mensajes"


# ---------------- Conexión ----------------
def clave_valida(clave):
    """La clave de Cosmos es texto en base64 (termina normalmente en '==')."""
    try:
        base64.b64decode(clave, validate=True)
        return len(clave) > 40
    except (binascii.Error, ValueError):
        return False


ARCHIVO_CLAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clave.txt")


def pedir_clave():
    clave = os.environ.get("COSMOS_KEY", "").strip()
    # Opción fácil: pegar la clave en clave.txt (está en .gitignore, no se sube a GitHub).
    if not clave and os.path.exists(ARCHIVO_CLAVE):
        with open(ARCHIVO_CLAVE, encoding="utf-8-sig") as f:
            clave = f.read().strip()
        print("Clave leída de clave.txt")
    while not clave_valida(clave):
        if clave:
            print("Esa no parece una clave válida. Copia SOLO la 'CLAVE PRINCIPAL' "
                  "(Portal > tu cuenta > Configuración > Claves) y pégala otra vez.")
        clave = getpass("Clave principal (no se ve al escribir): ").strip()
    return clave


def conectar():
    """Crea el cliente y deja listos la base de datos y el contenedor."""
    url = os.environ.get("COSMOS_URL") or input("URI de Cosmos DB: ").strip()
    clave = pedir_clave()

    cliente = CosmosClient(url, credential=clave)

    # Si ya existen, solo los abre; si no, los crea.
    base = cliente.create_database_if_not_exists(id=NOMBRE_BD)
    contenedor = base.create_container_if_not_exists(
        id=NOMBRE_CONTENEDOR,
        # Clave de partición: Cosmos agrupa los mensajes de cada usuario juntos,
        # así consultar "los mensajes de un usuario" es rápido y barato.
        partition_key=PartitionKey(path="/idUsuario"),
    )
    print(f"Conectado a la base '{NOMBRE_BD}', contenedor '{NOMBRE_CONTENEDOR}'.\n")
    return contenedor


# ---------------- Crear mensajes ----------------
def crear_mensaje(id_mensaje, id_usuario, fecha_hora, texto, url):
    """Arma un mensaje como diccionario de Python (se guarda como JSON)."""
    return {
        "id": id_mensaje,
        "idUsuario": id_usuario,
        "fechaHora": fecha_hora,
        "texto": texto,
        "url": url,
    }


MENSAJES_DE_EJEMPLO = [
    crear_mensaje("msg-001", "usuario-ana", "2026-11-20T08:15:00Z",
                  "¡Buenos días a todos! Arrancando la semana.", "https://ejemplo.com/ana/cafe.jpg"),
    crear_mensaje("msg-002", "usuario-ana", "2026-11-21T19:40:00Z",
                  "Terminé el proyecto de bases de datos 🎉", "https://ejemplo.com/ana/proyecto"),
    crear_mensaje("msg-003", "usuario-carlos", "2026-11-21T10:05:00Z",
                  "Alguien tiene los apuntes de Azure?", "https://ejemplo.com/carlos/apuntes"),
    crear_mensaje("msg-004", "usuario-carlos", "2026-11-23T14:30:00Z",
                  "Partido de fútbol hoy a las 5", "https://ejemplo.com/carlos/futbol.png"),
    crear_mensaje("msg-005", "usuario-diego", "2026-11-22T22:10:00Z",
                  "Mi carro con ESP32 ya esquiva obstáculos solo", "https://ejemplo.com/diego/carro.mp4"),
    crear_mensaje("msg-006", "usuario-diego", "2026-11-24T09:00:00Z",
                  "Aprendiendo Cosmos DB con Python", "https://ejemplo.com/diego/cosmos"),
    crear_mensaje("msg-007", "usuario-laura", "2026-11-24T16:45:00Z",
                  "Nueva foto del atardecer", "https://ejemplo.com/laura/atardecer.jpg"),
    crear_mensaje("msg-008", "usuario-laura", "2026-11-25T11:20:00Z",
                  "¿Qué es JSON? Pregunta para el parcial", "https://ejemplo.com/laura/json"),
]


def agregar_mensajes(contenedor, mensajes):
    """Guarda los mensajes. upsert = inserta, o reemplaza si ese id ya existe
    (así puedes correr el programa varias veces sin errores de duplicado)."""
    for m in mensajes:
        contenedor.upsert_item(m)
        print(f"  Guardado {m['id']} de {m['idUsuario']}")
    print(f"Listo: {len(mensajes)} mensajes en el contenedor.\n")


def agregar_mensaje_ahora(contenedor, id_usuario, texto, url):
    """Ejemplo de un mensaje nuevo con la fecha-hora actual."""
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    id_mensaje = "msg-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    mensaje = crear_mensaje(id_mensaje, id_usuario, ahora, texto, url)
    contenedor.upsert_item(mensaje)
    return mensaje


# ---------------- Consultas ----------------
def consultar(contenedor, sql, parametros=None):
    """Ejecuta una consulta SQL de Cosmos y devuelve la lista de mensajes.
    Los parámetros (@algo) evitan armar el texto a mano (más seguro)."""
    return list(contenedor.query_items(
        query=sql,
        parameters=parametros or [],
        enable_cross_partition_query=True,   # buscar en todos los usuarios
    ))


def todos(contenedor):
    return consultar(contenedor, "SELECT * FROM c ORDER BY c.fechaHora")


def por_usuario(contenedor, id_usuario):
    return consultar(
        contenedor,
        "SELECT * FROM c WHERE c.idUsuario = @usuario ORDER BY c.fechaHora",
        [{"name": "@usuario", "value": id_usuario}],
    )


def por_rango_de_fechas(contenedor, desde, hasta):
    """Las fechas en formato ISO (2026-11-21T00:00:00Z) se pueden comparar
    como texto: el orden alfabético coincide con el orden en el tiempo."""
    return consultar(
        contenedor,
        "SELECT * FROM c WHERE c.fechaHora >= @desde AND c.fechaHora < @hasta "
        "ORDER BY c.fechaHora",
        [{"name": "@desde", "value": desde}, {"name": "@hasta", "value": hasta}],
    )


def por_dia(contenedor, dia):
    """dia en formato AAAA-MM-DD, por ejemplo 2026-11-21."""
    return consultar(
        contenedor,
        "SELECT * FROM c WHERE STARTSWITH(c.fechaHora, @dia) ORDER BY c.fechaHora",
        [{"name": "@dia", "value": dia}],
    )


def por_usuario_y_fechas(contenedor, id_usuario, desde, hasta):
    return consultar(
        contenedor,
        "SELECT * FROM c WHERE c.idUsuario = @usuario "
        "AND c.fechaHora >= @desde AND c.fechaHora < @hasta ORDER BY c.fechaHora",
        [{"name": "@usuario", "value": id_usuario},
         {"name": "@desde", "value": desde},
         {"name": "@hasta", "value": hasta}],
    )


def por_texto(contenedor, palabra):
    """Mensajes cuyo texto contiene la palabra (sin importar mayúsculas)."""
    return consultar(
        contenedor,
        "SELECT * FROM c WHERE CONTAINS(c.texto, @palabra, true) ORDER BY c.fechaHora",
        [{"name": "@palabra", "value": palabra}],
    )


def contar_por_usuario(contenedor):
    """Cuántos mensajes ha enviado cada usuario.
    (El SDK de Python no soporta GROUP BY entre particiones, así que primero
    se listan los usuarios con DISTINCT y luego se cuenta cada uno.)"""
    usuarios = consultar(contenedor, "SELECT DISTINCT VALUE c.idUsuario FROM c")
    resultado = []
    for u in sorted(usuarios):
        total = consultar(
            contenedor,
            "SELECT VALUE COUNT(1) FROM c WHERE c.idUsuario = @usuario",
            [{"name": "@usuario", "value": u}],
        )[0]
        resultado.append({"idUsuario": u, "total": total})
    return resultado


# ---------------- Mostrar resultados ----------------
def mostrar(titulo, mensajes):
    print(f"=== {titulo} ({len(mensajes)}) ===")
    for m in mensajes:
        if "texto" in m:
            print(f"  [{m['fechaHora']}] {m['idUsuario']}: {m['texto']}  ({m['url']})")
        else:
            print(f"  {m}")
    print()


# ---------------- Programa principal ----------------
def main():
    try:
        contenedor = conectar()

        print("Agregando mensajes de ejemplo...")
        agregar_mensajes(contenedor, MENSAJES_DE_EJEMPLO)

        nuevo = agregar_mensaje_ahora(contenedor, "usuario-diego",
                                      "Mensaje enviado desde Python ahora mismo",
                                      "https://ejemplo.com/diego/python")
        print(f"Mensaje nuevo con la fecha-hora actual: {nuevo['id']} ({nuevo['fechaHora']})\n")

        mostrar("Todos los mensajes", todos(contenedor))
        mostrar("Mensajes de usuario-ana", por_usuario(contenedor, "usuario-ana"))
        mostrar("Mensajes del 21 de noviembre de 2026", por_dia(contenedor, "2026-11-21"))
        mostrar("Mensajes entre el 22 y el 24 de noviembre (sin incluir el 25)",
                por_rango_de_fechas(contenedor, "2026-11-22T00:00:00Z", "2026-11-25T00:00:00Z"))
        mostrar("Mensajes de usuario-carlos desde el 22 de noviembre",
                por_usuario_y_fechas(contenedor, "usuario-carlos",
                                     "2026-11-22T00:00:00Z", "2026-12-01T00:00:00Z"))
        mostrar("Mensajes que mencionan 'azure'", por_texto(contenedor, "azure"))
        mostrar("Cantidad de mensajes por usuario", contar_por_usuario(contenedor))

    except exceptions.CosmosHttpResponseError as e:
        print(f"Error de Cosmos DB ({e.status_code}): {e.message}")
        print("Revisa el URI, la clave y que la cuenta exista en el portal de Azure.")


if __name__ == "__main__":
    main()
