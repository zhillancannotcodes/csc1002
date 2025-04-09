'''
GOAL: balance between clean code, coding style and performance
	- Efficient logic can be developed to determine if two shapes overlap, intersect, 
		or if one is contained within the other, using one or two functions. 
		However, this logic tends to be complex and challenging 
		to read and follow. Additionally, testing the logic can be difficult, 
		particularly when it comes to evaluating the internal structure of the function.
	- Instead, break down the problem into smaller sub-problems, and solve each sub-problem
		one by one, using simple and easy-to-read functions, combining the proper usage of function
		parameters to enhance reusability and maintainability, and finally integrating them
		together to produce the solution to the original problem.
	- To acheive optimal efficiency and performance, analyses the code structure and flow to ensure the correct
		order of execution and avoid unnecessary calculations.

Process: 
	Pick a random polygon shape and a color
	Stretch the chosen polygon
	Repeatedly pick a random x,y position and try to fit the choosen shape so that
		1/ it doesn't touch any other shapes
		2/ it doesn't overlap with any other shapes
		3/ it doesn't hide inside another shape
'''
import turtle
import random
import time

# global constants
YOUR_ID = '124040006' # TODO: your student id
COLORS = ('red', 'blue', 'green', 'yellow', 'purple', 'orange', 'white')
SHAPE_FILE = 'shapes.txt'
SCREEN_DIM_X = 0.7 # screen width factor
SCREEN_DIM_Y = 0.7 #screen height factor
XY_SPAN = 0.8      # canvas factor
XY_STEP = 10       # step size of x,y coordinates
MIN_DURATION = 5    
MAX_DURATION = 30
MIN_STRETCH = 1
MAX_STRETCH = 10
MIN_SEED = 1
MAX_SEED = 99

# global variables
g_shapes = []       # list of (position, coords, color)
g_screen = None
g_range_x = None
g_range_y = None

def is_shape_overlapped_any(pos:tuple, coords:list, stretch:float) -> bool:
    '''
    Check if shape at given position overlaps with any existing shapes
    
    Args:
        pos (tuple): (x,y) position of shape to check
        coords (list): List of (x,y) coordinates defining the shape
        stretch (float): Stretch factor applied to the shape
    
    Returns:
        bool: True if shape overlaps with any existing shape
    '''
    def pt_sub(p1, p2):
        return (p1[0] - p2[0], p1[1] - p2[1])

    def pt_cross(p1, p2):
        return p1[0] * p2[1] - p1[1] * p2[0]

    def pt_cross_with_points(p, a, b):
        a_minus_p = pt_sub(a, p)
        b_minus_p = pt_sub(b, p)
        return pt_cross(a_minus_p, b_minus_p)

    def sgn(x):
        return 1 if x > 0 else (-1 if x < 0 else 0)

    def inter1(a, b, c, d, buffer=3.5):
        if a > b:
            a, b = b, a
        if c > d:
            c, d = d, c
        return max(a - buffer, c - buffer) <= min(b + buffer, d + buffer)

    def expand_segment(start, end, buffer=3.5):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx**2 + dy**2)**0.5
        if length < 1e-10:  # Handle very short segments
            return (start[0] - buffer, start[1] - buffer), (end[0] + buffer, end[1] + buffer)
        dx, dy = dx/length, dy/length
        new_start = (start[0] - dx * buffer, start[1] - dy * buffer)
        new_end = (end[0] + dx * buffer, end[1] + dy * buffer)
        return new_start, new_end

    def check_inter(a, b, c, d, buffer=3.5):
        a_exp, b_exp = expand_segment(a, b, buffer)
        c_exp, d_exp = expand_segment(c, d, buffer)
        
        if pt_cross_with_points(c_exp, a_exp, d_exp) == 0 and pt_cross_with_points(c_exp, b_exp, d_exp) == 0:
            return (inter1(a[0], b[0], c[0], d[0], buffer) and 
                    inter1(a[1], b[1], c[1], d[1], buffer))
        return (sgn(pt_cross_with_points(a_exp, b_exp, c_exp)) != sgn(pt_cross_with_points(a_exp, b_exp, d_exp)) and
                sgn(pt_cross_with_points(c_exp, d_exp, a_exp)) != sgn(pt_cross_with_points(c_exp, d_exp, b_exp)))

    def point_in_polygon(point, polygon):
        x, y = point
        inside = False
        n = len(polygon)
        for i in range(n):
            j = (i - 1) % n
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y) and 
                x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
                inside = not inside
        return inside

    def get_bounding_box(coords, buffer=3.5):
        xs = [x for x, y in coords]
        ys = [y for x, y in coords]
        return (min(xs) - buffer, max(xs) + buffer, min(ys) - buffer, max(ys) + buffer)

    def distance(p1, p2):
        return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

    def point_to_segment_distance(p, seg_start, seg_end):
        v = pt_sub(seg_end, seg_start)
        w = pt_sub(p, seg_start)
        length_squared = v[0]**2 + v[1]**2
        if length_squared < 1e-10:
            return distance(p, seg_start)
        t = max(0, min(1, (w[0] * v[0] + w[1] * v[1]) / length_squared))
        projection = (seg_start[0] + t * v[0], seg_start[1] + t * v[1])
        return distance(p, projection)

    # Convert coordinates to stretched position
    new_coords = [(x * stretch + pos[0], y * stretch + pos[1]) for x, y in coords]
    new_segments = [(new_coords[i], new_coords[(i + 1) % len(new_coords)]) 
                   for i in range(len(new_coords))]
    
    # Get centroid of new shape for containment check
    centroid_x = sum(x for x, y in new_coords) / len(new_coords)
    centroid_y = sum(y for x, y in new_coords) / len(new_coords)
    centroid = (centroid_x, centroid_y)

    # Get bounding box of new shape with buffer
    new_box = get_bounding_box(new_coords)

    for existing_pos, existing_coords, _ in g_shapes:
        # Convert existing shape coordinates
        exist_coords = [(x * stretch + existing_pos[0], y * stretch + existing_pos[1]) 
                       for x, y in existing_coords]
        exist_segments = [(exist_coords[i], exist_coords[(i + 1) % len(exist_coords)]) 
                         for i in range(len(exist_coords))]
        
        # Check bounding boxes first (with buffer)
        exist_box = get_bounding_box(exist_coords)
        if not (new_box[1] < exist_box[0] or exist_box[1] < new_box[0] or 
                new_box[3] < exist_box[2] or exist_box[3] < new_box[2]):
            # Check vertex proximity
            buffer = 3.5
            for new_vertex in new_coords:
                for exist_vertex in exist_coords:
                    if distance(new_vertex, exist_vertex) < buffer:
                        return True
                for seg_start, seg_end in exist_segments:
                    if point_to_segment_distance(new_vertex, seg_start, seg_end) < buffer:
                        return True
            
            for exist_vertex in exist_coords:
                for seg_start, seg_end in new_segments:
                    if point_to_segment_distance(exist_vertex, seg_start, seg_end) < buffer:
                        return True
            
            # If bounding boxes overlap (including buffer), do detailed check
            for seg1_start, seg1_end in new_segments:
                for seg2_start, seg2_end in exist_segments:
                    if check_inter(seg1_start, seg1_end, seg2_start, seg2_end):
                        return True
        
        # Check if new shape is inside existing shape
        if point_in_polygon(centroid, exist_coords):
            return True
            
        # Check if existing shape is inside new shape
        exist_centroid_x = sum(x for x, y in exist_coords) / len(exist_coords)
        exist_centroid_y = sum(y for x, y in exist_coords) / len(exist_coords)
        exist_centroid = (exist_centroid_x, exist_centroid_y)
        if point_in_polygon(exist_centroid, new_coords):
            return True
                    
    return False


def create_shape(coords:list, color:str, stretch_factor:float) -> tuple:
    '''
    Create shape data with specified parameters
    
    Args:
        coords (list): List of (x,y) coordinates
        color (str): Color for the shape
        stretch_factor (float): Stretch factor
    
    Returns:
        tuple: (coords, color)
    '''
    return (coords, color)

def get_random_home_position(range_x:list, range_y:list) -> tuple:
    '''
    Generates a random (x, y) coordinate tuple
    
    Args:
        range_x (list): Range of x coordinates
        range_y (list): Range of y coordinates
    
    Returns:
        tuple: Random (x,y) position
    '''
    return (random.uniform(min(range_x) + 50, max(range_x) - 50),
            random.uniform(min(range_y) + 50, max(range_y) - 50))

def place_a_random_shape(shape_data:tuple, stretch:float, started:float, duration:int) -> bool:
    '''
    Try to place a shape on the canvas
    
    Args:
        shape_data (tuple): (coordinates, color)
        stretch (float): Stretch factor
        started (float): Start time
        duration (int): Time limit
    
    Returns:
        bool: True if shape was placed successfully
    '''
    coords, color = shape_data
    max_attempts = 10000
    
    for _ in range(max_attempts):
        if time.time() - started > duration:
            return False
            
        pos = get_random_home_position(g_range_x, g_range_y)
        if not is_shape_overlapped_any(pos, coords, stretch):
            turtle.penup()
            turtle.goto(pos)
            turtle.pendown()
            turtle.color(color)
            turtle.begin_fill()
            for x, y in coords:
                turtle.goto(x * stretch + pos[0], y * stretch + pos[1])
            first_x, first_y = coords[0]
            turtle.goto(first_x * stretch + pos[0], first_y * stretch + pos[1])
            turtle.end_fill()
            g_shapes.append((pos, coords, color))
            g_screen.title(f'{YOUR_ID} - {len(g_shapes)}')
            g_screen.update()
            return True
    return False

def fill_canvas_with_random_shapes(shapes:dict, colors:tuple, stretch_factor:float, duration:int) -> float:
    '''
    Fill canvas with random shapes
    
    Args:
        shapes (dict): Dictionary of shape names and coordinates
        colors (tuple): Tuple of colors
        stretch_factor (float): Stretch factor
        duration (int): Time limit
    
    Returns:
        float: Start time
    '''
    started = time.time()
    while time.time() - started <= duration:
        shape_name = random.choice(list(shapes.keys()))
        shape_data = create_shape(shapes[shape_name], random.choice(colors), stretch_factor)
        if not place_a_random_shape(shape_data, stretch_factor, started, duration):
            print(f"Could not place shape: {shape_name}")
    return started

def import_custom_shapes(file_name:str) -> dict:
    '''
    Args:
        file_name (str): Path to shapes file
    
    Returns:
        dict: Dictionary of shape names and coordinates
    '''
    shapes = {}
    try:
        with open(file_name, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                    
                name, coords_str = line.split(':', 1)
                name = name.strip()
                coords_str = coords_str.strip()
                
                if coords_str.startswith('(') and coords_str.endswith(')'):
                    coords_str = coords_str[1:-1]
                
                coords = []
                coord_pairs = coords_str.split('),')
                for pair in coord_pairs:
                    pair = pair.strip()
                    if pair.startswith('('):
                        pair = pair[1:]
                    if pair.endswith(')'):
                        pair = pair[:-1]
                    try:
                        x, y = map(float, pair.split(','))
                        coords.append((x, y))
                    except ValueError:
                        continue
                
                if coords:
                    shapes[name] = coords
                    
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        exit(1)
    
    if not shapes:
        print("No valid shapes could be loaded.")
        exit(1)
    return shapes

def setup_canvas_ranges(w:int, h:int, span:float=0.8, step:int=10) -> tuple:
    '''
    Calculate canvas coordinate ranges
    
    Args:
        w (int): Width
        h (int): Height
        span (float): Span factor
        step (int): Step size
    
    Returns:
        tuple: (x_range, y_range)
    '''
    sz_w, sz_h = w/2*span, h/2*span
    return ([-sz_w, sz_w], [-sz_h, sz_h])

def setup_screen() -> turtle.Screen:
    '''
    Setup turtle screen
    
    Returns:
        turtle.Screen: Configured screen
    '''
    scrn = turtle.Screen()
    scrn.tracer(0)
    scrn.setup(SCREEN_DIM_X,SCREEN_DIM_Y)
    scrn.bgcolor("white")
    scrn.mode("logo")
    turtle.hideturtle()
    turtle.speed(0)
    return scrn

def get_time_str(time_sec) -> str:
    return time.strftime("%H:%M:%S", time.localtime(time_sec))

def show_result(started:float, count:int) -> None:
    ended = time.time()
    start_time = get_time_str(started)
    end_time = get_time_str(ended)
    diff = round(ended - started, 1)
    g_screen.bgcolor("black")  # Change to black after drawing is complete
    g_screen.title(f'{YOUR_ID} {start_time} - {end_time} - {diff} - {count}')
    print(f"{YOUR_ID} {start_time} - {end_time} - {diff} - {count}")
    print(f"{YOUR_ID}, {count}")

def prompt(prompt:str, default) -> str:
    ret = input(f'{prompt} (default is {default}): ')
    return default if ret == "" else ret

def prompt_input() -> tuple:
    stretch = float(prompt("Stretch Value", MIN_STRETCH))
    stretch = max(MIN_STRETCH, min(stretch, MAX_STRETCH))
    
    seed = int(prompt("Random Seed", MIN_SEED))
    seed = max(MIN_SEED, min(seed, MAX_SEED))
    
    duration = float(prompt("Duration (s)", MIN_DURATION))
    duration = max(MIN_DURATION, min(duration, MAX_DURATION))
    
    termination = prompt("Terminate", 'n')
    termination = 'y' if termination.lower() == 'y' else 'n'
    
    return stretch, seed, duration, termination

def main() -> None:
    global g_screen, g_range_x, g_range_y
    
    g_screen = setup_screen()
    g_range_x, g_range_y = setup_canvas_ranges(g_screen.window_width(), 
                                              g_screen.window_height(),
                                              XY_SPAN, XY_STEP)
    
    shapes = import_custom_shapes(SHAPE_FILE)
    stretch, seed, duration, termination = prompt_input()
    
    random.seed(seed)
    started = fill_canvas_with_random_shapes(shapes, COLORS, stretch, duration)
    show_result(started, len(g_shapes))
    
    if termination == 'y':
        turtle.bye()
    else:
        g_screen.mainloop()

if __name__ == '__main__':
    main()
