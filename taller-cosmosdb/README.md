# RedSocial en Azure Cosmos DB (NoSQL) con Python

Taller: crear una instancia NoSQL de Cosmos DB, una base de datos **RedSocial**
con el contenedor **Mensajes**, y usar **Python** para agregar y consultar mensajes.

## 1. Crear la instancia NoSQL de Cosmos DB (portal de Azure)

1. Entra a <https://portal.azure.com> con tu cuenta de Microsoft Azure
   (si eres estudiante, **Azure for Students** da crédito gratis sin tarjeta).
2. **Crear un recurso** → busca **Azure Cosmos DB** → **Crear**.
3. Escoge **Azure Cosmos DB for NoSQL**.
4. Llena los datos:
   - **Suscripción**: la tuya (por ejemplo, Azure for Students).
   - **Grupo de recursos**: **Crear nuevo** → `rg-redsocial`.
   - **Nombre de la cuenta**: uno único, en minúsculas (ej. `redsocial-tunombre`).
   - **Ubicación**: la más cercana (ej. *East US* o *Brazil South*).
   - **Modo de capacidad**: **Sin servidor (Serverless)**, que es lo más barato para pruebas.
5. **Revisar y crear** → **Crear**. Tarda unos minutos.

## 2 y 3. Base de datos RedSocial y contenedor Mensajes

En la cuenta creada → **Data Explorer** → **New Container**:

| Campo | Valor |
|---|---|
| Database id | **Create new** → `RedSocial` |
| Container id | `Mensajes` |
| Partition key | `/idUsuario` |

> El script `redsocial.py` también los crea solo si no existen
> (`create_database_if_not_exists` y `create_container_if_not_exists`).

## 4. Estructura de un Mensaje

Cada mensaje es un documento JSON:

```json
{
  "id": "msg-001",
  "idUsuario": "usuario-ana",
  "fechaHora": "2026-11-20T08:15:00Z",
  "texto": "¡Buenos días a todos! Arrancando la semana.",
  "url": "https://ejemplo.com/ana/cafe.jpg"
}
```

| Campo | Significado |
|---|---|
| `id` | Id del mensaje (único) |
| `idUsuario` | Id del usuario que lo envió. Es la **clave de partición** |
| `fechaHora` | Fecha-hora de envío en formato ISO 8601 (UTC) |
| `texto` | Contenido del mensaje |
| `url` | Enlace adjunto (foto, video, página) |

La fecha va en **ISO 8601** (`AAAA-MM-DDTHH:MM:SSZ`) porque así se puede
ordenar y comparar como texto: el orden alfabético coincide con el orden en el tiempo.

## 5. Agregar y consultar mensajes con Python

### Datos de conexión
En el portal → tu cuenta de Cosmos DB → **Configuración → Claves**, copia:
- **URI** → variable `COSMOS_URL`
- **CLAVE PRINCIPAL** → variable `COSMOS_KEY`

> ⚠️ La clave es secreta: **no la pongas en el código ni la subas a GitHub**.
> Si no defines las variables, el programa te las pide al arrancar.

### Ejecutar (Windows, PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

$env:COSMOS_URL = "https://TU-CUENTA.documents.azure.com:443/"
$env:COSMOS_KEY = "TU-CLAVE-PRINCIPAL"
python redsocial.py
```

### Qué hace `redsocial.py`
- Agrega **8 mensajes de ejemplo** de 4 usuarios, más uno con la fecha-hora actual.
- Consulta los mensajes por varios criterios:

| Función | Criterio | Consulta (SQL de Cosmos) |
|---|---|---|
| `todos` | Todos, ordenados por fecha | `SELECT * FROM c ORDER BY c.fechaHora` |
| `por_usuario` | Id de usuario | `WHERE c.idUsuario = @usuario` |
| `por_dia` | Un día específico | `WHERE STARTSWITH(c.fechaHora, @dia)` |
| `por_rango_de_fechas` | Entre dos fechas | `WHERE c.fechaHora >= @desde AND c.fechaHora < @hasta` |
| `por_usuario_y_fechas` | Usuario + rango de fechas | combina las dos condiciones |
| `por_texto` | Palabra en el texto | `WHERE CONTAINS(c.texto, @palabra, true)` |
| `contar_por_usuario` | Cuántos mensajes tiene cada usuario | `DISTINCT` + `COUNT(1)` |

Las consultas usan **parámetros** (`@usuario`, `@desde`...) en vez de pegar
el texto a mano, lo que evita errores y ataques de inyección.

## 6. ¿Qué es el formato JSON y por qué es tan útil?

**JSON** (*JavaScript Object Notation*) es un formato de **texto** para guardar e
intercambiar datos estructurados. Usa:
- **objetos** entre llaves `{ }` con pares `"clave": valor`;
- **listas** entre corchetes `[ ]`;
- valores de tipo texto (`"hola"`), número (`42`), booleano (`true`/`false`),
  `null`, u otros objetos y listas anidados.

```json
{
  "idUsuario": "usuario-ana",
  "edad": 21,
  "activa": true,
  "intereses": ["fotografía", "café"],
  "perfil": { "ciudad": "Bogotá", "foto": "https://ejemplo.com/ana.jpg" }
}
```

**¿Por qué es tan útil?**
1. **Lo leen personas y máquinas**: es texto simple y fácil de entender.
2. **Es universal**: casi todos los lenguajes (Python, JavaScript, Java, C#,
   Dart...) lo leen y escriben. En Python, un objeto JSON es simplemente un
   **diccionario** (`dict`).
3. **Es el idioma de la web**: la mayoría de las APIs REST envían y reciben JSON.
4. **Es flexible**: no exige un esquema fijo; un documento puede tener campos
   que otro no tiene, ideal para datos que cambian (como mensajes con o sin foto).
5. **Es ligero**: ocupa menos que formatos como XML.
6. **Es la base de las bases de datos NoSQL de documentos**: Cosmos DB guarda
   cada mensaje directamente como un documento JSON, sin convertirlo a tablas.
