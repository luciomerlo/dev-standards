# Manual de Directivas de IngenierÝa (RULES.md)

Este documento consolidado establece los estßndares, patrones arquitect¾nicos y directrices de ingenierÝa obligatorios, extraÝdos y destilados de la experiencia acumulada en m·ltiples proyectos del ecosistema. Su cumplimiento es mandatorio para garantizar la resiliencia, mantenibilidad y escalabilidad del software.

---

## 1. Arquitectura y Dise±o de Sistemas

*   **1.1. Principio de la ┌nica Fuente de Verdad (SSoT):** Centralizar las configuraciones crÝticas, taxonomÝas y listados de dominio (como instrumentos objetivo, clases o parßmetros de procesamiento) en artefactos ·nicos compartidos (ej. archivos YAML) para evitar la deriva de configuraci¾n entre preprocesamiento, entrenamiento y ejecuci¾n.
*   **1.2. Desacoplamiento Modular y Patr¾n *Registry*:** Utilizar registros dinßmicos y mapeos polimÚricos centralizados para gestionar proveedores de servicios o fuentes de datos externas en tiempo de ejecuci¾n, permitiendo habilitar o deshabilitar integraciones de forma declarativa.
*   **1.3. Arquitectura Orientada a Modelos HÝbridos:** En arquitecturas de IA y procesamiento pesado, congelar los pesos y estructuras base del modelo y extender o reentrenar exclusivamente las capas finales (decodificadores, normalizaciones) para adaptarse a esquemas de salida personalizados.
*   **1.4. Aislamiento y Persistencia de Memoria en Agentes:** Estructurar la memoria interna, estados privados y configuraciones sensibles de agentes o entornos en archivos desacoplados (`memory/*.md`, `config.md`) excluidos explÝcitamente del control de versiones.
*   **1.5. Modelado de Datos y Flexibilidad de Esquemas:** Evitar restricciones de carpetas rÝgidas externas utilizando manifiestos tabulares planos (CSV) con columnas unÝvocas. Modelar colecciones complejas como estructuras serializadas (cadenas separadas por comas) dentro de la base de datos, encapsulando la conversi¾n a tipos nativos (`Set`, listas) mediante propiedades computadas en las entidades.

---

## 2. Resiliencia, Manejo de Errores y Concurrencia

*   **2.1. Estrategias de Reintento y Resiliencia en Red:** Implementar invariablemente mecanismos de *backoff* exponencial con limitadores de concurrencia (semßforos asÝncronos o limitadores basados en promesas como `p-limit`) y manejo de cabeceras HTTP de limitaci¾n de tasa (HTTP 429/503) para evitar bloqueos por *rate-limiting*.
*   **2.2. Cadenas de *Fallback* Multicapa para LLMs y APIs:** Dise±ar sistemas de respaldo automßticos ante caÝdas o lÝmites de tasa de proveedores externos. Transicionar de forma transparente al siguiente proveedor o modelo registrado, cortando la cadena inmediatamente ante errores fatales de autenticaci¾n.
*   **2.3. Gesti¾n Robusta de Bases de Datos y Concurrencia Local:** Configurar tiempos de espera extendidos (`busy_timeout`) y migraciones idempotentes mediante comprobaciones de esquema (`PRAGMA table_info` o equivalentes) para asegurar compatibilidad retroactiva. Aislar la conversi¾n de tipos mediante bloques de captura seguros (`runCatching`) para evitar fallos catastr¾ficos por cambios de esquema.
*   **2.4. Control de Instancias y Puertos CrÝticos:** En servicios locales o servidores HTTP, implementar interceptaci¾n de eventos de ocupaci¾n de puertos (`EADDRINUSE`) cerrando el proceso de manera controlada (`process.exit(1)`) para evitar fugas y solapamientos en entornos de desarrollo o despliegue.

---

## 3. Rendimiento, Procesamiento de Datos y Operaciones en Memoria

*   **3.1. Procesamiento Cero en Disco (Zero Disk I/O):** Priorizar el procesamiento y la indexaci¾n de contenidos pesados (como parsers XML complejos o benchmarks P2P) directamente en memoria RAM o mediante flujos de *streaming*, evitando la escritura innecesaria de archivos temporales en disco.
*   **3.2. AsincronÝa y Tareas No Bloqueantes:** Ejecutar tareas de inicializaci¾n pesadas (verificaci¾n de dependencias, impresiones de metadatos o diagn¾sticos) en hilos independientes o de manera asÝncrona para no bloquear el arranque de la aplicaci¾n.
*   **3.3. Estrategias de CachÚ Multinivel:** Implementar sistemas de cachÚ hÝbridos combinando almacenamiento volßtil en memoria (LRU) con persistencia externa (Redis, IndexedDB) aplicando polÝticas estrictas de expiraci¾n por TTL para minimizar llamadas repetitivas y latencias.

---

## 4. Calidad, Observabilidad y Diagn¾stico

*   **4.1. Diagn¾stico Separado y Clasificaci¾n de Excepciones:** Desarrollar clasificadores semßnticos y c¾digos de estado personalizados para categorizar errores externos (Auth, RateLimit, NotFound, Timeout). Separar las operaciones de diagn¾stico livianas (pings con bajo consumo de tokens) de las solicitudes de inferencia habituales.
*   **4.2. Trazabilidad y Evidencia en Respuestas:** Incorporar metadatos y etiquetas de evidencia explÝcitas en las respuestas y recomendaciones del sistema para diferenciar claramente entre datos analÝticos propios, fuentes externas e inferencias automatizadas.
*   **4.3. Observabilidad de Procesos Largos:** Dise±ar sistemas de progreso duales basados en persistencia incremental local y archivos de estado intermedios (`status.json`) para permitir la reanudaci¾n transparente de procesos masivos interrumpidos.

---

## 5. Versionado, CHANGELOG e Integridad de Repositorios

*   **5.1. Versionado Semántico (SemVer):** Todo proyecto debe adherirse estrictamente a SemVer (`MAJOR.MINOR.PATCH`). Cualquier cambio que rompa la compatibilidad de contratos o interfaces incrementará obligatoriamente la versión *Major*.
*   **5.2. Gestión de Cambios (CHANGELOG):** Mantener un archivo `CHANGELOG.md` actualizado y estructurado en cada repositorio, documentando de forma clara los cambios bajo las categorías de *Added*, *Changed*, *Deprecated*, *Removed*, *Fixed* y *Security*. Seguir el formato [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
*   **5.3. Higiene de Repositorios y Artefactos:** Excluir explícitamente mediante `.gitignore` directorios de datos generados (`data/`, `build/`, directorios de descargas, cachés de lenguaje, entornos virtuales y archivos binarios pesados o manuales), desacoplando estrictamente el código fuente de los artefactos transitorios.
*   **5.4. Sincronización de Dependencias y Entornos:** Versionar y fijar (*pin*) dependencias críticas de motores externos o binarios de terceros cuando se identifiquen regresiones. Especificar restricciones estrictas de versiones del entorno de ejecución (ej. campo `engines` en Node.js) alineadas con flujos de CI multiversión.
*   **5.5. README Ilustrativo y Badges:** Cada `README.md` debe incluir: (a) badges de estado (CI, versión, licencia, cobertura), (b) al menos un diagrama de arquitectura o flujo (Mermaid renderizado como SVG/PNG), (c) capturas de pantalla o GIFs de la UI/CLI cuando aplique, y (d) sección "Estándares aplicados" con checklist visual.
*   **5.6. Scaffolding Obligatorio:** Existe un script de arranque (`scripts/bootstrap-project.sh` o equivalente) que genera en cualquier repo nuevo: `README.md` plantilla, `CHANGELOG.md` (Keep a Changelog), `pyproject.toml`/`package.json` con `version = "0.1.0"`, `.gitignore`, `Dockerfile`, `.github/workflows/ci.yml`, `.env.example`, y `config.yaml` (SSoT). Su uso es obligatorio al crear un repositorio.
*   **5.7. Auditoría Periódica Automatizada:** Un job programado (GitHub Actions `schedule` mensual o cron externo) ejecuta `scripts/audit-standards.py` que valida: presencia de versión SemVer, CHANGELOG, README con imágenes, `.gitignore`, Dockerfile, CI, y cumplimiento de RULES.md §1‑4. Genera reporte en `AUDIT_REPORT.md` y abre issue si hay regresiones.
*   **5.8. Descripción del Repositorio:** Todo repositorio debe tener una descripción (campo "description" del hosting, ej. GitHub) de máximo 350 caracteres. Debe crearse al crear `README.md` y actualizarse cada vez que `README.md` cambie, manteniéndola alineada con el propósito vigente del proyecto.
