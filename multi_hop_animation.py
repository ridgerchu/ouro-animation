"""
Multi-Hop 3-hop Accuracy Line Chart Animation
展示不同 Loop 配置在训练过程中的准确率变化

运行命令:
  完整动画: manim -pql multi_hop_animation.py MultiHopLineChart
  高质量:   manim -pqh multi_hop_animation.py MultiHopLineChart
  1080p60:  manim -pqh --fps 60 multi_hop_animation.py MultiHopLineChart
"""

from manim import *
import numpy as np

# ==================== 数据配置 ====================
# 数据来自 em_steps_stats_tidy.json
STEPS = list(range(1000, 21000, 1000))  # 1k to 20k

# Loop1 数据 (mean values)
LOOP1_DATA = [
    4.93, 5.57, 6.80, 9.41, 10.02, 10.68, 10.78, 11.25, 12.02, 12.14,
    12.53, 13.22, 13.12, 13.33, 13.79, 13.83, 13.79, 13.83, 14.23, 14.14
]

# Loop2 数据 (mean values)
LOOP2_DATA = [
    4.71, 5.07, 11.30, 15.23, 19.11, 16.43, 18.38, 20.91, 24.19, 27.44,
    27.96, 29.70, 30.68, 31.56, 32.20, 32.87, 32.90, 33.43, 33.01, 32.97
]

# Loop4 数据 (mean values)
LOOP4_DATA = [
    3.52, 5.81, 10.58, 14.92, 19.38, 15.51, 28.82, 33.48, 40.35, 35.91,
    48.77, 53.20, 54.50, 56.87, 59.53, 60.35, 60.41, 61.15, 61.84, 62.06
]

# ==================== 颜色配置 ====================
LOOP1_COLOR = "#2A9D8F"    # 青色 - Loop1
LOOP2_COLOR = "#E9C46A"    # 金色 - Loop2
LOOP4_COLOR = "#E63946"    # 红色 - Loop4 (主角，最佳性能)
GRID_COLOR = "#404040"     # 网格
TEXT_COLOR = WHITE         # 文字


class MultiHopLineChart(Scene):
    """Multi-Hop 准确率变化动画"""

    def construct(self):
        # Scene setup
        self.camera.background_color = BLACK  # 纯黑色背景

        # ===== 创建坐标轴 =====
        axes = Axes(
            x_range=[0, 21000, 2000],
            y_range=[0, 70, 10],
            x_length=10,
            y_length=5.5,
            axis_config={
                "color": TEXT_COLOR,
                "stroke_width": 2,
                "include_ticks": True,
                "tick_size": 0.08,
                "include_tip": False,
            },
            x_axis_config={
                "numbers_to_include": [],
            },
            y_axis_config={
                "numbers_to_include": [0, 10, 20, 30, 40, 50, 60, 70],
                "decimal_number_config": {
                    "num_decimal_places": 0,
                    "color": TEXT_COLOR,
                },
                "font_size": 32,
            },
        ).shift(DOWN * 0.3 + LEFT * 0.3)

        # 自定义 X 轴标签 (以 k 为单位)
        x_labels = VGroup()
        for step in range(0, 21000, 2000):
            label = Tex(f"{step//1000}k" if step > 0 else "0", font_size=32, color=TEXT_COLOR)
            label.next_to(axes.c2p(step, 0), DOWN, buff=0.2)
            x_labels.add(label)

        # 修正 Y 轴数字颜色
        for num in axes.y_axis.numbers:
            num.set_color(TEXT_COLOR)

        # ===== 创建网格线 =====
        grid_lines = VGroup()

        # 垂直网格线
        for x in range(2000, 21000, 2000):
            line = DashedLine(
                axes.c2p(x, 0), axes.c2p(x, 70),
                color=GRID_COLOR,
                stroke_width=0.8,
                dash_length=0.05,
            )
            grid_lines.add(line)

        # 水平网格线
        for y in range(10, 71, 10):
            line = DashedLine(
                axes.c2p(0, y), axes.c2p(21000, y),
                color=GRID_COLOR,
                stroke_width=0.8,
                dash_length=0.05,
            )
            grid_lines.add(line)

        # ===== 标题 =====
        # title = Tex(r"\text{3-Hop Reasoning Accuracy}", font_size=36, color=TEXT_COLOR)
        # title.to_edge(UP, buff=0.5)

        # ===== 坐标轴标签 =====
        x_axis_label = Tex(r"\text{Training Steps}", font_size=36, color=TEXT_COLOR)
        x_axis_label.next_to(axes.x_axis, DOWN, buff=0.45)

        y_axis_label = Tex(r"\text{Accuracy (\%)}", font_size=36, color=TEXT_COLOR)
        y_axis_label.rotate(90 * DEGREES)
        y_axis_label.next_to(axes.y_axis, LEFT, buff=0.7)

        # ===== 创建数据点和线 =====
        def create_line_and_markers(data, color, marker_type="circle"):
            """创建线条和标记点"""
            points = [axes.c2p(step, val) for step, val in zip(STEPS, data)]

            # 创建平滑线条
            line = VMobject(color=color, stroke_width=3)
            line.set_points_smoothly(points)

            # 创建标记点
            markers = VGroup()
            for point in points:
                if marker_type == "circle":
                    marker = Dot(point, color=color, radius=0.06)
                elif marker_type == "square":
                    marker = Square(side_length=0.1, color=color, fill_color=color, fill_opacity=1)
                    marker.move_to(point)
                elif marker_type == "triangle":
                    marker = Triangle(color=color, fill_color=color, fill_opacity=1)
                    marker.scale(0.08)
                    marker.move_to(point)
                markers.add(marker)

            return line, markers

        # Loop1 - 方形标记
        loop1_line, loop1_markers = create_line_and_markers(LOOP1_DATA, LOOP1_COLOR, "square")

        # Loop2 - 三角形标记
        loop2_line, loop2_markers = create_line_and_markers(LOOP2_DATA, LOOP2_COLOR, "triangle")

        # Loop4 - 圆形标记 (主角)
        loop4_line, loop4_markers = create_line_and_markers(LOOP4_DATA, LOOP4_COLOR, "circle")

        # ===== 创建图例 =====
        legend_box = RoundedRectangle(
            corner_radius=0.08,
            width=1.6,
            height=1.2,
            color=TEXT_COLOR,
            stroke_width=1.5,
            fill_color="#0D1117",
            fill_opacity=0.9,
        )
        legend_box.to_corner(UR, buff=0.3).shift(DOWN * 0.3)

        # Loop1 图例
        legend_loop1_marker = Square(side_length=0.08, color=LOOP1_COLOR, fill_color=LOOP1_COLOR, fill_opacity=1)
        legend_loop1_line = Line(ORIGIN, RIGHT * 0.3, color=LOOP1_COLOR, stroke_width=2)
        legend_loop1_line.move_to(legend_box.get_center() + UP * 0.32 + LEFT * 0.38)
        legend_loop1_marker.move_to(legend_loop1_line.get_center())
        legend_loop1_text = Tex(r"\text{Loop1}", font_size=18, color=LOOP1_COLOR)
        legend_loop1_text.next_to(legend_loop1_line, RIGHT, buff=0.1)
        legend_loop1 = VGroup(legend_loop1_line, legend_loop1_marker, legend_loop1_text)

        # Loop2 图例
        legend_loop2_marker = Triangle(color=LOOP2_COLOR, fill_color=LOOP2_COLOR, fill_opacity=1).scale(0.07)
        legend_loop2_line = Line(ORIGIN, RIGHT * 0.3, color=LOOP2_COLOR, stroke_width=2)
        legend_loop2_line.move_to(legend_box.get_center() + LEFT * 0.38)
        legend_loop2_marker.move_to(legend_loop2_line.get_center())
        legend_loop2_text = Tex(r"\text{Loop2}", font_size=18, color=LOOP2_COLOR)
        legend_loop2_text.next_to(legend_loop2_line, RIGHT, buff=0.1)
        legend_loop2 = VGroup(legend_loop2_line, legend_loop2_marker, legend_loop2_text)

        # Loop4 图例
        legend_loop4_marker = Dot(color=LOOP4_COLOR, radius=0.04)
        legend_loop4_line = Line(ORIGIN, RIGHT * 0.3, color=LOOP4_COLOR, stroke_width=2)
        legend_loop4_line.move_to(legend_box.get_center() + DOWN * 0.32 + LEFT * 0.38)
        legend_loop4_marker.move_to(legend_loop4_line.get_center())
        legend_loop4_text = Tex(r"\text{Loop4}", font_size=18, color=LOOP4_COLOR)
        legend_loop4_text.next_to(legend_loop4_line, RIGHT, buff=0.1)
        legend_loop4 = VGroup(legend_loop4_line, legend_loop4_marker, legend_loop4_text)

        legend = VGroup(legend_box, legend_loop1, legend_loop2, legend_loop4)

        # ===== 动画序列 =====

        # 1. 显示标题
        #self.play(Write(title), run_time=1)

        # 2. 绘制坐标轴
        self.play(
            Create(axes),
            run_time=1.5
        )

        # 3. 添加标签
        self.play(
            Write(x_labels),
            Write(x_axis_label),
            Write(y_axis_label),
            run_time=1.2
        )

        # 4. 绘制网格
        self.play(
            *[Create(line) for line in grid_lines],
            run_time=0.8
        )

        # 5. 显示图例框
        self.play(
            FadeIn(legend_box),
            run_time=0.5
        )

        # 6. Loop1 出现
        self.play(
            *[FadeIn(m, scale=0.5) for m in loop1_markers],
            run_time=0.8
        )
        self.play(
            Create(loop1_line),
            FadeIn(legend_loop1),
            run_time=1.5,
            rate_func=linear
        )

        self.wait(0.5)

        # 7. Loop2 出现
        self.play(
            *[FadeIn(m, scale=0.5) for m in loop2_markers],
            run_time=0.8
        )
        self.play(
            Create(loop2_line),
            FadeIn(legend_loop2),
            run_time=1.5,
            rate_func=linear
        )

        self.wait(0.5)

        # 8. Loop4 出现 (高亮效果)
        self.play(
            *[FadeIn(m, scale=0.8) for m in loop4_markers],
            run_time=1
        )
        self.play(
            Create(loop4_line),
            FadeIn(legend_loop4),
            run_time=2,
            rate_func=linear
        )

        self.wait(0.5)

        # 9. 高亮 Loop4 最终结果
        final_value_text = Tex(r"\text{62.1\%}", font_size=36, color=LOOP4_COLOR)
        final_value_text.next_to(axes.c2p(20000, 62.06), DOWN, buff=0.2)

        # 高亮圆圈
        highlight_circle = Circle(radius=0.15, color=LOOP4_COLOR, stroke_width=3)
        highlight_circle.move_to(axes.c2p(20000, 62.06))

        self.play(
            Create(highlight_circle),
            FadeIn(final_value_text, shift=DOWN * 0.2),
            run_time=0.8
        )
        self.play(
            highlight_circle.animate.scale(1.5).set_opacity(0),
            run_time=0.6
        )
        self.remove(highlight_circle)

        # 等待
        self.wait(2)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class MultiHopAnimationWithHighlight(Scene):
    """带有渐进高亮效果的 Multi-Hop 动画"""

    def construct(self):
        self.camera.background_color = BLACK  # 纯黑色背景

        # ===== 创建坐标轴 =====
        axes = Axes(
            x_range=[0, 21000, 2000],
            y_range=[0, 70, 10],
            x_length=10,
            y_length=5.5,
            axis_config={
                "color": TEXT_COLOR,
                "stroke_width": 2,
                "include_ticks": True,
                "tick_size": 0.08,
                "include_tip": False,
            },
            x_axis_config={"numbers_to_include": []},
            y_axis_config={
                "numbers_to_include": [0, 10, 20, 30, 40, 50, 60, 70],
                "decimal_number_config": {"num_decimal_places": 0, "color": TEXT_COLOR},
                "font_size": 22,
            },
        ).shift(DOWN * 0.3 + LEFT * 0.3)

        # X 轴标签
        x_labels = VGroup()
        for step in range(0, 21000, 2000):
            label = Tex(f"{step//1000}k" if step > 0 else "0", font_size=22, color=TEXT_COLOR)
            label.next_to(axes.c2p(step, 0), DOWN, buff=0.2)
            x_labels.add(label)

        for num in axes.y_axis.numbers:
            num.set_color(TEXT_COLOR)

        # 网格线
        grid_lines = VGroup()
        for x in range(2000, 21000, 2000):
            line = DashedLine(axes.c2p(x, 0), axes.c2p(x, 70), color=GRID_COLOR, stroke_width=0.8, dash_length=0.05)
            grid_lines.add(line)
        for y in range(10, 71, 10):
            line = DashedLine(axes.c2p(0, y), axes.c2p(21000, y), color=GRID_COLOR, stroke_width=0.8, dash_length=0.05)
            grid_lines.add(line)

        # 标题
        title = Tex(r"\text{3-Hop Reasoning: Loop Depth Comparison}", font_size=32, color=TEXT_COLOR)
        title.to_edge(UP, buff=0.5)

        # 坐标轴标签
        x_axis_label = Tex(r"\text{Training Steps}", font_size=24, color=TEXT_COLOR)
        x_axis_label.next_to(axes.x_axis, DOWN, buff=0.6)

        y_axis_label = Tex(r"\text{Accuracy (\%)}", font_size=24, color=TEXT_COLOR)
        y_axis_label.rotate(90 * DEGREES)
        y_axis_label.next_to(axes.y_axis, LEFT, buff=0.6)

        # 创建线条
        def create_line(data, color):
            points = [axes.c2p(step, val) for step, val in zip(STEPS, data)]
            line = VMobject(color=color, stroke_width=3)
            line.set_points_smoothly(points)
            return line

        loop1_line = create_line(LOOP1_DATA, LOOP1_COLOR)
        loop2_line = create_line(LOOP2_DATA, LOOP2_COLOR)
        loop4_line = create_line(LOOP4_DATA, LOOP4_COLOR)

        # 动画
        self.play(Write(title), run_time=1)
        self.play(Create(axes), run_time=1)
        self.play(Write(x_labels), Write(x_axis_label), Write(y_axis_label), run_time=0.8)
        self.play(*[Create(line) for line in grid_lines], run_time=0.5)

        # 同时绘制三条线
        self.play(
            Create(loop1_line),
            Create(loop2_line),
            Create(loop4_line),
            run_time=3,
            rate_func=linear
        )

        # 图例
        legend_items = VGroup()
        legend_y = 2.5
        for i, (name, color, data) in enumerate([
            ("Loop1", LOOP1_COLOR, LOOP1_DATA),
            ("Loop2", LOOP2_COLOR, LOOP2_DATA),
            ("Loop4", LOOP4_COLOR, LOOP4_DATA),
        ]):
            final_val = data[-1]
            legend_line = Line(ORIGIN, RIGHT * 0.5, color=color, stroke_width=3)
            legend_text = Tex(f"\\text{{{name}: {final_val:.1f}\\%}}", font_size=18, color=color)
            legend_line.move_to(RIGHT * 4.5 + UP * (legend_y - i * 0.5))
            legend_text.next_to(legend_line, RIGHT, buff=0.15)
            legend_items.add(VGroup(legend_line, legend_text))

        self.play(
            LaggedStart(*[FadeIn(item) for item in legend_items], lag_ratio=0.2),
            run_time=1.2
        )

        # 高亮 Loop4 的优势
        self.wait(0.5)

        # 淡化其他线
        self.play(
            loop1_line.animate.set_stroke(opacity=0.3),
            loop2_line.animate.set_stroke(opacity=0.3),
            legend_items[0].animate.set_opacity(0.4),
            legend_items[1].animate.set_opacity(0.4),
            run_time=0.8
        )

        # Loop4 脉冲效果
        pulse = loop4_line.copy()
        pulse.set_stroke(width=8, opacity=0.5)

        self.play(
            pulse.animate.set_stroke(width=15, opacity=0),
            run_time=0.8
        )
        self.remove(pulse)

        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("Multi-Hop 3-hop Accuracy Line Chart Animation")
    print("=" * 60)
    print("\n运行命令:")
    print("  基础版: manim -pql multi_hop_animation.py MultiHopLineChart")
    print("  高亮版: manim -pql multi_hop_animation.py MultiHopAnimationWithHighlight")
    print("  高质量: manim -pqh multi_hop_animation.py MultiHopLineChart")
    print("=" * 60)

