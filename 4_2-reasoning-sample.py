from manim import *

class NeuralNetworkCalculation(Scene):
    def construct(self):
        # Colors
        bg_circle_color = "#6EB5D9"
        node_color = WHITE
        text_color = WHITE
        arrow_color = WHITE
        
        # Create the neural network visualization
        # Background circle - shifted left
        bg_circle = Circle(radius=2, color=bg_circle_color, fill_opacity=1, stroke_width=0)
        bg_circle.shift(LEFT * 1.5)  # Shift entire network left
        
        # Neural network nodes - 3 layers (3x4x3 structure)
        node_radius = 0.2  # Slightly larger neurons
        layer_spacing = 1.1  # Increased horizontal spacing
        
        layer_1 = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=1, stroke_width=0) 
                          for _ in range(3)])
        layer_1.arrange(DOWN, buff=0.5)
        layer_1.shift(LEFT * (layer_spacing + 1.5))  # Adjusted for circle shift
        
        layer_2 = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=1, stroke_width=0) 
                          for _ in range(4)])
        layer_2.arrange(DOWN, buff=0.4)
        layer_2.shift(LEFT * 1.5)  # Adjusted for circle shift
        
        layer_3 = VGroup(*[Circle(radius=node_radius, color=node_color, fill_opacity=1, stroke_width=0) 
                          for _ in range(3)])
        layer_3.arrange(DOWN, buff=0.5)
        layer_3.shift(LEFT * (1.5 - layer_spacing))  # Adjusted for circle shift
        
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
        
        # Group all neural network elements (no dashed line)
        neural_net = VGroup(connections, layer_1, layer_2, layer_3)
        network_group = VGroup(bg_circle, neural_net)
        
        # Arrow styling (uniform for both) - bigger and white
        arrow_config = {
            "color": arrow_color,
            "stroke_width": 4,
            "max_tip_length_to_length_ratio": 0.35,
            "tip_length": 0.4
        }
        
        # Input text template (for positioning)
        input_template = MathTex(r"(6 \times 4) / 2", font_size=42, color=text_color)
        input_template.next_to(bg_circle, LEFT, buff=1.4)
        
        input_arrow = Arrow(
            start=input_template.get_right() + RIGHT * 0.2,
            end=bg_circle.get_left() + LEFT * 0.1,
            **arrow_config
        )
        
        # Output text templates - multiple possible answers
        output_line1 = MathTex(r"6", font_size=38, color=text_color)
        output_line2 = MathTex(r"12", font_size=38, color=text_color)
        output_line3 = Tex(r"Ask a calculator, man", font_size=32, color=text_color)
        output_line4 = MathTex(r"24", font_size=38, color=text_color)
        output_line5 = MathTex(r"67", font_size=38, color=text_color)
        output_group = VGroup(output_line1, output_line2, output_line3, output_line4, output_line5).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        output_group.next_to(bg_circle, RIGHT, buff=1.4)
        
        output_arrow = Arrow(
            start=bg_circle.get_right() + RIGHT * 0.1,
            end=output_group.get_left() + LEFT * 0.2,
            **arrow_config
        )
        
        # Typing cursor
        cursor = Line(UP * 0.25, DOWN * 0.25, color=text_color, stroke_width=3)
        
        # Animation sequence
        # 1. Show the neural network
        self.play(FadeIn(bg_circle), run_time=0.5)
        self.play(
            Create(connections, lag_ratio=0.01),
            FadeIn(layer_1, layer_2, layer_3),
            run_time=1.5
        )
        self.wait(0.5)
        
        # Helper function to type a line character by character
        def type_line_chars(text_string, start_pos, cursor_y, font_size, cursor_obj, char_delay=0.08):
            typed_chars = VGroup()
            current_x = start_pos[0]
            
            for i, char in enumerate(text_string):
                # Handle spaces by just moving cursor
                if char == ' ':
                    current_x += 0.15  # Space width
                    new_cursor_pos = np.array([current_x, cursor_y, 0])
                    self.play(
                        cursor_obj.animate.move_to(new_cursor_pos),
                        run_time=char_delay * 0.5
                    )
                    continue
                
                # Use Tex for all characters (consistent LaTeX font)
                if char == '×':
                    char_obj = MathTex(r"\times", font_size=font_size, color=text_color)
                elif char == ',':
                    char_obj = Tex(r",", font_size=font_size, color=text_color)
                else:
                    char_obj = Tex(char, font_size=font_size, color=text_color)
                
                # Position the character
                char_obj.move_to(np.array([current_x, cursor_y, 0]), aligned_edge=LEFT)
                
                typed_chars.add(char_obj)
                
                # Update current_x for next character
                char_width = char_obj.get_width()
                current_x += char_width + 0.02
                
                new_cursor_pos = np.array([current_x, cursor_y, 0])
                
                self.play(
                    FadeIn(char_obj, shift=DOWN * 0.05),
                    cursor_obj.animate.move_to(new_cursor_pos),
                    run_time=char_delay
                )
            return typed_chars
        
        # 2. Show input text and arrow statically (no animation)
        input_display = MathTex(r"(6 \times 4) / 2", font_size=42, color=text_color)
        input_display.move_to(input_template.get_center())
        self.play(FadeIn(input_display), FadeIn(input_arrow), run_time=0.5)
        
        self.wait(0.3)
        
        # 3. Animate "processing" through the network
        # Pulse effect on layers
        pulse_color = YELLOW
        for layer in [layer_1, layer_2, layer_3]:
            self.play(
                layer.animate.set_color(pulse_color),
                rate_func=there_and_back,
                run_time=0.4
            )
            layer.set_color(WHITE)
        
        self.wait(0.3)
        
        # 4. Show output arrow
        self.play(Create(output_arrow), run_time=0.5)
        
        # 5. Type output with cursor - 5 lines character by character
        cursor2 = Line(UP * 0.25, DOWN * 0.25, color=text_color, stroke_width=3)
        
        # Output text strings
        output_str1 = "6"
        output_str2 = "12"
        output_str3 = "Ask a calculator, man"
        output_str4 = "24"
        output_str5 = "67"
        
        # Position cursor at first line
        first_line_y = output_line1.get_center()[1]
        cursor2.move_to(output_line1.get_left() + LEFT * 0.1)
        cursor2.set_y(first_line_y)
        self.add(cursor2)
        
        # Blink cursor
        self.play(cursor2.animate.set_opacity(0), run_time=0.2)
        self.play(cursor2.animate.set_opacity(1), run_time=0.2)
        
        # Type line 1: "6"
        line1_start = output_line1.get_left()
        type_line_chars(output_str1, np.array([line1_start[0], first_line_y, 0]), first_line_y, 38, cursor2, char_delay=0.08)
        
        # Move to line 2
        self.play(cursor2.animate.set_opacity(0), run_time=0.1)
        second_line_y = output_line2.get_center()[1]
        new_pos = output_line2.get_left() + LEFT * 0.1
        new_pos[1] = second_line_y
        cursor2.move_to(new_pos)
        self.play(cursor2.animate.set_opacity(1), run_time=0.1)
        
        # Type line 2: "12" - save reference for tick mark
        line2_start = output_line2.get_left()
        typed_12 = type_line_chars(output_str2, np.array([line2_start[0], second_line_y, 0]), second_line_y, 38, cursor2, char_delay=0.08)
        
        # Move to line 3
        self.play(cursor2.animate.set_opacity(0), run_time=0.1)
        third_line_y = output_line3.get_center()[1]
        new_pos = output_line3.get_left() + LEFT * 0.1
        new_pos[1] = third_line_y
        cursor2.move_to(new_pos)
        self.play(cursor2.animate.set_opacity(1), run_time=0.1)
        
        # Type line 3: "Ask a calculator, man" - reveal character by character from pre-rendered Tex
        line3_display = Tex(r"Ask a calculator, man", font_size=32, color=text_color)
        line3_display.move_to(output_line3.get_center())
        
        # Iterate through each glyph in the Tex object and fade them in
        for i, glyph in enumerate(line3_display[0]):
            cursor_pos = np.array([glyph.get_right()[0] + 0.08, third_line_y, 0])
            self.play(
                FadeIn(glyph, shift=DOWN * 0.05),
                cursor2.animate.move_to(cursor_pos),
                run_time=0.06
            )
        
        # Move to line 4
        self.play(cursor2.animate.set_opacity(0), run_time=0.1)
        fourth_line_y = output_line4.get_center()[1]
        new_pos = output_line4.get_left() + LEFT * 0.1
        new_pos[1] = fourth_line_y
        cursor2.move_to(new_pos)
        self.play(cursor2.animate.set_opacity(1), run_time=0.1)
        
        # Type line 4: "24"
        line4_start = output_line4.get_left()
        type_line_chars(output_str4, np.array([line4_start[0], fourth_line_y, 0]), fourth_line_y, 38, cursor2, char_delay=0.08)
        
        # Move to line 5
        self.play(cursor2.animate.set_opacity(0), run_time=0.1)
        fifth_line_y = output_line5.get_center()[1]
        new_pos = output_line5.get_left() + LEFT * 0.1
        new_pos[1] = fifth_line_y
        cursor2.move_to(new_pos)
        self.play(cursor2.animate.set_opacity(1), run_time=0.1)
        
        # Type line 5: "67"
        line5_start = output_line5.get_left()
        type_line_chars(output_str5, np.array([line5_start[0], fifth_line_y, 0]), fifth_line_y, 38, cursor2, char_delay=0.08)
        
        # Fade out cursor
        self.play(FadeOut(cursor2), run_time=0.3)
        
        self.wait(0.5)
        
        # 6. Add tick mark next to "12"
        tick = MathTex(r"\checkmark", font_size=38, color=GREEN)
        tick.next_to(typed_12, RIGHT, buff=0.2)
        self.play(FadeIn(tick, scale=1.5), run_time=0.5)
        
        self.wait(1)
