import math

def join_coordinates(coordinates, max_step=10):
    # Convert input coordinates to tuples of integers
    coord_tuples = [(int(coord[0]), int(coord[1])) for coord in coordinates]

    if len(coord_tuples) < 2:
        return coord_tuples

    # Add the first coordinate to the end to create a closed loop
    coord_tuples.append(coord_tuples[0])

    result = [coord_tuples[0]]
    for i in range(1, len(coord_tuples)):
        prev_x, prev_y = result[-1]
        curr_x, curr_y = coord_tuples[i]
        
        dx = curr_x - prev_x
        dy = curr_y - prev_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= max_step:
            result.append((curr_x, curr_y))
        else:
            steps = math.ceil(distance / max_step)
            step_x = dx / steps
            step_y = dy / steps
            
            for j in range(1, steps):
                x = int(prev_x + j * step_x)
                y = int(prev_y + j * step_y)
                result.append((x, y))
            
            result.append((curr_x, curr_y))

    return result


# Example usage
coords = [(0, 0), (5, 0), (5, 5), (0, 5)]
max_step_size = 2
route = join_coordinates(coords, max_step_size)
print(route)