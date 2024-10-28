import json
import numpy as np
from PIL import Image, ImageDraw
import heapq
import os
import random
import math
# Define the size of the grid
SCALE_FACTOR = 20
# ROW = 1080 // SCALE_FACTOR
# max_col = 1920 // SCALE_FACTOR
COL = 1080 // SCALE_FACTOR
ROW = 1920 // SCALE_FACTOR

# Define the Cell class
class Cell:
    def __init__(self):
      # Parent cell's row index
        self.parent_i = 0
    # Parent cell's column index
        self.parent_j = 0
 # Total cost of the cell (g + h)
        self.f = float('inf')
    # Cost from start to this cell
        self.g = float('inf')
    # Heuristic cost from this cell to destination
        self.h = 0

def create_matrix_from_json(floor_num, scale_factor, padding=0, save_matrix_image=False, json_path='data/zones.json'):
    with open(json_path, 'r') as file:
        json_data = json.load(file)
    
    floor = f'Planta{floor_num}'
    # Extract size and walls data
    original_size = json_data[floor]["Size"]
    walls = json_data[floor]["Walls"]

    # Ensure size is in the correct order (width, height)
    size = (original_size[0] // scale_factor, original_size[1] // scale_factor)

    # Create an image to draw the walls
    img = Image.new('L', size, 255)
    draw = ImageDraw.Draw(img)

    def draw_thickened_line(start, end, width):
        """Draw a line with thickened midpoints"""
        x0, y0 = start
        x1, y1 = end
        dx = x1 - x0
        dy = y1 - y0
        distance = max(abs(dx), abs(dy))
        
        if distance == 0:
            draw.point([x0, y0], fill=0)
        else:
            for i in range(distance + 1):
                t = i / distance
                x = int(x0 + t * dx)
                y = int(y0 + t * dy)
                
                # Thicken all points except the start and end
                if 0 < i < distance:
                    for ox in range(-width, width + 1):
                        for oy in range(-width, width + 1):
                            draw.point([x + ox, y + oy], fill=0)
                else:
                    draw.point([x, y], fill=0)

    # Draw walls on the image
    for wall in walls:
        # Convert coordinates to tuples and reduced integers
        wall_coords = [tuple(map(lambda x: int(x) // scale_factor, point)) for point in wall]
        
        # Draw lines for walls
        for i in range(len(wall_coords) - 1):
            start = wall_coords[i]
            end = wall_coords[i + 1]
            draw_thickened_line(start, end, padding)

    # Convert image to numpy array and flip the values
    wall_array = np.array(img)
    matrix = np.where(wall_array == 0, 0, 1).astype(np.uint8)
    
    # Save the matrix as an image for visualization
    if save_matrix_image:
        image_name = f"data/images/matrix/floor_{floor_num}_p{padding}_matrix.png"
        if os.path.exists(image_name):
            os.remove(image_name)
        Image.fromarray(matrix * 255).save(image_name)

    return matrix.transpose()

def fill_rectangle_with_zeros(matrix, top_left, bottom_right):
    """
    Fill a rectangular area in a NumPy matrix with zeros.
    
    Args:
    matrix (np.array): The input NumPy matrix
    top_left (tuple): (row, col) of the top-left corner of the rectangle
    bottom_right (tuple): (row, col) of the bottom-right corner of the rectangle
    
    Returns:
    np.array: The modified matrix
    """
    row1, col1 = top_left
    row2, col2 = bottom_right
    
    # Ensure row1 <= row2 and col1 <= col2
    row1, row2 = min(row1, row2), max(row1, row2)
    col1, col2 = min(col1, col2), max(col1, col2)
    
    # Fill the rectangular area with zeros
    matrix[row1:row2+1, col1:col2+1] = 0
    
    return matrix

def variable_a_star_search_from_grid(matrix, start, goal, scale_factor, debug=False, noise_factor=0.1, heuristic_type='euclidean', max_step_size=3, speed=5):
    
    start_scaled = (start[0] // scale_factor, start[1] // scale_factor)
    goal_scaled = (goal[0] // scale_factor, goal[1] // scale_factor)

    def euclidean_heuristic(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def manhattan_heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def diagonal_heuristic(a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)

    heuristics = {
        'euclidean': euclidean_heuristic,
        'manhattan': manhattan_heuristic,
        'diagonal': diagonal_heuristic
    }

    heuristic = heuristics.get(heuristic_type, euclidean_heuristic)

    def is_valid(x, y):
        return 0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] == 1

    def get_neighbors(node):
        base_directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        random.shuffle(base_directions)
        result = []
        # if debug:
        #     print(f"Checking neighbors for node {node}")
        for dx, dy in base_directions:
            for step in range(max_step_size, 0, -1):
                nx, ny = node[0] + dx * step, node[1] + dy * step
                if is_valid(nx, ny):
                    # Check if the path to this neighbor is clear
                    if all(is_valid(node[0] + i * dx, node[1] + i * dy) for i in range(1, step + 1)):
                        # if debug:
                        #     print(f"  Neighbor ({nx}, {ny}): valid (step size: {step})")
                        result.append((nx, ny))
                        break  # Found a valid step size, move to next direction
                # elif debug:
                #     print(f"  Neighbor ({nx}, {ny}): invalid (step size: {step})")
        # if debug:
        #     print(f"Valid neighbors: {result}")
        return result

    def add_noise(value):
        return value * (1 + random.uniform(-noise_factor, noise_factor))

    open_set = []
    heapq.heappush(open_set, (0, start_scaled))
    came_from = {}
    g_score = {start_scaled: 0}
    f_score = {start_scaled: add_noise(heuristic(start_scaled, goal_scaled))}

    # if debug:
    #     print(f"Start: {start} (scaled: {start_scaled})")
    #     print(f"Goal: {goal} (scaled: {goal_scaled})")
    #     print(f"Matrix shape: {len(matrix)}x{len(matrix[0])}")

    iterations = 0
    max_iterations = len(matrix) * len(matrix[0]) * 2  # Increased max iterations

    while open_set and iterations < max_iterations:
        iterations += 1
        current = heapq.heappop(open_set)[1]

        if debug and iterations % 1000 == 0:
            print(f"Iteration {iterations}, Current: {current}, Open set size: {len(open_set)}")

        if current == goal_scaled:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_scaled)
            if debug:
                print(f"Path found in {iterations} iterations. {start} -> {goal}")
            path = [(x * scale_factor, y * scale_factor) for x, y in reversed(path)]
            if speed is None:
                return path
            else:
                return interpolate_path(path, speed)
            
        neighbors = get_neighbors(current)
        if debug and not neighbors:
            print(f"No valid neighbors for {current}")

        for neighbor in neighbors:
            tentative_g_score = g_score[current] + euclidean_heuristic(current, neighbor)

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + add_noise(heuristic(neighbor, goal_scaled))
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    if debug:
        print(f"No path found after {iterations} iterations")
    return None

def interpolate_path(original_path, step_size=10):
    """
    Interpolate additional points between each pair of points in the original path,
    using a fixed step size.
    
    :param original_path: List of tuples representing the original path coordinates
    :param step_size: The size of each step in the interpolated path
    :return: A new path with interpolated points
    """
    interpolated_path = []
    for i in range(len(original_path) - 1):
        start = original_path[i]
        end = original_path[i + 1]
        
        interpolated_path.append(start)
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= step_size:
            continue  # No need to interpolate if points are already close enough
        
        steps = int(distance / step_size)
        
        for step in range(1, steps):
            t = step * step_size / distance
            x = start[0] + t * dx
            y = start[1] + t * dy
            interpolated_path.append((round(x), round(y)))
    
    interpolated_path.append(original_path[-1])  # Add the final point
    return interpolated_path

def get_easy_route(start, end, step = 10):
    """
    Generate a route between two points with a maximum step size.
    
    Args:
        start (tuple): Starting coordinates (x, y)
        end (tuple): Ending coordinates (x, y)
        step (float): Maximum distance between consecutive points
        
    Returns:
        list: List of coordinate tuples forming the route
    """
    points = []
    current_x, current_y = start
    points.append((current_x, current_y))
    
    while True:
        # Calculate distances
        dx = end[0] - current_x
        dy = end[1] - current_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # If we're close enough to the end, add it and break
        if distance <= step:
            points.append(end)
            break
            
        # Calculate the ratio to maintain direction but limit step size
        ratio = step / distance
        
        # Calculate next point
        current_x = current_x + dx * ratio
        current_y = current_y + dy * ratio
        
        points.append((current_x, current_y))
    
    return points

def find_route(df, floor_num, start, goal, speed, input_type='coordinates'):
    """
    Find a precalculated route between two points on a specific floor.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing the precalculated routes
    floor_num (int): Floor number (0 for Planta0, 1 for Planta1, etc.)
    start: Either a tuple of (x, y) coordinates or a string with the zone/point name
    goal: Either a tuple of (x, y) coordinates or a string with the zone/point name
    input_type (str): Either 'coordinates' or 'names' to specify input format
    
    Returns:
    list: Route coordinates if found, None if no route exists
    """
    # Convert floor number to floor name format
    floor_name = f"Planta{floor_num}"
    
    # Filter by floor first
    floor_df = df[df['floor'] == floor_name]
    
    if floor_df.empty:
        return None
    
    if input_type == 'coordinates':
        start_x, start_y = start
        goal_x, goal_y = goal
        
        # Try direct match
        direct_match = floor_df[
            (floor_df['start_x'] == start_x) &
            (floor_df['start_y'] == start_y) &
            (floor_df['goal_x'] == goal_x) &
            (floor_df['goal_y'] == goal_y)
        ]
        
        if not direct_match.empty:
            path = direct_match.iloc[0]['route']
            return interpolate_path(path, speed)
            
        # Try reverse match
        reverse_match = floor_df[
            (floor_df['start_x'] == goal_x) &
            (floor_df['start_y'] == goal_y) &
            (floor_df['goal_x'] == start_x) &
            (floor_df['goal_y'] == start_y)
        ]
        
        if not reverse_match.empty:
            path = reverse_match.iloc[0]['route'][::-1]
            return interpolate_path(path, speed)
            
    elif input_type == 'names':
        # Try direct match by names
        direct_match = floor_df[
            (floor_df['start_name'] == start) &
            (floor_df['goal_name'] == goal)
        ]
        
        if not direct_match.empty:
            path = direct_match.iloc[0]['route']
            return interpolate_path(path, speed)
            
        # Try reverse match
        reverse_match = floor_df[
            (floor_df['start_name'] == goal) &
            (floor_df['goal_name'] == start)
        ]
        
        if not reverse_match.empty:
            path = reverse_match.iloc[0]['route'][::-1]
            return interpolate_path(path, speed)
    
    else:
        raise ValueError("input_type must be either 'coordinates' or 'names'")
    
    return None

# def main():
#     start = (510, 862)
#     goal = (1500, 660)
    
#     for _ in range(50):
#         matrix = create_matrix_from_json(1, 10, 1, False)
#     for _ in range(50):
#         path = variable_a_star_search_from_grid(matrix, start, goal, scale_factor=10, debug=False)
#     for _ in range(50):
#         path2 = interpolate_path(path)
    
if __name__ == "__main__":
    
    # import cProfile
    # cProfile.run('main()')
    
    # start = (510, 862)
    # goal = (1500, 660)

    # matrix = create_matrix_from_json(1, 10, 1, False)
    # path = variable_a_star_search_from_grid(matrix, start, goal, scale_factor=10, debug=False)
    # print(path)

    # # for floor in range(4):
    # #     create_matrix_from_json(floor, 10, 1, True)
    
    # Load the DataFrame
    import pandas as pd
    df = pd.read_csv('data/routes/spawn_to_nonfunctional_routes.csv')
    df['route'] = df['route'].apply(eval)
    # Using names
    route = find_route(
        df,
        floor_num=1,
        goal=(973,1051),
        start=(1351,731),
        input_type='coordinates'
    )
    print(route)