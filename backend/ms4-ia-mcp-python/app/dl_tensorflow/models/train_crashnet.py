"""
=============================================================================
 AegisCore AI - MS4: [TRAINING & EXPORT] Red Neuronal Convolucional CrashNet
 Caso de Uso 11 (CU11): Analizar Fotografia/Video de Siniestro con Deep Learning
 Arquitectura: TensorFlow 2.x CNN con Inferencia por Tensores [224, 224, 3]
 Exporta modelos para Backend (.keras) y Movil/Web (.tflite)
 Metodologia ICONIX - Componente de Modelo y Entrenamiento Deep Learning
=============================================================================
"""

import os
import sys
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

CLASSES = ["LEVE", "MODERADO", "GRAVE", "PERDIDA_TOTAL"]
INPUT_SHAPE = (224, 224, 3)
MODEL_FILENAME = "crashnet_v1_weights.keras"
TFLITE_FILENAME = "crashnet_model.tflite"


def construir_modelo_crashnet_cnn(input_shape=INPUT_SHAPE, num_classes=4):
    """
    Construye la arquitectura convolucional profunda CrashNet CNN:
      - Capa de entrada de tensores de imagen normalizados (224, 224, 3)
      - Bloque 1: Conv2D 32 filtros + MaxPooling
      - Bloque 2: Conv2D 64 filtros + MaxPooling
      - Bloque 3: Conv2D 128 filtros + MaxPooling
      - GlobalAveragePooling2D + Dense 128 con Dropout
      - Softmax output para las 4 clases de severidad
    """
    inputs = layers.Input(shape=input_shape, name="tensor_imagen_vehiculo")
    
    # Bloque Convolucional 1: Deteccion de bordes y fracturas en carroceria
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same", name="conv1_features")(inputs)
    x = layers.MaxPooling2D((2, 2), name="pool1")(x)
    
    # Bloque Convolucional 2: Deteccion de deformaciones de paneles y luces
    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same", name="conv2_features")(x)
    x = layers.MaxPooling2D((2, 2), name="pool2")(x)
    
    # Bloque Convolucional 3: Deteccion de dano estructural y chasis
    x = layers.Conv2D(128, (3, 3), activation="relu", padding="same", name="conv3_features")(x)
    x = layers.MaxPooling2D((2, 2), name="pool3")(x)
    
    # Capa de clasificacion de severidad actuarial
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.Dense(128, activation="relu", name="dense_actuarial")(x)
    x = layers.Dropout(0.3, name="dropout_regularization")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="probabilidades_severidad")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="CrashNet_CNN_v2_1")
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def entrenar_y_exportar_modelo():
    """Genera dataset sintetico de tensores vehiculares, compila y guarda el modelo."""
    models_dir = Path(__file__).resolve().parent
    model_path = models_dir / MODEL_FILENAME
    tflite_path = models_dir / TFLITE_FILENAME
    
    print(f"[*] Construyendo arquitectura TensorFlow CrashNet en {models_dir}...")
    model = construir_modelo_crashnet_cnn()
    model.summary()
    
    # Sintetizar 120 muestras de entrenamiento para calibrar pesos de la red
    np.random.seed(42)
    X_train = np.random.uniform(0.0, 1.0, size=(120, 224, 224, 3)).astype(np.float32)
    intensidades = X_train.mean(axis=(1, 2, 3))
    y_train = np.digitize(intensidades, bins=np.percentile(intensidades, [25, 50, 75]))
    
    print("[*] Ajustando pesos de la red convolucional con tensores de calibracion...")
    model.fit(X_train, y_train, epochs=2, batch_size=16, verbose=1)
    
    print(f"[*] Exportando modelo convolucional Keras a {model_path}...")
    model.save(str(model_path))
    print(f"[+] Modelo CrashNet exportado exitosamente en: {model_path}")
    
    # Exportar a TFLite para dispositivo movil y web
    try:
        print(f"[*] Convirtiendo a TensorFlow Lite ({tflite_path})...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        print(f"[+] Modelo TensorFlow Lite cuantizado exportado exitosamente en: {tflite_path}")
    except Exception as e:
        print(f"[!] Advertencia al exportar a TFLite: {e}")
        
    return model_path


if __name__ == "__main__":
    entrenar_y_exportar_modelo()
