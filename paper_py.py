# paper_py.py
#
# This file contains the core logic for generating and rendering
# ASC3/4 symbolic art. The Asc3Core class provides a canvas-like
# interface for creating text-based visuals with defined styles and fonts.

class Asc3Core:
    """
    A core class for generating structured ASCII art.

    Manages a canvas, defines custom fonts, and provides methods
    to write text and set styles, ultimately rendering the final
    text-based output.
    """
    def __init__(self, canvas_width=80, canvas_height=24, fill_char=' '):
        """
        Initializes the Asc3Core canvas and state.

        Args:
            canvas_width (int): The width of the drawing canvas.
            canvas_height (int): The height of the drawing canvas.
            fill_char (str): The character used to fill the canvas initially.
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.fill_char = fill_char
        self.styles = {'default': {'color': 'white'}}
        self.fonts = {}
        self.current_style_name = 'default'
        self.current_style = self.styles[self.current_style_name]
        self.cursor_x = 0
        self.cursor_y = 0
        self.canvas = self._create_canvas()
    
    def _create_canvas(self):
        """
        Creates an empty canvas filled with the specified character.
        """
        return [
            [self.fill_char for _ in range(self.canvas_width)]
            for _ in range(self.canvas_height)
        ]

    def define_font(self, font_name, font_map):
        """
        Defines a new font for use on the canvas.

        A font is a dictionary where each key is a character and its value
        is a list of strings representing the character's ASCII art shape.

        Args:
            font_name (str): The name to assign to the new font.
            font_map (dict): A dictionary mapping characters to their ASCII art.
        """
        self.fonts[font_name] = font_map

    def set_style(self, style_name='default', color='white', x=0, y=0):
        """
        Sets the current drawing style and cursor position.

        Args:
            style_name (str): The name of the style to set.
            color (str): The color for the text (e.g., 'cyan', 'magenta').
            x (int): The new horizontal cursor position.
            y (int): The new vertical cursor position.
        """
        # Note: This is a simplified style system. A full implementation
        # would need to handle ANSI color codes or other formatting.
        if style_name not in self.styles:
            self.styles[style_name] = {'color': color}
        self.current_style_name = style_name
        self.current_style = self.styles[style_name]
        self.cursor_x = x
        self.cursor_y = y

    def write_text(self, font_name, text):
        """
        Writes a string of text to the canvas using a defined font.

        Args:
            font_name (str): The name of the font to use.
            text (str): The text to write.
        """
        if font_name not in self.fonts:
            print(f"Error: Font '{font_name}' not defined.")
            return

        font_map = self.fonts[font_name]
        
        # Iterate through each character in the text
        for char in text:
            if char in font_map:
                char_art = font_map[char]
                char_height = len(char_art)
                char_width = len(char_art[0])

                # Draw each line of the character
                for y_offset, line in enumerate(char_art):
                    for x_offset, pixel in enumerate(line):
                        canvas_x = self.cursor_x + x_offset
                        canvas_y = self.cursor_y + y_offset
                        
                        # Only draw if the pixel is not a space
                        if pixel != ' ':
                            if 0 <= canvas_x < self.canvas_width and 0 <= canvas_y < self.canvas_height:
                                self.canvas[canvas_y][canvas_x] = pixel

                # Advance the cursor for the next character
                self.cursor_x += char_width + 1  # Add a space between characters
            else:
                print(f"Warning: Character '{char}' not in font '{font_name}'.")

    def render(self):
        """
        Renders the entire canvas into a single string.

        Returns:
            str: The final rendered ASCII art.
        """
        # This simple render method joins the canvas rows.
        # A more advanced version would add ANSI color codes based on styles.
        return "\n".join(["".join(row) for row in self.canvas])


# Example Usage (for testing purposes)
if __name__ == '__main__':
    # 1. Create a new core instance with a specific size
    core = Asc3Core(canvas_width=80, canvas_height=10, fill_char='.')
    
    # 2. Define a custom font for 'A' and 'I'
    custom_font = {
        'A': [
            '  _  ',
            ' / \\ ',
            '/___\\',
        ],
        'I': [
            ' ___ ',
            '  |  ',
            '  |  ',
        ]
    }
    core.define_font('my_font', custom_font)

    # 3. Set a style and write some text
    core.set_style(color='cyan', x=2, y=1)
    core.write_text('my_font', 'AI')

    # 4. Render and print the final output
    final_art = core.render()
    print(final_art)

