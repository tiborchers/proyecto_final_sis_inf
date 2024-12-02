from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WriteOptions
import json

app = Flask(__name__)


file_path = "token.json"
with open(file_path, 'r') as file:
    data = json.load(file)
    token=data["token"]

# Configuración de InfluxDB
INFLUXDB_URL = "https://eu-central-1-1.aws.cloud2.influxdata.com"  # URL de tu servidor InfluxDB
INFLUXDB_TOKEN = token  # Token de autenticación
INFLUXDB_ORG = "ProyectoFinalSisInf"  # Nombre de la organización
INFLUXDB_BUCKET = "proyecto_final"  # Nombre del bucket en InfluxDB

# Crear cliente de InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

# Obtener el escritor de datos
write_api = client.write_api(write_options=WriteOptions(batch_size=1))
query_api = client.query_api()

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
        required_fields = ['temperatura', 'humedad', 'distancia1', 'distancia2', 'contador', 'sensor_id']
        
        if not all(field in content for field in required_fields):
            return jsonify({"error": "Faltan campos en los datos recibidos"}), 400

        # Crear un punto para InfluxDB
        point = Point("mediciones") \
            .tag("sensor_id", content["sensor_id"]) \
            .field("temperatura", content['temperatura']) \
            .field("humedad", content['humedad']) \
            .field("distancia1", content['distancia1']) \
            .field("distancia2", content["distancia2"]) \
            .field("contador", content['contador'])

        # Escribir el punto en InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)

        # Confirmación de recepción de los datos
        return jsonify({
            "status": "Recibido correctamente!",
            "temperatura": content['temperatura'],
            "humedad": content['humedad'],
            "distancia1": content['distancia1'],
            "distancia2": content['distancia2'],
            "contador": content['contador']
        }), 200

    except Exception as e:
        return jsonify({"error": repr(e)}), 500

@app.route('/sensor_values', methods=['GET'])
def get_sensor_values():

    try:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "mediciones")
        '''

        tables = query_api.query(query)

        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time(),
                    "sensor_id": record["sensor_id"],
                    "field": record.get_field(),
                    "value": record.get_value()
                })
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": repr(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
