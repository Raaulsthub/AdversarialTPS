import math

def rectCircleCollision(rectLeft, rectTop, rectWidth, rectHeight, circleCenterX, circleCenterY, circleRadius):

    # Encontra o ponto central mais próximo do círculo dentro do retângulo
    centro_x = circleCenterX
    centro_y = circleCenterY

    if circleCenterX < rectLeft:
        centro_x = rectLeft
    elif circleCenterX > rectLeft + rectWidth:
        centro_x = rectLeft + rectWidth

    if circleCenterY < rectTop:
        centro_y = rectTop
    elif circleCenterY > rectTop + rectHeight:
        centro_y = rectTop + rectHeight

    # Calcula a distância entre o centro do círculo e o ponto central encontrado acima
    distancia = math.sqrt((circleCenterX - centro_x) ** 2 + (circleCenterY - centro_y) ** 2)

    # Verifica se a distância é menor ou igual ao raio do círculo
    if distancia <= circleRadius:
        return True  # Houve colisão
    else:
        return False  # Não houve colisão

def circleCollision(circleCenterX1, circleCenterY1, circleRadius1, circleCenterX2, circleCenterY2, circleRadius2):
    distance = math.sqrt((circleCenterX2 - circleCenterX1) ** 2 + (circleCenterY2 - circleCenterY1) ** 2)
    if distance <= circleRadius1 + circleRadius2:
        return True
    else:
        return False 