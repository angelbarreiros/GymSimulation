import json
import numpy as np
from PIL import Image, ImageDraw
import heapq
import os
import random
import math
# Define the size of the grid
SCALE_FACTOR = 10
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

# def fill_rectangle_with_zeros(matrix, top_left, bottom_right):
#     """
#     Fill a rectangular area in a NumPy matrix with zeros.
    
#     Args:
#     matrix (np.array): The input NumPy matrix
#     top_left (tuple): (row, col) of the top-left corner of the rectangle
#     bottom_right (tuple): (row, col) of the bottom-right corner of the rectangle
    
#     Returns:
#     np.array: The modified matrix
#     """
#     row1, col1 = top_left
#     row2, col2 = bottom_right
    
#     # Ensure row1 <= row2 and col1 <= col2
#     row1, row2 = min(row1, row2), max(row1, row2)
#     col1, col2 = min(col1, col2), max(col1, col2)
    
#     # Fill the rectangular area with zeros
#     matrix[row1:row2+1, col1:col2+1] = 0
    
#     return matrix

# Check if a cell is valid (within the grid)
def is_valid(row, col, max_row, max_col):
    return (row >= 0) and (row < max_row) and (col >= 0) and (col < max_col)

# Check if a cell is unblocked
def is_unblocked(grid, row, col):
    return grid[row, col] == 1

# Check if a cell is the destination
def is_destination(row, col, dest):
    return row == dest[0] and col == dest[1]

# Calculate the heuristic value of a cell (Euclidean distance to destination)
def calculate_h_value(row, col, dest):
    return ((row - dest[0]) ** 2 + (col - dest[1]) ** 2) ** 0.5

# Trace the path from source to destination
def trace_path(cell_details, dest, show=False):
    path = []
    row = dest[0]
    col = dest[1]

    # Trace the path from destination to source using parent cells
    while not (cell_details[row][col].parent_i == row and cell_details[row][col].parent_j == col):
        path.append((row, col))
        temp_row = cell_details[row][col].parent_i
        temp_col = cell_details[row][col].parent_j
        row = temp_row
        col = temp_col

    # Add the source cell to the path
    path.append((row, col))
    # Reverse the path to get the path from source to destination
    path.reverse()

    if show:
        # Print the path
        print("The Path is ")
        for i in path:
            print("->", i, end=" ")
        print()
    
    return path

# Implement the A* search algorithm
def a_star_search_from_grid(grid, src, dest, scale_factor, debug=False):
    
    # Scale points
    src_scaled = (src[0]//scale_factor, src[1]//scale_factor)
    dest_scaled = (dest[0]//scale_factor, dest[1]//scale_factor)
    
    # if banned_areas_corners:
    #     for points in banned_areas_corners:
    #         top_left, bottom_right = points[0], points[2]
    #         grid = fill_rectangle_with_zeros(grid, top_left, bottom_right)
            
    # size = (size[0]//scale_factor, size[1]//scale_factor)
    # if path_reduced != None:
    #     path = [(x * scale_factor, y * scale_factor) for x, y in path_reduced]
    # else:
    #     path = [src]
    # return path
    max_row, max_col = grid.shape
    # Check if the source and destination are valid
    if not is_valid(src_scaled[0], src_scaled[1], max_row, max_col):
        if debug:
            print(f"Source is invalid: {src}->{dest}, {src_scaled}->{dest_scaled}")
        return [src]
    
    if not is_valid(dest_scaled[0], dest_scaled[1], max_row, max_col):
        if debug:
            print(f"Destination is invalid: {src}->{dest}, {src_scaled}->{dest_scaled}")
        return [src]
    
    # Check if the source and destination are blocked
    if not is_unblocked(grid, src_scaled[0], src_scaled[1]):
        if debug:
            print(f"Source is blocked: {src}->{dest}, {src_scaled}->{dest_scaled}")
        return [src]
    
    if not is_unblocked(grid, dest_scaled[0], dest_scaled[1]):
        if debug:
            print(f"Destination is blocked: {src}->{dest}, {src_scaled}->{dest_scaled}")
        return [src]

    # Check if we are already at the destination
    if is_destination(src_scaled[0], src_scaled[1], dest_scaled):
        if debug:
            print("We are already at the destination")
        return [src]

    # Initialize the closed list (visited cells)
    closed_list = [[False for _ in range(max_col)] for _ in range(max_row)]
    # Initialize the details of each cell
    cell_details = [[Cell() for _ in range(max_col)] for _ in range(max_row)]

    # Initialize the start cell details
    i = src_scaled[0]
    j = src_scaled[1]
    cell_details[i][j].f = 0
    cell_details[i][j].g = 0
    cell_details[i][j].h = 0
    cell_details[i][j].parent_i = i
    cell_details[i][j].parent_j = j

    # Initialize the open list (cells to be visited) with the start cell
    open_list = []
    heapq.heappush(open_list, (0.0, i, j))

    # Initialize the flag for whether destination is found
    found_dest = False

    # Main loop of A* search algorithm
    while len(open_list) > 0:
        # Pop the cell with the smallest f value from the open list
        p = heapq.heappop(open_list)

        # Mark the cell as visited
        i = p[1]
        j = p[2]
        closed_list[i][j] = True

        # For each direction, check the successors
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dir in directions:
            new_i = i + dir[0]
            new_j = j + dir[1]

            # If the successor is valid, unblocked, and not visited
            if is_valid(new_i, new_j, max_row, max_col) and is_unblocked(grid, new_i, new_j) and not closed_list[new_i][new_j]:
                # If the successor is the destination
                if is_destination(new_i, new_j, dest_scaled):
                    # Set the parent of the destination cell
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    # if debug:
                    #     print("The destination cell is found")
                    # Trace and print the path from source to destination
                    found_dest = True
                    path_reduced = trace_path(cell_details, dest_scaled)
                    path = [(x * scale_factor, y * scale_factor) for x, y in path_reduced]
                    return path
                else:
                    # Calculate the new f, g, and h values
                    g_new = cell_details[i][j].g + 1.0
                    h_new = calculate_h_value(new_i, new_j, dest_scaled)
                    f_new = g_new + h_new

                    # If the cell is not in the open list or the new f value is smaller
                    if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                        # Add the cell to the open list
                        heapq.heappush(open_list, (f_new, new_i, new_j))
                        # Update the cell details
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j

    # If the destination is not found after visiting all cells
    if not found_dest:
        if debug:
            print(f"Failed to find the destination cell: {src, dest}, {src_scaled, dest_scaled}")
        return [src] 

def a_star_search(src, dest, floor, json_path='data/zones.json', padding=0, scale_factor=SCALE_FACTOR, save_matrix_image=False, debug=False):

    # Create the matrix with padded walls
    matrix = create_matrix_from_json(json_path, floor=floor, padding=padding, scale_factor=scale_factor)

    # Save the matrix as an image for visualization
    if save_matrix_image:
        image_name = "floor_plan_matrix_padded.png"
        if os.path.exists(image_name):
            os.remove(image_name)
        Image.fromarray(matrix.transpose() * 255).save(image_name)

    # Run the A* search algorithm
    path_reduced = a_star_search_from_grid(matrix, src, dest, scale_factor, debug)
    # print(path_reduced)
    if path_reduced != None:
        path = [(x * scale_factor, y * scale_factor) for x, y in path_reduced]
    else:
        path = [src]
    return path
    # return a_star_search_from_grid(matrix, src, dest)

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
        if debug:
            print(f"Checking neighbors for node {node}")
        for dx, dy in base_directions:
            for step in range(max_step_size, 0, -1):
                nx, ny = node[0] + dx * step, node[1] + dy * step
                if is_valid(nx, ny):
                    # Check if the path to this neighbor is clear
                    if all(is_valid(node[0] + i * dx, node[1] + i * dy) for i in range(1, step + 1)):
                        if debug:
                            print(f"  Neighbor ({nx}, {ny}): valid (step size: {step})")
                        result.append((nx, ny))
                        break  # Found a valid step size, move to next direction
                elif debug:
                    print(f"  Neighbor ({nx}, {ny}): invalid (step size: {step})")
        if debug:
            print(f"Valid neighbors: {result}")
        return result

    def add_noise(value):
        return value * (1 + random.uniform(-noise_factor, noise_factor))

    open_set = []
    heapq.heappush(open_set, (0, start_scaled))
    came_from = {}
    g_score = {start_scaled: 0}
    f_score = {start_scaled: add_noise(heuristic(start_scaled, goal_scaled))}

    if debug:
        print(f"Start: {start} (scaled: {start_scaled})")
        print(f"Goal: {goal} (scaled: {goal_scaled})")
        print(f"Matrix shape: {len(matrix)}x{len(matrix[0])}")

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
                print(f"Path found in {iterations} iterations")
            path = [(x * scale_factor, y * scale_factor) for x, y in reversed(path)]
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

def interpolate_path(original_path, step_size):
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

if __name__ == "__main__":
    
    start = (510, 862)
    goal = (1500, 660)
    scale_factor = SCALE_FACTOR
    
    # start_scaled = (start[0] // scale_factor, start[1] // scale_factor)
    # goal_scaled = (goal[0] // scale_factor, goal[1] // scale_factor)
    
    matrix = create_matrix_from_json(1, 10, 1, False)
    # path = random_walk_pathfinder(matrix, start_scaled, goal_scaled, 2, 10000)
    path = variable_a_star_search_from_grid(matrix, start, goal, scale_factor=10, debug=False)
    # path = a_star_search(src, dest, floor='Planta0', padding=0, scale_factor=10, save_matrix_image=True)
    # print(path)
    print(path)
    # path = smooth_path(path, matrix, 10)
    # print(path)
    # print_matrix_neighborhood(matrix, src)

    # for floor in range(4):
    #     create_matrix_from_json(floor, 10, 1, True)