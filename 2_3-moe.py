from manim import *

class DenseToMoE(Scene):
    def construct(self):
        self.camera.background_color = "#0a0a0f"
        
        # Colors
        box_color = "#4a6fa5"
        text_color = WHITE
        arrow_color = "#6a8fc5"
        highlight_color = "#7aa2d4"
        
        # Uniform sizing
        BOX_WIDTH = 3.0
        BOX_HEIGHT = 0.7
        VERTICAL_SPACING = 0.9
        
        # Input tokens - start higher without title
        input_circle = Circle(radius=0.15, color=text_color, stroke_width=2)
        input_circle.move_to(UP * 3)
        input_label = Tex("Input Tokens", font_size=26, color=text_color)
        input_label.next_to(input_circle, LEFT, buff=0.25)
        input_group = VGroup(input_label, input_circle)
        
        # Helper to create uniform boxes with centered text
        def create_box_with_text(text_content):
            box = RoundedRectangle(
                width=BOX_WIDTH, height=BOX_HEIGHT, corner_radius=0.1,
                stroke_color=box_color, stroke_width=2, fill_opacity=0
            )
            text = Tex(text_content, font_size=22, color=text_color)
            text.move_to(box.get_center())
            return VGroup(box, text)
        
        # Self Attention 1
        sa1 = create_box_with_text("Self-Attention")
        sa1.next_to(input_circle, DOWN, buff=VERTICAL_SPACING)
        sa1_box = sa1[0]
        
        # Arrow from input to SA1
        arrow1 = Arrow(
            input_circle.get_bottom(), sa1_box.get_top(),
            buff=0.08, color=arrow_color, stroke_width=2,
            max_tip_length_to_length_ratio=0.12
        )
        
        # Feed-Forward Network 1
        ffn1 = create_box_with_text("Feed-Forward Network")
        ffn1.next_to(sa1, DOWN, buff=VERTICAL_SPACING)
        ffn1_box = ffn1[0]
        
        # Arrow from SA1 to FFN1
        arrow2 = Arrow(
            sa1_box.get_bottom(), ffn1_box.get_top(),
            buff=0.08, color=arrow_color, stroke_width=2,
            max_tip_length_to_length_ratio=0.12
        )
        
        # Self Attention 2
        sa2 = create_box_with_text("Self-Attention")
        sa2.next_to(ffn1, DOWN, buff=VERTICAL_SPACING)
        sa2_box = sa2[0]
        
        # Arrow from FFN1 to SA2
        arrow3 = Arrow(
            ffn1_box.get_bottom(), sa2_box.get_top(),
            buff=0.08, color=arrow_color, stroke_width=2,
            max_tip_length_to_length_ratio=0.12
        )
        
        # Feed-Forward Network 2
        ffn2 = create_box_with_text("Feed-Forward Network")
        ffn2.next_to(sa2, DOWN, buff=VERTICAL_SPACING)
        ffn2_box = ffn2[0]
        
        # Arrow from SA2 to FFN2
        arrow4 = Arrow(
            sa2_box.get_bottom(), ffn2_box.get_top(),
            buff=0.08, color=arrow_color, stroke_width=2,
            max_tip_length_to_length_ratio=0.12
        )
        
        # Animate the dense model appearing
        self.play(FadeIn(input_group), run_time=0.5)
        self.play(GrowArrow(arrow1), run_time=0.3)
        self.play(FadeIn(sa1), run_time=0.5)
        self.play(GrowArrow(arrow2), run_time=0.3)
        self.play(FadeIn(ffn1), run_time=0.5)
        self.play(GrowArrow(arrow3), run_time=0.3)
        self.play(FadeIn(sa2), run_time=0.5)
        self.play(GrowArrow(arrow4), run_time=0.3)
        self.play(FadeIn(ffn2), run_time=0.5)
        
        self.wait(1)
        
        # Highlight the FFN boxes to indicate transformation
        self.play(
            ffn1_box.animate.set_stroke(color=highlight_color, width=4),
            ffn2_box.animate.set_stroke(color=highlight_color, width=4),
            run_time=0.8
        )
        self.wait(0.5)
        
        # Create Expert boxes - uniform size
        EXPERT_BOX_WIDTH = 1.4
        EXPERT_BOX_HEIGHT = 0.55
        
        def create_expert_box(label, highlight=False):
            stroke_w = 3 if highlight else 2
            fill_op = 0.15 if highlight else 0
            box = RoundedRectangle(
                width=EXPERT_BOX_WIDTH, height=EXPERT_BOX_HEIGHT, corner_radius=0.08,
                stroke_color=highlight_color if highlight else box_color, 
                stroke_width=stroke_w, 
                fill_opacity=fill_op,
                fill_color=highlight_color if highlight else None
            )
            text = Tex(label, font_size=22, color=text_color)
            text.move_to(box.get_center())
            return VGroup(box, text)
        
        # First set of experts
        experts1 = VGroup(*[
            create_expert_box(f"Expert {i+1}", highlight=(i==0))
            for i in range(4)
        ]).arrange(RIGHT, buff=0.1)
        experts1.move_to(ffn1.get_center())
        
        # Second set of experts
        experts2 = VGroup(*[
            create_expert_box(f"Expert {i+1}", highlight=(i==2))
            for i in range(4)
        ]).arrange(RIGHT, buff=0.1)
        experts2.move_to(ffn2.get_center())
        
        # Helper function to create curved arrow (path + tip as separate objects for animation)
        def create_curved_arrow(start, end, color):
            start_buffered = start + DOWN * 0.05
            end_buffered = end + UP * 0.12
            
            ctrl1 = start_buffered + DOWN * 0.25
            ctrl2 = end_buffered + UP * 0.25
            
            path = CubicBezier(start_buffered, ctrl1, ctrl2, end_buffered, color=color, stroke_width=2)
            
            tangent = normalize(end_buffered - ctrl2)
            
            tip = Triangle(fill_color=color, fill_opacity=1, stroke_width=0)
            tip.scale(0.08)
            tip.move_to(end_buffered)
            
            angle = np.arctan2(tangent[1], tangent[0]) - PI/2
            tip.rotate(angle)
            
            return VGroup(path, tip)
        
        def create_branch_arrows_group(source_box, expert_group, color):
            arrows = VGroup()
            start = source_box.get_bottom()
            
            for expert in expert_group:
                end = expert[0].get_top()
                arrow = create_curved_arrow(start, end, color)
                arrows.add(arrow)
            
            return arrows
        
        def create_merge_arrows_group(expert_group, target_box, color):
            arrows = VGroup()
            end = target_box.get_top()
            
            for expert in expert_group:
                start = expert[0].get_bottom()
                arrow = create_curved_arrow(start, end, color)
                arrows.add(arrow)
            
            return arrows
        
        # Custom animation function: draw path then fade in tip
        def animate_arrows_from_start(arrows, run_time=0.8):
            """Animate arrows by drawing path from start to end, then showing tip"""
            animations = []
            for arrow in arrows:
                path = arrow[0]
                tip = arrow[1]
                # Create the path drawing and tip fade in as a succession
                animations.append(Succession(
                    Create(path, run_time=run_time * 0.8),
                    FadeIn(tip, run_time=run_time * 0.2)
                ))
            return animations
        
        # Animate transformation
        self.play(
            FadeOut(arrow2, shift=DOWN * 0.2),
            FadeOut(arrow3, shift=DOWN * 0.2),
            run_time=0.5
        )
        
        self.play(
            ReplacementTransform(ffn1, experts1),
            run_time=1.0
        )
        
        branch_arrows1 = create_branch_arrows_group(sa1_box, experts1, arrow_color)
        merge_arrows1 = create_merge_arrows_group(experts1, sa2_box, arrow_color)
        
        # Animate branch arrows from start to tip
        self.play(*animate_arrows_from_start(branch_arrows1, run_time=0.8))
        
        # Animate merge arrows from start to tip
        self.play(*animate_arrows_from_start(merge_arrows1, run_time=0.8))
        
        self.play(
            FadeOut(arrow4, shift=DOWN * 0.2),
            run_time=0.5
        )
        
        self.play(
            ReplacementTransform(ffn2, experts2),
            run_time=1.0
        )
        
        branch_arrows2 = create_branch_arrows_group(sa2_box, experts2, arrow_color)
        
        # Animate branch arrows from start to tip
        self.play(*animate_arrows_from_start(branch_arrows2, run_time=0.8))
        
        self.wait(2)

