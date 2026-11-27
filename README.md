# Curso de Azure

Actividades del curso de Azure, hechas con una cuenta **Azure for Students**.

| # | Actividad | Servicio de Azure | Dónde está |
|---|---|---|---|
| 1 | Calculadora de interés simple publicada en la web | **Static Web Apps** | [`index.html`](index.html) |
| 2 | Blobs, archivos, tablas y colas | **Storage** (cuenta de almacenamiento) | [`taller-azure/`](taller-azure/) |
| 3 | Base de datos **RedSocial** con mensajes | **Cosmos DB** (NoSQL) | [`taller-cosmosdb/`](taller-cosmosdb/) |
<img width="1913" height="957" alt="image" src="https://github.com/user-attachments/assets/9d1bddb6-30a1-4b0b-8206-4de09542af5f" />


<img width="1916" height="954" alt="image" src="https://github.com/user-attachments/assets/d28f0789-569a-4768-8d35-b0ecd880da9d" />


---

## 1. Calculadora de interés simple (Azure Static Web Apps)

🔗 **Sitio publicado:** <https://happy-flower-03b92d01e.6.azurestaticapps.net>

Página web (HTML, CSS y JavaScript en un solo archivo, [`index.html`](index.html))
que calcula el **interés simple**:

- **I = C × i × t**: interés = capital × tasa (en decimal) × tiempo en años
- **M = C + I**: monto final

El tiempo se puede escribir en años, meses (÷ 12) o días (÷ 360, año comercial).
Si algún campo está vacío o es negativo, muestra un mensaje de error.

**Cómo se publica:** el Static Web App de Azure está conectado a este repositorio.
Azure creó el archivo
[`.github/workflows/azure-static-web-apps-happy-flower-03b92d01e.yml`](.github/workflows/),
que es un flujo de **GitHub Actions**: cada vez que se hace *push* a `main`,
GitHub sube `index.html` a Azure y el sitio se actualiza solo (CI/CD).

## 2. Azure Storage

Cuenta `wilsonstorage2026` con un contenedor de blobs, un recurso compartido de
archivos con carpetas (Fotos, Videos, Documentos), una tabla `sensores` cargada
con Python y la explicación del almacenamiento de colas.
👉 Detalle y capturas en [`taller-azure/README.md`](taller-azure/README.md).

## 3. Azure Cosmos DB: RedSocial

Cuenta `redsocial-taller2026` (NoSQL, nivel gratis), base `RedSocial` y contenedor
`Mensajes`. Un programa en Python agrega mensajes y los consulta por usuario,
fecha, rango de fechas y texto. Incluye la explicación de qué es JSON.
👉 Detalle y capturas en [`taller-cosmosdb/README.md`](taller-cosmosdb/README.md).

---

> 🔒 Ninguna clave ni cadena de conexión está en el repositorio: los programas
> las piden al ejecutarse o las leen de archivos ignorados por git.
