from manim import *
import numpy as np

class NeuralNetworkCalculation(Scene):
    def construct(self):
        # Colors
        bg_circle_color = "#6EB5D9"
        node_color = WHITE
        text_color = WHITE
        arrow_color = WHITE
        loop_color = WHITE
        
        # Create the neural network visualization
        bg_circle = Circle(radius=2, color=bg_circle_color, fill_opacity=1, stroke_width=0)
        bg_circle.shift(LEFT * 1.5)
        
        # Neural network nodes
        node_radius = 0.2
        layer_spacing = 1.1
        
        layer_1 = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=1, stroke_width=0) 
                          for _ in range(3)])
        layer_1.arrange(DOWN, buff=0.5)
        layer_1.shift(LEFT * (layer_spacing + 1.5))
        
        layer_2 = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=1, stroke_width=0) 
                          for _ in range(4)])
        layer_2.arrange(DOWN, buff=0.4)
        layer_2.shift(LEFT * 1.5)
        
        layer_3 = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=1, stroke_width=0) 
                          for _ in range(3)])
        layer_3.arrange(DOWN, buff=0.5)
        layer_3.shift(LEFT * (1.5 - layer_spacing))
        
        # Connections between layers
        connections = VGroup()
        for n1 in layer_1:
            for n2 in layer_2:
                line = Line(n1.get_center(), n2.get_center(), 
                           color=WHITE, stroke_width=1.5, stroke_opacity=0.7)
                connections.add(line)
        
        for n2 in layer_2:
            for n3 in layer_3:
                line = Line(n2.get_center(), n3.get_center(), 
                           color=WHITE, stroke_width=1.5, stroke_opacity=0.7)
                connections.add(line)
        
        neural_net = VGroup(connections, layer_1, layer_2, layer_3)
        
        # Create feedback loop - a fuller elliptical loop underneath the blue circle
        network_center = bg_circle.get_center()
        
        # Loop start/end points on lower part of the blue circle
        loop_start = network_center + np.array([1.4, -1.4, 0])  # Bottom-right of circle
        loop_end = network_center + np.array([-1.4, -1.4, 0])   # Bottom-left of circle
        
        # Create the loop path as a partial ellipse (no arrow head, just the arc)
        feedback_loop_path = ArcBetweenPoints(
            start=loop_start,
            end=loop_end,
            angle=-PI * 1.1,  # Fuller loop going downward
            color=loop_color,
            stroke_width=2.5
        )
        
        # Create the inner path for characters (very close to the loop line)
        inner_loop_start = loop_start + np.array([-0.08, 0.08, 0])
        inner_loop_end = loop_end + np.array([0.08, 0.08, 0])
        
        # Arrow styling
        arrow_config = {
            "color": arrow_color,
            "stroke_width": 4,
            "max_tip_length_to_length_ratio": 0.35,
            "tip_length": 0.4
        }
        
        # Input text template
        input_template = MathTex(r"(6 \times 4) / 2", font_size=42, color=text_color)
        input_template.next_to(bg_circle, LEFT, buff=1.4)
        
        input_arrow = Arrow(
            start=input_template.get_right() + RIGHT * 0.2,
            end=bg_circle.get_left() + LEFT * 0.1,
            **arrow_config
        )
        
        # Output text templates
        output_line1 = MathTex(r"6 \times 4 = 6 + 6 + 6 + 6", font_size=38, color=text_color)
        output_line2 = MathTex(r"= 24", font_size=38, color=text_color)
        output_line3 = MathTex(r"24/2 = 12", font_size=38, color=text_color)
        output_group = VGroup(output_line1, output_line2, output_line3).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        output_group.next_to(bg_circle, RIGHT, buff=1.4)
        
        output_arrow = Arrow(
            start=bg_circle.get_right() + RIGHT * 0.1,
            end=output_group.get_left() + LEFT * 0.2,
            **arrow_config
        )
        
        # Typing cursor
        cursor = Line(UP * 0.25, DOWN * 0.25, color=text_color, stroke_width=3)
        
        # Helper function to type input character by character
        def type_line_chars_simple(text_string, start_pos, cursor_y, font_size, cursor_obj, char_delay=0.08):
            typed_chars = VGroup()
            current_x = start_pos[0]
            
            for char in text_string:
                if char == ' ':
                    current_x += 0.15
                    new_cursor_pos = np.array([current_x, cursor_y, 0])
                    self.play(cursor_obj.animate.move_to(new_cursor_pos), run_time=char_delay * 0.5)
                    continue
                
                if char in ['×', '=', '+', '/']:
                    if char == '×':
                        char_obj = MathTex(r"\times", font_size=font_size, color=text_color)
                    else:
                        char_obj = MathTex(char, font_size=font_size, color=text_color)
                else:
                    char_obj = Text(char, font_size=int(font_size * 0.55), color=text_color)
                
                char_obj.move_to(np.array([current_x, cursor_y, 0]), aligned_edge=LEFT)
                typed_chars.add(char_obj)
                char_width = char_obj.get_width()
                current_x += char_width + 0.05
                new_cursor_pos = np.array([current_x, cursor_y, 0])
                
                self.play(
                    FadeIn(char_obj, shift=DOWN * 0.05),
                    cursor_obj.animate.move_to(new_cursor_pos),
                    run_time=char_delay
                )
            return typed_chars
        
        # Function to create a character object
        def create_char_obj(char, font_size):
            if char in ['×', '=', '+', '/']:
                if char == '×':
                    return MathTex(r"\times", font_size=font_size, color=text_color)
                else:
                    return MathTex(char, font_size=font_size, color=text_color)
            else:
                return Text(char, font_size=int(font_size * 0.55), color=text_color)
        
        # Function to generate characters - text appears at output while duplicate travels loop
        def generate_chars_with_loop(text_string, line_y, start_x, font_size):
            typed_chars = VGroup()
            current_x = start_x
            
            for char in text_string:
                if char == ' ':
                    current_x += 0.15
                    continue
                
                # Create the final character (appears at output)
                char_obj = create_char_obj(char, font_size)
                final_pos = np.array([current_x + char_obj.get_width()/2, line_y, 0])
                char_obj.move_to(final_pos)
                char_obj.set_opacity(0)
                
                # Create a duplicate that travels the loop (very close to the arc)
                loop_char = create_char_obj(char, font_size)
                loop_char.move_to(inner_loop_start)
                loop_char.set_opacity(0.7)
                
                # Create the inner loop travel path (very close to the visible arc)
                inner_travel_path = ArcBetweenPoints(
                    start=inner_loop_start,
                    end=inner_loop_end,
                    angle=-PI * 1.05,
                )
                
                self.add(char_obj, loop_char)
                
                # Animate: character fades in at final position while duplicate starts
                self.play(
                    char_obj.animate.set_opacity(1),
                    loop_char.animate.set_opacity(1),
                    run_time=0.2
                )
                
                # Duplicate travels the loop (2x slower = 0.7s)
                self.play(
                    MoveAlongPath(loop_char, inner_travel_path),
                    run_time=0.7,
                    rate_func=smooth
                )
                
                # Character enters network: start fading out immediately while layer 1 lights up
                self.play(
                    layer_1.animate.set_color(YELLOW),
                    loop_char.animate.set_opacity(0),
                    run_time=0.08
                )
                # Layer 2 lights up, layer 1 fades
                self.play(
                    layer_1.animate.set_color(WHITE),
                    layer_2.animate.set_color(YELLOW),
                    run_time=0.08
                )
                # Layer 3 lights up, layer 2 fades
                self.play(
                    layer_2.animate.set_color(WHITE),
                    layer_3.animate.set_color(YELLOW),
                    run_time=0.08
                )
                # Layer 3 fades back, remove loop char
                self.play(
                    layer_3.animate.set_color(WHITE),
                    run_time=0.08
                )
                self.remove(loop_char)
                
                typed_chars.add(char_obj)
                current_x += char_obj.get_width() + 0.05
            
            return typed_chars
        
        # === ANIMATION SEQUENCE ===
        
        # 1. Show the neural network
        self.play(FadeIn(bg_circle), run_time=0.5)
        self.play(
            Create(connections, lag_ratio=0.01),
            FadeIn(layer_1, layer_2, layer_3),
            run_time=1.5
        )
        self.wait(0.5)
        
        # 2. Type the input with cursor
        input_text_str = "(6 × 4) / 2"
        input_start_pos = input_template.get_left()
        input_line_y = input_template.get_center()[1]
        
        cursor.move_to(input_start_pos + LEFT * 0.1)
        cursor.set_y(input_line_y)
        self.add(cursor)
        
        for _ in range(2):
            self.play(cursor.animate.set_opacity(0), run_time=0.25)
            self.play(cursor.animate.set_opacity(1), run_time=0.25)
        
        type_line_chars_simple(input_text_str, np.array([input_start_pos[0], input_line_y, 0]), input_line_y, 42, cursor, char_delay=0.08)
        
        self.play(cursor.animate.set_opacity(0), run_time=0.2)
        self.play(cursor.animate.set_opacity(1), run_time=0.2)
        self.play(FadeOut(cursor), run_time=0.2)
        
        self.wait(0.3)
        
        # 3. Show arrow feeding into network
        self.play(Create(input_arrow), run_time=0.5)
        
        # 4. Initial processing pulse through the network
        for layer in [layer_1, layer_2, layer_3]:
            self.play(
                layer.animate.set_color(YELLOW),
                rate_func=there_and_back,
                run_time=0.4
            )
            layer.set_color(WHITE)
        
        self.wait(0.3)
        
        # 5. Show output arrow
        self.play(Create(output_arrow), run_time=0.5)
        
        # 6. Show the feedback loop (just the arc, no arrow head)
        self.play(
            Create(feedback_loop_path),
            run_time=0.6
        )
        
        self.wait(0.3)
        
        # 7. Generate output - text appears while duplicates travel the loop
        output_str1 = "6 × 4 = 6 + 6 + 6 + 6"
        output_str2 = "= 24"
        output_str3 = "24/2 = 12"
        
        first_line_y = output_line1.get_center()[1]
        line1_start_x = output_line1.get_left()[0]
        generate_chars_with_loop(output_str1, first_line_y, line1_start_x, 38)
        
        self.wait(0.1)
        
        second_line_y = output_line2.get_center()[1]
        line2_start_x = output_line2.get_left()[0]
        generate_chars_with_loop(output_str2, second_line_y, line2_start_x, 38)
        
        self.wait(0.1)
        
        third_line_y = output_line3.get_center()[1]
        line3_start_x = output_line3.get_left()[0]
        generate_chars_with_loop(output_str3, third_line_y, line3_start_x, 38)
        
        self.wait(1.5)