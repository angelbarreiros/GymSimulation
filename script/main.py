import json

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

    return [x_prime, y_prime]
# Puntos de referencia del plano inicial y final (ajustalos según tu escenario)
p1_inicial = [413, 334]
p2_inicial = [555, 646]
p1_final = [609, 514]
p2_final = [695, 666]
punto_1= [1587,128]
punto_2=[
                    1334,
                    627
                ]
punto_3 =[
                    484,
                    632
                ]
punto_4 =[
                    1104,
                    418
                ]
punto_5=[
                    704,
                    543
                ]

punto_1_transformado = convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto_1)
punto_2_transformado = convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto_2)
punto_3_transformado = convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto_3)
punto_4_transformado = convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto_4)
punto_5_transformado = convertir_punto(p1_inicial, p2_inicial, p1_final, p2_final, punto_5)
print(punto_1_transformado)
print(punto_2_transformado)
print(punto_3_transformado)
print(punto_4_transformado)
print(punto_5_transformado)