import serial
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ----------------------------
# CONFIGURACIÓN DEL SERIAL
# ----------------------------
SERIAL_PORT = "/dev/cu.usbserial-54790509811"   # puerto de tu T-Beam
BAUD_RATE = 115200

# ----------------------------
# CONFIGURACIÓN DE MYSQL
# ----------------------------
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "TU_PASSWORD_AQUI",   # <-- pon aquí la misma clave que en Workbench
    "database": "sensoresdb",         # <-- ajusta al nombre real de tu schema
    "port": 3306
}

# ----------------------------
# CREAR TABLA SI NO EXISTE
# ----------------------------
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tbeam_realtime (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME,
    timestamp_esp BIGINT,
    humedad_aire FLOAT,
    temp_aire FLOAT,
    soil_raw INT,
    soil_percent INT,
    lat DOUBLE,
    lon DOUBLE,
    satelites INT
)
"""

# ----------------------------
# INSERT SQL
# ----------------------------
INSERT_SQL = """
INSERT INTO tbeam_realtime 
(fecha_hora, timestamp_esp, humedad_aire, temp_aire, soil_raw, soil_percent, lat, lon, satelites)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


def connect_mysql():
    """Conecta a MySQL y crea tabla si no existe."""
    try:
        print("Conectando con MySQL...")
        conn = mysql.connector.connect(**MYSQL_CONFIG)

        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(CREATE_TABLE_SQL)
            conn.commit()
            print("✔ Conectado y tabla lista.")
            return conn

    except Error as e:
        print(f"❌ Error MySQL: {e}")
        return None


def main():
    print(">>> Iniciando script de T-Beam → MySQL...")

    conn = connect_mysql()
    if conn is None:
        return

    cursor = conn.cursor()

    # Abrir el puerto serial
    print("Abriendo puerto serial...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✔ Conectado a: {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"❌ Error abriendo puerto serial: {e}")
        return

    print("Escuchando datos... (Ctrl+C para detener)\n")

    try:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue  # línea vacía

            print("RAW:", line)  # para ver qué llega desde la T-Beam

            # esperamos formato: timestamp,humedad,temp,soilRaw,soilPct,lat,lon,sats
            if "," in line and line[0].isdigit():
                partes = [p.strip() for p in line.split(",")]

                if len(partes) < 8:
                    print("⚠ Línea incompleta, se omite.")
                    continue

                # fecha y hora del sistema
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    timestamp_esp = int(float(partes[0]))
                    humedad_aire = float(partes[1])
                    temp_aire = float(partes[2])
                    soil_raw = int(float(partes[3]))
                    soil_percent = int(float(partes[4]))
                    lat = float(partes[5])
                    lon = float(partes[6])
                    satelites = int(float(partes[7]))

                    datos = (
                        fecha_hora,
                        timestamp_esp,
                        humedad_aire,
                        temp_aire,
                        soil_raw,
                        soil_percent,
                        lat,
                        lon,
                        satelites
                    )

                    cursor.execute(INSERT_SQL, datos)
                    conn.commit()

                    print("✔ Insertado en MySQL:", datos)

                except ValueError as e:
                    print("⚠ Error convirtiendo datos:", e)
                    continue

    except KeyboardInterrupt:
        print("\nFinalizando programa...")

    finally:
        cursor.close()
        conn.close()
        ser.close()
        print("Conexiones cerradas correctamente.")


if __name__ == "__main__":
    main()
