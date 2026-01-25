from manim import *

class LoopLayersAnimation(Scene):
    def construct(self):
        # ===== FONT SIZE CONTROLS =====
        # Adjust these values to scale text sizes
        
        # Layer labels (Layer 1, Layer 2, Layer N)
        LAYER_FONT_SIZE = 24
        
        # Gate labels (Head, Exit Gate)
        GATE_FONT_SIZE = 20
        
        # Output labels (L_i, p_i)
        OUTPUT_FONT_SIZE = 24
        
        # Other labels
        INPUT_FONT_SIZE = 20
        TIMES_R_FONT_SIZE = 28
        CURRENT_LOOP_FONT_SIZE = 18
        DOTS_FONT_SIZE = 42
        
        # ===== END FONT SIZE CONTROLS =====
        
        # Colors matching the diagram
        LAYER_COLOR = "#E8A850"  # Orange/tan color for layers
        OUTPUT_COLOR = "#B8C8D8"  # Light blue-gray for outputs
        BOX_COLOR = "#1A1A2E"  # Dark blue-gray for background box
        
        # Consistent stroke width for all lines/arrows
        STROKE_WIDTH = 2.5
        TIP_SIZE = 0.08  # Smaller, consistent tip size
        
        # Helper function to create uniform arrows with FIXED tip size
        def make_arrow(start, end, buff=0.08):
            direction = normalize(end - start)
            actual_start = start + direction * buff
            actual_end = end - direction * buff
            
            line = Line(actual_start, actual_end, color=WHITE, stroke_width=STROKE_WIDTH)
            
            # Create triangle with fixed absolute size
            tip = Triangle(fill_opacity=1, fill_color=WHITE, stroke_width=0)
            tip.set_height(TIP_SIZE * 2)
            tip.set_width(TIP_SIZE * 1.5)
            tip.rotate(np.arctan2(direction[1], direction[0]) - PI/2)
            tip.move_to(actual_end)
            
            return VGroup(line, tip)
        
        # Helper function to create curved arrow from branch point pointing DOWN into target
        def make_branch_arrow(start, end):
            # Create a curved path from branch point to target, ending pointing down
            path = CubicBezier(
                start,
                start + DOWN * 0.3,
                end + UP * 0.4,
                end + UP * 0.08,
                color=WHITE,
                stroke_width=STROKE_WIDTH
            )
            
            # Arrow tip pointing DOWN
            tip = Triangle(fill_opacity=1, fill_color=WHITE, stroke_width=0)
            tip.set_height(TIP_SIZE * 2)
            tip.set_width(TIP_SIZE * 1.5)
            tip.rotate(PI)  # Point down
            tip.move_to(end + UP * 0.08)
            
            return VGroup(path, tip)
        
        # ===== STEP 1: Input token (smaller circle) =====
        input_circle = Circle(radius=0.18, color=WHITE, fill_opacity=0.1, stroke_width=2)
        input_label = Tex("Input token", font_size=INPUT_FONT_SIZE)
        input_label.next_to(input_circle, LEFT, buff=0.15)
        input_group = VGroup(input_circle, input_label)
        input_group.to_edge(UP, buff=0.6)
        input_group.shift(RIGHT * 0.5)
        
        self.play(
            FadeIn(input_circle, scale=0.8),
            FadeIn(input_label, shift=LEFT*0.2)
        )
        # self.wait(0.1)
        
        # ===== STEP 2: Arrow into Layer 1 & Layer 1 appears =====
        layer1 = RoundedRectangle(
            width=1.8, height=0.5, corner_radius=0.1,
            fill_color=LAYER_COLOR, fill_opacity=1, stroke_color=WHITE, stroke_width=1.5
        )
        layer1_text = Tex("Layer 1", font_size=LAYER_FONT_SIZE, color=BLACK)
        layer1_text.move_to(layer1.get_center())
        layer1_group = VGroup(layer1, layer1_text)
        layer1_group.next_to(input_circle, DOWN, buff=0.5)
        
        # Simple arrow from input to Layer 1
        arrow1 = make_arrow(input_circle.get_bottom(), layer1.get_top())
        
        self.play(Create(arrow1))
        self.play(FadeIn(layer1), FadeIn(layer1_text))
        # self.wait(0.1)
        
        # ===== STEP 3: Arrow into Layer 2 & Layer 2 appears =====
        layer2 = RoundedRectangle(
            width=1.8, height=0.5, corner_radius=0.1,
            fill_color=LAYER_COLOR, fill_opacity=1, stroke_color=WHITE, stroke_width=1.5
        )
        layer2_text = Tex("Layer 2", font_size=LAYER_FONT_SIZE, color=BLACK)
        layer2_text.move_to(layer2.get_center())
        layer2_group = VGroup(layer2, layer2_text)
        layer2_group.next_to(layer1_group, DOWN, buff=0.5)
        
        arrow2 = make_arrow(layer1.get_bottom(), layer2.get_top())
        
        self.play(Create(arrow2))
        self.play(FadeIn(layer2), FadeIn(layer2_text))
        # self.wait(0.1)
        
        # ===== STEP 4: Dots appear =====
        dots = MathTex(r"\vdots", font_size=DOTS_FONT_SIZE, color=WHITE)
        dots.next_to(layer2_group, DOWN, buff=0.3)
        
        self.play(FadeIn(dots))
        # self.wait(0.1)
        
        # ===== STEP 5: Layer N appears =====
        layerN = RoundedRectangle(
            width=1.8, height=0.5, corner_radius=0.1,
            fill_color=LAYER_COLOR, fill_opacity=1, stroke_color=WHITE, stroke_width=1.5
        )
        layerN_text = Tex("Layer N", font_size=LAYER_FONT_SIZE, color=BLACK)
        layerN_text.move_to(layerN.get_center())
        layerN_group = VGroup(layerN, layerN_text)
        layerN_group.next_to(dots, DOWN, buff=0.3)
        
        self.play(FadeIn(layerN), FadeIn(layerN_text))
        # self.wait(0.1)
        
        # ===== STEP 6: Dark shaded box appears behind layers =====
        box_top = layer1.get_top()[1] + 0.2
        box_bottom = layerN.get_bottom()[1] - 0.2
        box_center_y = (box_top + box_bottom) / 2
        box_height = box_top - box_bottom
        
        background_box = RoundedRectangle(
            width=2.4,
            height=box_height,
            corner_radius=0.15,
            fill_color=BOX_COLOR,
            fill_opacity=0.8,
            stroke_color=WHITE,
            stroke_width=1,
            stroke_opacity=0.4
        )
        background_box.move_to([layer1.get_center()[0], box_center_y, 0])
        
        background_box.z_index = -10
        self.add(background_box)
        self.bring_to_back(background_box)
        
        background_box.set_fill(opacity=0)
        background_box.set_stroke(opacity=0)
        
        self.play(
            background_box.animate.set_fill(opacity=0.8).set_stroke(opacity=0.4)
        )
        # self.wait(0.3)
        
        # ===== Define output elements =====
        exit_gate = RoundedRectangle(
            width=1.4, height=0.45, corner_radius=0.08,
            fill_color="#4A7C9B", fill_opacity=1, stroke_color=WHITE, stroke_width=1.5
        )
        exit_gate_text = Tex("Exit Gate", font_size=GATE_FONT_SIZE, color=WHITE)
        exit_gate_text.move_to(exit_gate.get_center())
        exit_gate_group = VGroup(exit_gate, exit_gate_text)
        exit_gate_group.next_to(layerN_group, DOWN, buff=1.2)
        exit_gate_group.shift(LEFT * 1.3)
        
        p_i_text = MathTex(r"p_i", font_size=OUTPUT_FONT_SIZE, color=OUTPUT_COLOR)
        p_i_text.next_to(exit_gate_group, DOWN, buff=0.5)
        
        head = RoundedRectangle(
            width=1.4, height=0.45, corner_radius=0.08,
            fill_color="#4A7C9B", fill_opacity=1, stroke_color=WHITE, stroke_width=1.5
        )
        head_text = Tex("Head", font_size=GATE_FONT_SIZE, color=WHITE)
        head_text.move_to(head.get_center())
        head_group = VGroup(head, head_text)
        head_group.next_to(layerN_group, DOWN, buff=1.2)
        head_group.shift(RIGHT * 1.3)
        
        L_i_text = MathTex(r"\mathcal{L}_i", font_size=OUTPUT_FONT_SIZE, color=OUTPUT_COLOR)
        L_i_text.next_to(head_group, DOWN, buff=0.5)
        
        # Y-shaped branching
        stem_start = layerN.get_bottom() + DOWN * 0.08
        branch_point = layerN.get_bottom() + DOWN * 0.5
        
        stem_line = Line(
            stem_start, branch_point,
            color=WHITE, stroke_width=STROKE_WIDTH
        )
        
        arrow_left = make_branch_arrow(branch_point, exit_gate.get_top())
        arrow_right = make_branch_arrow(branch_point, head.get_top())
        
        arrow_to_pi = make_arrow(exit_gate.get_bottom(), p_i_text.get_top(), buff=0.12)
        arrow_to_Li = make_arrow(head.get_bottom(), L_i_text.get_top(), buff=0.12)
        
        # ===== STEP 7: Stem appears =====
        self.play(Create(stem_line))
        
        # ===== STEP 8: Head and L_i first (right side) =====
        self.play(Create(arrow_right))
        self.play(FadeIn(head), FadeIn(head_text))
        self.play(Create(arrow_to_Li), FadeIn(L_i_text))
        
        # ===== STEP 9: Exit Gate and p_i (left side) =====
        self.play(Create(arrow_left))
        self.play(FadeIn(exit_gate), FadeIn(exit_gate_text))
        self.play(Create(arrow_to_pi), FadeIn(p_i_text))
        
        # self.wait(0.5)


        # ===== STEP 10: Feedback loop =====
        # Start point: on the stem line, shortly after Layer N bottom
        feedback_start = stem_start + DOWN * 0.15

        # End point: top of Layer 1 (where input line connects)
        feedback_end = layer1.get_top() + UP * 0.08

        # Left offset for the arc (further left, in line with ×R)
        left_x = background_box.get_left()[0] - 1.2

        # Define corner points
        bottom_corner = np.array([left_x, feedback_start[1], 0])
        top_corner = np.array([left_x, feedback_end[1], 0])

        arc_radius = 0.3
        bottom_offset = 0.1
        top_offset = 0.25
        dash_density = 8
        vertical_tip_scale = 1.5   # Multiplier for vertical arrow head size (1.0 = same as others)
        vertical_shift = 0.4      # Positive = right, negative = left
        current_loop_vertical = -1.4 # Positive = down, negative = up
        current_loop_horizontal = -2.4  # Positive = right, negative = left

        # Adjusted left_x with shift
        left_x = background_box.get_left()[0] - 1.2 + vertical_shift

        # Define corner points USING left_x (inherits the shift)
        bottom_corner = np.array([left_x, feedback_start[1], 0])
        top_corner = np.array([left_x, feedback_end[1], 0])

        # BOTTOM: shifted DOWN
        bottom_line = Line(
            feedback_start + DOWN * bottom_offset,
            bottom_corner + RIGHT * arc_radius + DOWN * bottom_offset,
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )

        bottom_arc = ArcBetweenPoints(
            bottom_corner + RIGHT * arc_radius + DOWN * bottom_offset,
            bottom_corner + UP * arc_radius,
            angle=-PI/2,
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )

        # VERTICAL: unchanged
        vertical_line = Line(
            bottom_corner + UP * arc_radius,
            top_corner + DOWN * arc_radius,
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )

        # TOP: shifted UP - use CubicBezier for smooth connection
        arc_control = 0.4  # Controls the curve tightness

        top_arc = CubicBezier(
            top_corner + DOWN * arc_radius,                                    # Start (matches vertical line end)
            top_corner + DOWN * arc_radius + UP * arc_control,                 # Control 1: leaves going UP
            top_corner + RIGHT * arc_radius + UP * top_offset + LEFT * arc_control,  # Control 2: arrives going RIGHT
            top_corner + RIGHT * arc_radius + UP * top_offset,                 # End (matches top line start)
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )

        top_line = Line(
            top_corner + RIGHT * arc_radius + UP * top_offset,
            feedback_end + UP * top_offset,
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )

        # Dash each segment proportionally to its length
        def dash_segment(segment, density=dash_density, ratio=0.6):
            length = segment.get_arc_length()
            num_dashes = max(1, int(length * density))
            return DashedVMobject(segment, num_dashes=num_dashes, dashed_ratio=ratio)

        # Arrow tip pointing DOWN into Layer 1
        feedback_arrow_tip = Triangle(fill_opacity=1, fill_color=WHITE, stroke_width=0)
        feedback_arrow_tip.set_height(TIP_SIZE * 2)
        feedback_arrow_tip.set_width(TIP_SIZE * 1.5)
        feedback_arrow_tip.rotate(PI)  # Point down
        feedback_arrow_tip.move_to(feedback_end)

        # Arrow tip on vertical line pointing UP
        vertical_arrow_tip = Triangle(fill_opacity=1, fill_color=WHITE, stroke_width=0)
        vertical_arrow_tip.set_height(TIP_SIZE * 2 * vertical_tip_scale)
        vertical_arrow_tip.set_width(TIP_SIZE * 1.5 * vertical_tip_scale)
        vertical_center_y = (bottom_corner[1] + top_corner[1]) / 2
        arrow_tip_pos = np.array([left_x, vertical_center_y, 0])
        vertical_arrow_tip.move_to(arrow_tip_pos)

        # Split vertical line into two parts: below and above the arrow tip
        vertical_line_bottom = Line(
            bottom_corner + UP * arc_radius,
            arrow_tip_pos,
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )
        vertical_line_top = Line(
            arrow_tip_pos,
            top_corner + DOWN * arc_radius,
            color=WHITE,
            stroke_width=STROKE_WIDTH
        )

        # Create dashed versions of all segments
        dashed_bottom_line = dash_segment(bottom_line)
        dashed_bottom_arc = dash_segment(bottom_arc)
        dashed_vertical_bottom = dash_segment(vertical_line_bottom)
        dashed_vertical_top = dash_segment(vertical_line_top)
        dashed_top_arc = dash_segment(top_arc)
        dashed_top_line = dash_segment(top_line)

        # Animate sequentially with arrow tip appearing as vertical line passes through
        self.play(Create(dashed_bottom_line), run_time=0.25)
        self.play(Create(dashed_bottom_arc), run_time=0.2)
        self.play(Create(dashed_vertical_bottom), run_time=0.3)
        self.play(FadeIn(vertical_arrow_tip, scale=1.2), run_time=0.15)
        self.play(Create(dashed_vertical_top), run_time=0.3)
        self.play(Create(dashed_top_arc), run_time=0.2)
        self.play(Create(dashed_top_line), run_time=0.25)
        self.play(FadeIn(feedback_arrow_tip))


        # ===== STEP 11: ×R and Current Loop = i =====
        times_R = MathTex(r"\times R", font_size=TIMES_R_FONT_SIZE)
        times_R.next_to(vertical_line, RIGHT, buff=0.15)

        current_loop = Tex(r"Current Loop = $i$", font_size=CURRENT_LOOP_FONT_SIZE, color=WHITE)
        current_loop.next_to(exit_gate_group, DOWN, buff=0.15)
        current_loop.shift(RIGHT * 2.5 + DOWN * current_loop_vertical + RIGHT * current_loop_horizontal)

        self.play(FadeIn(times_R, shift=LEFT*0.2))
        self.play(FadeIn(current_loop, shift=UP*0.1))
        
        self.wait(1.5)