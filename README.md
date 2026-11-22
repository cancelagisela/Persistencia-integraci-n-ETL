# Persistencia e Integración de Scripts ETL

Flujo automatizado de extracción, transformación y carga (ETL) que lee datos de pedidos desde un archivo CSV, limpia y agrega la información por usuario, y la guarda en una base de datos SQLite local de forma repetible.

## Requisitos

- Python 3.x
- Librería `pandas` (`pip install pandas`)
- Módulo estándar `sqlite3` (incluido en Python)

## Configuración del entorno

1. Clonar o descargar el repositorio público en el entorno de trabajo.
2. Tener disponible el archivo `schema.sql` (definición DDL de la tabla de destino `user_order_metrics`) y el archivo CSV de entrada (por ejemplo, `sample_orders.csv` con las columnas `order_id`, `user_id`, `amount` y `status`).
3. Mantener el archivo `.gitignore` configurado para no subir archivos locales generados o temporales (como bases `.db`, caché de Python o entornos virtuales).

## Patrón de datos y lógica del pipeline

- **Esquema de destino (DDL):** `schema.sql` define la tabla `user_order_metrics` (`user_id`, `total_orders`, `total_amount`) utilizando `CREATE TABLE IF NOT EXISTS`.

- **Extracción y transformación:** `etl_pipeline.py` lee el CSV de origen, descarta filas con nulos en campos clave, filtra registros con `status = 'completed'` y `amount > 0`, y agrupa por `user_id` para calcular la cantidad de pedidos únicos y el monto total acumulado.

- **Carga anti-duplicidad y manejo de errores:** La carga se ejecuta dentro de bloques `try / except / finally` con `rollback()` ante fallos de archivo o base de datos, y realiza `DELETE FROM user_order_metrics` antes de insertar los datos del lote actual para evitar duplicados si se vuelve a correr el script.

## Pasos para ejecutar

1. Ubicar `etl_pipeline.py`, `schema.sql` y el archivo CSV de entrada en el mismo directorio de trabajo.

2. Ejecutar el script:

```bash
python etl_pipeline.py
