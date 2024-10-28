import json
import pandas as pd
import numpy as np
from itertools import product
from shortest_path import variable_a_star_search_from_grid, create_matrix_from_json, SCALE_FACTOR

def extract_nonfunctional_points(floor_data):
    """Extract coordinates of all NOFUNCIONAL machines."""
    points = []
    for zone in floor_data['Zones']:
        if zone['Type'] == 'NOFUNCIONAL':
            for machine in zone['Machines']:
                points.append({
                    'coordinates': (machine[0][0], machine[0][1]),
                    'zone_type': zone['Type'],
                    'zone_name': zone['Name']
                })
    return points

def extract_spawn_points(floor_data):
    """Extract coordinates of all spawn points."""
    spawn_points = []
    if 'Spawns' in floor_data:
        for spawn in floor_data['Spawns']:
            spawn_points.append({
                'coordinates': (spawn['Coordinates'][0], spawn['Coordinates'][1]),
                'zone_type': 'SPAWN',
                'zone_name': spawn['Name']
            })
    return spawn_points

def calculate_zone_midpoint(coordinates):
    """Calculate the midpoint of a zone based on its corner coordinates."""
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[1] for coord in coordinates]
    
    mid_x = sum(x_coords) / len(x_coords)
    mid_y = sum(y_coords) / len(y_coords)
    
    return (int(mid_x), int(mid_y))

def extract_zone_goals(floor_data):
    """Extract machine coordinates or midpoint of non-NOFUNCIONAL zones."""
    goals = []
    for zone in floor_data['Zones']:
        if zone['Type'] != 'NOFUNCIONAL':
            if zone['Machines']:  # If zone has machines
                # Add each machine as a goal point
                for machine in zone['Machines']:
                    goals.append({
                        'coordinates': (machine[0][0], machine[0][1]),
                        'zone_type': zone['Type'],
                        'zone_name': zone['Name']
                    })
            else:  # If zone has no machines, use midpoint
                midpoint = calculate_zone_midpoint(zone['Coordinates'])
                goals.append({
                    'coordinates': midpoint,
                    'zone_type': zone['Type'],
                    'zone_name': zone['Name']
                })
    return goals

def create_routes_dataframe(json_data, variable_a_star_search_from_grid, create_matrix_from_json, scale_factor=10, padding=1):
    """Create a DataFrame with all possible routes."""
    all_routes = []
    
    # Process each floor separately
    for floor_name, floor_data in json_data.items():
        print(f"Processing {floor_name}...")
        
        # Extract floor number from floor name
        floor_num = int(floor_name.replace("Planta", ""))
        
        # Get the matrix for this floor
        matrix = create_matrix_from_json(
            floor_num=floor_num,
            scale_factor=scale_factor,
            padding=padding,
            save_matrix_image=False
        )
        
        # Get all points for this floor
        nonfunctional_points = extract_nonfunctional_points(floor_data)
        spawn_points = extract_spawn_points(floor_data)
        zone_goals = extract_zone_goals(floor_data)
        
        # Calculate routes for nonfunctional starts to zone goals
        for start_point in nonfunctional_points:
            for goal in zone_goals:
                try:
                    route = variable_a_star_search_from_grid(
                        matrix=matrix,
                        start=start_point['coordinates'],
                        goal=goal['coordinates'],
                        scale_factor=scale_factor,
                        debug=False,
                        noise_factor=0.1,
                        heuristic_type='euclidean',
                        max_step_size=3,
                        speed=5
                    )
                    
                    all_routes.append({
                        'floor': floor_name,
                        'start_x': start_point['coordinates'][0],
                        'start_y': start_point['coordinates'][1],
                        'start_type': start_point['zone_type'],
                        'start_name': start_point['zone_name'],
                        'goal_x': goal['coordinates'][0],
                        'goal_y': goal['coordinates'][1],
                        'goal_type': goal['zone_type'],
                        'goal_name': goal['zone_name'],
                        'route': route
                    })
                    
                except Exception as e:
                    print(f"Error calculating route on {floor_name} from {start_point['coordinates']} to {goal['coordinates']}: {str(e)}")
                    continue
        
        # Calculate routes from spawn points to nonfunctional points
        for spawn in spawn_points:
            for goal in nonfunctional_points:
                try:
                    route = variable_a_star_search_from_grid(
                        matrix=matrix,
                        start=spawn['coordinates'],
                        goal=goal['coordinates'],
                        scale_factor=scale_factor,
                        debug=False,
                        noise_factor=0.1,
                        heuristic_type='euclidean',
                        max_step_size=3,
                        speed=5
                    )
                    
                    all_routes.append({
                        'floor': floor_name,
                        'start_x': spawn['coordinates'][0],
                        'start_y': spawn['coordinates'][1],
                        'start_type': spawn['zone_type'],
                        'start_name': spawn['zone_name'],
                        'goal_x': goal['coordinates'][0],
                        'goal_y': goal['coordinates'][1],
                        'goal_type': goal['zone_type'],
                        'goal_name': goal['zone_name'],
                        'route': route
                    })
                    
                except Exception as e:
                    print(f"Error calculating route on {floor_name} from {spawn['coordinates']} to {goal['coordinates']}: {str(e)}")
                    continue
    
    # Create DataFrame
    df = pd.DataFrame(all_routes)
    
    return df
# Example usage:
def main():
    # Load your JSON data
    with open('data/zones.json', 'r') as f:
        json_data = json.load(f)
    
    # Create the routes DataFrame with specific scale factor and padding
    routes_df = create_routes_dataframe(
        json_data, 
        variable_a_star_search_from_grid,
        create_matrix_from_json,
        scale_factor=SCALE_FACTOR,
        padding=1
    )
    
    # Save to CSV or other format if needed
    routes_df.to_csv('precalculated_routes.csv', index=False)
    
    return routes_df


if __name__ == "__main__":
    main()