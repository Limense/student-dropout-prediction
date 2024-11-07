#  Datos sintéticos

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def generate_synthetic_data(n_samples=1000):
    np.random.seed(42)

    # Generar datos sintéticos
    grades = np.random.normal(70, 15, n_samples)  # Calificaciones (0-100)
    attendance = np.random.normal(85, 10, n_samples)  # Asistencia (0-100)
    behavior_incidents = np.random.poisson(2, n_samples)  # Número de incidentes

    # Ajustar valores a rangos realistas
    grades = np.clip(grades, 0, 100)
    attendance = np.clip(attendance, 0, 100)
    behavior_incidents = np.clip(behavior_incidents, 0, 10)

    # Crear función para determinar probabilidad de deserción
    def dropout_probability(grade, attendance, incidents):
        prob = 0.0
        if grade < 60: prob += 0.4
        if attendance < 70: prob += 0.35
        prob += incidents * 0.05
        return min(prob, 1.0)

    # Calcular probabilidades y determinar deserción
    probabilities = [dropout_probability(g, a, b)
                     for g, a, b in zip(grades, attendance, behavior_incidents)]
    dropout = [1 if np.random.random() < p else 0 for p in probabilities]

    # Crear DataFrame
    data = pd.DataFrame({
        'calificaciones': grades,
        'asistencia': attendance,
        'incidentes_comportamiento': behavior_incidents,
        'desercion': dropout
    })

    # Guardar datos
    data.to_csv('ml/data/student_data.csv', index=False)
    return data


if __name__ == "__main__":
    data = generate_synthetic_data()
    print("Datos generados y guardados en 'student_data.csv'")
    print("\nResumen de los datos:")
    print(data.describe())
    print("\nDistribución de deserción:")
    print(data['desercion'].value_counts(normalize=True))