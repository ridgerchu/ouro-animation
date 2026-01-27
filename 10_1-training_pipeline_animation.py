"""
神经网络训练流程动画
展示完整的预训练流程，包含：
1. 顶部区域：动态阶段标题
2. 中间区域：水平增长的流程图
3. 底部区域：学习率曲线图

运行命令:
  完整动画: manim -pqh training_pipeline_animation.py TrainingPipelineAnimation
  高质量:   manim -pqh --fps 60 training_pipeline_animation.py TrainingPipelineAnimation
  4K:       manim -qk training_pipeline_animation.py TrainingPipelineAnimation
"""

from manim import *
import numpy as np

# ==================== 颜色配置 ====================
TEAL_COLOR = "#2A9D8F"      # 共享路径
GOLD_COLOR = "#F4A261"      # 2.6B 分支
BLUE_COLOR = "#4361EE"      # 1.4B 分支
GRID_COLOR = "#404040"      # 网格
TEXT_COLOR = WHITE          # 文字
ACCENT_COLOR = "#E63946"    # 高亮

# ==================== 时间线数据 ====================
# X轴: Billions of tokens
T_START = 0
T_WARMUP_END = 50           # 快速 warmup 完成
T_SPLIT = 3000              # 分支点
T_ANNEAL_START = 6000       # 退火开始
T_ANNEAL_END = 7400         # 退火结束
T_LONGCT_END = 7420         # LongCT 结束
T_MID_END = 7720            # Mid-Training 结束
T_END = 8500                # 总长

# 学习率
LR_MAX = 5e-4
LR_ANNEALED = 5e-5
LR_FINAL = 1e-5


class FlowchartBox(VGroup):
    """流程图盒子组件"""
    def __init__(self, text, color=TEAL_COLOR, width=1.6, height=0.5, font_size=14, **kwargs):
        super().__init__(**kwargs)

        # 创建圆角矩形
        self.box = RoundedRectangle(
            corner_radius=0.1,
            width=width,
            height=height,
            color=color,
            stroke_width=2,
            fill_color=color,
            fill_opacity=0.15
        )

        # 创建文本 - 使用 Tex 渲染
        # 文本应该已经正确转义（使用 r"text\\(line2)" 格式）
        self.label = Tex(text, font_size=font_size, color=TEXT_COLOR)
        self.label.move_to(self.box.get_center())

        # 如果文本太长，缩放
        if self.label.width > width - 0.15:
            self.label.scale((width - 0.15) / self.label.width)
        if self.label.height > height - 0.1:
            self.label.scale((height - 0.1) / self.label.height)

        self.add(self.box, self.label)

    def get_right_connector(self):
        return self.box.get_right()

    def get_left_connector(self):
        return self.box.get_left()


class FlowchartArrow(VGroup):
    """流程图箭头"""
    def __init__(self, start, end, color=TEAL_COLOR, **kwargs):
        super().__init__(**kwargs)

        self.arrow = Arrow(
            start, end,
            color=color,
            stroke_width=2,
            buff=0,
            max_tip_length_to_length_ratio=0.25,
            tip_length=0.15
        )
        self.add(self.arrow)


class CurvedBranchArrow(VGroup):
    """曲线分叉（无箭头）"""
    def __init__(self, start, end, color=TEAL_COLOR, direction="up", **kwargs):
        super().__init__(**kwargs)

        # 计算控制点实现平滑曲线
        # 使用更平滑的控制点计算
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        # 控制点距离根据方向调整
        if direction == "up":
            # 上分支：先向右，然后向上弯曲
            control1 = start + RIGHT * (dx * 0.4 + 0.2)
            control2 = np.array([start[0] + dx * 0.6, end[1] - dy * 0.2, 0])
        else:
            # 下分支：先向右，然后向下弯曲
            control1 = start + RIGHT * (dx * 0.4 + 0.2)
            control2 = np.array([start[0] + dx * 0.6, end[1] - dy * 0.2, 0])

        # 创建贝塞尔曲线（无箭头头部）
        self.curve = CubicBezier(start, control1, control2, end, color=color, stroke_width=2)

        self.add(self.curve)


class TrainingPipelineAnimation(Scene):
    """完整的训练流程动画"""

    def construct(self):
        self.camera.background_color = BLACK  # 纯黑色背景

        # 设置三个区域的位置
        self.header_y = 3.2
        self.flowchart_y = 0.8
        self.graph_y = -2.0

        # 流程图缩放因子
        self.box_scale = 0.85
        self.box_spacing = 2.0  # 盒子间距

        # 初始化各个组件
        self.setup_axes()
        self.setup_header()

        # 存储流程图元素
        self.flowchart_elements = VGroup()
        self.current_x = -6.0  # 流程图起始 x 位置

        # 存储学习率线
        self.lr_line_points = []
        self.lr_line = None

        # 运行动画序列
        self.run_animation_sequence()

    def setup_axes(self):
        """设置学习率图表坐标轴"""
        self.axes = Axes(
            x_range=[0, 8500, 1000],
            y_range=[0, 6e-4, 1e-4],
            x_length=10,
            y_length=2.8,
            axis_config={
                "color": GREY_B,
                "stroke_width": 1.5,
                "include_ticks": True,
                "tick_size": 0.05,
                "include_tip": False,
            },
            x_axis_config={
                "numbers_to_include": [],  # 不自动生成数字，我们将手动创建 Tex 标签
                "decimal_number_config": {
                    "num_decimal_places": 0,
                    "color": GREY,
                },
            },
            y_axis_config={
                "numbers_to_include": [],  # 不自动生成数字，我们将手动创建
                "decimal_number_config": {
                    "num_decimal_places": 4,
                    "color": GREY,
                },
            },
        )
        self.axes.shift(DOWN * 1.8)

        # 手动创建 X 轴标签（使用 Tex，格式为 1T-8T）
        x_values = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000]
        x_labels_text = ["1T", "2T", "3T", "4T", "5T", "6T", "7T", "8T"]
        self.x_axis_labels = VGroup()
        for x_val, label_text in zip(x_values, x_labels_text):
            label = Tex(label_text, font_size=36, color=GREY)
            label.scale(0.5)  # 与 y 轴使用相同的缩放（更小）
            label.next_to(self.axes.c2p(x_val, 0), DOWN, buff=0.15)
            self.x_axis_labels.add(label)

        # 手动创建 Y 轴标签（使用科学计数法）- 与 x 轴字体大小保持一致
        y_values = [0, 2e-4, 4e-4, 6e-4]
        self.y_axis_labels = VGroup()
        for y_val in y_values:
            if y_val == 0:
                label = Tex("0", font_size=36, color=GREY)
            else:
                # 转换为科学计数法格式：2e-4 -> 2×10⁻⁴
                coeff = int(y_val * 1e4)  # 2e-4 -> 2
                label = Tex(f"${coeff} \\times 10^{{-4}}$", font_size=36, color=GREY)
            label.scale(0.5)  # 与 x 轴使用相同的缩放（更小）
            label.next_to(self.axes.c2p(0, y_val), LEFT, buff=0.15)
            self.y_axis_labels.add(label)

        # X轴标签
        x_label = Tex(r"\text{Training Tokens}", font_size=18, color=GREY)
        x_label.next_to(self.axes.x_axis, DOWN, buff=0.4)

        # Y轴标签 - 放在坐标轴左侧
        y_label = Tex(r"\text{Learning Rate}", font_size=18, color=GREY)
        y_label.rotate(90 * DEGREES)
        y_label.next_to(self.axes.y_axis, LEFT, buff=0.8)  # 增加距离，确保在左侧更明显

        self.axis_labels = VGroup(x_label, y_label)  # 包含 X 和 Y 轴标签

        # 创建网格线
        self.grid_lines = VGroup()
        for x in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000]:
            line = DashedLine(
                self.axes.c2p(x, 0),
                self.axes.c2p(x, 6e-4),
                color=GRID_COLOR,
                stroke_width=0.5,
                dash_length=0.03,
            )
            self.grid_lines.add(line)

        for y in [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]:
            line = DashedLine(
                self.axes.c2p(0, y),
                self.axes.c2p(8500, y),
                color=GRID_COLOR,
                stroke_width=0.5,
                dash_length=0.03,
            )
            self.grid_lines.add(line)

    def setup_header(self):
        """设置顶部标题"""
        self.header = Tex(
            r"\text{Neural Network Training Pipeline}",
            font_size=36,
            color=TEXT_COLOR
        )
        self.header.move_to(UP * self.header_y)

        self.phase_text = None
        self.phase_text_initialized = False

    def update_header(self, new_text, color=GREY_B):
        """更新阶段标题"""
        new_phase = Tex(new_text, font_size=28, color=color)
        new_phase.next_to(self.header, DOWN, buff=0.3)

        if not self.phase_text_initialized:
            self.play(FadeIn(new_phase, shift=UP * 0.2), run_time=0.6)
            self.phase_text_initialized = True
        else:
            self.play(
                FadeTransform(self.phase_text, new_phase),
                run_time=0.6
            )
        self.phase_text = new_phase

    def add_flowchart_box(self, text, color=TEAL_COLOR, with_arrow=True, y_offset=0):
        """添加流程图盒子"""
        box = FlowchartBox(text, color=color)
        box.move_to(np.array([self.current_x, self.flowchart_y + y_offset, 0]))

        animations = [FadeIn(box, scale=0.8)]

        if with_arrow and len(self.flowchart_elements) > 0:
            # 找到前一个元素
            prev_element = self.flowchart_elements[-1]
            if isinstance(prev_element, FlowchartBox):
                arrow = FlowchartArrow(
                    prev_element.get_right_connector(),
                    box.get_left_connector(),
                    color=color
                )
                animations.insert(0, Create(arrow))
                self.flowchart_elements.add(arrow)

        self.play(*animations, run_time=0.8)
        self.flowchart_elements.add(box)
        self.current_x += 2.8

        return box

    def draw_lr_segment(self, x_start, x_end, y_start, y_end, color=TEAL_COLOR, run_time=1.5):
        """绘制学习率曲线段"""
        start_point = self.axes.c2p(x_start, y_start)
        end_point = self.axes.c2p(x_end, y_end)

        line_segment = Line(start_point, end_point, color=color, stroke_width=3)

        # 追踪点
        dot = Dot(start_point, color=color, radius=0.08)

        self.play(
            Create(line_segment),
            dot.animate.move_to(end_point),
            run_time=run_time,
            rate_func=linear
        )

        self.remove(dot)

        if self.lr_line is None:
            self.lr_line = line_segment
        else:
            new_line = VGroup(self.lr_line, line_segment)
            self.lr_line = new_line

        return line_segment

    def run_animation_sequence(self):
        """运行完整动画序列"""

        # ===== 初始化场景 =====
        # 移除初始标题显示
        # self.play(Write(self.header), run_time=1)
        self.play(
            Create(self.axes),
            FadeIn(self.axis_labels),
            FadeIn(self.x_axis_labels),
            FadeIn(self.y_axis_labels),
            run_time=1.5
        )
        self.play(
            *[Create(line) for line in self.grid_lines],
            run_time=0.8
        )

        # ===== Phase 1: Warmup =====
        self.update_header(r"\text{Phase 1: Linear Warmup}", TEAL_COLOR)

        # 添加 Warmup 盒子
        warmup_box = self.add_flowchart_box(r"\text{Warmup}", TEAL_COLOR, with_arrow=False)

        # 学习率快速上升
        self.draw_lr_segment(0, T_WARMUP_END, 0, LR_MAX, TEAL_COLOR, run_time=0.8)

        self.wait(0.5)

        # ===== Phase 2: Stable Training (Shared) =====
        self.update_header(r"\text{Phase 2: Stable Pre-training (Shared Backbone)}", TEAL_COLOR)

        # 添加 Stable Training 盒子
        stable_box = self.add_flowchart_box(r"Stable Training\\(3T)", TEAL_COLOR)

        # 学习率保持平稳
        self.draw_lr_segment(T_WARMUP_END, T_SPLIT, LR_MAX, LR_MAX, TEAL_COLOR, run_time=2)

        self.wait(0.5)

        # ===== Phase 3: The Split (Branching) =====
        self.update_header(r"\text{Phase 3: Model Upcycling \& Branching}", ACCENT_COLOR)

        # 创建分支视觉效果
        split_point = stable_box.get_right_connector()

        # 分支点标记
        split_dot = Dot(split_point, color=ACCENT_COLOR, radius=0.08)
        split_dot.set_z_index(10)

        # 在图表上标记分支点
        split_vline = DashedLine(
            self.axes.c2p(T_SPLIT, 0),
            self.axes.c2p(T_SPLIT, 6e-4),
            color=ACCENT_COLOR,
            stroke_width=1.5,
            dash_length=0.1
        )
        split_text = Tex(r"\text{Split}", font_size=12, color=ACCENT_COLOR)
        split_text.next_to(self.axes.c2p(T_SPLIT, 6e-4), UP, buff=0.1)

        # 更新位置为分支后
        self.current_x = split_point[0] + 2.0

        # 上分支盒子 (2.6B)
        top_stable_box = FlowchartBox(r"Stable Train\\(3T)", GOLD_COLOR)
        top_stable_box.move_to(np.array([self.current_x, self.flowchart_y + 0.55, 0]))

        # 下分支盒子 (1.4B)
        bottom_stable_box = FlowchartBox(r"Stable Train\\(3T)", BLUE_COLOR)
        bottom_stable_box.move_to(np.array([self.current_x, self.flowchart_y - 0.55, 0]))

        # 创建曲线分叉箭头 - 直接连接到盒子
        top_branch = CurvedBranchArrow(
            split_point,
            top_stable_box.get_left_connector(),
            color=GOLD_COLOR,
            direction="up"
        )
        bottom_branch = CurvedBranchArrow(
            split_point,
            bottom_stable_box.get_left_connector(),
            color=BLUE_COLOR,
            direction="down"
        )

        # 分支标签 - 位置往左移动，并增加垂直距离避免重叠
        top_label_pos = top_branch.curve.point_from_proportion(0.3)  # 使用 0.3，更靠左
        top_label = Tex(r"\text{Upcycle 2.6B}", font_size=12, color=GOLD_COLOR)
        top_label.move_to(top_label_pos + UP * 0.3)  # 增加上移距离到 0.3

        bottom_label_pos = bottom_branch.curve.point_from_proportion(0.3)  # 使用 0.3，更靠左
        bottom_label = Tex(r"\text{Keep 1.4B}", font_size=12, color=BLUE_COLOR)
        bottom_label.move_to(bottom_label_pos + DOWN * 0.3)  # 增加下移距离到 0.3

        # 一次性完成分叉动画
        self.play(
            GrowFromCenter(split_dot),
            Flash(split_dot, color=ACCENT_COLOR, num_lines=8, flash_radius=0.3),
            Create(split_vline),
            FadeIn(split_text),
            run_time=0.6
        )

        self.play(
            Create(top_branch),
            Create(bottom_branch),
            FadeIn(top_label, shift=UP * 0.1),
            FadeIn(bottom_label, shift=DOWN * 0.1),
            FadeIn(top_stable_box, scale=0.8),
            FadeIn(bottom_stable_box, scale=0.8),
            run_time=1
        )

        self.flowchart_elements.add(split_dot, top_branch, bottom_branch, top_label, bottom_label, top_stable_box, bottom_stable_box)

        self.wait(0.3)

        # ===== Phase 4: Stable Training (Branched) =====
        self.update_header(r"\text{Phase 4: Parallel Stable Training}", GREY_B)

        # 学习率继续平稳（双线）
        lr_line_top = self.draw_lr_segment(T_SPLIT, T_ANNEAL_START, LR_MAX, LR_MAX, GOLD_COLOR, run_time=1.5)
        lr_line_bottom = Line(
            self.axes.c2p(T_SPLIT, LR_MAX),
            self.axes.c2p(T_ANNEAL_START, LR_MAX),
            color=BLUE_COLOR,
            stroke_width=3
        )
        lr_line_bottom.shift(DOWN * 0.03)  # 稍微偏移以显示两条线
        self.add(lr_line_bottom)

        self.current_x += 2.0

        # ===== 提前滑动以容纳更多内容 =====
        shift_amount = LEFT * 2.5
        self.play(
            self.flowchart_elements.animate.shift(shift_amount),
            run_time=0.6
        )
        self.current_x += -2.5

        # ===== Phase 5: CT Annealing =====
        self.update_header(r"\text{Phase 5: Cool-down / Annealing}", GREY_B)

        # 添加退火盒子
        top_anneal_box = FlowchartBox(r"Annealing\\(1.4T)", GOLD_COLOR)
        top_anneal_box.move_to(np.array([self.current_x, self.flowchart_y + 0.55, 0]))

        bottom_anneal_box = FlowchartBox(r"Annealing\\(1.4T)", BLUE_COLOR)
        bottom_anneal_box.move_to(np.array([self.current_x, self.flowchart_y - 0.55, 0]))

        # 连接箭头 - 从 Stable Train 框后面开始（滑动后位置已更新）
        top_anneal_arrow = Arrow(
            top_stable_box.get_right_connector(),
            top_anneal_box.get_left_connector(),
            color=GOLD_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )
        bottom_anneal_arrow = Arrow(
            bottom_stable_box.get_right_connector(),
            bottom_anneal_box.get_left_connector(),
            color=BLUE_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )

        self.play(
            Create(top_anneal_arrow),
            Create(bottom_anneal_arrow),
            FadeIn(top_anneal_box, scale=0.8),
            FadeIn(bottom_anneal_box, scale=0.8),
            run_time=0.6
        )

        self.flowchart_elements.add(top_anneal_arrow, bottom_anneal_arrow, top_anneal_box, bottom_anneal_box)

        # 学习率下降
        lr_anneal_top = Line(
            self.axes.c2p(T_ANNEAL_START, LR_MAX),
            self.axes.c2p(T_ANNEAL_END, LR_ANNEALED),
            color=GOLD_COLOR,
            stroke_width=3
        )
        lr_anneal_bottom = Line(
            self.axes.c2p(T_ANNEAL_START, LR_MAX),
            self.axes.c2p(T_ANNEAL_END, LR_ANNEALED),
            color=BLUE_COLOR,
            stroke_width=3
        )
        lr_anneal_bottom.shift(DOWN * 0.03)

        self.play(
            Create(lr_anneal_top),
            Create(lr_anneal_bottom),
            run_time=1
        )

        self.current_x += 2.0

        # ===== Phase 6: Long Context (LongCT) =====
        self.update_header(r"\text{Phase 6: Long Context Extension (LongCT)}", GREY_B)

        # 添加 LongCT 盒子
        top_longct_box = FlowchartBox(r"LongCT\\(20B)", GOLD_COLOR, width=1.4)
        top_longct_box.move_to(np.array([self.current_x, self.flowchart_y + 0.55, 0]))

        bottom_longct_box = FlowchartBox(r"LongCT\\(20B)", BLUE_COLOR, width=1.4)
        bottom_longct_box.move_to(np.array([self.current_x, self.flowchart_y - 0.55, 0]))

        # 连接箭头
        top_longct_arrow = Arrow(
            top_anneal_box.get_right_connector(),
            top_longct_box.get_left_connector(),
            color=GOLD_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )
        bottom_longct_arrow = Arrow(
            bottom_anneal_box.get_right_connector(),
            bottom_longct_box.get_left_connector(),
            color=BLUE_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )

        self.play(
            Create(top_longct_arrow),
            Create(bottom_longct_arrow),
            FadeIn(top_longct_box, scale=0.8),
            FadeIn(bottom_longct_box, scale=0.8),
            run_time=0.6
        )

        self.flowchart_elements.add(top_longct_arrow, bottom_longct_arrow, top_longct_box, bottom_longct_box)

        # 学习率保持平稳（短段）
        lr_longct_top = Line(
            self.axes.c2p(T_ANNEAL_END, LR_ANNEALED),
            self.axes.c2p(T_LONGCT_END, LR_ANNEALED),
            color=GOLD_COLOR,
            stroke_width=3
        )
        lr_longct_bottom = Line(
            self.axes.c2p(T_ANNEAL_END, LR_ANNEALED),
            self.axes.c2p(T_LONGCT_END, LR_ANNEALED),
            color=BLUE_COLOR,
            stroke_width=3
        )
        lr_longct_bottom.shift(DOWN * 0.03)

        self.play(
            Create(lr_longct_top),
            Create(lr_longct_bottom),
            run_time=0.5
        )

        self.current_x += 1.8

        # ===== Phase 7: Mid-Training =====
        self.update_header(r"\text{Phase 7: Mid-Training Adjustment}", GREY_B)

        # 添加 Mid-Training 盒子
        top_mid_box = FlowchartBox(r"Mid-Train\\(300B)", GOLD_COLOR, width=1.4)
        top_mid_box.move_to(np.array([self.current_x, self.flowchart_y + 0.55, 0]))

        bottom_mid_box = FlowchartBox(r"Mid-Train\\(300B)", BLUE_COLOR, width=1.4)
        bottom_mid_box.move_to(np.array([self.current_x, self.flowchart_y - 0.55, 0]))

        # 连接箭头
        top_mid_arrow = Arrow(
            top_longct_box.get_right_connector(),
            top_mid_box.get_left_connector(),
            color=GOLD_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )
        bottom_mid_arrow = Arrow(
            bottom_longct_box.get_right_connector(),
            bottom_mid_box.get_left_connector(),
            color=BLUE_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )

        self.play(
            Create(top_mid_arrow),
            Create(bottom_mid_arrow),
            FadeIn(top_mid_box, scale=0.8),
            FadeIn(bottom_mid_box, scale=0.8),
            run_time=0.6
        )

        self.flowchart_elements.add(top_mid_arrow, bottom_mid_arrow, top_mid_box, bottom_mid_box)

        # 学习率继续下降
        lr_mid_top = Line(
            self.axes.c2p(T_LONGCT_END, LR_ANNEALED),
            self.axes.c2p(T_MID_END, LR_FINAL),
            color=GOLD_COLOR,
            stroke_width=3
        )
        lr_mid_bottom = Line(
            self.axes.c2p(T_LONGCT_END, LR_ANNEALED),
            self.axes.c2p(T_MID_END, LR_FINAL),
            color=BLUE_COLOR,
            stroke_width=3
        )
        lr_mid_bottom.shift(DOWN * 0.03)

        self.play(
            Create(lr_mid_top),
            Create(lr_mid_bottom),
            run_time=0.8
        )

        # ===== 第二次滑动 =====
        shift_amount2 = LEFT * 2.5
        self.play(
            self.flowchart_elements.animate.shift(shift_amount2),
            run_time=0.6
        )
        self.current_x += -2.5

        # ===== Phase 8: Post-Training (SFT & Thinking) =====
        self.update_header(r"\text{Phase 8: Reasoning SFT \& Thinking Models}", ACCENT_COLOR)

        # 学习率曲线停在 SFT 之前，不再延长
        # 学习率已经在 Mid-Training 结束时达到 LR_FINAL，不需要继续绘制

        # Mid-Train 框直接变换成 Ouro Base 框
        top_ouro_box = FlowchartBox(r"\text{Ouro-2.6B}", GOLD_COLOR, width=1.5)
        top_ouro_box.move_to(top_mid_box.get_center())

        bottom_ouro_box = FlowchartBox(r"\text{Ouro-1.4B}", BLUE_COLOR, width=1.5)
        bottom_ouro_box.move_to(bottom_mid_box.get_center())

        # 变换动画
        self.play(
            Transform(top_mid_box, top_ouro_box),
            Transform(bottom_mid_box, bottom_ouro_box),
            run_time=0.8
        )

        # 更新引用
        top_ouro_box = top_mid_box
        bottom_ouro_box = bottom_mid_box

        self.current_x = top_ouro_box.get_center()[0] + 1.8

        # SFT 盒子
        top_sft_box = FlowchartBox(r"Reasoning\\SFT", GOLD_COLOR, width=1.4)
        top_sft_box.move_to(np.array([self.current_x, self.flowchart_y + 0.55, 0]))

        bottom_sft_box = FlowchartBox(r"Reasoning\\SFT", BLUE_COLOR, width=1.4)
        bottom_sft_box.move_to(np.array([self.current_x, self.flowchart_y - 0.55, 0]))

        top_sft_arrow = Arrow(
            top_ouro_box.get_right_connector(),
            top_sft_box.get_left_connector(),
            color=GOLD_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )
        bottom_sft_arrow = Arrow(
            bottom_ouro_box.get_right_connector(),
            bottom_sft_box.get_left_connector(),
            color=BLUE_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )

        self.play(
            Create(top_sft_arrow),
            Create(bottom_sft_arrow),
            FadeIn(top_sft_box, scale=0.8),
            FadeIn(bottom_sft_box, scale=0.8),
            run_time=0.5
        )

        self.current_x += 1.8

        # Thinking 模型盒子 - 最终产品
        top_thinking_box = FlowchartBox(r"\text{Ouro-2.6B Thinking}", GOLD_COLOR, width=1.6)
        top_thinking_box.move_to(np.array([self.current_x, self.flowchart_y + 0.55, 0]))
        top_thinking_box.box.set_stroke(width=3)
        top_thinking_box.box.set_fill(opacity=0.25)

        bottom_thinking_box = FlowchartBox(r"\text{Ouro-1.4B Thinking}", BLUE_COLOR, width=1.6)
        bottom_thinking_box.move_to(np.array([self.current_x, self.flowchart_y - 0.55, 0]))
        bottom_thinking_box.box.set_stroke(width=3)
        bottom_thinking_box.box.set_fill(opacity=0.25)

        top_thinking_arrow = Arrow(
            top_sft_box.get_right_connector(),
            top_thinking_box.get_left_connector(),
            color=GOLD_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )
        bottom_thinking_arrow = Arrow(
            bottom_sft_box.get_right_connector(),
            bottom_thinking_box.get_left_connector(),
            color=BLUE_COLOR,
            stroke_width=2,
            buff=0,
            tip_length=0.12
        )

        self.play(
            Create(top_thinking_arrow),
            Create(bottom_thinking_arrow),
            run_time=0.3
        )

        self.play(
            FadeIn(top_thinking_box, scale=0.9),
            FadeIn(bottom_thinking_box, scale=0.9),
            Flash(top_thinking_box, color=GOLD_COLOR, num_lines=8, flash_radius=0.5),
            Flash(bottom_thinking_box, color=BLUE_COLOR, num_lines=8, flash_radius=0.5),
            run_time=0.8
        )

        # 完成标记
        complete_text = Tex(r"\text{Training Complete!}", font_size=32, color=ACCENT_COLOR)
        complete_text.next_to(self.axes, DOWN, buff=0.8)

        self.play(
            FadeIn(complete_text, scale=1.2),
            run_time=0.8
        )

        # 最终等待
        self.wait(3)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )


if __name__ == "__main__":
    print("=" * 60)
    print("神经网络训练流程动画 - Manim")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pqh training_pipeline_animation.py TrainingPipelineAnimation")
    print("  高质量:   manim -pqh --fps 60 training_pipeline_animation.py TrainingPipelineAnimation")
    print("=" * 60)

