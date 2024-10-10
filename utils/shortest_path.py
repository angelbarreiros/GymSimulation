import json
import numpy as np
from PIL import Image, ImageDraw
import math
import heapq


# Define the size of the grid
SCALE_FACTOR = 20
# ROW = 1080 // SCALE_FACTOR
# COL = 1920 // SCALE_FACTOR
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

def create_matrix_from_json(json_data, floor="Planta2", padding=0, scale_factor=SCALE_FACTOR):
    # Extract size and walls data
    original_size = json_data[floor]["Size"]
    walls = json_data[floor]["Walls"]

    # Ensure size is in the correct order (width, height)
    size = (original_size[0] // scale_factor, original_size[1] // scale_factor)

    # Create an image to draw the walls
    img = Image.new('L', size, 255)
    draw = ImageDraw.Draw(img)

    # Draw walls on the image with padding
    for wall in walls:
        # Convert coordinates to tuples and reduced integers
        wall_coords = [tuple(map(lambda x: int(x) // scale_factor, point)) for point in wall]
        
        # Draw thick lines for walls
        draw.line(wall_coords, fill=0, width=1 + 2*padding)
        
        # Draw circles at vertices for rounded corners
        # for point in wall_coords:
        #     x, y = point
        #     draw.ellipse([x-padding, y-padding, x+padding, y+padding], fill=0)

    # Convert image to numpy array and flip the values
    wall_array = np.array(img)
    matrix = np.where(wall_array == 0, 0, 1).astype(np.uint8)

    return matrix

# Check if a cell is valid (within the grid)
def is_valid(row, col):
    return (row >= 0) and (row < ROW) and (col >= 0) and (col < COL)

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
def a_star_search_from_grid(grid, src, dest, debug=False):
    
    # Check if the source and destination are valid
    if not is_valid(src[0], src[1]):
        if debug:
            print(f"Source is invalid: {src}")
        return
    
    if not is_valid(dest[0], dest[1]):
        if debug:
            print(f"Destination is invalid: {dest}")
        return
    
    if not is_unblocked(grid, src[0], src[1]):
        if debug:
            print(f"Source is blocked: {src}")
        return
    
    if not is_unblocked(grid, dest[0], dest[1]):
        if debug:
            print(f"Destination is blocked: {dest}")
        return
    
    # # Check if the source and destination are valid
    # if not is_valid(src[0], src[1]) or not is_valid(dest[0], dest[1]):
    #     print("Source or destination is invalid")
    #     return

    # # Check if the source and destination are unblocked
    # if not is_unblocked(grid, src[0], src[1]) or not is_unblocked(grid, dest[0], dest[1]):
    #     print("Source or the destination is blocked")
    #     return

    # Check if we are already at the destination
    if is_destination(src[0], src[1], dest):
        # if debug:
        #     print("We are already at the destination")
        return

    # Initialize the closed list (visited cells)
    closed_list = [[False for _ in range(COL)] for _ in range(ROW)]
    # Initialize the details of each cell
    cell_details = [[Cell() for _ in range(COL)] for _ in range(ROW)]

    # Initialize the start cell details
    i = src[0]
    j = src[1]
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
            if is_valid(new_i, new_j) and is_unblocked(grid, new_i, new_j) and not closed_list[new_i][new_j]:
                # If the successor is the destination
                if is_destination(new_i, new_j, dest):
                    # Set the parent of the destination cell
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    # if debug:
                    #     print("The destination cell is found")
                    # Trace and print the path from source to destination
                    path = trace_path(cell_details, dest)
                    found_dest = True
                    return path
                else:
                    # Calculate the new f, g, and h values
                    g_new = cell_details[i][j].g + 1.0
                    h_new = calculate_h_value(new_i, new_j, dest)
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
        print("Failed to find the destination cell")

def a_star_search(src, dest, floor, json_path='data/zones.json', padding=0, scale_factor=SCALE_FACTOR, save_matrix_image=False):
    
    src_transformed = (src[0]//scale_factor, src[1]//scale_factor)
    dest_transformed = (dest[0]//scale_factor, dest[1]//scale_factor)
    
    with open(json_path, 'r') as file:
        json_data = json.load(file)

    # Create the matrix with padded walls
    matrix = create_matrix_from_json(json_data, floor=floor, padding=padding, scale_factor=scale_factor)
    matrix_transposed = matrix.transpose()

    # Save the matrix as an image for visualization
    if save_matrix_image:
        Image.fromarray(matrix * 255).save("floor_plan_matrix_padded.png")

    # Run the A* search algorithm
    path_reduced = a_star_search_from_grid(matrix_transposed, src_transformed, dest_transformed)
    # print(path_reduced)
    if path_reduced != None:
        path = [(x * scale_factor, y * scale_factor) for x, y in path_reduced]
    else:
        path = [src]
    return path
    # return a_star_search_from_grid(matrix, src, dest)

if __name__ == "__main__":
    
    # src_transformed=(24, 32)
    # dest_transformed=(50, 15)
    src_transformed = (66, 25)
    dest_transformed=(50, 15)
    
    src = (src_transformed[0]*SCALE_FACTOR, src_transformed[1]*SCALE_FACTOR)
    dest = (dest_transformed[0]*SCALE_FACTOR, dest_transformed[1]*SCALE_FACTOR)
    
    path = a_star_search(src, dest, padding=0, save_matrix_image=True)
    print(path)

