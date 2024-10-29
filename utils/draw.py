import cv2
import numpy as np

COLORS = {
    'Red': (0, 0, 255),
    'Green': (0, 255, 0),
    'Blue': (255, 0, 0),
    'Yellow': (0, 255, 255),
    'Cyan': (255, 255, 0),
    'Magenta': (255, 0, 255),
    'White': (255, 255, 255),
    'Black': (0, 0, 0),
    'Gray': (128, 128, 128),
    'Dark Gray': (64, 64, 64),
    'Light Gray': (192, 192, 192),
    'Orange': (0, 140, 255),
    'Purple': (128, 0, 128),
    'Brown': (42, 42, 165),
    'Pink': (203, 192, 255)
}

def draw_boundary(frame, boundary, color=(0, 0, 0), thickness=2):
    pts = boundary.points.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=thickness)

def draw_target_area(frame, area, color=(255, 0, 0), thickness=2):
    pts = area.points.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
    center = area.points.mean(axis=0).astype(int)
    cv2.putText(frame, f"Area {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 1)
    cv2.putText(frame, f"Aforo {area.targetCapacity}", center-10, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 2)

def draw_spawn_point(frame, spawn_point, color=(0, 255, 0), thickness=10):
    start_point = (spawn_point.coords[0], spawn_point.coords[1])
    end_point = (spawn_point.coords[0], spawn_point.coords[1] - 50)  # Arrow pointing upwards
    cv2.arrowedLine(frame, start_point, end_point, color, thickness)
    cv2.putText(frame, f"Spawn {spawn_point.name}", (spawn_point.coords[0] + 10, spawn_point.coords[1] - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def draw_class(frame, area, color):
    pts = area.Area.points.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=10)
    center = area.Area.points.mean(axis=0).astype(int)
    center[0] -= 100  # Move 100 px to the left
    cv2.putText(frame, f"Class: {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # cv2.putText(frame, f"Class: {area.Area.targetCapacity}", center+25, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def paint_area(frame, area, persons, frame_num):
    pts = area.points.reshape((-1, 1, 2))

    if area.totalCapacity == 0:
        fill_color = (0, 0, 255)  # Red
    else:
        n = sum(1 for person in persons 
                if person.startFrame <= frame_num
                and frame_num < person.startFrame + len(person.history)
                and person.history[frame_num - person.startFrame][3] == 'reached'
                and person.history[frame_num - person.startFrame][4] == area.name)
        # print(f"Area {area.name} has {n} persons, actually has {area.actualCapacity}")
        occupancy_percent = (n / area.totalCapacity) * 100
        if 0 <= occupancy_percent < 20:
            fill_color = COLORS['Red']
        elif 20 <= occupancy_percent < 40:
            fill_color = COLORS['Orange']
        elif 40 <= occupancy_percent < 60:
            fill_color = COLORS['Yellow']
        elif 60 <= occupancy_percent < 80:
            fill_color = COLORS['Green']
        else:
            fill_color = COLORS['Black']
    overlay = frame.copy()
    cv2.fillPoly(overlay, [pts], fill_color)
    alpha = 0.3
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    # cv2.putText(frame, area.name, (pts[0][0][0], pts[0][0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # for machine in area.machines:
    #     cv2.circle(frame, (machine[0]), 5, (0, 0, 255), -1)

def paint_noarea(frame, area, color):
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    pts = area.points.reshape((-1, 1, 2))
    cv2.fillPoly(mask, [pts], 255)

    color_overlay = np.full(frame.shape, color, dtype=np.uint8)

    masked_overlay = cv2.bitwise_and(color_overlay, color_overlay, mask=mask)

    alpha = 0.5
    frame[:] = cv2.addWeighted(frame, 1, masked_overlay, alpha, 0)

    return frame

def draw_person(frame, x, y, color):
    cv2.circle(frame, (int(x), int(y)), 7, color, -1) # black

def draw_colorLegend(frame):
    height, width, _ = frame.shape
    legend_width = 300
    legend_height = 50 * len(COLORS)
    start_x = (width - legend_width) // 2
    start_y = 10
    occupancy_rates = [0, 20, 40, 60, 80, 100]
    colors = [COLORS['Red'], COLORS['Orange'], COLORS['Yellow'], COLORS['Green'], COLORS['Black']]
    for i in range(len(colors)):
        y = start_y + 50 * i
        cv2.putText(frame, f"Del {occupancy_rates[i]}% al {occupancy_rates[i+1]}%", (start_x + 40, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.rectangle(frame, (start_x, y), (start_x + 30, y + 30), colors[i], -1)

def draw_legend(frame, areas, persons, frame_num):
    height, width, _ = frame.shape
    legend_width = 300
    filtered_areas = [area for area in areas if area.type != 'NOFUNCIONAL']
    legend_height = 50 * len(filtered_areas)
    start_x = (width - legend_width) // 2 - 50
    start_y = 10 + 50 * 5 + 20  # Adjust start_y to be below the color legend
    for i, area in enumerate(filtered_areas):
        n = sum(1 for person in persons 
        if person.startFrame <= frame_num
        and frame_num < person.startFrame + len(person.history)
        and person.history[frame_num - person.startFrame][3] == 'reached'
        and person.history[frame_num - person.startFrame][4] == area.name)
        # print(f"Area {area.name} has {n} persons, actually has {area.actualCapacity}")

        y = start_y + 50 * i
        cv2.putText(frame, f"{area.name}: {n}/{area.totalCapacity} ", (start_x + 40, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
