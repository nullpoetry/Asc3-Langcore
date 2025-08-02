import numpy as np
from rich.console import Console
from rich.color import Color
from rich.style import Style
from rich.text import Text
import math

# Initialize the console for colored output
console = Console()

def generate_paper3d_design(width: int, height: int, depth: int,
                           cell_size: float = 1.0,
                           perspective_factor: float = 0.5) -> List[List[str]]:
    """
    Generates a 2D ASCII representation of a 3D grid, simulating a paper-like
    geometric pattern.

    Args:
        width (int): The width of the 3D grid (x-axis).
        height (int): The height of the 3D grid (y-axis).
        depth (int): The depth of the 3D grid (z-axis).
        cell_size (float): The size of each cell in the grid.
        perspective_factor (float): Controls the perspective distortion.

    Returns:
        List[List[str]]: A 2D list of characters representing the design.
    """
    # Create an empty canvas
    canvas_width = 80
    canvas_height = 40
    canvas = [[' ' for _ in range(canvas_width)] for _ in range(canvas_height)]
    
    # Define a set of characters for drawing the lines
    characters = {
        'x_line': '-',
        'y_line': '|',
        'z_line': '/',
        'node': '•'
    }

    # Define color styles
    node_style = Style(color=Color.from_rgb(255, 165, 0)) # Orange
    x_style = Style(color=Color.from_rgb(0, 180, 255))   # Cyan
    y_style = Style(color=Color.from_rgb(255, 0, 180))   # Magenta
    z_style = Style(color=Color.from_rgb(180, 255, 0))   # Yellow

    # Center the projection
    center_x = canvas_width // 2
    center_y = canvas_height // 2

    def project_3d_to_2d(x: float, y: float, z: float) -> Tuple[int, int]:
        """Projects a 3D point to 2D screen coordinates with perspective."""
        # Scale the coordinates for projection
        screen_x = center_x + x * (1 - z * perspective_factor)
        screen_y = center_y + y * (1 - z * perspective_factor)
        return int(round(screen_x)), int(round(screen_y))

    # Iterate through the 3D grid and draw the lines and nodes
    for i in range(width + 1):
        for j in range(height + 1):
            for k in range(depth + 1):
                x, y, z = (i - width / 2) * cell_size, \
                          (j - height / 2) * cell_size, \
                          (k - depth / 2) * cell_size

                # Project the current node
                proj_x, proj_y = project_3d_to_2d(x, y, z)
                if 0 <= proj_x < canvas_width and 0 <= proj_y < canvas_height:
                    canvas[proj_y][proj_x] = node_style.render(characters['node'])

                # Draw x-axis lines
                if i < width:
                    next_x, next_y, next_z = ((i + 1) - width / 2) * cell_size, \
                                             (j - height / 2) * cell_size, \
                                             (k - depth / 2) * cell_size
                    proj_x2, proj_y2 = project_3d_to_2d(next_x, next_y, next_z)
                    # Draw a line between the two points
                    if 0 <= proj_y < canvas_height and 0 <= proj_y2 < canvas_height:
                        start = min(proj_x, proj_x2)
                        end = max(proj_x, proj_x2)
                        for cx in range(start + 1, end):
                            if 0 <= cx < canvas_width:
                                canvas[proj_y][cx] = x_style.render(characters['x_line'])
                
                # Draw y-axis lines
                if j < height:
                    next_x, next_y, next_z = (i - width / 2) * cell_size, \
                                             ((j + 1) - height / 2) * cell_size, \
                                             (k - depth / 2) * cell_size
                    proj_x2, proj_y2 = project_3d_to_2d(next_x, next_y, next_z)
                    # Draw a line between the two points
                    if 0 <= proj_x < canvas_width and 0 <= proj_x2 < canvas_width:
                        start = min(proj_y, proj_y2)
                        end = max(proj_y, proj_y2)
                        for cy in range(start + 1, end):
                            if 0 <= cy < canvas_height:
                                canvas[cy][proj_x] = y_style.render(characters['y_line'])

                # Draw z-axis lines
                if k < depth:
                    next_x, next_y, next_z = (i - width / 2) * cell_size, \
                                             (j - height / 2) * cell_size, \
                                             ((k + 1) - depth / 2) * cell_size
                    proj_x2, proj_y2 = project_3d_to_2d(next_x, next_y, next_z)
                    # Draw a line between the two points
                    for step in np.linspace(0, 1, num=10):
                        cx = int(round(proj_x + (proj_x2 - proj_x) * step))
                        cy = int(round(proj_y + (proj_y2 - proj_y) * step))
                        if 0 <= cx < canvas_width and 0 <= cy < canvas_height:
                            canvas[cy][cx] = z_style.render(characters['z_line'])

    # Flatten the canvas to a list of strings
    output_lines = ["".join(row) for row in canvas]
    return output_lines

if __name__ == "__main__":
    # Define the parameters for the design
    grid_width = 8
    grid_height = 8
    grid_depth = 8
    cell_size = 3.0
    perspective = 0.5

    # Generate the design
    design_output = generate_paper3d_design(grid_width, grid_height, grid_depth, cell_size, perspective)

    # Print the output to the console
    console.print("\n" + "=" * 30 + " 3D Paper Grid Design " + "=" * 30 + "\n", style="bold white")
    for line in design_output:
        console.print(line)
    console.print("\n" + "=" * 82 + "\n", style="bold white")
                    
