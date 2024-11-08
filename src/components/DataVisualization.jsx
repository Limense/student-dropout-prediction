// Importación de las librerias necesarias
import React, { useEffect, useState } from 'react';
import {
  BarChart, // Gráfico de barras
  Bar,
  XAxis,         // Eje X
  YAxis,           // Eje Y
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export default function DataVisualization() {
  // Estados para manejar los datos y el estado de carga
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Realizacar peticion http al end point /stats
    fetch('http://localhost:5000/stats')
      .then(response => {
        if (!response.ok) {
          throw new Error('Error al cargar los datos');
        }
        return response.json();
      })
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-gray-600">Cargando estadísticas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-gray-600">No hay datos disponibles</p>
      </div>
    );
  }

  // Datos de la distribución de deserción y asistencia
  const distributionData = [
    { name: 'No Deserción', cantidad: stats.distribucion_desercion['0'] || 0 },
    { name: 'Deserción', cantidad: stats.distribucion_desercion['1'] || 0 }
  ];

  // Datos de la asistencia
  const attendanceData = [
    { name: 'Asistencia', porcentaje: stats.promedio_asistencia || 0 }
  ];

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="text-sm text-gray-600">Total Estudiantes</h4>
          <p className="text-2xl font-bold text-blue-600">{stats.total_estudiantes}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="text-sm text-gray-600">Promedio Calificaciones</h4>
          <p className="text-2xl font-bold text-green-600">
            {stats.promedio_calificaciones.toFixed(1)}
          </p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <h4 className="text-sm text-gray-600">Tasa de Deserción</h4>
          <p className="text-2xl font-bold text-purple-600">
            {(stats.tasa_desercion * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <h4 className="text-sm text-gray-600">Promedio Incidentes Comportamiento</h4>
          <p className="text-2xl font-bold text-yellow-600">
            {stats.promedio_incidentes_comportamiento.toFixed(1)}
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold mb-4">Distribución de Deserción</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={distributionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="cantidad" fill="#3B82F6" name="Estudiantes" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Gráfico de Asistencia */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-bold mb-4">Promedio de Asistencia</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={attendanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="porcentaje" fill="#34D399" name="Porcentaje" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
