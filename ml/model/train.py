import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import joblib
import os


def crear_directorios():
    """Crea los directorios necesarios si no existen"""
    os.makedirs('ml/model', exist_ok=True)
    os.makedirs('ml/data', exist_ok=True)


def cargar_y_preprocesar_datos():
    """
    Carga y preprocesa los datos para el entrenamiento

    Returns:
        tuple: Datos de entrenamiento y prueba
    """
    # Cargar datos
    data = pd.read_csv(r'C:\Users\Jeffe\Desktop\student-dropout-prediction\ml\data\student_data.csv')

    # Eliminar filas con valores NaN en cualquier columna
    data = data.dropna()

    # Separar features y target
    X = data[['calificaciones', 'asistencia', 'incidentes_comportamiento']]
    y = data['desercion']

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Escalar datos
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Guardar scaler
    joblib.dump(scaler, 'ml/model/scaler.pkl')

    return X_train_scaled, X_test_scaled, y_train, y_test


def crear_modelo():
    """
    Crea el modelo de red neuronal

    Returns:
        tensorflow.keras.Model: Modelo compilado
    """
    model = Sequential([
        # Capa de entrada
        Dense(64, input_shape=(3,)),
        BatchNormalization(),
        Dense(64, activation='relu'),
        Dropout(0.3),

        # Capas ocultas
        Dense(32, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),

        Dense(16, activation='relu'),
        BatchNormalization(),
        Dropout(0.1),

        # Capa de salida
        Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )

    return model


def entrenar_y_guardar_modelo():
    """
    Entrena el modelo y lo guarda

    Returns:
        tuple: Historial de entrenamiento y métricas de evaluación
    """
    # Crear directorios necesarios
    crear_directorios()

    # Cargar y preprocesar datos
    X_train_scaled, X_test_scaled, y_train, y_test = cargar_y_preprocesar_datos()

    # Crear modelo
    model = crear_modelo()

    # Callbacks
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )

    model_checkpoint = ModelCheckpoint(
        'ml/model/dropout_model.h5',
        monitor='val_loss',
        save_best_only=True
    )

    # Entrenar modelo
    history = model.fit(
        X_train_scaled, y_train,
        validation_data=(X_test_scaled, y_test),
        epochs=100,
        batch_size=32,
        callbacks=[early_stopping, model_checkpoint],
        verbose=1
    )

    # Evaluar modelo
    evaluacion = model.evaluate(X_test_scaled, y_test)
    metricas = dict(zip(model.metrics_names, evaluacion))

    print("\nMétricas en datos de prueba:")
    for nombre, valor in metricas.items():
        print(f"{nombre}: {valor:.4f}")

    # Guardar modelo
    model.save('ml/model/dropout_model.h5')

    return history, metricas


if __name__ == "__main__":
    print("Iniciando entrenamiento del modelo...")
    history, metricas = entrenar_y_guardar_modelo()
    print("\nEntrenamiento completado exitosamente!")
