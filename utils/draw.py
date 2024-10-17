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

def draw_boundary(frame, boundary, color=(0, 0, 0), thickness=10):
    pts = boundary.points.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=False, color=color, thickness=thickness)

def draw_target_area(frame, area, color=(255, 0, 0), thickness=2):
    pts = area.points.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
    center = area.points.mean(axis=0).astype(int)
    cv2.putText(frame, f"Area {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 1)
    cv2.putText(frame, f"Aforo {area.targetCapacity}", center-10, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 2)

def draw_spawn_point(frame, spawn_point, color=(0, 255, 0), thickness=2):
    top_left = (spawn_point.coords[0] - 20, spawn_point.coords[1] - 20)
    bottom_right = (spawn_point.coords[0] + 20, spawn_point.coords[1] + 20)
    cv2.rectangle(frame, top_left, bottom_right, color, thickness)
    cv2.putText(frame, f"Spawn {spawn_point.name}", (spawn_point.coords[0] + 10, spawn_point.coords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

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

def paint_noarea(frame, area, color):
    overlay = frame.copy()
    pts = area.points.reshape((-1, 1, 2))
    cv2.fillPoly(overlay, [pts], color)
    alpha = 0.5
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

def draw_person(frame, x, y, color):
    cv2.circle(frame, (int(x), int(y)), 15, color, -1)

def draw_class(frame, area, color):
    pts = area.Area.points.reshape((-1, 1, 2))
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=10)
    center = area.Area.points.mean(axis=0).astype(int)
    #cv2.putText(frame, f"Class {area.name}", center, cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 0), 1)
