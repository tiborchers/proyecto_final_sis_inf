from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WriteOptions
import os

app = Flask(__name__)

# Configuración de InfluxDB
INFLUXDB_URL = "http://localhost:8086"  # URL de tu servidor InfluxDB
INFLUXDB_TOKEN = "tu_token_aqui"  # Token de autenticación
INFLUXDB_ORG = "tu_organizacion_aqui"  # Nombre de la organización
INFLUXDB_BUCKET = "sensores"  # Nombre del bucket en InfluxDB

# Crear cliente de InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

# Obtener el escritor de datos
write_api = client.write_api(write_options=WriteOptions(batch_size=1))

@app.route('/')
def index():
    return '<h1>Proyecto Final!</h1>'

@app.route('/mipaginanueva')
def mipaginanueva():
    return '<h1>Mediciones de AIPA</h1>'

@app.route('/sensor_values', methods=['POST'])
def read_sensors():
    try:
        content = request.get_json()

        # Validación de los campos
        required_fields = ['temperatura', 'temperaturaMax', 'temperaturaMin', 'pos']
        if not all(field in content for field in required_fields):
            return jsonify({"error": "Faltan campos en los datos recibidos"}), 400

        # Crear un punto para InfluxDB
        point = Point("mediciones") \
            .tag("sensor", "temperatura") \
            .field("temperatura", content['temperatura']) \
            .field("temperaturaMax", content['temperaturaMax']) \
            .field("temperaturaMin", content['temperaturaMin']) \
            .field("pos", content['pos'])

        # Escribir el punto en InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)

        # Confirmación de recepción de los datos
        return jsonify({
            "status": "Recibido correctamente!",
            "temperatura": content['temperatura'],
            "temperaturaMax": content['temperaturaMax'],
            "temperaturaMin": content['temperaturaMin'],
            "pos": content['pos']
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sensor_values', methods=['GET'])
def get_sensor_values():
    return jsonify({"message": "Acción GET no implementada con InfluxDB"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
