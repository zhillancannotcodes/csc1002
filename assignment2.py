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
YOUR_ID = '124040006'
COLORS = ('red', 'blue', 'green', 'yellow', 'purple', 'orange', 'white')
SHAPE_FILE = 'shapes.txt'
SCREEN_DIM_X = 0.7
SCREEN_DIM_Y = 0.7
XY_SPAN = 0.8
XY_STEP = 10
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
    def get_bounding_box(pos, coords, stretch):
        stretched = [(x * stretch + pos[0], y * stretch + pos[1]) for x, y in coords]
        xs = [x for x, _ in stretched]
        ys = [y for _, y in stretched]
        return min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1

    for existing_pos, existing_coords, _ in g_shapes:
        box1 = get_bounding_box(pos, coords, stretch)
        box2 = get_bounding_box(existing_pos, existing_coords, stretch)
        
        if not (box1[1] + 2 < box2[0] or box2[1] + 2 < box1[0] or 
                box1[3] + 2 < box2[2] or box2[3] + 2 < box1[2]):
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
    scrn.setup(SCREEN_DIM_X, SCREEN_DIM_Y)
    scrn.bgcolor("black")
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
