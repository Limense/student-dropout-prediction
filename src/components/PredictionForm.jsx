import React, { useState } from 'react';

// Componente de formulario para predicción de deserción
const PredictionForm = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

// Manejador del envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.target);
    const data = {
      // Convertir valores del formulario a números
      calificaciones: Number(formData.get('calificaciones')),
      asistencia: Number(formData.get('asistencia')),
      incidentes_comportamiento: Number(formData.get('incidentes_comportamiento'))
    };

    try {
      // Realizar petición POST al endpoint de predicción
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error('Error en la predicción');
      }

      const resultData = await response.json();
      setResult(resultData);
    } catch (err) {
      setError('Error al realizar la predicción. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  // Colores para los niveles de riesgo
  const getRiskColor = (riesgo) => {
    switch (riesgo) {
      case 'Alto':
        return 'text-red-600 bg-red-50';
      case 'Medio':
        return 'text-yellow-600 bg-yellow-50';
      case 'Bajo':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="calificaciones" className="block text-sm font-medium text-gray-700">
            Calificaciones Promedio (0-100)
          </label>
          <input
            type="number"
            name="calificaciones"
            id="calificaciones"
            min="0"
            max="100"
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="asistencia" className="block text-sm font-medium text-gray-700">
            Porcentaje de Asistencia (0-100)
          </label>
          <input
            type="number"
            name="asistencia"
            id="asistencia"
            min="0"
            max="100"
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="incidentes_comportamiento" className="block text-sm font-medium text-gray-700">
            Número de Incidentes de Comportamiento (0-10)
          </label>
          <input
            type="number"
            name="incidentes_comportamiento"
            id="incidentes_comportamiento"
            min="0"
            max="10"
            required
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {loading ? 'Procesando...' : 'Realizar Predicción'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-6 p-6 bg-white rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Resultado de la Predicción</h3>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="text-gray-600">Probabilidad de Deserción:</span>
              <span className="font-semibold">
                {(result.probabilidad_desercion * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="flex justify-between items-center p-3 rounded">
              <span className="text-gray-600">Nivel de Riesgo:</span>
              <span className={`font-semibold px-3 py-1 rounded-full ${getRiskColor(result.riesgo)}`}>
                {result.riesgo}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictionForm;