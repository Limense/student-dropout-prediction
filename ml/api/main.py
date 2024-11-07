# Importaciones necesarias
from flask import Flask, request, jsonify  # Framework web y utilidades HTTP
from flask_cors import CORS  # Manejo de Cross-Origin Resource Sharing
import tensorflow as tf  # Framework para el modelo de ML
import joblib  # Para cargar el scaler
import numpy as np  # Operaciones numéricas
import pandas as pd  # Manipulación de datos
import os  # Operaciones del sistema de archivos
from datetime import datetime  # Manejo de fechas y tiempo
import logging  # Sistema de logging

# Configuración del sistema de logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de detalle del logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Formato del mensaje
)
logger = logging.getLogger(__name__)

# Inicialización de la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Carga del modelo y scaler al inicio de la aplicación
try:
    # Carga el modelo de TensorFlow pre-entrenado
    modelo = tf.keras.models.load_model(
        r'C:\Users\Andriy\Documents\GitHub\student-dropout-prediction\ml\model\ml\model\dropout_model.h5')
    # Carga el scaler para normalizar los datos de entrada
    scaler = joblib.load(r'C:\Users\Andriy\Documents\GitHub\student-dropout-prediction\ml\model\ml\model\scaler.pkl')
    logger.info("Modelo y scaler cargados exitosamente")
except Exception as e:
    logger.error(f"Error al cargar el modelo o scaler: {str(e)}")
    raise


def validar_datos_entrada(data):
    """
    Valida que los datos de entrada cumplan con los requisitos necesarios

    Args:
        data (dict): Diccionario con los datos a validar
                    Debe contener: calificaciones, asistencia, incidentes_comportamiento

    Returns:
        tuple: (es_válido, mensaje_error)
               es_válido (bool): True si los datos son válidos
               mensaje_error (str): Descripción del error si los datos no son válidos
    """
    # Lista de campos que deben estar presentes en los datos
    campos_requeridos = ['calificaciones', 'asistencia', 'incidentes_comportamiento']

    # Verifica que todos los campos requeridos estén presentes
    for campo in campos_requeridos:
        if campo not in data:
            return False, f"Campo requerido faltante: {campo}"

    # Valida que los valores estén dentro de los rangos permitidos
    try:
        # Calificaciones deben estar entre 0 y 100
        if not (0 <= data['calificaciones'] <= 100):
            return False, "Calificaciones debe estar entre 0 y 100"

        # Asistencia debe estar entre 0 y 100
        if not (0 <= data['asistencia'] <= 100):
            return False, "Asistencia debe estar entre 0 y 100"

        # Incidentes de comportamiento deben estar entre 0 y 10
        if not (0 <= data['incidentes_comportamiento'] <= 10):
            return False, "Incidentes de comportamiento debe estar entre 0 y 10"

    except TypeError:
        return False, "Los valores deben ser numéricos"

    return True, ""


@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint que realiza la predicción de deserción estudiantil

    Espera un JSON con:
    - calificaciones: float (0-100)
    - asistencia: float (0-100)
    - incidentes_comportamiento: float (0-10)

    Returns:
        JSON con la probabilidad de deserción y nivel de riesgo
    """
    try:
        # Obtiene los datos del request
        data = request.get_json()

        # Valida los datos recibidos
        es_valido, mensaje_error = validar_datos_entrada(data)
        if not es_valido:
            return jsonify({
                'error': 'Datos inválidos',
                'mensaje': mensaje_error
            }), 400

        # Prepara los datos para la predicción
        input_data = np.array([[
            data['calificaciones'],
            data['asistencia'],
            data['incidentes_comportamiento']
        ]])

        # Escala los datos usando el mismo scaler usado en el entrenamiento
        input_scaled = scaler.transform(input_data)

        # Realiza la predicción usando el modelo
        prediccion = modelo.predict(input_scaled)[0][0]

        # Determina el nivel de riesgo basado en la probabilidad
        if prediccion > 0.7:
            nivel_riesgo = "Alto"
        elif prediccion > 0.3:
            nivel_riesgo = "Medio"
        else:
            nivel_riesgo = "Bajo"

        # Prepara la respuesta
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
    """
    Endpoint que proporciona estadísticas generales sobre los datos de estudiantes

    Returns:
        JSON con estadísticas descriptivas de los datos
    """
    try:
        # Carga el dataset completo
        data = pd.read_csv(r'C:\Users\Andriy\Documents\GitHub\student-dropout-prediction\ml\data\student_data.csv')

        # Calcula estadísticas descriptivas
        stats = {
            'total_estudiantes': len(data),
            'tasa_desercion': float(data['desercion'].mean()),
            'promedio_calificaciones': float(data['calificaciones'].mean()),
            'promedio_asistencia': float(data['asistencia'].mean()),
            'promedio_incidentes_comportamiento': float(data['incidentes_comportamiento'].mean()),
            'distribucion_desercion': data['desercion'].value_counts().to_dict(),

            # Estadísticas detalladas para calificaciones
            'estadisticas_calificaciones': {
                'min': float(data['calificaciones'].min()),
                'max': float(data['calificaciones'].max()),
                'promedio': float(data['calificaciones'].mean()),
                'mediana': float(data['calificaciones'].median())
            },

            # Estadísticas detalladas para asistencia
            'estadisticas_asistencia': {
                'min': float(data['asistencia'].min()),
                'max': float(data['asistencia'].max()),
                'promedio': float(data['asistencia'].mean()),
                'mediana': float(data['asistencia'].median())
            },

            # Estadísticas detalladas para incidentes de comportamiento
            'estadisticas_incidentes_comportamiento': {
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
    """
    Endpoint para verificar el estado del servicio

    Returns:
        JSON con el estado actual del servicio y timestamp
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


# Punto de entrada principal
if __name__ == '__main__':
    # Lista de archivos necesarios para el funcionamiento
    required_files = [
        r'C:\Users\Andriy\Documents\GitHub\student-dropout-prediction\ml\model\ml\model\dropout_model.h5',
        r'C:\Users\Andriy\Documents\GitHub\student-dropout-prediction\ml\model\ml\model\scaler.pkl',
        r'C:\Users\Andriy\Documents\GitHub\student-dropout-prediction\ml\data\student_data.csv'
    ]

    # Verifica que todos los archivos necesarios existan
    for file in required_files:
        if not os.path.exists(file):
            logger.error(f"Archivo requerido no encontrado: {file}")
            raise FileNotFoundError(f"Archivo requerido no encontrado: {file}")

    # Obtiene el puerto del ambiente o usa 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    # Inicia el servidor
    app.run(host='0.0.0.0', port=port, debug=True)  # debug=True no debería usarse en producción