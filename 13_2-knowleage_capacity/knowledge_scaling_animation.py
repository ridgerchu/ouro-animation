"""
Knowledge Capacity Scaling Animation
展示知识容量随参数量的变化规律，对比 Loop-1 和 Loop-4 模型

运行命令:
  完整动画: manim -pql knowledge_scaling_animation.py KnowledgeScalingAnimation
  高质量:   manim -pqh knowledge_scaling_animation.py KnowledgeScalingAnimation
  1080p60:  manim -pqh --fps 60 knowledge_scaling_animation.py KnowledgeScalingAnimation
"""

from manim import *
import numpy as np
import json
import os

# ==================== 加载数据 ====================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SCRIPT_DIR, 'results.json')

with open(RESULTS_PATH, 'r') as f:
    results = json.load(f)

# ==================== 颜色配置 ====================
DATASET_COLORS = {
    20: "#3498DB",     # 蓝色 - 20k
    50: "#2ECC71",     # 绿色 - 50k
    100: "#F39C12",    # 橙色 - 100k
    200: "#9B59B6",    # 紫色 - 200k
    500: "#E74C3C",    # 红色 - 500k
}

LOOP_COLORS = {
    1: "#7F8C8D",      # 灰色 - Loop1
    4: "#E63946",      # 红色 - Loop4
}

GRID_COLOR = "#404040"
TEXT_COLOR = WHITE
BG_COLOR = BLACK
LINE_2BIT_COLOR = "#E74C3C"
LINE_1BIT_COLOR = "#566573"


def extract_data():
    """从 results.json 提取需要的数据"""
    data_loop1 = []
    data_loop4 = []

    for item in results:
        p_params = item['P_params']
        capacity_ratio = item['capacity_ratio']['R']
        bits_of_knowledge = capacity_ratio * p_params
        dataset_size_k = item['checkpoint_info']['dataset_size_k']
        max_loops = item['checkpoint_info'].get('max_loops', 1)

        data_point = {
            'x': p_params,
            'y': bits_of_knowledge,
            'dataset_size_k': dataset_size_k,
            'max_loops': max_loops,
        }

        if max_loops == 1:
            data_loop1.append(data_point)
        elif max_loops == 4:
            data_loop4.append(data_point)

    return data_loop1, data_loop4


DATA_LOOP1, DATA_LOOP4 = extract_data()


def get_data_by_dataset_and_loop(dataset_k, max_loops):
    """筛选指定数据集大小和循环次数的数据点"""
    source = DATA_LOOP4 if max_loops == 4 else DATA_LOOP1
    return [d for d in source if d['dataset_size_k'] == dataset_k]


def get_smallest_param_data(dataset_k, max_loops):
    """获取指定数据集中参数量最小的数据点"""
    data = get_data_by_dataset_and_loop(dataset_k, max_loops)
    if not data:
        return None
    return min(data, key=lambda d: d['x'])


def get_remaining_data(dataset_k, max_loops, exclude_smallest=True):
    """获取指定数据集中除最小参数外的数据点（按参数量排序）"""
    data = get_data_by_dataset_and_loop(dataset_k, max_loops)
    data_sorted = sorted(data, key=lambda d: d['x'])
    if exclude_smallest and len(data_sorted) > 0:
        return data_sorted[1:]  # 排除最小的
    return data_sorted


# 计算数据范围（对数坐标）
ALL_X = [d['x'] for d in DATA_LOOP1 + DATA_LOOP4]
ALL_Y = [d['y'] for d in DATA_LOOP1 + DATA_LOOP4]

LOG_X_MIN = min(np.floor(np.log10(min(ALL_X))) - 0.2, 5 - 0.2)  # Ensure 0.1M (10^5) is included
LOG_X_MAX = np.ceil(np.log10(max(ALL_X))) + 0.2
LOG_Y_MIN = min(np.floor(np.log10(min(ALL_Y))) - 0.2, 5 - 0.2)  # Ensure 0.1M (10^5) is included
LOG_Y_MAX = np.ceil(np.log10(max(ALL_Y))) + 0.2


class KnowledgeScalingAnimation(Scene):
    """知识容量缩放动画 - 主场景"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # ===== 坐标轴参数 =====
        x_length = 7
        y_length = 4.5
        origin = LEFT * 3.5 + DOWN * 2.5  # 整体往下移，让图表更居中

        # ===== 辅助函数：对数坐标转换 =====
        def log_to_screen(log_x, log_y):
            """将对数坐标转换为屏幕坐标"""
            sx = (log_x - LOG_X_MIN) / (LOG_X_MAX - LOG_X_MIN) * x_length
            sy = (log_y - LOG_Y_MIN) / (LOG_Y_MAX - LOG_Y_MIN) * y_length
            return origin + RIGHT * sx + UP * sy

        def data_to_screen(x, y):
            """将原始数据转换为屏幕坐标"""
            return log_to_screen(np.log10(x), np.log10(y))

        # ===== 创建坐标轴 =====
        x_axis = Arrow(
            origin + LEFT * 0.3,
            origin + RIGHT * (x_length + 0.3),
            color=TEXT_COLOR,
            stroke_width=2,
            tip_length=0.2
        )
        y_axis = Arrow(
            origin + DOWN * 0.3,
            origin + UP * (y_length + 0.3),
            color=TEXT_COLOR,
            stroke_width=2,
            tip_length=0.2
        )

        # ===== X 轴刻度和标签 =====
        x_ticks = VGroup()
        x_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            pos = log_to_screen(log_val, LOG_Y_MIN)
            tick = Line(pos + DOWN * 0.1, pos + UP * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            x_ticks.add(tick)

            val = 10 ** log_val
            if val >= 1e6:
                label_text = f"{val/1e6:.0f}M"
            else:
                label_text = f"{val/1e6:.1f}M"
            label = Tex(label_text, font_size=18, color=TEXT_COLOR)
            label.next_to(tick, DOWN, buff=0.15)
            x_labels.add(label)

        # ===== Y 轴刻度和标签 =====
        y_ticks = VGroup()
        y_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            pos = log_to_screen(LOG_X_MIN, log_val)
            tick = Line(pos + LEFT * 0.1, pos + RIGHT * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            y_ticks.add(tick)

            val = 10 ** log_val
            if val >= 1e6:
                label_text = f"{val/1e6:.0f}M"
            else:
                label_text = f"{val/1e6:.1f}M"
            label = Tex(label_text, font_size=18, color=TEXT_COLOR)
            label.next_to(tick, LEFT, buff=0.15)
            y_labels.add(label)

        # ===== 网格线 =====
        grid_lines = VGroup()
        for log_x in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            start = log_to_screen(log_x, LOG_Y_MIN)
            end = log_to_screen(log_x, LOG_Y_MAX)
            line = DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05)
            grid_lines.add(line)
        for log_y in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            start = log_to_screen(LOG_X_MIN, log_y)
            end = log_to_screen(LOG_X_MAX, log_y)
            line = DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05)
            grid_lines.add(line)

        # ===== 标题（用 Loop 标签替代）=====
        loop1_label = Tex(r"Standard Models (Loop-1)", font_size=24, color=GREY_B)
        loop1_label.to_edge(UP, buff=0.4).shift(LEFT * 2.5)

        loop4_label = Tex(r"Looped Models (Loop-4)", font_size=24, color=GREY_B)
        loop4_label.to_edge(UP, buff=0.4).shift(RIGHT * 2.5)

        # ===== 坐标轴标签 =====
        x_axis_label = Tex(r"Parameters (log scale)", font_size=20, color=TEXT_COLOR)
        x_axis_label.next_to(x_axis, DOWN, buff=0.4)

        y_axis_label = Tex(r"Bits of Knowledge (log scale)", font_size=20, color=TEXT_COLOR)
        y_axis_label.rotate(90 * DEGREES)
        y_axis_label.next_to(y_axis, LEFT, buff=0.5)

        # ===== 参考线 =====
        # 2 bit/param 线
        ref_2bit_points = []
        for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50):
            x = 10 ** log_x
            y = 2 * x
            log_y = np.log10(y)
            if LOG_Y_MIN <= log_y <= LOG_Y_MAX:
                ref_2bit_points.append(log_to_screen(log_x, log_y))

        ref_line_2bit = DashedVMobject(
            VMobject(color=LINE_2BIT_COLOR, stroke_width=2.5).set_points_as_corners(ref_2bit_points),
            num_dashes=25
        ) if len(ref_2bit_points) >= 2 else VGroup()

        # 1 bit/param 线
        ref_1bit_points = []
        for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50):
            x = 10 ** log_x
            y = x
            log_y = np.log10(y)
            if LOG_Y_MIN <= log_y <= LOG_Y_MAX:
                ref_1bit_points.append(log_to_screen(log_x, log_y))

        ref_line_1bit = VMobject(color=LINE_1BIT_COLOR, stroke_width=2)
        if len(ref_1bit_points) >= 2:
            ref_line_1bit.set_points_as_corners(ref_1bit_points)

        # ===== 创建数据点（带 jitter 避免重叠）=====
        def create_data_points(data, is_loop4=False):
            points = VGroup()
            for i, d in enumerate(data):
                # 添加 jitter：主要在 y 方向区分，x 方向保持相同参数量
                jitter_x = 0.01 * (1 if is_loop4 else -1)  # x 轴很小的偏移
                jitter_y = 0.06 * (1 if is_loop4 else -1)  # y 轴较大的偏移用于区分

                log_x = np.log10(d['x']) + jitter_x
                log_y = np.log10(d['y']) + jitter_y
                pos = log_to_screen(log_x, log_y)

                color = DATASET_COLORS.get(d['dataset_size_k'], WHITE)

                if is_loop4:
                    dot = Dot(pos, color=color, radius=0.1)
                    dot.set_stroke(color=WHITE, width=1.5)
                else:
                    dot = Dot(pos, color=color, radius=0.06)
                    dot.set_stroke(color=WHITE, width=0.8)

                points.add(dot)
            return points

        loop1_points = create_data_points(DATA_LOOP1, is_loop4=False)
        loop4_points = create_data_points(DATA_LOOP4, is_loop4=True)

        # ===== 图例 =====
        legend_box = RoundedRectangle(
            corner_radius=0.1, width=2.6, height=3.5,
            color=TEXT_COLOR, stroke_width=1.5,
            fill_color=BG_COLOR, fill_opacity=0.95,
        )
        # 将图例框与图表垂直居中对齐
        graph_center_y = origin[1] + y_length / 2
        legend_box.move_to(RIGHT * 5 + UP * graph_center_y)

        # 数据集大小图例
        dataset_legend = VGroup()
        legend_title = Tex(r"\textbf{Dataset Size}", font_size=14, color=TEXT_COLOR)
        legend_title.move_to(legend_box.get_top() + DOWN * 0.25)
        dataset_legend.add(legend_title)

        for i, (size, color) in enumerate(sorted(DATASET_COLORS.items())):
            dot = Dot(color=color, radius=0.06)
            text = Tex(f"{size}k", font_size=13, color=color)
            dot.move_to(legend_box.get_top() + DOWN * (0.5 + i * 0.3) + LEFT * 0.7)
            text.next_to(dot, RIGHT, buff=0.12)
            dataset_legend.add(VGroup(dot, text))

        # Loop 类型图例
        loop_legend = VGroup()
        loop_title = Tex(r"\textbf{Model Type}", font_size=14, color=TEXT_COLOR)
        loop_title.move_to(legend_box.get_top() + DOWN * 2.0)
        loop_legend.add(loop_title)

        loop1_legend_dot = Dot(color=GREY, radius=0.05)
        loop1_legend_text = Tex(r"Loop-1 (small)", font_size=12, color=GREY)
        loop1_legend_dot.move_to(legend_box.get_top() + DOWN * 2.3 + LEFT * 0.7)
        loop1_legend_text.next_to(loop1_legend_dot, RIGHT, buff=0.1)
        loop_legend.add(VGroup(loop1_legend_dot, loop1_legend_text))

        loop4_legend_dot = Dot(color=GREY, radius=0.08)
        loop4_legend_dot.set_stroke(color=WHITE, width=1)
        loop4_legend_text = Tex(r"Loop-4 (large)", font_size=12, color=GREY)
        loop4_legend_dot.move_to(legend_box.get_top() + DOWN * 2.6 + LEFT * 0.7)
        loop4_legend_text.next_to(loop4_legend_dot, RIGHT, buff=0.1)
        loop_legend.add(VGroup(loop4_legend_dot, loop4_legend_text))

        # 参考线图例
        ref_legend = VGroup()
        ref_2bit_legend = DashedLine(ORIGIN, RIGHT * 0.4, color=LINE_2BIT_COLOR, stroke_width=2)
        ref_2bit_legend_text = Tex(r"2 bit/param", font_size=11, color=LINE_2BIT_COLOR)
        ref_2bit_legend.move_to(legend_box.get_top() + DOWN * 3.1 + LEFT * 0.5)
        ref_2bit_legend_text.next_to(ref_2bit_legend, RIGHT, buff=0.08)
        ref_legend.add(VGroup(ref_2bit_legend, ref_2bit_legend_text))

        ref_1bit_legend = Line(ORIGIN, RIGHT * 0.4, color=LINE_1BIT_COLOR, stroke_width=2)
        ref_1bit_legend_text = Tex(r"1 bit/param", font_size=11, color=LINE_1BIT_COLOR)
        ref_1bit_legend.move_to(legend_box.get_top() + DOWN * 3.35 + LEFT * 0.5)
        ref_1bit_legend_text.next_to(ref_1bit_legend, RIGHT, buff=0.08)
        ref_legend.add(VGroup(ref_1bit_legend, ref_1bit_legend_text))

        legend = VGroup(legend_box, dataset_legend, loop_legend, ref_legend)

        # ===== 动画序列 =====

        # 1. 坐标轴
        self.play(Create(x_axis), Create(y_axis), run_time=1)
        self.play(
            *[Create(t) for t in x_ticks], *[Write(l) for l in x_labels],
            *[Create(t) for t in y_ticks], *[Write(l) for l in y_labels],
            run_time=1
        )
        self.play(Write(x_axis_label), Write(y_axis_label), run_time=0.6)

        # 3. 网格
        self.play(*[Create(line) for line in grid_lines], run_time=0.6)

        # 4. 参考线
        self.play(Create(ref_line_2bit), Create(ref_line_1bit), run_time=1.2)

        # 5. 图例
        self.play(FadeIn(legend_box), run_time=0.4)
        self.play(
            LaggedStart(*[FadeIn(item) for item in dataset_legend], lag_ratio=0.08),
            run_time=0.8
        )
        self.play(
            LaggedStart(*[FadeIn(item) for item in loop_legend], lag_ratio=0.1),
            run_time=0.5
        )
        self.play(
            LaggedStart(*[FadeIn(item) for item in ref_legend], lag_ratio=0.1),
            run_time=0.4
        )

        self.wait(0.3)

        # 6. Loop-1 标签和数据点
        self.play(Write(loop1_label), run_time=0.5)
        self.play(
            LaggedStart(*[GrowFromCenter(p) for p in loop1_points], lag_ratio=0.015),
            run_time=1.5
        )

        self.wait(0.5)

        # 7. Loop-4 标签和数据点
        self.play(Write(loop4_label), run_time=0.5)
        self.play(
            LaggedStart(*[GrowFromCenter(p) for p in loop4_points], lag_ratio=0.015),
            run_time=1.5
        )

        self.wait(1)

        # 8. 结论
        conclusion = Tex(
            r"Loop-1 and Loop-4 models achieve similar knowledge capacity",
            font_size=22, color="#FFD700"
        )
        conclusion.to_edge(DOWN, buff=0.35)

        self.play(Write(conclusion), run_time=1)
        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


class LoopComparison(Scene):
    """Loop-1 vs Loop-4 直接对比"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # 坐标轴参数
        x_length = 7
        y_length = 4.5
        origin = LEFT * 3.5 + DOWN * 1.8

        def log_to_screen(log_x, log_y):
            sx = (log_x - LOG_X_MIN) / (LOG_X_MAX - LOG_X_MIN) * x_length
            sy = (log_y - LOG_Y_MIN) / (LOG_Y_MAX - LOG_Y_MIN) * y_length
            return origin + RIGHT * sx + UP * sy

        # 坐标轴
        x_axis = Arrow(origin + LEFT * 0.3, origin + RIGHT * (x_length + 0.3),
                       color=TEXT_COLOR, stroke_width=2, tip_length=0.2)
        y_axis = Arrow(origin + DOWN * 0.3, origin + UP * (y_length + 0.3),
                       color=TEXT_COLOR, stroke_width=2, tip_length=0.2)

        # 刻度
        x_ticks = VGroup()
        x_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            pos = log_to_screen(log_val, LOG_Y_MIN)
            tick = Line(pos + DOWN * 0.1, pos + UP * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            x_ticks.add(tick)
            val = 10 ** log_val
            label = Tex(f"{val/1e6:.1f}M" if val < 1e6 else f"{val/1e6:.0f}M", font_size=18, color=TEXT_COLOR)
            label.next_to(tick, DOWN, buff=0.15)
            x_labels.add(label)

        y_ticks = VGroup()
        y_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            pos = log_to_screen(LOG_X_MIN, log_val)
            tick = Line(pos + LEFT * 0.1, pos + RIGHT * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            y_ticks.add(tick)
            val = 10 ** log_val
            label = Tex(f"{val/1e6:.1f}M" if val < 1e6 else f"{val/1e6:.0f}M", font_size=18, color=TEXT_COLOR)
            label.next_to(tick, LEFT, buff=0.15)
            y_labels.add(label)

        # 网格
        grid_lines = VGroup()
        for log_x in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            start = log_to_screen(log_x, LOG_Y_MIN)
            end = log_to_screen(log_x, LOG_Y_MAX)
            grid_lines.add(DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05))
        for log_y in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            start = log_to_screen(LOG_X_MIN, log_y)
            end = log_to_screen(LOG_X_MAX, log_y)
            grid_lines.add(DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05))

        # 标题
        title = Tex(r"\textbf{Loop-1 vs Loop-4: Knowledge Capacity}", font_size=34, color=TEXT_COLOR)
        title.to_edge(UP, buff=0.4)

        # 坐标轴标签
        x_label = Tex(r"Parameters (log scale)", font_size=20, color=TEXT_COLOR)
        x_label.next_to(x_axis, DOWN, buff=0.4)
        y_label = Tex(r"Bits of Knowledge (log scale)", font_size=20, color=TEXT_COLOR)
        y_label.rotate(90 * DEGREES).next_to(y_axis, LEFT, buff=0.5)

        # 参考线
        ref_2bit_points = [log_to_screen(log_x, np.log10(2 * 10**log_x))
                          for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50)
                          if LOG_Y_MIN <= np.log10(2 * 10**log_x) <= LOG_Y_MAX]
        ref_line_2bit = DashedVMobject(
            VMobject(color=LINE_2BIT_COLOR, stroke_width=2.5).set_points_as_corners(ref_2bit_points),
            num_dashes=25
        ) if len(ref_2bit_points) >= 2 else VGroup()

        ref_1bit_points = [log_to_screen(log_x, log_x)
                          for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50)
                          if LOG_Y_MIN <= log_x <= LOG_Y_MAX]
        ref_line_1bit = VMobject(color=LINE_1BIT_COLOR, stroke_width=2)
        if len(ref_1bit_points) >= 2:
            ref_line_1bit.set_points_as_corners(ref_1bit_points)

        # 数据点（按 Loop 类型区分颜色）
        def create_loop_points(data, color, radius, jitter_sign):
            points = VGroup()
            for d in data:
                jitter_x = 0.01 * jitter_sign  # x 轴很小的偏移
                jitter_y = 0.06 * jitter_sign  # y 轴较大的偏移用于区分
                log_x = np.log10(d['x']) + jitter_x
                log_y = np.log10(d['y']) + jitter_y
                pos = log_to_screen(log_x, log_y)
                dot = Dot(pos, color=color, radius=radius)
                dot.set_stroke(color=WHITE, width=1 if radius < 0.08 else 1.5)
                points.add(dot)
            return points

        loop1_points = create_loop_points(DATA_LOOP1, LOOP_COLORS[1], 0.06, -1)
        loop4_points = create_loop_points(DATA_LOOP4, LOOP_COLORS[4], 0.1, 1)

        # 图例
        legend_loop1 = VGroup(
            Dot(color=LOOP_COLORS[1], radius=0.06),
            Tex(r"Loop-1 (Standard)", font_size=16, color=LOOP_COLORS[1])
        )
        legend_loop1[1].next_to(legend_loop1[0], RIGHT, buff=0.1)
        legend_loop1.move_to(RIGHT * 4.5 + UP * 2.5)

        legend_loop4 = VGroup(
            Dot(color=LOOP_COLORS[4], radius=0.09).set_stroke(WHITE, 1),
            Tex(r"Loop-4 (Looped)", font_size=16, color=LOOP_COLORS[4])
        )
        legend_loop4[1].next_to(legend_loop4[0], RIGHT, buff=0.1)
        legend_loop4.move_to(RIGHT * 4.5 + UP * 2.0)

        ref_legend = VGroup(
            DashedLine(ORIGIN, RIGHT * 0.4, color=LINE_2BIT_COLOR, stroke_width=2),
            Tex(r"2 bit/param", font_size=14, color=LINE_2BIT_COLOR)
        )
        ref_legend[1].next_to(ref_legend[0], RIGHT, buff=0.1)
        ref_legend.move_to(RIGHT * 4.5 + UP * 1.4)

        ref_legend2 = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=LINE_1BIT_COLOR, stroke_width=2),
            Tex(r"1 bit/param", font_size=14, color=LINE_1BIT_COLOR)
        )
        ref_legend2[1].next_to(ref_legend2[0], RIGHT, buff=0.1)
        ref_legend2.move_to(RIGHT * 4.5 + UP * 1.0)

        # ===== 动画 =====
        self.play(Write(title), run_time=1)
        self.play(Create(x_axis), Create(y_axis), run_time=1)
        self.play(
            *[Create(t) for t in x_ticks], *[Write(l) for l in x_labels],
            *[Create(t) for t in y_ticks], *[Write(l) for l in y_labels],
            run_time=0.8
        )
        self.play(Write(x_label), Write(y_label), run_time=0.5)
        self.play(*[Create(line) for line in grid_lines], run_time=0.5)
        self.play(
            Create(ref_line_2bit), Create(ref_line_1bit),
            FadeIn(ref_legend), FadeIn(ref_legend2),
            run_time=1
        )

        # Loop-1
        self.play(
            LaggedStart(*[GrowFromCenter(p) for p in loop1_points], lag_ratio=0.01),
            FadeIn(legend_loop1),
            run_time=1.2
        )
        self.wait(0.5)

        # Loop-4
        self.play(
            LaggedStart(*[GrowFromCenter(p) for p in loop4_points], lag_ratio=0.01),
            FadeIn(legend_loop4),
            run_time=1.2
        )
        self.wait(0.5)

        # 高亮
        self.play(
            *[p.animate.set_opacity(0.25) for p in loop1_points],
            legend_loop1.animate.set_opacity(0.4),
            run_time=0.6
        )

        # 结论
        conclusion = VGroup(
            Tex(r"Loop-4 models consistently achieve", font_size=20, color="#FFD700"),
            Tex(r"higher knowledge capacity", font_size=20, color="#FFD700"),
        )
        conclusion.arrange(DOWN, buff=0.08).to_edge(DOWN, buff=0.35)

        self.play(Write(conclusion), run_time=1)
        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


class KnowledgeScalingByDataset(Scene):
    """按数据集大小分组展示"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        x_length = 7
        y_length = 4.5
        origin = LEFT * 3.5 + DOWN * 1.8

        def log_to_screen(log_x, log_y):
            sx = (log_x - LOG_X_MIN) / (LOG_X_MAX - LOG_X_MIN) * x_length
            sy = (log_y - LOG_Y_MIN) / (LOG_Y_MAX - LOG_Y_MIN) * y_length
            return origin + RIGHT * sx + UP * sy

        # 坐标轴
        x_axis = Arrow(origin + LEFT * 0.3, origin + RIGHT * (x_length + 0.3),
                       color=TEXT_COLOR, stroke_width=2, tip_length=0.2)
        y_axis = Arrow(origin + DOWN * 0.3, origin + UP * (y_length + 0.3),
                       color=TEXT_COLOR, stroke_width=2, tip_length=0.2)

        # 刻度
        x_ticks = VGroup()
        x_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            pos = log_to_screen(log_val, LOG_Y_MIN)
            tick = Line(pos + DOWN * 0.1, pos + UP * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            x_ticks.add(tick)
            val = 10 ** log_val
            label = Tex(f"{val/1e6:.1f}M" if val < 1e6 else f"{val/1e6:.0f}M", font_size=18, color=TEXT_COLOR)
            label.next_to(tick, DOWN, buff=0.15)
            x_labels.add(label)

        y_ticks = VGroup()
        y_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            pos = log_to_screen(LOG_X_MIN, log_val)
            tick = Line(pos + LEFT * 0.1, pos + RIGHT * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            y_ticks.add(tick)
            val = 10 ** log_val
            label = Tex(f"{val/1e6:.1f}M" if val < 1e6 else f"{val/1e6:.0f}M", font_size=18, color=TEXT_COLOR)
            label.next_to(tick, LEFT, buff=0.15)
            y_labels.add(label)

        # 网格
        grid_lines = VGroup()
        for log_x in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            start = log_to_screen(log_x, LOG_Y_MIN)
            end = log_to_screen(log_x, LOG_Y_MAX)
            grid_lines.add(DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05))
        for log_y in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            start = log_to_screen(LOG_X_MIN, log_y)
            end = log_to_screen(LOG_X_MAX, log_y)
            grid_lines.add(DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05))

        # 标题
        title = Tex(r"\textbf{Knowledge Scaling by Dataset Size}", font_size=34, color=TEXT_COLOR)
        title.to_edge(UP, buff=0.4)

        # 坐标轴标签
        x_label = Tex(r"Parameters (log scale)", font_size=20, color=TEXT_COLOR)
        x_label.next_to(x_axis, DOWN, buff=0.4)
        y_label = Tex(r"Bits of Knowledge (log scale)", font_size=20, color=TEXT_COLOR)
        y_label.rotate(90 * DEGREES).next_to(y_axis, LEFT, buff=0.5)

        # 参考线
        ref_2bit_points = [log_to_screen(log_x, np.log10(2 * 10**log_x))
                          for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50)
                          if LOG_Y_MIN <= np.log10(2 * 10**log_x) <= LOG_Y_MAX]
        ref_line_2bit = DashedVMobject(
            VMobject(color=LINE_2BIT_COLOR, stroke_width=2).set_points_as_corners(ref_2bit_points),
            num_dashes=25
        ) if len(ref_2bit_points) >= 2 else VGroup()

        ref_1bit_points = [log_to_screen(log_x, log_x)
                          for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50)
                          if LOG_Y_MIN <= log_x <= LOG_Y_MAX]
        ref_line_1bit = VMobject(color=LINE_1BIT_COLOR, stroke_width=2)
        if len(ref_1bit_points) >= 2:
            ref_line_1bit.set_points_as_corners(ref_1bit_points)

        # 按数据集分组
        all_data = DATA_LOOP1 + DATA_LOOP4
        dataset_groups = {}
        for d in all_data:
            size = d['dataset_size_k']
            if size not in dataset_groups:
                dataset_groups[size] = []
            dataset_groups[size].append(d)

        def create_point(d):
            is_loop4 = d['max_loops'] == 4
            jitter_x = 0.01 * (1 if is_loop4 else -1)  # x 轴很小的偏移
            jitter_y = 0.06 * (1 if is_loop4 else -1)  # y 轴较大的偏移用于区分
            log_x = np.log10(d['x']) + jitter_x
            log_y = np.log10(d['y']) + jitter_y
            pos = log_to_screen(log_x, log_y)
            color = DATASET_COLORS.get(d['dataset_size_k'], WHITE)
            radius = 0.1 if is_loop4 else 0.06
            dot = Dot(pos, color=color, radius=radius)
            dot.set_stroke(color=WHITE, width=1.5 if is_loop4 else 0.8)
            return dot

        # ===== 动画 =====
        self.play(Write(title), run_time=1)
        self.play(Create(x_axis), Create(y_axis), run_time=1)
        self.play(
            *[Create(t) for t in x_ticks], *[Write(l) for l in x_labels],
            *[Create(t) for t in y_ticks], *[Write(l) for l in y_labels],
            run_time=0.8
        )
        self.play(Write(x_label), Write(y_label), run_time=0.5)
        self.play(*[Create(line) for line in grid_lines], run_time=0.5)
        self.play(Create(ref_line_2bit), Create(ref_line_1bit), run_time=0.8)

        # 按数据集依次显示
        all_points = VGroup()
        legend_items = VGroup()

        for i, (size, points_data) in enumerate(sorted(dataset_groups.items())):
            color = DATASET_COLORS.get(size, WHITE)
            points = VGroup(*[create_point(d) for d in points_data])

            legend_dot = Dot(color=color, radius=0.07)
            legend_text = Tex(f"{size}k samples", font_size=16, color=color)
            legend_dot.move_to(RIGHT * 5 + UP * (2.5 - i * 0.45))
            legend_text.next_to(legend_dot, RIGHT, buff=0.12)
            legend_item = VGroup(legend_dot, legend_text)

            self.play(
                LaggedStart(*[GrowFromCenter(p) for p in points], lag_ratio=0.03),
                FadeIn(legend_item),
                run_time=1
            )

            all_points.add(points)
            legend_items.add(legend_item)
            self.wait(0.2)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


class NarrativeKnowledgeScaling(Scene):
    """叙事式知识容量缩放动画 - 按脚本顺序逐步展示数据"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # ===== 坐标轴参数 =====
        x_length = 7
        y_length = 4.5
        origin = LEFT * 3.5 + DOWN * 2.0

        # ===== 辅助函数 =====
        def log_to_screen(log_x, log_y):
            sx = (log_x - LOG_X_MIN) / (LOG_X_MAX - LOG_X_MIN) * x_length
            sy = (log_y - LOG_Y_MIN) / (LOG_Y_MAX - LOG_Y_MIN) * y_length
            return origin + RIGHT * sx + UP * sy

        def create_dot(data_point, is_loop4=False):
            """根据数据点创建圆点"""
            # 无偏移，完全重叠显示
            log_x = np.log10(data_point['x'])
            log_y = np.log10(data_point['y'])
            pos = log_to_screen(log_x, log_y)
            color = DATASET_COLORS.get(data_point['dataset_size_k'], WHITE)

            if is_loop4:
                dot = Dot(pos, color=color, radius=0.1, fill_opacity=0.6)
                dot.set_stroke(color=WHITE, width=1.5)
            else:
                dot = Dot(pos, color=color, radius=0.06, fill_opacity=0.6)
                dot.set_stroke(color=WHITE, width=0.8)
            return dot

        def create_dots_for_data(data_list, is_loop4=False):
            """为数据列表创建圆点组"""
            return VGroup(*[create_dot(d, is_loop4) for d in data_list])

        # ==================== Phase 0: Setup ====================
        # 坐标轴
        x_axis = Arrow(
            origin + LEFT * 0.3,
            origin + RIGHT * (x_length + 0.3),
            color=TEXT_COLOR, stroke_width=2, tip_length=0.2
        )
        y_axis = Arrow(
            origin + DOWN * 0.3,
            origin + UP * (y_length + 0.3),
            color=TEXT_COLOR, stroke_width=2, tip_length=0.2
        )

        # 刻度
        x_ticks = VGroup()
        x_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            pos = log_to_screen(log_val, LOG_Y_MIN)
            tick = Line(pos + DOWN * 0.1, pos + UP * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            x_ticks.add(tick)
            val = 10 ** log_val
            label_text = f"{val/1e6:.0f}M" if val >= 1e6 else f"{val/1e6:.1f}M"
            label = Tex(label_text, font_size=18, color=TEXT_COLOR)
            label.next_to(tick, DOWN, buff=0.15)
            x_labels.add(label)

        y_ticks = VGroup()
        y_labels = VGroup()
        for log_val in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            pos = log_to_screen(LOG_X_MIN, log_val)
            tick = Line(pos + LEFT * 0.1, pos + RIGHT * 0.1, color=TEXT_COLOR, stroke_width=1.5)
            y_ticks.add(tick)
            val = 10 ** log_val
            label_text = f"{val/1e6:.0f}M" if val >= 1e6 else f"{val/1e6:.1f}M"
            label = Tex(label_text, font_size=18, color=TEXT_COLOR)
            label.next_to(tick, LEFT, buff=0.15)
            y_labels.add(label)

        # 网格线
        grid_lines = VGroup()
        for log_x in range(int(np.ceil(LOG_X_MIN)), int(np.floor(LOG_X_MAX)) + 1):
            start = log_to_screen(log_x, LOG_Y_MIN)
            end = log_to_screen(log_x, LOG_Y_MAX)
            grid_lines.add(DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05))
        for log_y in range(int(np.ceil(LOG_Y_MIN)), int(np.floor(LOG_Y_MAX)) + 1):
            start = log_to_screen(LOG_X_MIN, log_y)
            end = log_to_screen(LOG_X_MAX, log_y)
            grid_lines.add(DashedLine(start, end, color=GRID_COLOR, stroke_width=0.8, dash_length=0.05))

        # 坐标轴标签
        x_axis_label = Tex(r"Number of Params", font_size=24, color=TEXT_COLOR)
        x_axis_label.next_to(x_axis, DOWN, buff=0.5)

        y_axis_label = Tex(r"Bits of Knowledge", font_size=24, color=TEXT_COLOR)
        y_axis_label.rotate(90 * DEGREES)
        y_axis_label.next_to(y_axis, LEFT, buff=0.6)

        # 参考线（只保留 2bit/param）
        ref_2bit_points = []
        for log_x in np.linspace(LOG_X_MIN, LOG_X_MAX, 50):
            y = 2 * (10 ** log_x)
            log_y = np.log10(y)
            if LOG_Y_MIN <= log_y <= LOG_Y_MAX:
                ref_2bit_points.append(log_to_screen(log_x, log_y))

        ref_line_2bit = DashedVMobject(
            VMobject(color=LINE_2BIT_COLOR, stroke_width=2.5).set_points_as_corners(ref_2bit_points),
            num_dashes=25
        ) if len(ref_2bit_points) >= 2 else VGroup()

        # 2bit/param 线的标注（直接放在图上右侧）
        ref_2bit_label = Tex(r"2 bit/param", font_size=18, color=LINE_2BIT_COLOR)
        if len(ref_2bit_points) >= 2:
            # 放在线的右端点旁边
            ref_2bit_label.next_to(ref_2bit_points[-1], RIGHT, buff=0.1)

        # ==================== 创建常驻图例（无边框）====================
        # 图例基准位置
        legend_base = RIGHT * 4.8 + UP * 2.0

        # Model Type 图例（常驻）
        loop_legend = VGroup()
        loop_title = Tex(r"\textbf{Model Type}", font_size=20, color=TEXT_COLOR)
        loop_title.move_to(legend_base)
        loop_legend.add(loop_title)

        loop1_legend_dot = Dot(color=GREY, radius=0.08)
        loop1_legend_dot.set_stroke(color=WHITE, width=1)
        loop1_legend_text = Tex(r"Loop-1 (small)", font_size=18, color=GREY)
        loop1_legend_dot.move_to(legend_base + DOWN * 0.45 + LEFT * 0.6)
        loop1_legend_text.next_to(loop1_legend_dot, RIGHT, buff=0.12)
        loop_legend.add(VGroup(loop1_legend_dot, loop1_legend_text))

        loop4_legend_dot = Dot(color=GREY, radius=0.12)
        loop4_legend_dot.set_stroke(color=WHITE, width=1.5)
        loop4_legend_text = Tex(r"Loop-4 (large)", font_size=18, color=GREY)
        loop4_legend_dot.move_to(legend_base + DOWN * 0.9 + LEFT * 0.6)
        loop4_legend_text.next_to(loop4_legend_dot, RIGHT, buff=0.12)
        loop_legend.add(VGroup(loop4_legend_dot, loop4_legend_text))

        # Dataset Size 标题
        dataset_title = Tex(r"\textbf{Dataset Size}", font_size=20, color=TEXT_COLOR)
        dataset_title.move_to(legend_base + DOWN * 1.5)

        # 预创建各数据集图例项（稍后逐个显示）
        dataset_legend_items = {}
        for i, (size, color) in enumerate(sorted(DATASET_COLORS.items())):
            dot = Dot(color=color, radius=0.09)
            text = Tex(f"{size}k", font_size=18, color=color)
            dot.move_to(legend_base + DOWN * (2.0 + i * 0.4) + LEFT * 0.6)
            text.next_to(dot, RIGHT, buff=0.15)
            dataset_legend_items[size] = VGroup(dot, text)

        # Phase 0 动画: 绘制坐标系 + 常驻图例
        self.play(Create(x_axis), Create(y_axis), run_time=1)
        self.play(
            *[Create(t) for t in x_ticks], *[Write(l) for l in x_labels],
            *[Create(t) for t in y_ticks], *[Write(l) for l in y_labels],
            run_time=1
        )
        self.play(Write(x_axis_label), Write(y_axis_label), run_time=0.6)
        self.play(*[Create(line) for line in grid_lines], run_time=0.6)

        # 显示 Model Type 图例（常驻）
        self.play(FadeIn(loop_legend), FadeIn(dataset_title), run_time=0.8)
        self.wait(0.3)

        # ==================== Phase 1: 1M Model, Loop-1 ====================
        # "First, a one million parameter model with one loop."
        smallest_loop1_20k = get_smallest_param_data(20, 1)
        if smallest_loop1_20k:
            dot_1m_loop1 = create_dot(smallest_loop1_20k, is_loop4=False)
            # 同时显示 20k 图例
            self.play(
                GrowFromCenter(dot_1m_loop1),
                FadeIn(dataset_legend_items[20]),
                run_time=0.8
            )
            self.wait(1.0)

        # ==================== Phase 2: 1M Model, Loop-4 ====================
        # "Then we cycled over 4 loops. Damn, no improvement."
        smallest_loop4_20k = get_smallest_param_data(20, 4)
        if smallest_loop4_20k:
            dot_1m_loop4 = create_dot(smallest_loop4_20k, is_loop4=True)
            self.play(GrowFromCenter(dot_1m_loop4), run_time=0.8)
            self.wait(1.0)

        # ==================== Phase 3: Scale Model Size, Loop-1 ====================
        # "We could try and increase the model size for a single loop"
        remaining_loop1_20k = get_remaining_data(20, 1, exclude_smallest=True)
        remaining_loop1_20k_sorted = sorted(remaining_loop1_20k, key=lambda d: d['x'])
        if remaining_loop1_20k_sorted:
            dots_loop1_20k = create_dots_for_data(remaining_loop1_20k_sorted, is_loop4=False)
            self.play(
                LaggedStart(*[GrowFromCenter(d) for d in dots_loop1_20k], lag_ratio=0.05),
                run_time=1.5
            )
            self.wait(0.5)

        # ==================== Phase 4: Scale Model Size, Loop-4 ====================
        # "And then test across four loops, but still there's no improvement."
        remaining_loop4_20k = get_remaining_data(20, 4, exclude_smallest=True)
        remaining_loop4_20k_sorted = sorted(remaining_loop4_20k, key=lambda d: d['x'])
        if remaining_loop4_20k_sorted:
            dots_loop4_20k = create_dots_for_data(remaining_loop4_20k_sorted, is_loop4=True)
            self.play(
                LaggedStart(*[GrowFromCenter(d) for d in dots_loop4_20k], lag_ratio=0.05),
                run_time=1.5
            )
            self.wait(0.5)

        # ==================== Phase 5: 50k Dataset ====================
        # "Maybe we need to train on larger datasets? 50,000 samples."
        data_50k_loop1 = sorted(get_data_by_dataset_and_loop(50, 1), key=lambda d: d['x'])
        data_50k_loop4 = sorted(get_data_by_dataset_and_loop(50, 4), key=lambda d: d['x'])

        dots_50k_loop1 = create_dots_for_data(data_50k_loop1, is_loop4=False)
        dots_50k_loop4 = create_dots_for_data(data_50k_loop4, is_loop4=True)

        # 同时显示 Loop-1 和 Loop-4，以及 50k 图例
        all_50k_anims = []
        for d1, d4 in zip(dots_50k_loop1, dots_50k_loop4):
            all_50k_anims.extend([GrowFromCenter(d1), GrowFromCenter(d4)])

        if all_50k_anims:
            self.play(
                LaggedStart(*all_50k_anims, lag_ratio=0.03),
                FadeIn(dataset_legend_items[50]),
                run_time=1.5
            )
            self.wait(0.5)

        # ==================== Phase 6: 100k, 200k, 500k Datasets ====================
        # "And this holds true across all parameter scales, and dataset scales."
        for dataset_k in [100, 200, 500]:
            data_loop1 = sorted(get_data_by_dataset_and_loop(dataset_k, 1), key=lambda d: d['x'])
            data_loop4 = sorted(get_data_by_dataset_and_loop(dataset_k, 4), key=lambda d: d['x'])

            dots_loop1 = create_dots_for_data(data_loop1, is_loop4=False)
            dots_loop4 = create_dots_for_data(data_loop4, is_loop4=True)

            all_anims = []
            for d1, d4 in zip(dots_loop1, dots_loop4):
                all_anims.extend([GrowFromCenter(d1), GrowFromCenter(d4)])
            # 处理长度不等的情况
            if len(dots_loop1) > len(dots_loop4):
                for d in dots_loop1[len(dots_loop4):]:
                    all_anims.append(GrowFromCenter(d))
            elif len(dots_loop4) > len(dots_loop1):
                for d in dots_loop4[len(dots_loop1):]:
                    all_anims.append(GrowFromCenter(d))

            if all_anims:
                self.play(
                    LaggedStart(*all_anims, lag_ratio=0.02),
                    FadeIn(dataset_legend_items[dataset_k]),
                    run_time=1.2
                )
                self.wait(0.3)

        # ==================== Phase 7: 2bit/param 参考线 + End ====================
        # 最后显示 2bit/param 参考线（标注直接在图上）
        self.play(
            Create(ref_line_2bit),
            FadeIn(ref_2bit_label),
            run_time=1
        )
        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("Knowledge Capacity Scaling Animation")
    print("=" * 60)
    print("\nCommands:")
    print("  Main:      manim -pql knowledge_scaling_animation.py KnowledgeScalingAnimation")
    print("  Narrative: manim -pql knowledge_scaling_animation.py NarrativeKnowledgeScaling")
    print("  Compare:   manim -pql knowledge_scaling_animation.py LoopComparison")
    print("  Dataset:   manim -pql knowledge_scaling_animation.py KnowledgeScalingByDataset")
    print("  HQ:        manim -pqh knowledge_scaling_animation.py NarrativeKnowledgeScaling")
    print("=" * 60)
