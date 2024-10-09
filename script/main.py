import json
import numpy as np
def convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto_a_convertir):
    # Calcular los factores de escala y traslación en el eje x
    a = (p2_final[0] - p1_final[0]) / (p2_inicial[0] - p1_inicial[0])
    b = p1_final[0] - a * p1_inicial[0]

    # Calcular los factores de escala y traslación en el eje y
    c = (p2_final[1] - p1_final[1]) / (p2_inicial[1] - p1_inicial[1])
    d = p1_final[1] - c * p1_inicial[1]

    # Convertir el punto
    x_prime = a * punto_a_convertir[0] + b
    y_prime = c * punto_a_convertir[1] + d

    return (x_prime, y_prime)
def convertir_conjunto_puntos(p1_inicial, p2_inicial, p1_final, p2_final, conjuntos_puntos):
    puntos_convertidos = []
    for conjunto in conjuntos_puntos:
        conjunto_convertido = []
        for punto in conjunto:
            punto_convertido = convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto)
            conjunto_convertido.append(punto_convertido)
        puntos_convertidos.append(conjunto_convertido)
    return puntos_convertidos

with open('/home/angel/startup/GymSimulation/data/zones.json', 'r') as file:
        data = json.load(file)

p1_inicial = np.array([413, 334])
p2_inicial = np.array([555, 646])

# Puntos de referencia del plano final
p1_final = np.array([609, 514])
p2_final = np.array([695, 666])
conjuntos_puntos = data['Planta1']['Walls']
puntos_convertidos =convertir_conjunto_puntos(p1_inicial, p2_inicial, p1_final, p2_final, conjuntos_puntos)
print(puntos_convertidos)
