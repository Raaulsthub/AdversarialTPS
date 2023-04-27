import math

import math

def circle_rect_collision(cx, cy, r, x, y, w, h):
    # Calculate the x and y coordinates of the center of the circle.
    circle_x = cx
    circle_y = cy

    # If the center of the circle is inside the rectangle, then the distance is 0.
    if x <= circle_x <= x + w and y <= circle_y <= y + h:
        return True

    # Otherwise, calculate the x and y coordinates of the closest point on the rectangle to the center of the circle.
    closest_x = max(x, min(circle_x, x + w))
    closest_y = max(y, min(circle_y, y + h))

    # Calculate the distance between the center of the circle and the closest point on the rectangle using the distance formula.
    distance = math.sqrt((circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2)

    # If the distance is less than or equal to the radius of the circle, then the circle and rectangle are colliding.
    if distance <= r:
        return True
    else:
        return False

def circleCollision(circleCenterX1, circleCenterY1, circleRadius1, circleCenterX2, circleCenterY2, circleRadius2):
    distance = math.sqrt((circleCenterX2 - circleCenterX1) ** 2 + (circleCenterY2 - circleCenterY1) ** 2)
    if distance <= circleRadius1 + circleRadius2:
        return True
    else:
        return False 