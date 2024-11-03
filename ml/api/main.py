from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Verificar y cargar modelo y scaler
try:
    modelo = tf.keras.models.load_model('C:/Users/Jeffe/Desktop/student-dropout-prediction/ml/model/ml/model/dropout_model.h5')  # Ruta actualizada
    scaler = joblib.load('C:/Users/Jeffe/Desktop/student-dropout-prediction/ml/model/ml/model/scaler.pkl')  # Ruta actualizada
    logger.info("Modelo y scaler cargados exitosamente")
except Exception as e:
    logger.error(f"Error al cargar el modelo o scaler: {str(e)}")
    raise

def validar_datos_entrada(data):
    """
    Valida los datos de entrada

    Args:
        data (dict): Datos a validar

    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)
    """
    campos_requeridos = ['calificaciones', 'asistencia', 'incidentes_comportamiento']

    # Verificar campos requeridos
    for campo in campos_requeridos:
        if campo not in data:
            return False, f"Campo requerido faltante: {campo}"

    # Validar rangos
    try:
        if not (0 <= data['calificaciones'] <= 100):
            return False, "Calificaciones debe estar entre 0 y 100"

        if not (0 <= data['asistencia'] <= 100):
            return False, "Asistencia debe estar entre 0 y 100"

        if not (0 <= data['incidentes_comportamiento'] <= 10):
            return False, "Incidentes de comportamiento debe estar entre 0 y 10"

    except TypeError:
        return False, "Los valores deben ser numéricos"

    return True, ""

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para realizar predicciones"""
    try:
        # Obtener datos
        data = request.get_json()

        # Validar datos
        es_valido, mensaje_error = validar_datos_entrada(data)
        if not es_valido:
            return jsonify({
                'error': 'Datos inválidos',
                'mensaje': mensaje_error
            }), 400

        # Preparar datos para predicción
        input_data = np.array([[data['calificaciones'], data['asistencia'], data['incidentes_comportamiento']]])

        # Escalar datos
        input_scaled = scaler.transform(input_data)

        # Realizar predicción
        prediccion = modelo.predict(input_scaled)[0][0]

        # Determinar nivel de riesgo
        if prediccion > 0.7:
            nivel_riesgo = "Alto"
        elif prediccion > 0.3:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Bajo"

        # Preparar respuesta
        respuesta = {
            'probabilidad_desercion': float(prediccion),
            'riesgo': nivel_riesgo,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"Predicción exitosa: {respuesta}")
        return jsonify(respuesta)

    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'mensaje': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para obtener estadísticas"""
    try:
        # Cargar datos
        data = pd.read_csv(r'C:\Users\Jeffe\Desktop\student-dropout-prediction\ml\data\student_data.csv')

        # Calcular estadísticas
        stats = {
            'total_estudiantes': len(data),
            'tasa_desercion': float(data['desercion'].mean()),
            'promedio_calificaciones': float(data['calificaciones'].mean()),
            'promedio_asistencia': float(data['asistencia'].mean()),
            'promedio_incidentes_comportamiento': float(data['incidentes_comportamiento'].mean()),  # Nueva estadística
            'distribucion_desercion': data['desercion'].value_counts().to_dict(),
            'estadisticas_calificaciones': {
                'min': float(data['calificaciones'].min()),
                'max': float(data['calificaciones'].max()),
                'promedio': float(data['calificaciones'].mean()),
                'mediana': float(data['calificaciones'].median())
            },
            'estadisticas_asistencia': {
                'min': float(data['asistencia'].min()),
                'max': float(data['asistencia'].max()),
                'promedio': float(data['asistencia'].mean()),
                'mediana': float(data['asistencia'].median())
            },
            'estadisticas_incidentes_comportamiento': {  # Nueva sección para incidentes de comportamiento
                'min': float(data['incidentes_comportamiento'].min()),
                'max': float(data['incidentes_comportamiento'].max()),
                'promedio': float(data['incidentes_comportamiento'].mean()),
                'mediana': float(data['incidentes_comportamiento'].median())
            }
        }

        logger.info("Estadísticas generadas exitosamente")
        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error al generar estadísticas: {str(e)}")
        return jsonify({
            'error': 'Error al generar estadísticas',
            'mensaje': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Verificar que los archivos necesarios existen
    required_files = [
        'C:/Users/Jeffe/Desktop/student-dropout-prediction/ml/model/ml/model/dropout_model.h5',  # Ruta actualizada
        'C:/Users/Jeffe/Desktop/student-dropout-prediction/ml/model/ml/model/scaler.pkl',  # Ruta actualizada
        'C:/Users/Jeffe/Desktop/student-dropout-prediction/ml/data/student_data.csv'
    ]

    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"Archivo requerido no encontrado: {file}")
            raise FileNotFoundError(f"Archivo requerido no encontrado: {file}")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
