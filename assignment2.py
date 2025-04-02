import turtle
import random
import time

# Step 1: Set up the drawing canvas
def setup_canvas():
    screen = turtle.Screen()
    screen.setup(width=0.7, height=0.7)
    screen.bgcolor("black")
    screen.mode("logo")
    turtle.hideturtle()
    turtle.speed(0)
    return screen

# Step 2: Load custom shapes from shapes.txt
def load_shapes(filename):
    shapes = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    name, coords = line.split(':')
                    name = name.strip()
                    coord_str = coords.strip()[1:-1]
                    coord_list = coord_str.split('),')
                    coordinates = []
                    for coord in coord_list:
                        coord = coord.strip()[1:] if coord.strip().startswith('(') else coord.strip()
                        coord = coord[:-1] if coord.endswith(')') else coord
                        x, y = map(float, coord.split(','))
                        coordinates.append((x, y))
                    shapes[name] = coordinates
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        exit(1)
    return shapes

# Step 3: Get user input
def get_user_input():
    stretch_value = float(input("Enter stretch value (default is 1): ") or 1)
    duration = float(input("Enter duration in seconds (default is 5): ") or 5)
    random_seed = int(input("Enter random seed (default is 1): ") or 1)
    terminate = input("Terminate immediately? (y/n, default is n): ") or 'n'
    return stretch_value, duration, random_seed, terminate.lower() == 'y'

# Step 4: collision detection
def do_shapes_touch(pos1, coords1, pos2, coords2, stretch):
    def get_precise_bounding_box(pos, coords, stretch):
        # Get stretched coordinates
        stretched_coords = [(x * stretch + pos[0], y * stretch + pos[1]) for x, y in coords]
        
        # Calculate precise bounding box with minimal buffer
        xs = [x for x, y in stretched_coords]
        ys = [y for x, y in stretched_coords]
        
        # Add minimal padding to prevent touching
        min_x = min(xs) - 1  # Reduced buffer
        max_x = max(xs) + 1  # Reduced buffer
        min_y = min(ys) - 1  # Reduced buffer
        max_y = max(ys) + 1  # Reduced buffer
        
        return min_x, max_x, min_y, max_y

    # Get bounding boxes with minimal padding
    box1 = get_precise_bounding_box(pos1, coords1, stretch)
    box2 = get_precise_bounding_box(pos2, coords2, stretch)

    # Check if bounding boxes are completely separate
    if (box1[1] + 2 < box2[0] or  # Left of
        box2[1] + 2 < box1[0] or  # Right of
        box1[3] + 2 < box2[2] or  # Below
        box2[3] + 2 < box1[2]):   # Above
        return False
    
    return True  # Shapes are too close or touching

# Step 5: Place shapes on the canvas
def place_shapes(shapes, stretch_value, duration, random_seed):
    random.seed(random_seed)
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "white", 
              "pink", "maroon", "navy", "forest green", "gold"]
    
    screen = turtle.getscreen()
    canvas_width = screen.window_width()
    canvas_height = screen.window_height()
    
    start_time = time.time()
    placed_polygons = []
    polygon_count = 0

    # Adjust placement to center the shapes
    x_offset = -canvas_width / 2
    y_offset = -canvas_height / 2

    max_attempts = 10000  # Kept high to ensure placement

    while time.time() - start_time < duration:
        # Select random shape and color
        shape_name = random.choice(list(shapes.keys()))
        coords = shapes[shape_name]
        color = random.choice(colors)
        
        # Try to find a non-touching position
        placed = False
        for _ in range(max_attempts):
            # Random position within canvas
            x = random.uniform(x_offset + 50, x_offset + canvas_width - 50)
            y = random.uniform(y_offset + 50, y_offset + canvas_height - 50)
            
            # Check for touches with existing shapes
            touches = any(
                do_shapes_touch((x, y), coords, pos, existing_coords, stretch_value)
                for pos, _, existing_coords in placed_polygons
            )
            
            # If they don't touch, place the shape
            if not touches:
                # Draw the shape
                turtle.penup()
                turtle.goto(x, y)
                turtle.pendown()
                turtle.color(color)
                turtle.begin_fill()
                for coord_x, coord_y in coords:
                    stretched_x = coord_x * stretch_value + x
                    stretched_y = coord_y * stretch_value + y
                    turtle.goto(stretched_x, stretched_y)
                # Close the shape
                first_x, first_y = coords[0]
                stretched_x = first_x * stretch_value + x
                stretched_y = first_y * stretch_value + y
                turtle.goto(stretched_x, stretched_y)
                turtle.end_fill()
                
                # Record the placed polygon
                placed_polygons.append(((x, y), shape_name, coords))
                polygon_count += 1
                placed = True
                break
        
        # If shape couldn't be placed, skip
        if not placed:
            print(f"Could not place shape: {shape_name}")

    elapsed_time = time.time() - start_time
    return polygon_count, elapsed_time

# Step 6: Main function
def main():
    screen = setup_canvas()
    shapes = load_shapes("shapes.txt")
    stretch_value, duration, random_seed, terminate_immediately = get_user_input()
    polygon_count, elapsed_time = place_shapes(shapes, stretch_value, duration, random_seed)

    start_time_str = time.strftime("%H:%M:%S", time.localtime(time.time() - elapsed_time))
    end_time_str = time.strftime("%H:%M:%S", time.localtime())
    print(f"124040006 {start_time_str} - {end_time_str} - {elapsed_time:.1f} - {polygon_count}")
    print(f"124040006, {polygon_count}")

    if not terminate_immediately:
        screen.mainloop()
    else:
        screen.bye()

if __name__ == "__main__":
    main()