from manim import *
import numpy as np
import math

"""
雷达图模型性能对比动画
运行命令:
  完整动画: manim -pql qwen_line_chart.py QwenLineChart
  高质量:   manim -pqh qwen_line_chart.py QwenLineChart
"""

class QwenLineChart(Scene):
    def construct(self):
        # Scene setup
        self.camera.background_color = BLACK

        # Color definitions
        TEAL_COLOR = "#1C6E68"
        RED_COLOR = "#FF6B6B"
        GRID_COLOR = "#404040"  # 深灰色，在黑色背景下可见
        TEXT_COLOR = WHITE

        # Data points (x in original scale, y)
        base_data = [
            (1, 0.08), (2, 0.12), (4, 0.16), (8, 0.22), (16, 0.30),
            (32, 0.40), (64, 0.50), (128, 0.60), (256, 0.68), (1024, 0.78)
        ]

        rl_data = [
            (1, 0.16), (2, 0.20), (4, 0.24), (8, 0.30), (16, 0.36),
            (32, 0.42), (64, 0.48), (128, 0.54), (256, 0.58), (1024, 0.62)
        ]

        # Convert x to log4 scale for plotting
        def log4(x):
            return math.log(x) / math.log(4)

        base_data_log = [(log4(x), y) for x, y in base_data]
        rl_data_log = [(log4(x), y) for x, y in rl_data]

        # Create axes (x: 0 to 5 in log4 space, y: 0 to 1)
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1.0, 0.2],
            x_length=7,
            y_length=6,
            axis_config={
                "color": TEXT_COLOR,
                "stroke_width": 2,
                "include_ticks": True,
                "tick_size": 0.1,
                "include_tip": False,
            },
            x_axis_config={
                "numbers_to_include": [],
            },
            y_axis_config={
                "numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "decimal_number_config": {
                    "num_decimal_places": 1,
                    "color": TEXT_COLOR,
                },
                "font_size": 24,  # 与 x 轴标签大小匹配
            },
        ).shift(RIGHT * 0.3)

        # Custom x-axis labels (1, 4, 16, 64, 256, 1024)
        x_labels = VGroup()
        x_tick_values = [1, 4, 16, 64, 256, 1024]
        for i, val in enumerate(x_tick_values):
            label = Tex(str(val), font_size=24, color=TEXT_COLOR)
            label.next_to(axes.c2p(i, 0), DOWN, buff=0.2)
            x_labels.add(label)

        # Fix y-axis number colors
        for num in axes.y_axis.numbers:
            num.set_color(TEXT_COLOR)

        # Create grid
        grid_lines = VGroup()

        # Vertical grid lines
        for i in range(6):
            line = DashedLine(
                axes.c2p(i, 0), axes.c2p(i, 1),
                color=GRID_COLOR,
                stroke_width=1,
                dash_length=0.05,
            )
            grid_lines.add(line)

        # Horizontal grid lines
        for y_val in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            line = DashedLine(
                axes.c2p(0, y_val), axes.c2p(5, y_val),
                color=GRID_COLOR,
                stroke_width=1,
                dash_length=0.05,
            )
            grid_lines.add(line)

        # Title
        title = Tex(r"\text{Qwen-2.5-7B}", font_size=30, color=TEXT_COLOR)
        title.next_to(axes, UP, buff=0.4)

        # Y-axis main label "AIME24"
        y_main_label = Tex(r"\text{AIME24}", font_size=32, color=TEXT_COLOR)
        y_main_label.rotate(90 * DEGREES)
        y_main_label.next_to(axes, LEFT, buff=1.2)

        # Y-axis sub label "Coverage (pass@k)"
        y_sub_label = Tex(r"\text{Coverage (pass@k)}", font_size=22, color=TEXT_COLOR)
        y_sub_label.rotate(90 * DEGREES)
        y_sub_label.next_to(axes, LEFT, buff=0.5)

        # Function to create triangle marker
        def create_triangle_marker(position, color, size=0.12):
            triangle = Triangle(color=color, fill_color=color, fill_opacity=1)
            triangle.scale(size)
            triangle.move_to(position)
            return triangle

        # Create Base line and markers
        base_points = [axes.c2p(x, y) for x, y in base_data_log]
        base_line = VMobject(color=TEAL_COLOR, stroke_width=3)
        base_line.set_points_smoothly(base_points)

        base_markers = VGroup()
        for point in base_points:
            marker = create_triangle_marker(point, TEAL_COLOR)
            base_markers.add(marker)

        # Create RL line and markers
        rl_points = [axes.c2p(x, y) for x, y in rl_data_log]
        rl_line = VMobject(color=RED_COLOR, stroke_width=3)
        rl_line.set_points_smoothly(rl_points)

        rl_markers = VGroup()
        for point in rl_points:
            marker = create_triangle_marker(point, RED_COLOR)
            rl_markers.add(marker)

        # Create Legend
        legend_box = RoundedRectangle(
            corner_radius=0.1,
            width=1.8,
            height=1.0,
            color=TEXT_COLOR,
            stroke_width=1.5,
            fill_color=BLACK,
            fill_opacity=0.8,
        )
        legend_box.move_to(axes.c2p(0.8, 0.92))

        # Legend content - Base
        legend_base_line = Line(ORIGIN, RIGHT * 0.4, color=TEAL_COLOR, stroke_width=3)
        legend_base_marker = create_triangle_marker(legend_base_line.get_center(), TEAL_COLOR, size=0.1)
        legend_base_text = Tex(r"\text{Base}", font_size=26, color=TEXT_COLOR)
        legend_base_group = VGroup(legend_base_line, legend_base_marker, legend_base_text)
        legend_base_text.next_to(legend_base_line, RIGHT, buff=0.15)
        legend_base_group.move_to(legend_box.get_center() + UP * 0.2)

        # Legend content - RL
        legend_rl_line = Line(ORIGIN, RIGHT * 0.4, color=RED_COLOR, stroke_width=3)
        legend_rl_marker = create_triangle_marker(legend_rl_line.get_center(), RED_COLOR, size=0.1)
        legend_rl_text = Tex(r"\text{RL}", font_size=26, color=TEXT_COLOR)
        legend_rl_group = VGroup(legend_rl_line, legend_rl_marker, legend_rl_text)
        legend_rl_text.next_to(legend_rl_line, RIGHT, buff=0.15)
        legend_rl_group.move_to(legend_box.get_center() + DOWN * 0.2)

        # Align legend items
        legend_base_group.align_to(legend_box, LEFT).shift(RIGHT * 0.2)
        legend_rl_group.align_to(legend_box, LEFT).shift(RIGHT * 0.2)

        legend = VGroup(legend_box, legend_base_group, legend_rl_group)

        # ===== ANIMATIONS =====

        # 1. Draw axes
        self.play(
            Create(axes),
            run_time=1.5
        )

        # 2. Add labels
        self.play(
            Write(x_labels),
            Write(title),
            Write(y_main_label),
            Write(y_sub_label),
            run_time=1.5
        )

        # 3. Draw grid
        self.play(
            *[Create(line) for line in grid_lines],
            run_time=1
        )

        # 4. Add markers first (points appear first)
        self.play(
            *[FadeIn(m, scale=0.5) for m in base_markers],
            *[FadeIn(m, scale=0.5) for m in rl_markers],
            run_time=1.2
        )

        # 5. Trace out both lines simultaneously (then lines connect the points)
        self.play(
            Create(base_line),
            Create(rl_line),
            run_time=2.5,
            rate_func=linear
        )

        # 6. Add legend (step number unchanged)
        self.play(
            FadeIn(legend),
            run_time=0.8
        )

        # Hold final frame
        self.wait(2)


# For running with: manim -pqh qwen_line_chart.py QwenLineChart
if __name__ == "__main__":
    # This allows running the script directly
    pass

