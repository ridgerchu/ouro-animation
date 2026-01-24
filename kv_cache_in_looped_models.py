"""
KV-Cache in Looped Models 可视化动画
运行命令:
  完整动画: manim -pql kv_cache_in_looped_models.py KVCacheAnimation
  单独场景: manim -pql kv_cache_in_looped_models.py Scene1Title
           manim -pql kv_cache_in_looped_models.py Scene2Introduction
           manim -pql kv_cache_in_looped_models.py Scene3GridSetup
           manim -pql kv_cache_in_looped_models.py Scene4TrainingPrefill
           manim -pql kv_cache_in_looped_models.py Scene5IdealImpractical
           manim -pql kv_cache_in_looped_models.py Scene6DecodingTransition
           manim -pql kv_cache_in_looped_models.py Scene7DecodingDefault
           manim -pql kv_cache_in_looped_models.py Scene8GroundTruth
           manim -pql kv_cache_in_looped_models.py Scene9AlternativeStrategies
           manim -pql kv_cache_in_looped_models.py Scene10Results
           manim -pql kv_cache_in_looped_models.py Scene11Conclusion
  高质量渲染: manim -pqh kv_cache_in_looped_models.py KVCacheAnimation
"""

from manim import *
import numpy as np

# ===== 颜色配置 =====
COLORS = {
    'background': '#0d1117',
    'primary_text': '#ffffff',
    'secondary_text': '#8b949e',
    'loop_1': '#58a6ff',      # Blue for loop 1
    'loop_2': '#3fb950',      # Green for loop 2
    'loop_3': '#f0883e',      # Orange for loop 3
    'inactive': '#30363d',    # Gray for inactive
    'kv_arrow': '#8b949e',    # Light gray for KV arrows
    'failure': '#f85149',     # Red for failures
    'success': '#3fb950',     # Green for success
    'highlight': '#d29922',   # Yellow highlight
    'warning': '#f0883e',     # Orange warning
}

# 简化颜色引用
LOOP_1_COLOR = COLORS['loop_1']
LOOP_2_COLOR = COLORS['loop_2']
LOOP_3_COLOR = COLORS['loop_3']
INACTIVE_COLOR = COLORS['inactive']
KV_ARROW_COLOR = COLORS['kv_arrow']
FAILURE_COLOR = COLORS['failure']
SUCCESS_COLOR = COLORS['success']
HIGHLIGHT_COLOR = COLORS['highlight']
WARNING_COLOR = COLORS['warning']
SECONDARY_TEXT = COLORS['secondary_text']


class GridCell(VGroup):
    """Grid cell representing hidden state at position and loop"""
    def __init__(self, radius=0.3, color=INACTIVE_COLOR, fill_opacity=0.3, **kwargs):
        super().__init__(**kwargs)
        self.circle = Circle(
            radius=radius,
            color=color,
            fill_opacity=fill_opacity,
            stroke_width=2
        )
        self.add(self.circle)
        self.current_color = color

    def fill_with_color(self, color, fill_opacity=0.8):
        self.current_color = color
        return self.circle.animate.set_fill(color, opacity=fill_opacity).set_stroke(color, width=3)

    def reset(self):
        return self.circle.animate.set_fill(INACTIVE_COLOR, opacity=0.3).set_stroke(INACTIVE_COLOR, width=2)

    def pulse(self):
        return Succession(
            self.circle.animate.scale(1.2).set_fill(opacity=1),
            self.circle.animate.scale(1/1.2).set_fill(opacity=0.8)
        )


class KVGrid(VGroup):
    """3x3 Grid for KV-Cache visualization"""
    def __init__(self, cell_size=1.0, spacing=0.3, cell_radius=0.3, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = cell_size
        self.spacing = spacing
        self.cell_radius = cell_radius
        self.cells = {}
        self._create_grid()

    def _create_grid(self):
        """Create 3x3 grid of cells"""
        for row in range(3):  # t1, t2, t3
            for col in range(3):  # x1, x2, x3
                cell = GridCell(radius=self.cell_radius)
                x_pos = col * (self.cell_size + self.spacing)
                y_pos = -row * (self.cell_size + self.spacing)  # Top to bottom
                cell.move_to([x_pos, y_pos, 0])
                self.cells[(row, col)] = cell
                self.add(cell)

        # Center the grid
        self.center()

    def get_cell(self, row, col):
        return self.cells[(row, col)]

    def get_row(self, row):
        return VGroup(*[self.cells[(row, col)] for col in range(3)])

    def get_col(self, col):
        return VGroup(*[self.cells[(row, col)] for row in range(3)])


# ===== Scene 1: Section Title =====
class Scene1Title(Scene):
    """Scene 1: Section Title (2 seconds)"""
    def construct(self):
        # Main title
        title = Text(
            "KV-Caching",
            font_size=72,
            weight=BOLD,
            color=WHITE
        )
        title.scale(0.95)

        # Subtitle
        subtitle = Text(
            "Looped models are kind of weird when it comes to KV-caching.",
            font_size=28,
            color=SECONDARY_TEXT
        )
        subtitle.next_to(title, DOWN, buff=0.5)

        title_group = VGroup(title, subtitle)

        # Animation: Fade in with slight scale
        self.play(
            FadeIn(title, scale=0.95),
            title.animate.scale(1.0 / 0.95),
            run_time=0.8
        )
        self.play(Write(subtitle), run_time=0.8)

        self.wait(0.5)

        # Fade out
        self.play(FadeOut(title_group), run_time=0.5)


# ===== Scene 2: Introduction - Constraints and Flexibility =====
class Scene2Introduction(Scene):
    """Scene 2: Introduction - Constraints vs Flexibility (6 seconds)"""
    def construct(self):
        # Left panel: Constraints
        left_panel = RoundedRectangle(
            width=5, height=4.5,
            corner_radius=0.2,
            color=FAILURE_COLOR,
            fill_opacity=0.1,
            stroke_width=2
        )
        left_panel.shift(LEFT * 3.2)

        # Warning icon for constraints
        warning_icon = MathTex(r"\triangle", font_size=48, color=FAILURE_COLOR)
        warning_icon.next_to(left_panel.get_top(), DOWN, buff=0.3)

        constraints_title = Text("Constraints", font_size=32, color=FAILURE_COLOR, weight=BOLD)
        constraints_title.next_to(warning_icon, DOWN, buff=0.2)

        constraints_list = VGroup(
            Text("• Training vs Inference", font_size=22, color=WHITE),
            Text("• Prefill vs Decoding", font_size=22, color=WHITE),
            Text("• Different KV rules", font_size=22, color=WHITE),
        )
        constraints_list.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        constraints_list.next_to(constraints_title, DOWN, buff=0.5)

        left_content = VGroup(warning_icon, constraints_title, constraints_list)

        # Right panel: Flexibility
        right_panel = RoundedRectangle(
            width=5, height=4.5,
            corner_radius=0.2,
            color=SUCCESS_COLOR,
            fill_opacity=0.1,
            stroke_width=2
        )
        right_panel.shift(RIGHT * 3.2)

        # Lightbulb icon for flexibility
        lightbulb_icon = MathTex(r"\star", font_size=48, color=SUCCESS_COLOR)
        lightbulb_icon.next_to(right_panel.get_top(), DOWN, buff=0.3)

        flexibility_title = Text("Flexibility", font_size=32, color=SUCCESS_COLOR, weight=BOLD)
        flexibility_title.next_to(lightbulb_icon, DOWN, buff=0.2)

        flexibility_list = VGroup(
            Text("• Extra loops per token", font_size=22, color=WHITE),
            Text("• More KV sharing options", font_size=22, color=WHITE),
            Text("• Room to experiment", font_size=22, color=WHITE),
        )
        flexibility_list.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        flexibility_list.next_to(flexibility_title, DOWN, buff=0.5)

        right_content = VGroup(lightbulb_icon, flexibility_title, flexibility_list)

        # Balance scale in center
        scale_base = Line(DOWN * 1.5, UP * 1, color=SECONDARY_TEXT, stroke_width=3)
        scale_beam = Line(LEFT * 1.5, RIGHT * 1.5, color=SECONDARY_TEXT, stroke_width=3)
        scale_beam.move_to(scale_base.get_top())

        scale = VGroup(scale_base, scale_beam)

        # Animation sequence
        # Left panel slides in first
        self.play(
            FadeIn(left_panel, shift=RIGHT * 0.5),
            FadeIn(left_content, shift=RIGHT * 0.5),
            run_time=1
        )

        self.wait(0.3)

        # Right panel follows
        self.play(
            FadeIn(right_panel, shift=LEFT * 0.5),
            FadeIn(right_content, shift=LEFT * 0.5),
            run_time=1
        )

        # Balance scale animation
        self.play(
            FadeIn(scale, scale=0.8),
            run_time=0.5
        )

        # Tilt animation to show push-pull
        self.play(
            Rotate(scale_beam, angle=PI/12, about_point=scale_base.get_top()),
            run_time=0.5
        )
        self.play(
            Rotate(scale_beam, angle=-PI/6, about_point=scale_base.get_top()),
            run_time=0.5
        )
        self.play(
            Rotate(scale_beam, angle=PI/12, about_point=scale_base.get_top()),
            run_time=0.5
        )

        self.wait(1)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 3: Grid Structure - Initial Setup =====
class Scene3GridSetup(Scene):
    """Scene 3: Grid Structure Initial Setup (6 seconds)"""
    def construct(self):
        # Header
        header = Text("Training / Prefill Mode", font_size=36, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.5)

        # Create grid
        grid = KVGrid(cell_size=1.2, spacing=0.4, cell_radius=0.35)
        grid.shift(DOWN * 0.3)

        # Axis labels
        # Token position labels (x-axis): x₁, x₂, x₃
        x_labels = VGroup()
        token_label = Text("Token Position", font_size=20, color=SECONDARY_TEXT)
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=32, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 1.2)
            x_labels.add(label)
        token_label.next_to(x_labels, UP, buff=0.3)

        # Loop iteration labels (y-axis): t₁, t₂, t₃
        t_labels = VGroup()
        loop_label = Text("Loop Iteration", font_size=20, color=SECONDARY_TEXT)
        loop_label.rotate(PI/2)
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=32, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 1.3)
            t_labels.add(label)
        loop_label.next_to(t_labels, LEFT, buff=0.3)

        # Annotation
        annotation = Text(
            "Each circle = hidden state h at loop t for position ℓ",
            font_size=20,
            color=SECONDARY_TEXT
        )
        annotation.to_edge(DOWN, buff=0.8)

        # Animation sequence
        # First, axis labels and header fade in
        self.play(Write(header), run_time=0.6)
        self.play(
            Write(token_label),
            LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1),
            run_time=0.8
        )
        self.play(
            Write(loop_label),
            LaggedStart(*[Write(l) for l in t_labels], lag_ratio=0.1),
            run_time=0.8
        )

        # Grid lines draw from left to right and top to bottom
        # Draw horizontal lines
        h_lines = VGroup()
        for i in range(4):
            y_pos = grid.get_cell(0, 0).get_center()[1] + 0.6 - i * (grid.cell_size + grid.spacing)
            line = Line(
                grid.get_cell(0, 0).get_center() + LEFT * 0.8 + UP * (0.6 - i * (grid.cell_size + grid.spacing)),
                grid.get_cell(0, 2).get_center() + RIGHT * 0.8 + UP * (0.6 - i * (grid.cell_size + grid.spacing)),
                color=INACTIVE_COLOR,
                stroke_width=1
            )
            h_lines.add(line)

        # Draw vertical lines
        v_lines = VGroup()
        for i in range(4):
            x_pos = grid.get_cell(0, 0).get_center()[0] - 0.6 + i * (grid.cell_size + grid.spacing)
            line = Line(
                grid.get_cell(0, 0).get_center() + LEFT * (0.6 - i * (grid.cell_size + grid.spacing)) + UP * 0.6,
                grid.get_cell(2, 0).get_center() + LEFT * (0.6 - i * (grid.cell_size + grid.spacing)) + DOWN * 0.6,
                color=INACTIVE_COLOR,
                stroke_width=1
            )
            v_lines.add(line)

        self.play(
            LaggedStart(*[Create(l) for l in h_lines], lag_ratio=0.1),
            run_time=0.6
        )
        self.play(
            LaggedStart(*[Create(l) for l in v_lines], lag_ratio=0.1),
            run_time=0.6
        )

        # Circles appear at intersections
        self.play(
            LaggedStart(*[FadeIn(cell, scale=0.8) for cell in grid.cells.values()], lag_ratio=0.05),
            run_time=1
        )

        # Pulse animation to emphasize structure
        self.play(
            *[cell.circle.animate.set_stroke(width=4) for cell in grid.cells.values()],
            run_time=0.3
        )
        self.play(
            *[cell.circle.animate.set_stroke(width=2) for cell in grid.cells.values()],
            run_time=0.3
        )

        self.play(Write(annotation), run_time=0.6)

        self.wait(1)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 4: Training/Prefill - Parallel Loop Execution =====
class Scene4TrainingPrefill(Scene):
    """Scene 4: Training/Prefill - Parallel Loop Execution (8 seconds)"""
    def construct(self):
        # Header
        header = Text("Training / Prefill Mode", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        # Create grid
        grid = KVGrid(cell_size=1.2, spacing=0.4, cell_radius=0.35)
        grid.shift(DOWN * 0.2 + LEFT * 0.5)

        # Token labels
        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=28, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 1.0)
            x_labels.add(label)

        # Loop labels
        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=28, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 1.1)
            t_labels.add(label)

        # Show grid immediately
        self.play(
            Write(header),
            FadeIn(grid),
            LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in t_labels], lag_ratio=0.1),
            run_time=0.8
        )

        # Colors for each loop
        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Phase A (0-2.5s): Loop 1 - all three circles fill blue simultaneously
        phase_label_1 = Text("Loop 1: Parallel execution", font_size=22, color=LOOP_1_COLOR)
        phase_label_1.to_corner(UR, buff=0.5)

        row_0_cells = [grid.get_cell(0, col) for col in range(3)]
        self.play(
            *[cell.fill_with_color(LOOP_1_COLOR) for cell in row_0_cells],
            Write(phase_label_1),
            run_time=0.8
        )

        # Horizontal arrows within row 0
        h_arrows_1 = VGroup()
        for i in range(2):
            arrow = Arrow(
                row_0_cells[i].get_center() + RIGHT * 0.4,
                row_0_cells[i+1].get_center() + LEFT * 0.4,
                color=KV_ARROW_COLOR,
                stroke_width=3,
                buff=0
            )
            h_arrows_1.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in h_arrows_1], lag_ratio=0.2),
            run_time=0.8
        )

        self.wait(0.5)

        # Phase B (2.5-5s): Loop 2 - green, with vertical dotted arrows
        phase_label_2 = Text("Loop 2: Uses KV from corresponding loop (t₁)", font_size=20, color=LOOP_2_COLOR)
        phase_label_2.to_corner(UR, buff=0.5)

        row_1_cells = [grid.get_cell(1, col) for col in range(3)]
        self.play(
            *[cell.fill_with_color(LOOP_2_COLOR) for cell in row_1_cells],
            Transform(phase_label_1, phase_label_2),
            run_time=0.8
        )

        # Horizontal arrows within row 1
        h_arrows_2 = VGroup()
        for i in range(2):
            arrow = Arrow(
                row_1_cells[i].get_center() + RIGHT * 0.4,
                row_1_cells[i+1].get_center() + LEFT * 0.4,
                color=KV_ARROW_COLOR,
                stroke_width=3,
                buff=0
            )
            h_arrows_2.add(arrow)

        # Vertical dotted arrows from row 0 to row 1
        v_arrows_1 = VGroup()
        for col in range(3):
            arrow = DashedLine(
                row_0_cells[col].get_center() + DOWN * 0.4,
                row_1_cells[col].get_center() + UP * 0.4,
                color=LOOP_1_COLOR,
                stroke_width=2,
                dash_length=0.1
            )
            # Add arrowhead
            tip = Triangle(fill_opacity=1, color=LOOP_1_COLOR, stroke_width=0)
            tip.scale(0.1)
            tip.rotate(-PI/2)
            tip.move_to(arrow.get_end())
            v_arrows_1.add(VGroup(arrow, tip))

        self.play(
            LaggedStart(*[GrowArrow(a) for a in h_arrows_2], lag_ratio=0.2),
            LaggedStart(*[Create(a) for a in v_arrows_1], lag_ratio=0.1),
            run_time=0.8
        )

        self.wait(0.5)

        # Phase C (5-7s): Loop 3 - orange
        phase_label_3 = Text("Loop 3: Uses KV from corresponding loop (t₂)", font_size=20, color=LOOP_3_COLOR)
        phase_label_3.to_corner(UR, buff=0.5)

        row_2_cells = [grid.get_cell(2, col) for col in range(3)]
        self.play(
            *[cell.fill_with_color(LOOP_3_COLOR) for cell in row_2_cells],
            Transform(phase_label_1, phase_label_3),
            run_time=0.8
        )

        # Horizontal arrows within row 2
        h_arrows_3 = VGroup()
        for i in range(2):
            arrow = Arrow(
                row_2_cells[i].get_center() + RIGHT * 0.4,
                row_2_cells[i+1].get_center() + LEFT * 0.4,
                color=KV_ARROW_COLOR,
                stroke_width=3,
                buff=0
            )
            h_arrows_3.add(arrow)

        # Vertical dotted arrows from row 1 to row 2
        v_arrows_2 = VGroup()
        for col in range(3):
            arrow = DashedLine(
                row_1_cells[col].get_center() + DOWN * 0.4,
                row_2_cells[col].get_center() + UP * 0.4,
                color=LOOP_2_COLOR,
                stroke_width=2,
                dash_length=0.1
            )
            tip = Triangle(fill_opacity=1, color=LOOP_2_COLOR, stroke_width=0)
            tip.scale(0.1)
            tip.rotate(-PI/2)
            tip.move_to(arrow.get_end())
            v_arrows_2.add(VGroup(arrow, tip))

        self.play(
            LaggedStart(*[GrowArrow(a) for a in h_arrows_3], lag_ratio=0.2),
            LaggedStart(*[Create(a) for a in v_arrows_2], lag_ratio=0.1),
            run_time=0.8
        )

        # Phase D (7-8s): Summary
        summary_box = RoundedRectangle(
            width=8, height=1.2,
            corner_radius=0.15,
            color=HIGHLIGHT_COLOR,
            fill_opacity=0.1,
            stroke_width=2
        )
        summary_box.to_edge(DOWN, buff=0.5)

        summary_text = Text(
            "Each loop runs in parallel across all tokens",
            font_size=24,
            color=WHITE
        )
        summary_text.move_to(summary_box.get_center() + UP * 0.15)

        summary_sub = Text(
            "Vertical arrows: KV from same loop index in previous iteration",
            font_size=18,
            color=SECONDARY_TEXT
        )
        summary_sub.move_to(summary_box.get_center() + DOWN * 0.25)

        self.play(
            FadeIn(summary_box),
            Write(summary_text),
            Write(summary_sub),
            run_time=1
        )

        self.wait(1)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 5: The Ideal but Impractical Approach =====
class Scene5IdealImpractical(Scene):
    """Scene 5: The Ideal but Impractical Approach (6 seconds)"""
    def construct(self):
        # Header
        header = Text("What Would Be Ideal?", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        self.play(Write(header), run_time=0.6)

        # Create grid
        grid = KVGrid(cell_size=1.0, spacing=0.35, cell_radius=0.3)
        grid.shift(LEFT * 1)

        # Token labels
        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 0.9)
            x_labels.add(label)

        # Loop labels
        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 0.9)
            t_labels.add(label)

        self.play(
            FadeIn(grid),
            LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05),
            run_time=0.6
        )

        # Phase A (0-3s): Sequential processing - staircase pattern
        # x₁ processes through all loops first
        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Animate x₁ going through all loops
        for row in range(3):
            cell = grid.get_cell(row, 0)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.4)

        # "Waiting" indicator next to x₂
        waiting_text = Text("waiting...", font_size=18, color=SECONDARY_TEXT, slant=ITALIC)
        waiting_text.next_to(grid.get_cell(0, 1).get_center(), RIGHT, buff=0.5)
        self.play(FadeIn(waiting_text), run_time=0.3)

        # Arrow from x₁'s final loop to x₂
        diagonal_arrow = Arrow(
            grid.get_cell(2, 0).get_center() + RIGHT * 0.35 + UP * 0.1,
            grid.get_cell(0, 1).get_center() + LEFT * 0.35,
            color=LOOP_3_COLOR,
            stroke_width=4
        )
        self.play(GrowArrow(diagonal_arrow), run_time=0.5)

        # Now x₂ can start
        self.play(FadeOut(waiting_text), run_time=0.2)

        for row in range(3):
            cell = grid.get_cell(row, 1)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.3)

        # Arrow to x₃
        diagonal_arrow_2 = Arrow(
            grid.get_cell(2, 1).get_center() + RIGHT * 0.35 + UP * 0.1,
            grid.get_cell(0, 2).get_center() + LEFT * 0.35,
            color=LOOP_3_COLOR,
            stroke_width=4
        )
        self.play(GrowArrow(diagonal_arrow_2), run_time=0.3)

        for row in range(3):
            cell = grid.get_cell(row, 2)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.2)

        self.wait(0.3)

        # Phase B (3-6s): Large red X overlay and problem callouts
        big_x = Text("✗", font_size=180, color=FAILURE_COLOR)
        big_x.set_opacity(0.7)
        big_x.move_to(grid.get_center())

        self.play(FadeIn(big_x, scale=1.5), run_time=0.5)

        # Problem callouts
        problems = VGroup(
            Text("❌ Kills parallel training", font_size=20, color=FAILURE_COLOR),
            Text("❌ Sequential bottleneck", font_size=20, color=FAILURE_COLOR),
            Text("❌ Can't scale to trillions of tokens", font_size=20, color=FAILURE_COLOR),
        )
        problems.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        problems.to_edge(RIGHT, buff=0.8)

        self.play(
            LaggedStart(*[Write(p) for p in problems], lag_ratio=0.3),
            run_time=1.2
        )

        # Conclusion box
        conclusion_box = RoundedRectangle(
            width=6, height=0.8,
            corner_radius=0.1,
            color=FAILURE_COLOR,
            fill_opacity=0.2,
            stroke_width=2
        )
        conclusion_box.to_edge(DOWN, buff=0.6)

        conclusion_text = Text("Ideal in theory, impractical in reality", font_size=22, color=FAILURE_COLOR)
        conclusion_text.move_to(conclusion_box.get_center())

        self.play(
            FadeIn(conclusion_box),
            Write(conclusion_text),
            run_time=0.6
        )

        self.wait(1)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 6: Transition to Decoding =====
class Scene6DecodingTransition(Scene):
    """Scene 6: Transition to Decoding (2 seconds)"""
    def construct(self):
        # Transition card
        title = Text("Decoding During Inference", font_size=48, color=WHITE, weight=BOLD)

        subtitle = Text(
            "Different rules apply...",
            font_size=28,
            color=SECONDARY_TEXT,
            slant=ITALIC
        )
        subtitle.next_to(title, DOWN, buff=0.4)

        content = VGroup(title, subtitle)

        self.play(
            FadeIn(title, scale=0.9),
            run_time=0.6
        )
        self.play(Write(subtitle), run_time=0.6)

        self.wait(0.5)

        self.play(FadeOut(content), run_time=0.5)


# ===== Scene 7: Decoding - Default Approach =====
class Scene7DecodingDefault(Scene):
    """Scene 7: Decoding - Default Approach (8 seconds)"""
    def construct(self):
        # Header
        header = Text("Decoding: Default Approach", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        self.play(Write(header), run_time=0.5)

        # Create grid
        grid = KVGrid(cell_size=1.1, spacing=0.35, cell_radius=0.32)
        grid.shift(DOWN * 0.3 + LEFT * 0.5)

        # Token labels
        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=26, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 0.95)
            x_labels.add(label)

        # Loop labels
        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=26, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 1.0)
            t_labels.add(label)

        self.play(
            FadeIn(grid),
            LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05),
            run_time=0.6
        )

        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Phase A (0-3s): Only x₁ column is active, processes top to bottom
        phase_label = Text("Token 1 processing...", font_size=20, color=LOOP_1_COLOR)
        phase_label.to_corner(UR, buff=0.5)
        self.play(Write(phase_label), run_time=0.3)

        # Process x₁ through all loops
        for row in range(3):
            cell = grid.get_cell(row, 0)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.5)

            # Exit gate check indicator
            if row < 2:
                gate_check = Text("◇ check exit", font_size=14, color=SECONDARY_TEXT)
                gate_check.next_to(cell, RIGHT, buff=0.5)
                self.play(FadeIn(gate_check), run_time=0.15)
                self.play(FadeOut(gate_check), run_time=0.15)

        # Output token appears
        output_1 = MathTex(r"\hat{y}_1", font_size=24, color=LOOP_3_COLOR)
        output_1.move_to(grid.get_cell(2, 0).get_center() + DOWN * 1.0)

        output_arrow_1 = Arrow(
            grid.get_cell(2, 0).get_center() + DOWN * 0.4,
            output_1.get_center() + UP * 0.2,
            color=LOOP_3_COLOR,
            stroke_width=2
        )

        self.play(GrowArrow(output_arrow_1), Write(output_1), run_time=0.4)

        # Phase B (3-6s): Token 2 begins
        phase_label_2 = Text("Token 1 complete → Token 2 begins", font_size=18, color=SUCCESS_COLOR)
        phase_label_2.to_corner(UR, buff=0.5)
        self.play(Transform(phase_label, phase_label_2), run_time=0.4)

        # Horizontal arrows showing KV from corresponding loops
        h_kv_arrows = VGroup()
        for row in range(3):
            arrow = Arrow(
                grid.get_cell(row, 0).get_center() + RIGHT * 0.35,
                grid.get_cell(row, 1).get_center() + LEFT * 0.35,
                color=loop_colors[row],
                stroke_width=2
            )
            h_kv_arrows.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in h_kv_arrows], lag_ratio=0.2),
            run_time=0.8
        )

        # Process x₂
        for row in range(3):
            cell = grid.get_cell(row, 1)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.35)

        # Output token 2
        output_2 = MathTex(r"\hat{y}_2", font_size=24, color=LOOP_2_COLOR)
        output_2.move_to(grid.get_cell(1, 1).get_center() + DOWN * 1.55)  # Exit at t2

        output_arrow_2 = Arrow(
            grid.get_cell(1, 1).get_center() + DOWN * 0.4,
            output_2.get_center() + UP * 0.2,
            color=LOOP_2_COLOR,
            stroke_width=2
        )

        self.play(GrowArrow(output_arrow_2), Write(output_2), run_time=0.4)

        # Phase C (6-8s): Comparison with training
        comparison_box = RoundedRectangle(
            width=5, height=1.2,
            corner_radius=0.1,
            color=SUCCESS_COLOR,
            fill_opacity=0.1,
            stroke_width=2
        )
        comparison_box.to_edge(DOWN, buff=0.4)

        comparison_text = Text("Stays consistent with training", font_size=20, color=SUCCESS_COLOR)
        comparison_text.move_to(comparison_box.get_center() + UP * 0.15)

        checkmark = MathTex(r"\checkmark", font_size=36, color=SUCCESS_COLOR)
        checkmark.next_to(comparison_text, LEFT, buff=0.3)

        default_label = Text("Default approach", font_size=16, color=SECONDARY_TEXT)
        default_label.move_to(comparison_box.get_center() + DOWN * 0.25)

        self.play(
            FadeIn(comparison_box),
            Write(comparison_text),
            FadeIn(checkmark, scale=1.5),
            Write(default_label),
            run_time=0.8
        )

        self.wait(1)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 8: Ground Truth Output =====
class Scene8GroundTruth(Scene):
    """Scene 8: Ground Truth Output (4 seconds)"""
    def construct(self):
        # Header
        header = Text("Ground Truth Generation", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        # Create grid (already filled)
        grid = KVGrid(cell_size=1.0, spacing=0.3, cell_radius=0.28)
        grid.shift(UP * 0.5)

        # Token labels
        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 0.85)
            x_labels.add(label)

        # Loop labels
        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 0.9)
            t_labels.add(label)

        self.play(
            Write(header),
            FadeIn(grid),
            LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05),
            run_time=0.6
        )

        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Fill all cells
        for col in range(3):
            for row in range(3):
                cell = grid.get_cell(row, col)
                cell.circle.set_fill(loop_colors[row], opacity=0.8)
                cell.circle.set_stroke(loop_colors[row], width=2)

        self.wait(0.3)

        # Phase A (0-2s): Variable exit points
        # x₁ exits at t₃, x₂ exits at t₂, x₃ exits at t₁
        exit_positions = [(2, 0), (1, 1), (0, 2)]  # row, col for each token's exit

        for row, col in exit_positions:
            cell = grid.get_cell(row, col)
            # Glow effect for exit cell
            glow = Circle(
                radius=cell.cell_radius * 1.4,
                color=HIGHLIGHT_COLOR,
                stroke_width=4,
                fill_opacity=0
            )
            glow.move_to(cell.get_center())

            self.play(
                Create(glow),
                cell.circle.animate.set_stroke(HIGHLIGHT_COLOR, width=5),
                run_time=0.4
            )
            self.play(
                glow.animate.scale(1.3).set_opacity(0),
                run_time=0.3
            )
            self.remove(glow)

        # Phase B (2-4s): Output row with LM Head
        # LM Head icon
        lm_head_box = RoundedRectangle(
            width=2, height=0.6,
            corner_radius=0.1,
            color=SECONDARY_TEXT,
            fill_opacity=0.3,
            stroke_width=2
        )
        lm_head_box.next_to(grid, DOWN, buff=0.4)

        lm_head_label = Text("LM Head", font_size=18, color=WHITE)
        lm_head_label.move_to(lm_head_box.get_center())

        self.play(FadeIn(lm_head_box), Write(lm_head_label), run_time=0.4)

        # Output tokens
        outputs = VGroup()
        output_arrows = VGroup()
        output_labels = [r"\hat{y}_1", r"\hat{y}_2", r"\hat{y}_3"]
        exit_colors = [loop_colors[2], loop_colors[1], loop_colors[0]]  # t3, t2, t1

        for i, (label, color) in enumerate(zip(output_labels, exit_colors)):
            output = MathTex(label, font_size=24, color=color)
            output.move_to(grid.get_cell(0, i).get_center() + DOWN * 2.5)
            outputs.add(output)

            arrow = Arrow(
                lm_head_box.get_bottom() + RIGHT * (i - 1) * 1.6 + DOWN * 0.1,
                output.get_center() + UP * 0.2,
                color=color,
                stroke_width=2
            )
            output_arrows.add(arrow)

        self.play(
            LaggedStart(*[GrowArrow(a) for a in output_arrows], lag_ratio=0.15),
            LaggedStart(*[Write(o) for o in outputs], lag_ratio=0.15),
            run_time=0.8
        )

        # Ground truth label
        ground_truth = MathTex(
            r"\text{Ground Truth: } y = [\hat{y}_1, \hat{y}_2, \hat{y}_3]",
            font_size=26,
            color=WHITE
        )
        ground_truth.to_edge(DOWN, buff=0.4)

        self.play(Write(ground_truth), run_time=0.6)

        self.wait(1)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 9: Alternative KV Strategies =====
class Scene9AlternativeStrategies(Scene):
    """Scene 9: Alternative KV Strategies - 4-panel layout (8 seconds)"""
    def construct(self):
        # Header
        header = Text("Alternative KV Strategies", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.3)

        self.play(Write(header), run_time=0.5)

        # Create 2x2 panel layout
        panel_width = 5.5
        panel_height = 2.8

        panels = VGroup()
        panel_positions = [
            UP * 0.3 + LEFT * 3,   # Top-left
            UP * 0.3 + RIGHT * 3,  # Top-right
            DOWN * 2.8 + LEFT * 3,   # Bottom-left
            DOWN * 2.8 + RIGHT * 3,  # Bottom-right
        ]

        titles = ["Corresponding Loop", "Average All Loops", "Exit Loop Only", "First Loop Only"]
        title_colors = [SUCCESS_COLOR, LOOP_1_COLOR, LOOP_3_COLOR, FAILURE_COLOR]

        for i, (pos, title, color) in enumerate(zip(panel_positions, titles, title_colors)):
            panel = RoundedRectangle(
                width=panel_width, height=panel_height,
                corner_radius=0.15,
                color=color,
                fill_opacity=0.05,
                stroke_width=2
            )
            panel.move_to(pos)
            panels.add(panel)

        # Phase A (0-1s): Establish layout
        self.play(
            LaggedStart(*[FadeIn(p) for p in panels], lag_ratio=0.1),
            run_time=0.8
        )

        # Helper function to create mini token pair
        def create_token_pair(center, strategy_type):
            # x₁ and x₂ with simplified loops
            x1_pos = center + LEFT * 1.2
            x2_pos = center + RIGHT * 1.2

            x1_label = MathTex("x_1", font_size=20, color=WHITE)
            x1_label.move_to(x1_pos + UP * 1.0)

            x2_label = MathTex("x_2", font_size=20, color=WHITE)
            x2_label.move_to(x2_pos + UP * 1.0)

            # Three circles for x₁ (loops)
            x1_circles = VGroup()
            for j in range(3):
                c = Circle(radius=0.18, color=[LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR][j], fill_opacity=0.7, stroke_width=2)
                c.move_to(x1_pos + DOWN * j * 0.5)
                x1_circles.add(c)

            # One or three circles for x₂ depending on strategy
            x2_circles = VGroup()
            if strategy_type == "corresponding":
                for j in range(3):
                    c = Circle(radius=0.18, color=[LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR][j], fill_opacity=0.7, stroke_width=2)
                    c.move_to(x2_pos + DOWN * j * 0.5)
                    x2_circles.add(c)
            else:
                c = Circle(radius=0.18, color=SECONDARY_TEXT, fill_opacity=0.7, stroke_width=2)
                c.move_to(x2_pos)
                x2_circles.add(c)

            return VGroup(x1_label, x2_label, x1_circles, x2_circles), x1_circles, x2_circles, x1_pos, x2_pos

        # Phase B (1-3s): Top-Left - Corresponding Loop (Default)
        content_1, x1_c1, x2_c1, x1_p1, x2_p1 = create_token_pair(panel_positions[0] + DOWN * 0.3, "corresponding")

        title_1 = Text("Corresponding Loop", font_size=18, color=SUCCESS_COLOR, weight=BOLD)
        title_1.move_to(panel_positions[0] + UP * 1.1)

        default_tag = Text("✓ Default", font_size=14, color=SUCCESS_COLOR)
        default_tag.next_to(title_1, RIGHT, buff=0.3)

        # Three parallel arrows
        arrows_1 = VGroup()
        for j in range(3):
            arrow = Arrow(
                x1_p1 + DOWN * j * 0.5 + RIGHT * 0.25,
                x2_p1 + DOWN * j * 0.5 + LEFT * 0.25,
                color=[LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR][j],
                stroke_width=2,
                buff=0
            )
            arrows_1.add(arrow)

        match_label = Text("Matches training", font_size=14, color=SECONDARY_TEXT)
        match_label.move_to(panel_positions[0] + DOWN * 1.1)

        self.play(
            Write(title_1),
            FadeIn(default_tag),
            FadeIn(content_1),
            run_time=0.6
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_1], lag_ratio=0.1),
            Write(match_label),
            run_time=0.6
        )

        # Phase C (3-5s): Top-Right - Average All Loops
        x1_p2 = panel_positions[1] + DOWN * 0.3 + LEFT * 1.2
        x2_p2 = panel_positions[1] + DOWN * 0.3 + RIGHT * 1.2

        title_2 = Text("Average All Loops", font_size=18, color=LOOP_1_COLOR, weight=BOLD)
        title_2.move_to(panel_positions[1] + UP * 1.1)

        x1_label_2 = MathTex("x_1", font_size=20, color=WHITE)
        x1_label_2.move_to(x1_p2 + UP * 1.0)

        x2_label_2 = MathTex("x_2", font_size=20, color=WHITE)
        x2_label_2.move_to(x2_p2 + UP * 1.0)

        x1_circles_2 = VGroup()
        for j in range(3):
            c = Circle(radius=0.18, color=[LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR][j], fill_opacity=0.7, stroke_width=2)
            c.move_to(x1_p2 + DOWN * j * 0.5)
            x1_circles_2.add(c)

        # AVG node
        avg_node = RoundedRectangle(width=0.6, height=0.4, corner_radius=0.05, color=HIGHLIGHT_COLOR, fill_opacity=0.5, stroke_width=2)
        avg_node.move_to((x1_p2 + x2_p2) / 2)

        avg_text = Text("AVG", font_size=12, color=WHITE)
        avg_text.move_to(avg_node.get_center())

        # Arrows from all loops to AVG
        arrows_to_avg = VGroup()
        for j in range(3):
            arrow = Arrow(
                x1_p2 + DOWN * j * 0.5 + RIGHT * 0.25,
                avg_node.get_left() + UP * (0.1 - j * 0.1),
                color=[LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR][j],
                stroke_width=2,
                buff=0
            )
            arrows_to_avg.add(arrow)

        # Arrow from AVG to x₂
        x2_circle_2 = Circle(radius=0.18, color=HIGHLIGHT_COLOR, fill_opacity=0.7, stroke_width=2)
        x2_circle_2.move_to(x2_p2)

        arrow_from_avg = Arrow(
            avg_node.get_right(),
            x2_circle_2.get_left() + LEFT * 0.05,
            color=HIGHLIGHT_COLOR,
            stroke_width=2,
            buff=0
        )

        content_2 = VGroup(x1_label_2, x2_label_2, x1_circles_2, avg_node, avg_text, x2_circle_2)

        self.play(
            Write(title_2),
            FadeIn(content_2),
            run_time=0.6
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in arrows_to_avg], lag_ratio=0.1),
            GrowArrow(arrow_from_avg),
            run_time=0.6
        )

        # Phase D (5-7s): Bottom-Left - Exit Loop Only
        x1_p3 = panel_positions[2] + DOWN * 0.1 + LEFT * 1.2
        x2_p3 = panel_positions[2] + DOWN * 0.1 + RIGHT * 1.2

        title_3 = Text("Exit Loop Only", font_size=18, color=LOOP_3_COLOR, weight=BOLD)
        title_3.move_to(panel_positions[2] + UP * 1.1)

        x1_label_3 = MathTex("x_1", font_size=20, color=WHITE)
        x1_label_3.move_to(x1_p3 + UP * 0.8)

        x2_label_3 = MathTex("x_2", font_size=20, color=WHITE)
        x2_label_3.move_to(x2_p3 + UP * 0.8)

        # Grayed out circles for non-exit loops
        x1_circles_3 = VGroup()
        for j in range(3):
            opacity = 0.3 if j < 2 else 0.8
            color = INACTIVE_COLOR if j < 2 else LOOP_3_COLOR
            c = Circle(radius=0.18, color=color, fill_opacity=opacity, stroke_width=2)
            c.move_to(x1_p3 + DOWN * j * 0.5)
            x1_circles_3.add(c)

        x2_circle_3 = Circle(radius=0.18, color=LOOP_3_COLOR, fill_opacity=0.7, stroke_width=2)
        x2_circle_3.move_to(x2_p3)

        exit_arrow = Arrow(
            x1_p3 + DOWN * 1.0 + RIGHT * 0.25,
            x2_circle_3.get_left() + LEFT * 0.05,
            color=LOOP_3_COLOR,
            stroke_width=4,
            buff=0
        )

        note_3 = Text("Makes logical sense —\nexit gives the output", font_size=12, color=SECONDARY_TEXT)
        note_3.move_to(panel_positions[2] + DOWN * 1.0)

        content_3 = VGroup(x1_label_3, x2_label_3, x1_circles_3, x2_circle_3)

        self.play(
            Write(title_3),
            FadeIn(content_3),
            run_time=0.5
        )
        self.play(
            GrowArrow(exit_arrow),
            Write(note_3),
            run_time=0.5
        )

        # Phase E (7-8s): Bottom-Right - First Loop Only
        x1_p4 = panel_positions[3] + DOWN * 0.1 + LEFT * 1.2
        x2_p4 = panel_positions[3] + DOWN * 0.1 + RIGHT * 1.2

        title_4 = Text("First Loop Only", font_size=18, color=FAILURE_COLOR, weight=BOLD)
        title_4.move_to(panel_positions[3] + UP * 1.1)

        x1_label_4 = MathTex("x_1", font_size=20, color=WHITE)
        x1_label_4.move_to(x1_p4 + UP * 0.8)

        x2_label_4 = MathTex("x_2", font_size=20, color=WHITE)
        x2_label_4.move_to(x2_p4 + UP * 0.8)

        # Only first loop active
        x1_circles_4 = VGroup()
        for j in range(3):
            opacity = 0.8 if j == 0 else 0.3
            color = LOOP_1_COLOR if j == 0 else INACTIVE_COLOR
            c = Circle(radius=0.18, color=color, fill_opacity=opacity, stroke_width=2)
            c.move_to(x1_p4 + DOWN * j * 0.5)
            x1_circles_4.add(c)

        x2_circle_4 = Circle(radius=0.18, color=LOOP_1_COLOR, fill_opacity=0.7, stroke_width=2)
        x2_circle_4.move_to(x2_p4)

        first_arrow = Arrow(
            x1_p4 + RIGHT * 0.25,
            x2_circle_4.get_left() + LEFT * 0.05,
            color=LOOP_1_COLOR,
            stroke_width=2,
            buff=0
        )

        # Subtle red tint
        panels[3].set_fill(FAILURE_COLOR, opacity=0.1)

        content_4 = VGroup(x1_label_4, x2_label_4, x1_circles_4, x2_circle_4)

        self.play(
            Write(title_4),
            FadeIn(content_4),
            GrowArrow(first_arrow),
            run_time=0.6
        )

        self.wait(1)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 10: Results Comparison =====
class Scene10Results(Scene):
    """Scene 10: Results Comparison (6 seconds)"""
    def construct(self):
        # Header
        header = Text("Results Comparison", font_size=36, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.5)

        self.play(Write(header), run_time=0.5)

        # Strategy cards
        strategies = [
            ("Corresponding Loop", SUCCESS_COLOR, "✓ Good", True),
            ("Average All Loops", SUCCESS_COLOR, "✓ Good", True),
            ("Exit Loop Only", SUCCESS_COLOR, "✓ Good", True),
            ("First Loop Only", FAILURE_COLOR, "✗ Bad", False),
        ]

        cards = VGroup()
        for i, (name, color, result, is_good) in enumerate(strategies):
            card = RoundedRectangle(
                width=5, height=0.9,
                corner_radius=0.1,
                color=color,
                fill_opacity=0.15 if is_good else 0.25,
                stroke_width=2
            )

            card_name = Text(name, font_size=22, color=WHITE)
            card_name.move_to(card.get_center() + LEFT * 1)

            card_result = Text(result, font_size=22, color=color, weight=BOLD)
            card_result.move_to(card.get_center() + RIGHT * 1.5)

            card_group = VGroup(card, card_name, card_result)
            cards.add(card_group)

        cards.arrange(DOWN, buff=0.25)
        cards.shift(DOWN * 0.3)

        # Phase A (0-3s): Cards appear and rearrange
        self.play(
            LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.2),
            run_time=1.5
        )

        self.wait(0.5)

        # Phase B (3-6s): Group top three with bracket
        bracket_line_left = Line(
            cards[0].get_left() + LEFT * 0.3 + UP * 0.1,
            cards[2].get_left() + LEFT * 0.3 + DOWN * 0.1,
            color=SUCCESS_COLOR,
            stroke_width=3
        )
        bracket_top = Line(
            bracket_line_left.get_top(),
            bracket_line_left.get_top() + RIGHT * 0.2,
            color=SUCCESS_COLOR,
            stroke_width=3
        )
        bracket_bottom = Line(
            bracket_line_left.get_bottom(),
            bracket_line_left.get_bottom() + RIGHT * 0.2,
            color=SUCCESS_COLOR,
            stroke_width=3
        )
        bracket = VGroup(bracket_line_left, bracket_top, bracket_bottom)

        similar_label = Text("Similar\nPerformance", font_size=18, color=SUCCESS_COLOR)
        similar_label.next_to(bracket_line_left, LEFT, buff=0.2)

        self.play(
            Create(bracket),
            Write(similar_label),
            run_time=0.8
        )

        # Annotation for divergent strategies
        divergent_note = Text(
            "Exit Loop & Average diverge from training but still work!",
            font_size=18,
            color=HIGHLIGHT_COLOR
        )
        divergent_note.next_to(cards[2], DOWN, buff=0.6)

        thinking_emoji = Text("🤔", font_size=24)
        thinking_emoji.next_to(divergent_note, LEFT, buff=0.2)

        self.play(
            Write(divergent_note),
            FadeIn(thinking_emoji),
            run_time=0.8
        )

        # Separator line
        sep_line = Line(
            cards[2].get_bottom() + DOWN * 0.25 + LEFT * 2.5,
            cards[2].get_bottom() + DOWN * 0.25 + RIGHT * 2.5,
            color=FAILURE_COLOR,
            stroke_width=2
        )

        # Highlight bad strategy
        self.play(Create(sep_line), run_time=0.3)

        # Conclusion text
        conclusion = Text(
            "Worth exploring in future research",
            font_size=22,
            color=WHITE
        )
        conclusion.to_edge(DOWN, buff=0.5)

        self.play(Write(conclusion), run_time=0.6)

        self.wait(1.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Scene 11: Section Conclusion =====
class Scene11Conclusion(Scene):
    """Scene 11: Section Conclusion (3 seconds)"""
    def construct(self):
        # Header
        header = Text("Key Takeaways", font_size=40, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.8)

        # Three key points
        takeaways = VGroup(
            Text("1. Training uses parallel loops with corresponding KV", font_size=24, color=WHITE),
            Text("2. Inference uses sequential tokens with multiple KV options", font_size=24, color=WHITE),
            Text("3. Exit loop KV works despite training mismatch", font_size=24, color=WHITE),
        )
        takeaways.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        takeaways.shift(DOWN * 0.3)

        # Icons for each point
        icons = VGroup(
            Text("⚡", font_size=28),  # Parallel
            Text("🔄", font_size=28),  # Options
            Text("✓", font_size=28, color=SUCCESS_COLOR),  # Works
        )

        for i, icon in enumerate(icons):
            icon.next_to(takeaways[i], LEFT, buff=0.3)

        self.play(Write(header), run_time=0.5)

        for i, (takeaway, icon) in enumerate(zip(takeaways, icons)):
            self.play(
                Write(takeaway),
                FadeIn(icon, scale=1.3),
                run_time=0.6
            )

        self.wait(1)

        # Fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Complete Animation: KVCacheAnimation =====
class KVCacheAnimation(Scene):
    """Complete KV-Cache in Looped Models Animation"""
    def construct(self):
        # Scene 1: Title
        self.scene1_title()

        # Scene 2: Introduction
        self.scene2_introduction()

        # Scene 3: Grid Setup
        self.scene3_grid_setup()

        # Scene 4: Training/Prefill
        self.scene4_training_prefill()

        # Scene 5: Ideal but Impractical
        self.scene5_ideal_impractical()

        # Scene 6: Decoding Transition
        self.scene6_decoding_transition()

        # Scene 7: Decoding Default
        self.scene7_decoding_default()

        # Scene 8: Ground Truth
        self.scene8_ground_truth()

        # Scene 9: Alternative Strategies
        self.scene9_alternative_strategies()

        # Scene 10: Results
        self.scene10_results()

        # Scene 11: Conclusion
        self.scene11_conclusion()

    def scene1_title(self):
        """Scene 1: Section Title (2 seconds)"""
        title = Text("KV-Caching", font_size=72, weight=BOLD, color=WHITE)
        title.scale(0.95)

        subtitle = Text(
            "Looped models are kind of weird when it comes to KV-caching.",
            font_size=28, color=SECONDARY_TEXT
        )
        subtitle.next_to(title, DOWN, buff=0.5)

        self.play(
            FadeIn(title, scale=0.95),
            title.animate.scale(1.0 / 0.95),
            run_time=0.8
        )
        self.play(Write(subtitle), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.5)

    def scene2_introduction(self):
        """Scene 2: Introduction (6 seconds)"""
        # Left panel
        left_panel = RoundedRectangle(width=5, height=4.5, corner_radius=0.2, color=FAILURE_COLOR, fill_opacity=0.1, stroke_width=2)
        left_panel.shift(LEFT * 3.2)

        warning_icon = MathTex(r"\triangle", font_size=48, color=FAILURE_COLOR)
        warning_icon.next_to(left_panel.get_top(), DOWN, buff=0.3)

        constraints_title = Text("Constraints", font_size=32, color=FAILURE_COLOR, weight=BOLD)
        constraints_title.next_to(warning_icon, DOWN, buff=0.2)

        constraints_list = VGroup(
            Text("• Training vs Inference", font_size=22, color=WHITE),
            Text("• Prefill vs Decoding", font_size=22, color=WHITE),
            Text("• Different KV rules", font_size=22, color=WHITE),
        )
        constraints_list.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        constraints_list.next_to(constraints_title, DOWN, buff=0.5)

        # Right panel
        right_panel = RoundedRectangle(width=5, height=4.5, corner_radius=0.2, color=SUCCESS_COLOR, fill_opacity=0.1, stroke_width=2)
        right_panel.shift(RIGHT * 3.2)

        lightbulb_icon = MathTex(r"\star", font_size=48, color=SUCCESS_COLOR)
        lightbulb_icon.next_to(right_panel.get_top(), DOWN, buff=0.3)

        flexibility_title = Text("Flexibility", font_size=32, color=SUCCESS_COLOR, weight=BOLD)
        flexibility_title.next_to(lightbulb_icon, DOWN, buff=0.2)

        flexibility_list = VGroup(
            Text("• Extra loops per token", font_size=22, color=WHITE),
            Text("• More KV sharing options", font_size=22, color=WHITE),
            Text("• Room to experiment", font_size=22, color=WHITE),
        )
        flexibility_list.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        flexibility_list.next_to(flexibility_title, DOWN, buff=0.5)

        left_content = VGroup(warning_icon, constraints_title, constraints_list)
        right_content = VGroup(lightbulb_icon, flexibility_title, flexibility_list)

        # Balance scale
        scale_base = Line(DOWN * 1.5, UP * 1, color=SECONDARY_TEXT, stroke_width=3)
        scale_beam = Line(LEFT * 1.5, RIGHT * 1.5, color=SECONDARY_TEXT, stroke_width=3)
        scale_beam.move_to(scale_base.get_top())
        scale = VGroup(scale_base, scale_beam)

        self.play(FadeIn(left_panel, shift=RIGHT * 0.5), FadeIn(left_content, shift=RIGHT * 0.5), run_time=0.8)
        self.wait(0.2)
        self.play(FadeIn(right_panel, shift=LEFT * 0.5), FadeIn(right_content, shift=LEFT * 0.5), run_time=0.8)
        self.play(FadeIn(scale, scale=0.8), run_time=0.4)

        self.play(Rotate(scale_beam, angle=PI/12, about_point=scale_base.get_top()), run_time=0.4)
        self.play(Rotate(scale_beam, angle=-PI/6, about_point=scale_base.get_top()), run_time=0.4)
        self.play(Rotate(scale_beam, angle=PI/12, about_point=scale_base.get_top()), run_time=0.4)

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene3_grid_setup(self):
        """Scene 3: Grid Setup (6 seconds)"""
        header = Text("Training / Prefill Mode", font_size=36, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.5)

        grid = KVGrid(cell_size=1.2, spacing=0.4, cell_radius=0.35)
        grid.shift(DOWN * 0.3)

        # Token labels
        x_labels = VGroup()
        token_label = Text("Token Position", font_size=20, color=SECONDARY_TEXT)
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=32, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 1.2)
            x_labels.add(label)
        token_label.next_to(x_labels, UP, buff=0.3)

        # Loop labels
        t_labels = VGroup()
        loop_label = Text("Loop Iteration", font_size=20, color=SECONDARY_TEXT)
        loop_label.rotate(PI/2)
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=32, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 1.3)
            t_labels.add(label)
        loop_label.next_to(t_labels, LEFT, buff=0.3)

        annotation = Text("Each circle = hidden state h at loop t for position ℓ", font_size=20, color=SECONDARY_TEXT)
        annotation.to_edge(DOWN, buff=0.8)

        self.play(Write(header), run_time=0.5)
        self.play(Write(token_label), LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1), run_time=0.6)
        self.play(Write(loop_label), LaggedStart(*[Write(l) for l in t_labels], lag_ratio=0.1), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(cell, scale=0.8) for cell in grid.cells.values()], lag_ratio=0.05), run_time=0.8)
        self.play(*[cell.circle.animate.set_stroke(width=4) for cell in grid.cells.values()], run_time=0.2)
        self.play(*[cell.circle.animate.set_stroke(width=2) for cell in grid.cells.values()], run_time=0.2)
        self.play(Write(annotation), run_time=0.5)

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene4_training_prefill(self):
        """Scene 4: Training/Prefill (8 seconds)"""
        header = Text("Training / Prefill Mode", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        grid = KVGrid(cell_size=1.2, spacing=0.4, cell_radius=0.35)
        grid.shift(DOWN * 0.2 + LEFT * 0.5)

        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=28, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 1.0)
            x_labels.add(label)

        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=28, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 1.1)
            t_labels.add(label)

        self.play(Write(header), FadeIn(grid), LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05), run_time=0.6)

        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Loop 1
        phase_label = Text("Loop 1: Parallel execution", font_size=22, color=LOOP_1_COLOR)
        phase_label.to_corner(UR, buff=0.5)

        row_0_cells = [grid.get_cell(0, col) for col in range(3)]
        self.play(*[cell.fill_with_color(LOOP_1_COLOR) for cell in row_0_cells], Write(phase_label), run_time=0.6)

        h_arrows_1 = VGroup()
        for i in range(2):
            arrow = Arrow(row_0_cells[i].get_center() + RIGHT * 0.4, row_0_cells[i+1].get_center() + LEFT * 0.4, color=KV_ARROW_COLOR, stroke_width=3, buff=0)
            h_arrows_1.add(arrow)
        self.play(LaggedStart(*[GrowArrow(a) for a in h_arrows_1], lag_ratio=0.2), run_time=0.6)

        # Loop 2
        phase_label_2 = Text("Loop 2: Uses KV from t₁", font_size=20, color=LOOP_2_COLOR)
        phase_label_2.to_corner(UR, buff=0.5)

        row_1_cells = [grid.get_cell(1, col) for col in range(3)]
        self.play(*[cell.fill_with_color(LOOP_2_COLOR) for cell in row_1_cells], Transform(phase_label, phase_label_2), run_time=0.6)

        h_arrows_2 = VGroup()
        for i in range(2):
            arrow = Arrow(row_1_cells[i].get_center() + RIGHT * 0.4, row_1_cells[i+1].get_center() + LEFT * 0.4, color=KV_ARROW_COLOR, stroke_width=3, buff=0)
            h_arrows_2.add(arrow)

        v_arrows_1 = VGroup()
        for col in range(3):
            arrow = DashedLine(row_0_cells[col].get_center() + DOWN * 0.4, row_1_cells[col].get_center() + UP * 0.4, color=LOOP_1_COLOR, stroke_width=2, dash_length=0.1)
            v_arrows_1.add(arrow)

        self.play(LaggedStart(*[GrowArrow(a) for a in h_arrows_2], lag_ratio=0.2), LaggedStart(*[Create(a) for a in v_arrows_1], lag_ratio=0.1), run_time=0.6)

        # Loop 3
        phase_label_3 = Text("Loop 3: Uses KV from t₂", font_size=20, color=LOOP_3_COLOR)
        phase_label_3.to_corner(UR, buff=0.5)

        row_2_cells = [grid.get_cell(2, col) for col in range(3)]
        self.play(*[cell.fill_with_color(LOOP_3_COLOR) for cell in row_2_cells], Transform(phase_label, phase_label_3), run_time=0.6)

        h_arrows_3 = VGroup()
        for i in range(2):
            arrow = Arrow(row_2_cells[i].get_center() + RIGHT * 0.4, row_2_cells[i+1].get_center() + LEFT * 0.4, color=KV_ARROW_COLOR, stroke_width=3, buff=0)
            h_arrows_3.add(arrow)

        v_arrows_2 = VGroup()
        for col in range(3):
            arrow = DashedLine(row_1_cells[col].get_center() + DOWN * 0.4, row_2_cells[col].get_center() + UP * 0.4, color=LOOP_2_COLOR, stroke_width=2, dash_length=0.1)
            v_arrows_2.add(arrow)

        self.play(LaggedStart(*[GrowArrow(a) for a in h_arrows_3], lag_ratio=0.2), LaggedStart(*[Create(a) for a in v_arrows_2], lag_ratio=0.1), run_time=0.6)

        # Summary
        summary_box = RoundedRectangle(width=8, height=1.2, corner_radius=0.15, color=HIGHLIGHT_COLOR, fill_opacity=0.1, stroke_width=2)
        summary_box.to_edge(DOWN, buff=0.5)

        summary_text = Text("Each loop runs in parallel across all tokens", font_size=24, color=WHITE)
        summary_text.move_to(summary_box.get_center())

        self.play(FadeIn(summary_box), Write(summary_text), run_time=0.8)

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene5_ideal_impractical(self):
        """Scene 5: Ideal but Impractical (6 seconds)"""
        header = Text("What Would Be Ideal?", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        self.play(Write(header), run_time=0.5)

        grid = KVGrid(cell_size=1.0, spacing=0.35, cell_radius=0.3)
        grid.shift(LEFT * 1)

        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 0.9)
            x_labels.add(label)

        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 0.9)
            t_labels.add(label)

        self.play(FadeIn(grid), LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05), run_time=0.5)

        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Sequential processing
        for row in range(3):
            cell = grid.get_cell(row, 0)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.3)

        diagonal_arrow = Arrow(grid.get_cell(2, 0).get_center() + RIGHT * 0.35 + UP * 0.1, grid.get_cell(0, 1).get_center() + LEFT * 0.35, color=LOOP_3_COLOR, stroke_width=4)
        self.play(GrowArrow(diagonal_arrow), run_time=0.4)

        for row in range(3):
            cell = grid.get_cell(row, 1)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.2)

        # Big X
        big_x = Text("✗", font_size=180, color=FAILURE_COLOR)
        big_x.set_opacity(0.7)
        big_x.move_to(grid.get_center())

        self.play(FadeIn(big_x, scale=1.5), run_time=0.4)

        problems = VGroup(
            Text("❌ Kills parallel training", font_size=20, color=FAILURE_COLOR),
            Text("❌ Sequential bottleneck", font_size=20, color=FAILURE_COLOR),
            Text("❌ Can't scale", font_size=20, color=FAILURE_COLOR),
        )
        problems.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        problems.to_edge(RIGHT, buff=0.8)

        self.play(LaggedStart(*[Write(p) for p in problems], lag_ratio=0.25), run_time=1)

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene6_decoding_transition(self):
        """Scene 6: Transition (2 seconds)"""
        title = Text("Decoding During Inference", font_size=48, color=WHITE, weight=BOLD)
        subtitle = Text("Different rules apply...", font_size=28, color=SECONDARY_TEXT, slant=ITALIC)
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(FadeIn(title, scale=0.9), run_time=0.5)
        self.play(Write(subtitle), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.4)

    def scene7_decoding_default(self):
        """Scene 7: Decoding Default (8 seconds)"""
        header = Text("Decoding: Default Approach", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        self.play(Write(header), run_time=0.4)

        grid = KVGrid(cell_size=1.1, spacing=0.35, cell_radius=0.32)
        grid.shift(DOWN * 0.3 + LEFT * 0.5)

        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=26, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 0.95)
            x_labels.add(label)

        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=26, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 1.0)
            t_labels.add(label)

        self.play(FadeIn(grid), LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05), run_time=0.5)

        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Process x₁
        for row in range(3):
            cell = grid.get_cell(row, 0)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.4)

        output_1 = MathTex(r"\hat{y}_1", font_size=24, color=LOOP_3_COLOR)
        output_1.move_to(grid.get_cell(2, 0).get_center() + DOWN * 1.0)
        self.play(Write(output_1), run_time=0.3)

        # KV arrows to x₂
        h_kv_arrows = VGroup()
        for row in range(3):
            arrow = Arrow(grid.get_cell(row, 0).get_center() + RIGHT * 0.35, grid.get_cell(row, 1).get_center() + LEFT * 0.35, color=loop_colors[row], stroke_width=2)
            h_kv_arrows.add(arrow)

        self.play(LaggedStart(*[GrowArrow(a) for a in h_kv_arrows], lag_ratio=0.15), run_time=0.6)

        for row in range(3):
            cell = grid.get_cell(row, 1)
            self.play(cell.fill_with_color(loop_colors[row]), run_time=0.3)

        # Summary
        comparison_text = Text("Stays consistent with training ✓", font_size=22, color=SUCCESS_COLOR)
        comparison_text.to_edge(DOWN, buff=0.6)

        self.play(Write(comparison_text), run_time=0.5)

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene8_ground_truth(self):
        """Scene 8: Ground Truth (4 seconds)"""
        header = Text("Ground Truth Generation", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.4)

        grid = KVGrid(cell_size=1.0, spacing=0.3, cell_radius=0.28)
        grid.shift(UP * 0.5)

        x_labels = VGroup()
        for i in range(3):
            label = MathTex(f"x_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(0, i).get_center() + UP * 0.85)
            x_labels.add(label)

        t_labels = VGroup()
        for i in range(3):
            label = MathTex(f"t_{i+1}", font_size=24, color=WHITE)
            label.move_to(grid.get_cell(i, 0).get_center() + LEFT * 0.9)
            t_labels.add(label)

        self.play(Write(header), FadeIn(grid), LaggedStart(*[Write(l) for l in x_labels + t_labels], lag_ratio=0.05), run_time=0.5)

        loop_colors = [LOOP_1_COLOR, LOOP_2_COLOR, LOOP_3_COLOR]

        # Fill all cells
        for col in range(3):
            for row in range(3):
                cell = grid.get_cell(row, col)
                cell.circle.set_fill(loop_colors[row], opacity=0.8)
                cell.circle.set_stroke(loop_colors[row], width=2)

        # Exit points
        exit_positions = [(2, 0), (1, 1), (0, 2)]
        for row, col in exit_positions:
            cell = grid.get_cell(row, col)
            self.play(cell.circle.animate.set_stroke(HIGHLIGHT_COLOR, width=5), run_time=0.3)

        # LM Head and outputs
        lm_head_box = RoundedRectangle(width=2, height=0.6, corner_radius=0.1, color=SECONDARY_TEXT, fill_opacity=0.3, stroke_width=2)
        lm_head_box.next_to(grid, DOWN, buff=0.4)
        lm_head_label = Text("LM Head", font_size=18, color=WHITE)
        lm_head_label.move_to(lm_head_box.get_center())

        self.play(FadeIn(lm_head_box), Write(lm_head_label), run_time=0.3)

        outputs = VGroup()
        for i, label in enumerate([r"\hat{y}_1", r"\hat{y}_2", r"\hat{y}_3"]):
            output = MathTex(label, font_size=24, color=[loop_colors[2], loop_colors[1], loop_colors[0]][i])
            output.move_to(grid.get_cell(0, i).get_center() + DOWN * 2.5)
            outputs.add(output)

        self.play(LaggedStart(*[Write(o) for o in outputs], lag_ratio=0.15), run_time=0.6)

        ground_truth = MathTex(r"\text{Ground Truth: } y = [\hat{y}_1, \hat{y}_2, \hat{y}_3]", font_size=26, color=WHITE)
        ground_truth.to_edge(DOWN, buff=0.4)
        self.play(Write(ground_truth), run_time=0.5)

        self.wait(0.8)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene9_alternative_strategies(self):
        """Scene 9: Alternative Strategies (8 seconds)"""
        header = Text("Alternative KV Strategies", font_size=32, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.3)

        self.play(Write(header), run_time=0.4)

        panel_positions = [UP * 0.3 + LEFT * 3, UP * 0.3 + RIGHT * 3, DOWN * 2.8 + LEFT * 3, DOWN * 2.8 + RIGHT * 3]
        titles = ["Corresponding Loop", "Average All Loops", "Exit Loop Only", "First Loop Only"]
        title_colors = [SUCCESS_COLOR, LOOP_1_COLOR, LOOP_3_COLOR, FAILURE_COLOR]

        panels = VGroup()
        for pos, title, color in zip(panel_positions, titles, title_colors):
            panel = RoundedRectangle(width=5.5, height=2.8, corner_radius=0.15, color=color, fill_opacity=0.05, stroke_width=2)
            panel.move_to(pos)
            panels.add(panel)

        self.play(LaggedStart(*[FadeIn(p) for p in panels], lag_ratio=0.1), run_time=0.6)

        # Panel titles
        for i, (pos, title, color) in enumerate(zip(panel_positions, titles, title_colors)):
            title_text = Text(title, font_size=18, color=color, weight=BOLD)
            title_text.move_to(pos + UP * 1.1)
            self.play(Write(title_text), run_time=0.3)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene10_results(self):
        """Scene 10: Results (6 seconds)"""
        header = Text("Results Comparison", font_size=36, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.5)

        self.play(Write(header), run_time=0.4)

        strategies = [
            ("Corresponding Loop", SUCCESS_COLOR, "✓ Good"),
            ("Average All Loops", SUCCESS_COLOR, "✓ Good"),
            ("Exit Loop Only", SUCCESS_COLOR, "✓ Good"),
            ("First Loop Only", FAILURE_COLOR, "✗ Bad"),
        ]

        cards = VGroup()
        for name, color, result in strategies:
            card = RoundedRectangle(width=5, height=0.9, corner_radius=0.1, color=color, fill_opacity=0.15, stroke_width=2)
            card_name = Text(name, font_size=22, color=WHITE)
            card_name.move_to(card.get_center() + LEFT * 1)
            card_result = Text(result, font_size=22, color=color, weight=BOLD)
            card_result.move_to(card.get_center() + RIGHT * 1.5)
            cards.add(VGroup(card, card_name, card_result))

        cards.arrange(DOWN, buff=0.25)
        cards.shift(DOWN * 0.3)

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.2), run_time=1.2)

        conclusion = Text("Worth exploring in future research", font_size=22, color=WHITE)
        conclusion.to_edge(DOWN, buff=0.5)
        self.play(Write(conclusion), run_time=0.5)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def scene11_conclusion(self):
        """Scene 11: Conclusion (3 seconds)"""
        header = Text("Key Takeaways", font_size=40, color=WHITE, weight=BOLD)
        header.to_edge(UP, buff=0.8)

        takeaways = VGroup(
            Text("1. Training uses parallel loops with corresponding KV", font_size=24, color=WHITE),
            Text("2. Inference uses sequential tokens with multiple KV options", font_size=24, color=WHITE),
            Text("3. Exit loop KV works despite training mismatch", font_size=24, color=WHITE),
        )
        takeaways.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        takeaways.shift(DOWN * 0.3)

        self.play(Write(header), run_time=0.4)
        for takeaway in takeaways:
            self.play(Write(takeaway), run_time=0.5)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)


if __name__ == "__main__":
    print("=" * 60)
    print("KV-Cache in Looped Models - Manim Animation")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql kv_cache_in_looped_models.py KVCacheAnimation")
    print("  高质量:   manim -pqh kv_cache_in_looped_models.py KVCacheAnimation")
    print("\n单独场景:")
    print("  manim -pql kv_cache_in_looped_models.py Scene1Title")
    print("  manim -pql kv_cache_in_looped_models.py Scene2Introduction")
    print("  manim -pql kv_cache_in_looped_models.py Scene3GridSetup")
    print("  manim -pql kv_cache_in_looped_models.py Scene4TrainingPrefill")
    print("  manim -pql kv_cache_in_looped_models.py Scene5IdealImpractical")
    print("  manim -pql kv_cache_in_looped_models.py Scene6DecodingTransition")
    print("  manim -pql kv_cache_in_looped_models.py Scene7DecodingDefault")
    print("  manim -pql kv_cache_in_looped_models.py Scene8GroundTruth")
    print("  manim -pql kv_cache_in_looped_models.py Scene9AlternativeStrategies")
    print("  manim -pql kv_cache_in_looped_models.py Scene10Results")
    print("  manim -pql kv_cache_in_looped_models.py Scene11Conclusion")
    print("=" * 60)

