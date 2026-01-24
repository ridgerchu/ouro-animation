"""
PonderNet Early Exit Mechanism 可视化动画
运行命令:
  完整动画: manim -pql pondernet_early_exit.py PonderNetEarlyExit
  单独场景: manim -pql pondernet_early_exit.py Part1Setup
           manim -pql pondernet_early_exit.py Part2SigmoidProblem
           manim -pql pondernet_early_exit.py Part3WhyNotSoftmax
           manim -pql pondernet_early_exit.py Part4ConditionalToUnconditional
           manim -pql pondernet_early_exit.py Part5FinalStep
           manim -pql pondernet_early_exit.py Part6CDFThresholding
           manim -pql pondernet_early_exit.py Part7Recap
  高质量渲染: manim -pqh pondernet_early_exit.py PonderNetEarlyExit
"""

from manim import *
import numpy as np

# ===== 颜色配置 =====
EXIT_COLOR = "#FF6B6B"       # 退出/停止 - 橙红色
SURVIVE_COLOR = "#4ECDC4"    # 继续/生存 - 青色
HIGHLIGHT_COLOR = "#F39C12"  # 高亮 - 橙色
LOOP_COLOR = "#3498DB"       # Loop方块 - 蓝色
FORMULA_COLOR = "#9B59B6"    # 公式 - 紫色
FLOW_COLOR = "#E8D44D"       # 概率流 - 金黄色
THRESHOLD_COLOR = "#FFE66D"  # 阈值线 - 亮黄色

# ===== 字体配置 - 解决字间距问题 =====
# 使用 Tex 代替 Text 来避免字间距问题
def create_text(content, font_size=24, color=WHITE, **kwargs):
    """创建文本，使用 Tex 避免字间距问题"""
    # 转义特殊字符
    content = content.replace("→", r"$\rightarrow$")
    content = content.replace("≠", r"$\neq$")
    content = content.replace("≥", r"$\geq$")
    content = content.replace("✓", r"$\checkmark$")
    content = content.replace("✗", r"$\times$")
    content = content.replace("σ", r"$\sigma$")
    content = content.replace("λ", r"$\lambda$")
    # 处理换行
    if "\n" in content:
        lines = content.split("\n")
        tex_content = r" \\ ".join(lines)
        tex = Tex(tex_content, font_size=font_size, color=color, **kwargs)
    else:
        tex = Tex(content, font_size=font_size, color=color, **kwargs)
    return tex


class LoopBlock(VGroup):
    """可复用的 Loop 方块组件"""
    def __init__(self, label_text, scale_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.rect = RoundedRectangle(
            height=1.2 * scale_factor,
            width=1.5 * scale_factor,
            corner_radius=0.15 * scale_factor,
            color=LOOP_COLOR,
            fill_opacity=0.3,
            stroke_width=3
        )
        self.label = Tex(label_text, font_size=int(28 * scale_factor), color=WHITE)
        self.label.move_to(self.rect.get_center())
        self.add(self.rect, self.label)

    def highlight(self, color=HIGHLIGHT_COLOR):
        return self.rect.animate.set_stroke(color=color, width=5)

    def unhighlight(self):
        return self.rect.animate.set_stroke(color=LOOP_COLOR, width=3)


class ExitGate(VGroup):
    """Exit Gate 组件 - Dense → σ"""
    def __init__(self, scale_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.rect = RoundedRectangle(
            height=0.8 * scale_factor,
            width=1.8 * scale_factor,
            corner_radius=0.1 * scale_factor,
            color=EXIT_COLOR,
            fill_opacity=0.2,
            stroke_width=2
        )
        self.label = MathTex(r"\text{Dense} \rightarrow \sigma", font_size=int(22 * scale_factor))
        self.label.move_to(self.rect.get_center())
        self.add(self.rect, self.label)


class FlowPipe(VGroup):
    """概率流管道 - 可视化概率质量流动"""
    def __init__(self, width=3.0, height=0.4, fill_ratio=1.0, color=FLOW_COLOR, **kwargs):
        super().__init__(**kwargs)
        # 外框
        self.outline = Rectangle(
            width=width, height=height,
            color=WHITE, stroke_width=2, fill_opacity=0
        )
        # 填充部分
        self.fill = Rectangle(
            width=width * fill_ratio, height=height * 0.9,
            color=color, fill_opacity=0.7, stroke_width=0
        )
        self.fill.align_to(self.outline, LEFT)
        self.fill.shift(RIGHT * 0.02)
        self.add(self.outline, self.fill)

    def update_fill(self, new_ratio, color=None):
        """更新填充比例"""
        new_width = self.outline.width * new_ratio
        target = Rectangle(
            width=new_width, height=self.outline.height * 0.9,
            color=color if color else self.fill.get_color(),
            fill_opacity=0.7, stroke_width=0
        )
        target.align_to(self.outline, LEFT)
        target.shift(RIGHT * 0.02)
        return Transform(self.fill, target)


# ===== Part 1: The Setup =====
class Part1Setup(Scene):
    """Part 1: The Setup (15-20 sec)"""
    def construct(self):
        # 旁白标题
        narration = Tex(
            "How does the early exit mechanism work?",
            font_size=36, color=WHITE
        )
        narration.to_edge(UP, buff=0.5)

        self.play(Write(narration), run_time=1.5)
        self.wait(0.5)

        # ===== 简单流程: 垂直布局，所有元素居中对齐 =====
        # 固定 x 坐标，确保箭头在一条线上
        center_x = LEFT * 2.5

        # 创建所有组件 - 统一宽度使其对齐
        input_box = RoundedRectangle(
            height=0.6, width=1.6, corner_radius=0.1,
            color=SURVIVE_COLOR, fill_opacity=0.3, stroke_width=2
        )
        input_label = Tex("Input", font_size=22, color=WHITE)
        input_label.move_to(input_box.get_center())
        input_group = VGroup(input_box, input_label)

        loop_box = RoundedRectangle(
            height=0.8, width=1.6, corner_radius=0.12,
            color=LOOP_COLOR, fill_opacity=0.3, stroke_width=3
        )
        loop_label = Tex("Loop Block", font_size=22, color=WHITE)
        loop_label.move_to(loop_box.get_center())
        loop_group = VGroup(loop_box, loop_label)

        # 输出嵌入 - 统一宽度
        embed_box = RoundedRectangle(
            height=0.6, width=1.6, corner_radius=0.1,
            color=FLOW_COLOR, fill_opacity=0.6, stroke_width=2
        )
        # 发光效果
        embed_glow = embed_box.copy()
        embed_glow.set_stroke(color=FLOW_COLOR, width=6, opacity=0.3)
        embed_label = Tex("Embedding", font_size=20, color=WHITE)
        embed_label.move_to(embed_box.get_center())
        embed_group = VGroup(embed_glow, embed_box, embed_label)

        # Exit Gate - 统一宽度
        gate_box = RoundedRectangle(
            height=0.6, width=1.6, corner_radius=0.1,
            color=EXIT_COLOR, fill_opacity=0.2, stroke_width=2
        )
        gate_label = MathTex(r"\text{Dense} \rightarrow \sigma", font_size=20)
        gate_label.move_to(gate_box.get_center())
        gate_group = VGroup(gate_box, gate_label)

        # 垂直排列，间距适中
        all_boxes = [input_group, loop_group, embed_group, gate_group]
        y_positions = [UP * 1.2, UP * 0.1, DOWN * 1.0, DOWN * 2.1]

        for box, y_pos in zip(all_boxes, y_positions):
            box.move_to(center_x + y_pos)

        # 垂直箭头 - 确保在同一条线上
        arrow1 = Arrow(
            input_group.get_bottom(), loop_group.get_top(),
            buff=0.08, color=GREY_B, stroke_width=2
        )
        arrow2 = Arrow(
            loop_group.get_bottom(), embed_group.get_top(),
            buff=0.08, color=GREY_B, stroke_width=2
        )
        arrow3 = Arrow(
            embed_group.get_bottom(), gate_group.get_top(),
            buff=0.08, color=GREY_B, stroke_width=2
        )

        # 动画: 依次显示
        self.play(FadeIn(input_group, shift=DOWN * 0.3), run_time=0.6)
        self.play(GrowArrow(arrow1), run_time=0.4)
        self.play(FadeIn(loop_group, shift=DOWN * 0.3), run_time=0.6)
        self.play(GrowArrow(arrow2), run_time=0.4)
        self.play(FadeIn(embed_group, scale=1.1), run_time=0.6)

        self.wait(0.5)

        # 更新旁白
        narration2 = Tex(
            "The output embedding is passed to an exit gate.",
            font_size=28, color=GREY_B
        )
        narration2.next_to(narration, DOWN, buff=0.3)
        self.play(Write(narration2), run_time=1.2)

        self.play(GrowArrow(arrow3), run_time=0.4)
        self.play(FadeIn(gate_group, shift=DOWN * 0.3), run_time=0.6)

        # 右侧显示 Exit Gate 输出
        exit_output = MathTex(r"0.3", font_size=40, color=EXIT_COLOR)
        exit_output.next_to(gate_group, RIGHT, buff=1.0)

        exit_label = Tex(r"$P(\text{exit} \mid \text{this step})$", font_size=20, color=GREY_B)
        exit_label.next_to(exit_output, DOWN, buff=0.15)

        # 连接线
        connect_arrow = Arrow(gate_group.get_right(), exit_output.get_left(), buff=0.1, color=EXIT_COLOR, stroke_width=2)

        self.play(GrowArrow(connect_arrow), run_time=0.4)
        self.play(FadeIn(exit_output, scale=1.5), run_time=0.6)
        self.play(Write(exit_label), run_time=0.5)

        # 解释文字
        explain_text = Tex(
            r"A dense layer with sigmoid activation $\rightarrow$ instantaneous probability of exiting",
            font_size=20, color=GREY_B
        )
        explain_text.to_edge(DOWN, buff=0.5)
        self.play(Write(explain_text), run_time=1.5)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== Part 2: The Problem with Raw Sigmoid =====
class Part2SigmoidProblem(Scene):
    """Part 2: The Problem with Raw Sigmoid (25-30 sec)"""
    def construct(self):
        # 旁白
        narration = Tex(
            r"The output of sigmoid is bounded between 0 and 1. Is that good enough?",
            font_size=28, color=WHITE
        )
        narration.to_edge(UP, buff=0.5)
        self.play(Write(narration), run_time=1.5)

        # ===== Sigmoid 曲线 =====
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[0, 1.2, 0.2],
            x_length=6,
            y_length=3.5,
            axis_config={"color": GREY_B, "include_tip": True},
        )
        axes.shift(UP * 0.3 + LEFT * 2.5)

        # Sigmoid 函数
        sigmoid_curve = axes.plot(
            lambda x: 1 / (1 + np.exp(-x)),
            color=HIGHLIGHT_COLOR, stroke_width=3
        )

        # 标注 [0, 1] 范围
        y_0_line = DashedLine(
            axes.c2p(-5, 0), axes.c2p(5, 0),
            color=SURVIVE_COLOR, stroke_width=2, dash_length=0.1
        )
        y_1_line = DashedLine(
            axes.c2p(-5, 1), axes.c2p(5, 1),
            color=SURVIVE_COLOR, stroke_width=2, dash_length=0.1
        )

        range_label = MathTex(r"\sigma(x) \in [0, 1]", font_size=28, color=SURVIVE_COLOR)
        range_label.next_to(axes, RIGHT, buff=0.5)

        self.play(Create(axes), run_time=0.8)
        self.play(Create(sigmoid_curve), run_time=1)
        self.play(Create(y_0_line), Create(y_1_line), Write(range_label), run_time=0.8)

        # 绿色对勾
        checkmark = MathTex(r"\checkmark", font_size=40, color=SURVIVE_COLOR)
        checkmark.next_to(range_label, RIGHT, buff=0.3)
        self.play(FadeIn(checkmark, scale=1.5), run_time=0.5)

        self.wait(1)

        # 问题引入
        self.play(
            FadeOut(axes), FadeOut(sigmoid_curve), FadeOut(y_0_line), FadeOut(y_1_line),
            FadeOut(range_label), FadeOut(checkmark),
            run_time=0.8
        )

        # 更新旁白
        narration2 = Tex(
            "If we loop 4 times, each has some exit probability...",
            font_size=26, color=WHITE
        )
        narration2.move_to(narration.get_center())
        self.play(Transform(narration, narration2), run_time=0.8)

        # ===== 四个 Loop 方块 =====
        loops = VGroup(*[LoopBlock(f"Loop {i+1}", scale_factor=0.8) for i in range(4)])
        loops.arrange(RIGHT, buff=0.6)
        loops.shift(UP * 0.8)

        # 每个 loop 下方的 λ 值
        lambda_values = [0.3, 0.5, 0.4, 0.6]
        lambda_labels = VGroup()
        for i, (loop, lval) in enumerate(zip(loops, lambda_values)):
            lbl = MathTex(rf"\lambda_{i+1} = {lval}", font_size=24, color=EXIT_COLOR)
            lbl.next_to(loop, DOWN, buff=0.25)
            lambda_labels.add(lbl)

        # 箭头连接
        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops[i].get_right(), loops[i+1].get_left(),
                buff=0.05, color=GREY_B, stroke_width=2
            )
            arrows.add(arrow)

        self.play(
            LaggedStart(*[FadeIn(l, shift=DOWN * 0.2) for l in loops], lag_ratio=0.15),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[Write(l) for l in lambda_labels], lag_ratio=0.15),
            run_time=1
        )

        self.wait(0.5)

        # ===== 求和显示问题 =====
        sum_line1 = MathTex(
            r"\text{Sum} = 0.3 + 0.5 + 0.4 + 0.6",
            font_size=28
        )
        sum_line1.shift(DOWN * 1)

        sum_line2 = MathTex(
            r"= 1.8",
            font_size=32, color=EXIT_COLOR
        )
        sum_line2.next_to(sum_line1, DOWN, buff=0.2)

        self.play(Write(sum_line1), run_time=1)
        self.play(Write(sum_line2), run_time=0.6)

        # 红色 ≠ 1 和大红叉
        not_equal = MathTex(r"\neq 1", font_size=36, color=EXIT_COLOR)
        not_equal.next_to(sum_line2, RIGHT, buff=0.3)

        big_x = MathTex(r"\times", font_size=60, color=EXIT_COLOR)
        big_x.next_to(not_equal, RIGHT, buff=0.5)

        self.play(Write(not_equal), FadeIn(big_x, scale=1.5), run_time=0.8)

        # 问题说明
        problem_text = Tex(
            "The sum of exit probabilities doesn't equal 1!",
            font_size=24, color=EXIT_COLOR
        )
        problem_text.to_edge(DOWN, buff=0.6)
        self.play(Write(problem_text), run_time=1)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== Part 3: Why Not Softmax? =====
class Part3WhyNotSoftmax(Scene):
    """Part 3: Why Not Softmax? (15-20 sec)"""
    def construct(self):
        # 标题
        title = Tex("Why not just use Softmax?", font_size=40, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=1)

        # Softmax 公式
        softmax_formula = MathTex(
            r"\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_{j=1}^{N} e^{x_j}}",
            font_size=36
        )
        softmax_formula.shift(UP * 1.2)
        self.play(Write(softmax_formula), run_time=1.2)

        # 四个 Loop 方块
        loops = VGroup(*[LoopBlock(f"L{i+1}", scale_factor=0.7) for i in range(4)])
        loops.arrange(RIGHT, buff=0.5)
        loops.shift(DOWN * 0.3)

        # Loop 1 高亮, 其余灰色/模糊
        loops[0].rect.set_stroke(color=HIGHLIGHT_COLOR, width=4)
        for i in range(1, 4):
            loops[i].set_opacity(0.3)

        # 箭头和问号
        arrows = VGroup()
        question_marks = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops[i].get_right(), loops[i+1].get_left(),
                buff=0.05, color=GREY_B, stroke_width=2
            )
            arrows.add(arrow)

            qmark = MathTex("?", font_size=28, color=EXIT_COLOR)
            qmark.next_to(loops[i+1], UP, buff=0.15)
            question_marks.add(qmark)

        self.play(
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.1),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1),
            run_time=1
        )
        self.play(
            LaggedStart(*[FadeIn(q, scale=1.5) for q in question_marks], lag_ratio=0.15),
            run_time=0.8
        )

        # "现在" 指示器
        now_label = Tex("NOW", font_size=20, color=HIGHLIGHT_COLOR)
        now_label.next_to(loops[0], UP, buff=0.15)
        now_arrow = Arrow(
            now_label.get_bottom() + DOWN * 0.1,
            loops[0].get_top() + UP * 0.1,
            color=HIGHLIGHT_COLOR, stroke_width=2, buff=0
        )

        self.play(Write(now_label), GrowArrow(now_arrow), run_time=0.5)

        # 时间线可视化: Loop 1 高亮, 2-4 模糊
        timeline_text = Tex(
            "Can't see the future!",
            font_size=28, color=EXIT_COLOR
        )
        timeline_text.next_to(loops, DOWN, buff=0.8)

        # 迷雾效果覆盖后面的 loops
        fog = Rectangle(
            width=5, height=2,
            fill_color=BLACK, fill_opacity=0.6,
            stroke_width=0
        )
        fog.move_to(VGroup(loops[1], loops[2], loops[3]).get_center())

        self.play(FadeIn(fog, shift=RIGHT * 0.5), run_time=0.8)
        self.play(Write(timeline_text), run_time=0.8)

        # Softmax 划掉
        strike_line = Line(
            softmax_formula.get_left() + LEFT * 0.2,
            softmax_formula.get_right() + RIGHT * 0.2,
            color=EXIT_COLOR, stroke_width=4
        )
        self.play(Create(strike_line), run_time=0.5)

        # 解释文字
        explain_text = Tex(
            "Softmax requires knowing ALL loop outputs first",
            font_size=24, color=GREY_B
        )
        explain_text.to_edge(DOWN, buff=0.5)
        self.play(Write(explain_text), run_time=1)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== Part 4: The Solution — Conditional → Unconditional =====
class Part4ConditionalToUnconditional(Scene):
    """Part 4: The Solution — Conditional → Unconditional (60-75 sec)"""
    def construct(self):
        # 清屏, 新开始
        title = Tex(r"The Solution: Conditional $\rightarrow$ Unconditional", font_size=34, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1)

        # Lambda 值
        lambdas = [0.3, 0.5, 0.4]  # 最后一步是强制退出

        # ===== 创建主要可视化区域 =====
        # 左侧: 流程图
        # 右侧: 概率条形图

        # 流程图区域
        flow_area = VGroup()

        # 初始概率流 = 1.0
        flow_label_init = Tex("Probability mass = 1.0", font_size=22, color=FLOW_COLOR)
        flow_label_init.shift(UP * 1.5 + LEFT * 4)

        # Flow pipe
        flow_pipe = Rectangle(
            width=0.8, height=0.3,
            color=FLOW_COLOR, fill_opacity=0.8, stroke_width=2
        )
        flow_pipe.next_to(flow_label_init, DOWN, buff=0.3)

        self.play(Write(flow_label_init), FadeIn(flow_pipe), run_time=0.8)

        # ===== Loop 1 =====
        loop1 = LoopBlock("Loop 1", scale_factor=0.85)
        loop1.shift(LEFT * 1.5 + UP * 1)

        exit_gate1 = ExitGate(scale_factor=0.8)
        exit_gate1.next_to(loop1, DOWN, buff=0.5)

        self.play(FadeIn(loop1), FadeIn(exit_gate1), run_time=0.6)

        # 解说
        explain1 = Tex(r"Say we run the first loop. $\sigma$ gives us 0.3", font_size=22, color=GREY_B)
        explain1.to_edge(DOWN, buff=1.5)
        self.play(Write(explain1), run_time=1)

        # Lambda 输出
        lambda1_text = MathTex(r"\lambda_1 = 0.3", font_size=28, color=EXIT_COLOR)
        lambda1_text.next_to(exit_gate1, RIGHT, buff=0.3)
        self.play(Write(lambda1_text), run_time=0.6)

        # 流分裂: 30% 退出, 70% 继续
        # 退出箭头 (向下)
        exit_arrow1 = Arrow(
            exit_gate1.get_bottom(),
            exit_gate1.get_bottom() + DOWN * 1,
            color=EXIT_COLOR, stroke_width=3
        )
        exit_label1 = MathTex(r"p_1 = 0.3", font_size=24, color=EXIT_COLOR)
        exit_label1.next_to(exit_arrow1, LEFT, buff=0.15)

        # 继续箭头 (向右)
        survive_arrow1 = Arrow(
            loop1.get_right(),
            loop1.get_right() + RIGHT * 1.5,
            color=SURVIVE_COLOR, stroke_width=3
        )
        survive_label1 = MathTex(r"\text{Survive: } 0.7", font_size=20, color=SURVIVE_COLOR)
        survive_label1.next_to(survive_arrow1, UP, buff=0.1)

        self.play(
            GrowArrow(exit_arrow1), Write(exit_label1),
            GrowArrow(survive_arrow1), Write(survive_label1),
            run_time=1
        )

        # 右侧条形图开始
        bar_chart_title = Tex("Exit Probabilities", font_size=20, color=GREY_B)
        bar_chart_title.shift(RIGHT * 4.5 + UP * 2)
        self.play(Write(bar_chart_title), run_time=0.4)

        # 条形图基线
        bar_baseline = Line(
            RIGHT * 3.2 + UP * 0.5,
            RIGHT * 5.8 + UP * 0.5,
            color=GREY_B, stroke_width=2
        )
        self.play(Create(bar_baseline), run_time=0.3)

        # p1 条
        bar1 = Rectangle(
            width=0.4, height=0.3 * 5,  # 0.3 * scale
            color=EXIT_COLOR, fill_opacity=0.8, stroke_width=1
        )
        bar1.next_to(bar_baseline, UP, buff=0).shift(LEFT * 0.9)
        bar1_label = MathTex(r"p_1", font_size=18)
        bar1_label.next_to(bar1, DOWN, buff=0.1)
        bar1_val = Tex("0.30", font_size=16, color=WHITE)
        bar1_val.next_to(bar1, UP, buff=0.05)

        self.play(
            GrowFromEdge(bar1, DOWN),
            Write(bar1_label), Write(bar1_val),
            run_time=0.8
        )

        self.wait(1)

        # 清理并继续 Loop 2
        self.play(FadeOut(explain1), run_time=0.4)

        # ===== Loop 2 =====
        loop2 = LoopBlock("Loop 2", scale_factor=0.85)
        loop2.shift(RIGHT * 1.5 + UP * 1)

        exit_gate2 = ExitGate(scale_factor=0.8)
        exit_gate2.next_to(loop2, DOWN, buff=0.5)

        self.play(FadeIn(loop2), FadeIn(exit_gate2), run_time=0.6)

        # 流标签更新
        flow_label2 = MathTex(r"0.7 \text{ enters}", font_size=20, color=SURVIVE_COLOR)
        flow_label2.next_to(loop2, UP, buff=0.2)
        self.play(Write(flow_label2), run_time=0.5)

        # Lambda 输出
        lambda2_text = MathTex(r"\lambda_2 = 0.5", font_size=28, color=EXIT_COLOR)
        lambda2_text.next_to(exit_gate2, RIGHT, buff=0.3)
        self.play(Write(lambda2_text), run_time=0.6)

        # 解说: 条件概率
        explain2 = Tex(
            "This 0.5 is CONDITIONAL on surviving Loop 1!",
            font_size=22, color=HIGHLIGHT_COLOR
        )
        explain2.to_edge(DOWN, buff=1.8)
        self.play(Write(explain2), run_time=1)

        cond_formula = MathTex(
            r"P(\text{exit at } L_2 \mid \text{survived } L_1) = 0.5",
            font_size=22
        )
        cond_formula.next_to(explain2, DOWN, buff=0.2)
        self.play(Write(cond_formula), run_time=0.8)

        self.wait(1)

        # 无条件概率计算
        self.play(FadeOut(explain2), FadeOut(cond_formula), run_time=0.4)

        uncond_explain = Tex(
            r"Unconditional = P(survive L1) $\times$ P(exit $|$ survive)",
            font_size=22, color=GREY_B
        )
        uncond_explain.to_edge(DOWN, buff=1.8)
        self.play(Write(uncond_explain), run_time=0.8)

        uncond_formula = MathTex(
            r"p_2 = (1 - \lambda_1) \times \lambda_2 = 0.7 \times 0.5 = 0.35",
            font_size=26, color=HIGHLIGHT_COLOR
        )
        uncond_formula.next_to(uncond_explain, DOWN, buff=0.2)
        self.play(Write(uncond_formula), run_time=1)

        # 退出箭头 Loop 2
        exit_arrow2 = Arrow(
            exit_gate2.get_bottom(),
            exit_gate2.get_bottom() + DOWN * 1,
            color=EXIT_COLOR, stroke_width=3
        )
        exit_label2 = MathTex(r"p_2 = 0.35", font_size=24, color=EXIT_COLOR)
        exit_label2.next_to(exit_arrow2, LEFT, buff=0.15)

        self.play(GrowArrow(exit_arrow2), Write(exit_label2), run_time=0.8)

        # 更新条形图
        bar2 = Rectangle(
            width=0.4, height=0.35 * 5,
            color=HIGHLIGHT_COLOR, fill_opacity=0.8, stroke_width=1
        )
        bar2.next_to(bar_baseline, UP, buff=0).shift(LEFT * 0.3)
        bar2_label = MathTex(r"p_2", font_size=18)
        bar2_label.next_to(bar2, DOWN, buff=0.1)
        bar2_val = Tex("0.35", font_size=16, color=WHITE)
        bar2_val.next_to(bar2, UP, buff=0.05)

        self.play(
            GrowFromEdge(bar2, DOWN),
            Write(bar2_label), Write(bar2_val),
            run_time=0.8
        )

        self.wait(1)

        # ===== Loop 3 =====
        self.play(FadeOut(uncond_explain), FadeOut(uncond_formula), run_time=0.4)

        # 说明继续
        explain3 = Tex("Accumulate the unconditional probabilities...", font_size=22, color=GREY_B)
        explain3.to_edge(DOWN, buff=1.8)
        self.play(Write(explain3), run_time=0.8)

        # 存活流: 0.7 * 0.5 = 0.35 进入 Loop 3
        survive_label2 = MathTex(r"0.35 \text{ survives}", font_size=18, color=SURVIVE_COLOR)
        survive_label2.shift(RIGHT * 3.5 + UP * 1.5)

        # 公式框
        general_formula = MathTex(
            r"p_n = \lambda_n \prod_{j=1}^{n-1}(1-\lambda_j)",
            font_size=32, color=FORMULA_COLOR
        )
        general_formula.shift(LEFT * 4 + DOWN * 1)

        formula_box = SurroundingRectangle(general_formula, color=FORMULA_COLOR, buff=0.2)

        self.play(Write(general_formula), Create(formula_box), run_time=1.5)

        # Loop 3 计算 (简化显示)
        p3_formula = MathTex(
            r"p_3 = 0.35 \times 0.4 = 0.14",
            font_size=24, color=SURVIVE_COLOR
        )
        p3_formula.next_to(general_formula, DOWN, buff=0.5)
        self.play(Write(p3_formula), run_time=0.8)

        # 更新条形图
        bar3 = Rectangle(
            width=0.4, height=0.14 * 5,
            color=SURVIVE_COLOR, fill_opacity=0.8, stroke_width=1
        )
        bar3.next_to(bar_baseline, UP, buff=0).shift(RIGHT * 0.3)
        bar3_label = MathTex(r"p_3", font_size=18)
        bar3_label.next_to(bar3, DOWN, buff=0.1)
        bar3_val = Tex("0.14", font_size=16, color=WHITE)
        bar3_val.next_to(bar3, UP, buff=0.05)

        self.play(
            GrowFromEdge(bar3, DOWN),
            Write(bar3_label), Write(bar3_val),
            run_time=0.8
        )

        # 验证: 总和 < 1
        sum_so_far = MathTex(
            r"\sum = 0.30 + 0.35 + 0.14 = 0.79 < 1 \checkmark",
            font_size=24, color=SURVIVE_COLOR
        )
        sum_so_far.next_to(p3_formula, DOWN, buff=0.4)
        self.play(Write(sum_so_far), run_time=1)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== Part 5: Handling the Final Step =====
class Part5FinalStep(Scene):
    """Part 5: Handling the Final Step (20-25 sec)"""
    def construct(self):
        # 标题
        title = Tex("Handling the Final Step", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # 旁白
        narration = Tex(
            "This doesn't guarantee a probability distribution...",
            font_size=26, color=GREY_B
        )
        narration.next_to(title, DOWN, buff=0.3)
        self.play(Write(narration), run_time=1)

        # 条形图显示缺口
        bar_baseline = Line(LEFT * 2, RIGHT * 2, color=GREY_B, stroke_width=2)
        bar_baseline.shift(DOWN * 0.5)

        # 三个已有的条
        probs = [0.30, 0.35, 0.14]
        colors = [EXIT_COLOR, HIGHLIGHT_COLOR, SURVIVE_COLOR]
        bars = VGroup()
        labels = VGroup()

        scale = 4  # height scale
        bar_width = 0.5
        for i, (p, c) in enumerate(zip(probs, colors)):
            bar = Rectangle(
                width=bar_width, height=p * scale,
                color=c, fill_opacity=0.8, stroke_width=1
            )
            bar.next_to(bar_baseline, UP, buff=0)
            bar.shift(LEFT * 1.5 + RIGHT * (i * 0.8))
            bars.add(bar)

            lbl = MathTex(f"p_{i+1}", font_size=20)
            lbl.next_to(bar, DOWN, buff=0.1)
            labels.add(lbl)

        self.play(
            Create(bar_baseline),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.15),
            LaggedStart(*[Write(l) for l in labels], lag_ratio=0.15),
            run_time=1.2
        )

        # 总和显示
        total_text = MathTex(r"\text{Total} = 0.79", font_size=28)
        total_text.shift(RIGHT * 3 + UP * 0.5)
        self.play(Write(total_text), run_time=0.6)

        # 缺口标注
        gap_text = MathTex(r"\text{Missing: } 0.21", font_size=26, color=EXIT_COLOR)
        gap_text.next_to(total_text, DOWN, buff=0.3)

        question = MathTex("?", font_size=50, color=EXIT_COLOR)
        question.next_to(gap_text, RIGHT, buff=0.3)

        self.play(Write(gap_text), FadeIn(question, scale=1.5), run_time=0.8)

        self.wait(1)

        # 解决方案
        solution_text = Tex(
            "At max loops, FORCE an exit!",
            font_size=28, color=SURVIVE_COLOR
        )
        solution_text.shift(DOWN * 2)
        self.play(Write(solution_text), run_time=0.8)

        # Loop 4 - 强制退出
        loop4_box = RoundedRectangle(
            width=1.2, height=0.8, corner_radius=0.1,
            color=EXIT_COLOR, fill_opacity=0.5, stroke_width=3
        )
        loop4_box.shift(RIGHT * 1.3 + UP * 0.7)

        loop4_label = Tex("L4", font_size=24, color=WHITE)
        loop4_label.move_to(loop4_box.get_center())

        force_label = Tex("FORCE EXIT", font_size=16, color=EXIT_COLOR)
        force_label.next_to(loop4_box, UP, buff=0.1)

        self.play(
            FadeIn(loop4_box), Write(loop4_label), Write(force_label),
            run_time=0.8
        )

        # 剩余质量倾倒到 p4
        bar4 = Rectangle(
            width=bar_width, height=0.21 * scale,
            color=LOOP_COLOR, fill_opacity=0.8, stroke_width=1
        )
        bar4.next_to(bar_baseline, UP, buff=0)
        bar4.shift(LEFT * 1.5 + RIGHT * (3 * 0.8))

        p4_label = MathTex(r"p_4", font_size=20)
        p4_label.next_to(bar4, DOWN, buff=0.1)

        # 动画: 将剩余质量"倒入"
        pour_arrow = Arrow(
            gap_text.get_bottom() + DOWN * 0.1,
            bar4.get_top() + UP * 0.1,
            color=EXIT_COLOR, stroke_width=3
        )
        self.play(GrowArrow(pour_arrow), run_time=0.5)
        self.play(
            GrowFromEdge(bar4, DOWN),
            Write(p4_label),
            FadeOut(pour_arrow),
            run_time=0.8
        )

        # 公式
        final_formula = MathTex(
            r"p_N = 1 - \sum_{n=1}^{N-1} p_n = 0.21",
            font_size=28, color=LOOP_COLOR
        )
        final_formula.next_to(solution_text, DOWN, buff=0.3)
        self.play(Write(final_formula), run_time=1)

        # 总和验证
        self.play(FadeOut(total_text), FadeOut(gap_text), FadeOut(question))

        new_total = MathTex(
            r"p_1 + p_2 + p_3 + p_4 = 1.0 \checkmark",
            font_size=28, color=SURVIVE_COLOR
        )
        new_total.shift(RIGHT * 3 + UP * 0.5)
        self.play(Write(new_total), run_time=0.8)

        # 绿色对勾
        valid_text = Tex("Valid probability distribution!", font_size=24, color=SURVIVE_COLOR)
        valid_text.next_to(new_total, DOWN, buff=0.3)
        checkmark = MathTex(r"\checkmark", font_size=40, color=SURVIVE_COLOR)
        checkmark.next_to(valid_text, RIGHT, buff=0.2)

        self.play(Write(valid_text), FadeIn(checkmark, scale=1.5), run_time=0.8)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== Part 6: Inference via CDF Thresholding =====
class Part6CDFThresholding(Scene):
    """Part 6: Inference via CDF Thresholding (30-40 sec)"""
    def construct(self):
        # 标题
        title = Tex("Inference via CDF Thresholding", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # 旁白
        narration = Tex(
            "The unconditional probability is converted to a CDF and thresholded.",
            font_size=24, color=GREY_B
        )
        narration.next_to(title, DOWN, buff=0.2)
        self.play(Write(narration), run_time=1)

        # 数据
        probs = [0.30, 0.35, 0.14, 0.21]
        cdf_values = [0.30, 0.65, 0.79, 1.00]
        labels = ["L1", "L2", "L3", "L4"]

        # ===== 左侧: 概率条形图 → 右侧: CDF =====
        # 条形图
        axes_bar = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 0.5, 0.1],
            x_length=4,
            y_length=2.5,
            axis_config={"color": GREY_B, "include_tip": False},
        )
        axes_bar.shift(LEFT * 3.5 + DOWN * 0.5)

        bar_title = Tex("PDF", font_size=20, color=GREY_B)
        bar_title.next_to(axes_bar, UP, buff=0.2)

        colors = [EXIT_COLOR, HIGHLIGHT_COLOR, SURVIVE_COLOR, LOOP_COLOR]
        bars = VGroup()
        for i, (p, c) in enumerate(zip(probs, colors)):
            bar = Rectangle(
                width=0.35, height=p * 5,
                color=c, fill_opacity=0.8, stroke_width=1
            )
            bar.move_to(axes_bar.c2p(i + 1, p / 2))
            bars.add(bar)

        x_labels_bar = VGroup()
        for i, l in enumerate(labels):
            txt = Tex(l, font_size=16)
            txt.move_to(axes_bar.c2p(i + 1, 0) + DOWN * 0.3)
            x_labels_bar.add(txt)

        self.play(Create(axes_bar), Write(bar_title), run_time=0.8)
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in x_labels_bar], lag_ratio=0.1),
            run_time=1
        )

        # 转换箭头
        transform_arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=WHITE, stroke_width=3)
        transform_arrow.shift(DOWN * 0.5)
        transform_label = MathTex(r"\rightarrow \text{CDF}", font_size=24)
        transform_label.next_to(transform_arrow, UP, buff=0.1)

        self.play(GrowArrow(transform_arrow), Write(transform_label), run_time=0.6)

        # CDF 图
        axes_cdf = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1.2, 0.2],
            x_length=4.5,
            y_length=3,
            axis_config={"color": GREY_B, "include_tip": True},
        )
        axes_cdf.shift(RIGHT * 3 + DOWN * 0.3)

        cdf_title = Tex("CDF", font_size=20, color=GREY_B)
        cdf_title.next_to(axes_cdf, UP, buff=0.2)

        # CDF 阶梯线
        cdf_points = [(0, 0)]
        for i, cdf_val in enumerate(cdf_values):
            prev_val = cdf_values[i-1] if i > 0 else 0
            cdf_points.append((i + 1, prev_val))
            cdf_points.append((i + 1, cdf_val))

        cdf_line = VMobject(color=LOOP_COLOR, stroke_width=3)
        cdf_line.set_points_as_corners([axes_cdf.c2p(x, y) for x, y in cdf_points])

        cdf_dots = VGroup()
        cdf_labels = VGroup()
        for i, cdf_val in enumerate(cdf_values):
            dot = Dot(axes_cdf.c2p(i + 1, cdf_val), color=HIGHLIGHT_COLOR, radius=0.06)
            lbl = MathTex(f"{cdf_val:.2f}", font_size=16, color=HIGHLIGHT_COLOR)
            lbl.next_to(dot, UR, buff=0.05)
            cdf_dots.add(dot)
            cdf_labels.add(lbl)

        x_labels_cdf = VGroup()
        for i, l in enumerate(labels):
            txt = Tex(l, font_size=16)
            txt.move_to(axes_cdf.c2p(i + 1, 0) + DOWN * 0.3)
            x_labels_cdf.add(txt)

        self.play(Create(axes_cdf), Write(cdf_title), run_time=0.8)
        self.play(Create(cdf_line), run_time=1.2)
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.5) for d in cdf_dots], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in cdf_labels], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in x_labels_cdf], lag_ratio=0.1),
            run_time=1
        )

        self.wait(1)

        # ===== 阈值线 =====
        threshold = 0.7
        threshold_line = DashedLine(
            axes_cdf.c2p(0, threshold),
            axes_cdf.c2p(5, threshold),
            color=THRESHOLD_COLOR, stroke_width=3, dash_length=0.1
        )
        threshold_label = MathTex(r"q = 0.7", font_size=22, color=THRESHOLD_COLOR)
        threshold_label.next_to(threshold_line, RIGHT, buff=0.1)

        self.play(Create(threshold_line), Write(threshold_label), run_time=0.8)

        # 旁白更新
        narration2 = Tex(
            r"If CDF $\geq$ threshold $\rightarrow$ EXIT",
            font_size=24, color=SURVIVE_COLOR
        )
        narration2.to_edge(DOWN, buff=1.5)
        self.play(Write(narration2), run_time=0.8)

        # ===== 动画检查每个 Loop =====
        check_results = VGroup()

        # L1: CDF = 0.30 < 0.7 → Continue
        check1 = MathTex(r"L_1: 0.30 < 0.7 \rightarrow \text{Continue}", font_size=20)
        check1[-8:].set_color(SURVIVE_COLOR)
        check1.to_edge(DOWN, buff=0.8)

        indicator1 = Circle(radius=0.15, color=SURVIVE_COLOR, stroke_width=3)
        indicator1.move_to(axes_cdf.c2p(1, 0.3))

        self.play(Create(indicator1), run_time=0.4)
        self.play(Write(check1), run_time=0.6)
        self.play(FadeOut(indicator1), run_time=0.3)
        check_results.add(check1)

        # L2: CDF = 0.65 < 0.7 → Continue
        check2 = MathTex(r"L_2: 0.65 < 0.7 \rightarrow \text{Continue}", font_size=20)
        check2[-8:].set_color(SURVIVE_COLOR)
        check2.next_to(check1, DOWN, buff=0.15)

        indicator2 = Circle(radius=0.15, color=SURVIVE_COLOR, stroke_width=3)
        indicator2.move_to(axes_cdf.c2p(2, 0.65))

        self.play(Create(indicator2), run_time=0.4)
        self.play(Write(check2), run_time=0.6)
        self.play(FadeOut(indicator2), run_time=0.3)
        check_results.add(check2)

        # L3: CDF = 0.79 > 0.7 → EXIT!
        check3 = MathTex(r"L_3: 0.79 \geq 0.7 \rightarrow \textbf{EXIT!}", font_size=20)
        check3[-5:].set_color(EXIT_COLOR)
        check3.next_to(check2, DOWN, buff=0.15)

        indicator3 = Circle(radius=0.2, color=EXIT_COLOR, stroke_width=4)
        indicator3.move_to(axes_cdf.c2p(3, 0.79))

        self.play(Create(indicator3), run_time=0.4)
        self.play(Write(check3), run_time=0.6)

        # 闪烁效果
        self.play(
            indicator3.animate.scale(1.5).set_opacity(0),
            run_time=0.6
        )

        # 高亮 L3 输出
        exit_text = Tex(r"$\rightarrow$ Use L3's output!", font_size=22, color=EXIT_COLOR)
        exit_text.next_to(check3, RIGHT, buff=0.3)
        self.play(Write(exit_text), run_time=0.6)

        self.wait(1.5)

        # ===== 备选场景: 高阈值 =====
        self.play(
            FadeOut(check_results), FadeOut(exit_text), FadeOut(narration2),
            run_time=0.6
        )

        alt_narration = Tex(
            "With higher threshold (0.95), forced exit at final step:",
            font_size=22, color=GREY_B
        )
        alt_narration.to_edge(DOWN, buff=1.2)
        self.play(Write(alt_narration), run_time=0.8)

        # 移动阈值线
        new_threshold_line = DashedLine(
            axes_cdf.c2p(0, 0.95),
            axes_cdf.c2p(5, 0.95),
            color=THRESHOLD_COLOR, stroke_width=3, dash_length=0.1
        )
        new_threshold_label = MathTex(r"q = 0.95", font_size=22, color=THRESHOLD_COLOR)
        new_threshold_label.next_to(new_threshold_line, RIGHT, buff=0.1)

        self.play(
            Transform(threshold_line, new_threshold_line),
            Transform(threshold_label, new_threshold_label),
            run_time=0.8
        )

        # 结果
        forced_exit = Tex(r"L1-L3 all continue $\rightarrow$ Forced exit at L4", font_size=22, color=LOOP_COLOR)
        forced_exit.next_to(alt_narration, DOWN, buff=0.3)
        self.play(Write(forced_exit), run_time=0.8)

        # 指向下一个 token
        next_token = Tex(r"$\rightarrow$ Proceed to next token", font_size=20, color=GREY_B)
        next_token.next_to(forced_exit, DOWN, buff=0.2)
        self.play(Write(next_token), run_time=0.6)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== Part 7: Quick Recap =====
class Part7Recap(Scene):
    """Part 7: Quick Recap (10-15 sec)"""
    def construct(self):
        # 标题
        title = Tex("Quick Recap", font_size=42, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        # 左侧: 流程图简图
        left_title = Tex("Flow Diagram", font_size=24, color=GREY_B)
        left_title.shift(LEFT * 3.5 + UP * 1.5)

        # 简化的流程图
        loops_mini = VGroup()
        for i in range(4):
            loop = RoundedRectangle(
                width=0.8, height=0.6, corner_radius=0.08,
                color=LOOP_COLOR, fill_opacity=0.3, stroke_width=2
            )
            loop.shift(LEFT * (4.5 - i * 1.2) + UP * 0.5)
            lbl = Tex(f"L{i+1}", font_size=14, color=WHITE)
            lbl.move_to(loop.get_center())
            loops_mini.add(VGroup(loop, lbl))

        # 退出箭头
        exit_arrows_mini = VGroup()
        for i, loop in enumerate(loops_mini):
            arrow = Arrow(
                loop.get_bottom(),
                loop.get_bottom() + DOWN * 0.6,
                color=EXIT_COLOR, stroke_width=2, buff=0.05
            )
            exit_arrows_mini.add(arrow)

        # 连接箭头
        connect_arrows = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops_mini[i].get_right() + RIGHT * 0.05,
                loops_mini[i+1].get_left() + LEFT * 0.05,
                color=SURVIVE_COLOR, stroke_width=2, buff=0
            )
            connect_arrows.add(arrow)

        self.play(Write(left_title), run_time=0.4)
        self.play(
            LaggedStart(*[FadeIn(l) for l in loops_mini], lag_ratio=0.1),
            LaggedStart(*[GrowArrow(a) for a in connect_arrows], lag_ratio=0.1),
            LaggedStart(*[GrowArrow(a) for a in exit_arrows_mini], lag_ratio=0.1),
            run_time=1.2
        )

        # 右侧: 概率分布 + CDF 示意
        right_title = Tex("Probability Distribution + CDF", font_size=20, color=GREY_B)
        right_title.shift(RIGHT * 2.5 + UP * 1.5)

        # 简化的条形图
        bars_mini = VGroup()
        probs = [0.30, 0.35, 0.14, 0.21]
        colors = [EXIT_COLOR, HIGHLIGHT_COLOR, SURVIVE_COLOR, LOOP_COLOR]

        for i, (p, c) in enumerate(zip(probs, colors)):
            bar = Rectangle(
                width=0.3, height=p * 3,
                color=c, fill_opacity=0.8, stroke_width=1
            )
            bar.shift(RIGHT * (1 + i * 0.5) + DOWN * (0.2 - p * 1.5))
            bars_mini.add(bar)

        # 阈值线
        threshold_mini = DashedLine(
            RIGHT * 0.7 + UP * 0.2,
            RIGHT * 3.5 + UP * 0.2,
            color=THRESHOLD_COLOR, stroke_width=2, dash_length=0.08
        )

        self.play(Write(right_title), run_time=0.4)
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars_mini], lag_ratio=0.1),
            run_time=0.8
        )
        self.play(Create(threshold_mini), run_time=0.4)

        # ===== 关键公式 =====
        formulas = VGroup()

        formula1 = MathTex(
            r"p_n = \lambda_n \prod_{j=1}^{n-1}(1-\lambda_j)",
            font_size=28
        )
        formula1.shift(DOWN * 1.5 + LEFT * 2)

        formula2 = MathTex(
            r"p_N = 1 - \sum_{n=1}^{N-1} p_n",
            font_size=28
        )
        formula2.next_to(formula1, DOWN, buff=0.3)

        formula3 = Tex(
            r"Exit when CDF $\geq$ threshold",
            font_size=22, color=SURVIVE_COLOR
        )
        formula3.next_to(formula2, DOWN, buff=0.3)

        formulas.add(formula1, formula2, formula3)

        # 公式框
        formula_box = SurroundingRectangle(formulas, color=FORMULA_COLOR, buff=0.2)

        self.play(
            LaggedStart(*[Write(f) for f in formulas], lag_ratio=0.3),
            run_time=1.5
        )
        self.play(Create(formula_box), run_time=0.5)

        self.wait(2)

        # 最终结语
        final_text = Tex(
            "Sequential gating with automatic normalization!",
            font_size=26, color=SURVIVE_COLOR
        )
        final_text.to_edge(DOWN, buff=0.5)

        checkmark = MathTex(r"\checkmark", font_size=36, color=SURVIVE_COLOR)
        checkmark.next_to(final_text, RIGHT, buff=0.3)

        self.play(Write(final_text), FadeIn(checkmark, scale=1.5), run_time=1)

        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== 完整动画: PonderNetEarlyExit =====
class PonderNetEarlyExit(Scene):
    """完整的 PonderNet Early Exit Mechanism 动画"""
    def construct(self):
        # Part 1: The Setup
        self.part1_setup()

        # Part 2: The Problem with Raw Sigmoid
        self.part2_sigmoid_problem()

        # Part 3: Why Not Softmax?
        self.part3_why_not_softmax()

        # Part 4: The Solution
        self.part4_solution()

        # Part 5: Handling the Final Step
        self.part5_final_step()

        # Part 6: CDF Thresholding
        self.part6_cdf_threshold()

        # Part 7: Recap
        self.part7_recap()

    def part1_setup(self):
        """Part 1: The Setup (15-20 sec)"""
        # 旁白标题
        narration = Tex(
            "How does the early exit mechanism work?",
            font_size=34, color=WHITE
        )
        narration.to_edge(UP, buff=0.5)

        self.play(Write(narration), run_time=1.2)
        self.wait(0.3)

        # ===== 垂直布局，所有元素居中对齐 =====
        center_x = LEFT * 2.5

        # 创建所有组件 - 统一宽度
        input_box = RoundedRectangle(
            height=0.55, width=1.5, corner_radius=0.1,
            color=SURVIVE_COLOR, fill_opacity=0.3, stroke_width=2
        )
        input_label = Tex("Input", font_size=20, color=WHITE)
        input_label.move_to(input_box.get_center())
        input_group = VGroup(input_box, input_label)

        loop_box = RoundedRectangle(
            height=0.7, width=1.5, corner_radius=0.12,
            color=LOOP_COLOR, fill_opacity=0.3, stroke_width=3
        )
        loop_label = Tex("Loop Block", font_size=20, color=WHITE)
        loop_label.move_to(loop_box.get_center())
        loop_group = VGroup(loop_box, loop_label)

        embed_box = RoundedRectangle(
            height=0.55, width=1.5, corner_radius=0.1,
            color=FLOW_COLOR, fill_opacity=0.6, stroke_width=2
        )
        embed_label = Tex("Embedding", font_size=18, color=WHITE)
        embed_label.move_to(embed_box.get_center())
        embed_group = VGroup(embed_box, embed_label)

        gate_box = RoundedRectangle(
            height=0.55, width=1.5, corner_radius=0.1,
            color=EXIT_COLOR, fill_opacity=0.2, stroke_width=2
        )
        gate_label = MathTex(r"\text{Dense} \rightarrow \sigma", font_size=18)
        gate_label.move_to(gate_box.get_center())
        gate_group = VGroup(gate_box, gate_label)

        # 垂直排列
        y_positions = [UP * 1.0, UP * 0.05, DOWN * 0.9, DOWN * 1.85]
        for box, y_pos in zip([input_group, loop_group, embed_group, gate_group], y_positions):
            box.move_to(center_x + y_pos)

        # 垂直箭头
        arrow1 = Arrow(input_group.get_bottom(), loop_group.get_top(), buff=0.08, color=GREY_B, stroke_width=2)
        arrow2 = Arrow(loop_group.get_bottom(), embed_group.get_top(), buff=0.08, color=GREY_B, stroke_width=2)
        arrow3 = Arrow(embed_group.get_bottom(), gate_group.get_top(), buff=0.08, color=GREY_B, stroke_width=2)

        # 动画
        self.play(FadeIn(input_group, shift=DOWN * 0.2), run_time=0.4)
        self.play(GrowArrow(arrow1), run_time=0.3)
        self.play(FadeIn(loop_group, shift=DOWN * 0.2), run_time=0.4)
        self.play(GrowArrow(arrow2), run_time=0.3)
        self.play(FadeIn(embed_group, scale=1.1), run_time=0.4)
        self.play(GrowArrow(arrow3), run_time=0.3)
        self.play(FadeIn(gate_group, shift=DOWN * 0.2), run_time=0.4)

        # Exit Gate 输出
        exit_output = MathTex(r"0.3", font_size=36, color=EXIT_COLOR)
        exit_output.next_to(gate_group, RIGHT, buff=0.8)
        exit_label = Tex(r"$P(\text{exit} \mid \text{step})$", font_size=16, color=GREY_B)
        exit_label.next_to(exit_output, DOWN, buff=0.08)

        connect_arrow = Arrow(gate_group.get_right(), exit_output.get_left(), buff=0.1, color=EXIT_COLOR, stroke_width=2)

        self.play(GrowArrow(connect_arrow), run_time=0.3)
        self.play(FadeIn(exit_output, scale=1.3), run_time=0.4)
        self.play(Write(exit_label), run_time=0.4)

        # 说明
        explain_text = Tex(
            r"Dense layer + sigmoid $\rightarrow$ instantaneous exit probability",
            font_size=18, color=GREY_B
        )
        explain_text.to_edge(DOWN, buff=0.5)
        self.play(Write(explain_text), run_time=1)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part2_sigmoid_problem(self):
        """Part 2: The Problem with Raw Sigmoid (25-30 sec)"""
        narration = Tex(
            "Sigmoid outputs are in [0, 1]. Is that enough?",
            font_size=28, color=WHITE
        )
        narration.to_edge(UP, buff=0.5)
        self.play(Write(narration), run_time=1)

        # Sigmoid 曲线
        axes = Axes(
            x_range=[-4, 4, 1], y_range=[0, 1.1, 0.2],
            x_length=5, y_length=3,
            axis_config={"color": GREY_B},
        )
        axes.shift(LEFT * 3 + UP * 0.3)

        sigmoid_curve = axes.plot(lambda x: 1 / (1 + np.exp(-x)), color=HIGHLIGHT_COLOR, stroke_width=3)

        range_label = MathTex(r"\sigma(x) \in [0, 1]", font_size=26, color=SURVIVE_COLOR)
        range_label.next_to(axes, RIGHT, buff=0.4)
        checkmark = MathTex(r"\checkmark", font_size=32, color=SURVIVE_COLOR)
        checkmark.next_to(range_label, RIGHT, buff=0.2)

        self.play(Create(axes), run_time=0.6)
        self.play(Create(sigmoid_curve), run_time=0.8)
        self.play(Write(range_label), FadeIn(checkmark, scale=1.3), run_time=0.6)

        self.wait(0.8)

        self.play(
            FadeOut(axes), FadeOut(sigmoid_curve), FadeOut(range_label), FadeOut(checkmark),
            run_time=0.6
        )

        # 四个 Loop
        narration2 = Tex("But if we loop 4 times...", font_size=26, color=WHITE)
        narration2.move_to(narration.get_center())
        self.play(Transform(narration, narration2), run_time=0.6)

        loops = VGroup(*[LoopBlock(f"L{i+1}", scale_factor=0.75) for i in range(4)])
        loops.arrange(RIGHT, buff=0.5)
        loops.shift(UP * 0.7)

        lambda_values = [0.3, 0.5, 0.4, 0.6]
        lambda_labels = VGroup()
        for i, (loop, lval) in enumerate(zip(loops, lambda_values)):
            lbl = MathTex(rf"\lambda_{i+1}={lval}", font_size=22, color=EXIT_COLOR)
            lbl.next_to(loop, DOWN, buff=0.2)
            lambda_labels.add(lbl)

        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(loops[i].get_right(), loops[i+1].get_left(), buff=0.03, color=GREY_B, stroke_width=2)
            arrows.add(arrow)

        self.play(
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.1),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1),
            run_time=1
        )
        self.play(LaggedStart(*[Write(l) for l in lambda_labels], lag_ratio=0.1), run_time=0.8)

        # 求和
        sum_line = MathTex(
            r"\sum = 0.3 + 0.5 + 0.4 + 0.6 = 1.8 \neq 1",
            font_size=28, color=EXIT_COLOR
        )
        sum_line.shift(DOWN * 1)

        big_x = MathTex(r"\times", font_size=50, color=EXIT_COLOR)
        big_x.next_to(sum_line, RIGHT, buff=0.4)

        self.play(Write(sum_line), FadeIn(big_x, scale=1.5), run_time=1)

        problem_text = Tex(r"Sum $\neq$ 1 $\rightarrow$ Not a valid probability distribution!", font_size=22, color=EXIT_COLOR)
        problem_text.to_edge(DOWN, buff=0.5)
        self.play(Write(problem_text), run_time=0.8)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part3_why_not_softmax(self):
        """Part 3: Why Not Softmax? (15-20 sec)"""
        title = Tex("Why not just use Softmax?", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)

        softmax_formula = MathTex(
            r"\text{softmax}(x_i) = \frac{e^{x_i}}{\sum_j e^{x_j}}",
            font_size=32
        )
        softmax_formula.shift(UP * 1)
        self.play(Write(softmax_formula), run_time=1)

        # Loop 示意图
        loops = VGroup(*[LoopBlock(f"L{i+1}", scale_factor=0.65) for i in range(4)])
        loops.arrange(RIGHT, buff=0.4)
        loops.shift(DOWN * 0.3)

        loops[0].rect.set_stroke(color=HIGHLIGHT_COLOR, width=4)
        for i in range(1, 4):
            loops[i].set_opacity(0.25)

        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(loops[i].get_right(), loops[i+1].get_left(), buff=0.03, color=GREY_B, stroke_width=2)
            arrows.add(arrow)

        self.play(
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.08),
            LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.08),
            run_time=0.8
        )

        now_label = Tex("NOW", font_size=18, color=HIGHLIGHT_COLOR)
        now_label.next_to(loops[0], UP, buff=0.12)
        self.play(Write(now_label), run_time=0.4)

        # 迷雾
        fog = Rectangle(width=4.5, height=1.8, fill_color=BLACK, fill_opacity=0.65, stroke_width=0)
        fog.move_to(VGroup(loops[1], loops[2], loops[3]).get_center())

        cant_see = Tex("Can't see the future!", font_size=26, color=EXIT_COLOR)
        cant_see.next_to(loops, DOWN, buff=0.6)

        self.play(FadeIn(fog), Write(cant_see), run_time=0.8)

        # 划掉 softmax
        strike = Line(
            softmax_formula.get_left() + LEFT * 0.1,
            softmax_formula.get_right() + RIGHT * 0.1,
            color=EXIT_COLOR, stroke_width=4
        )
        self.play(Create(strike), run_time=0.5)

        explain = Tex(r"Softmax needs ALL outputs $\rightarrow$ can't use it sequentially", font_size=20, color=GREY_B)
        explain.to_edge(DOWN, buff=0.5)
        self.play(Write(explain), run_time=0.8)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part4_solution(self):
        """Part 4: The Solution (60-75 sec)"""
        title = Tex(r"Solution: Conditional $\rightarrow$ Unconditional Probability", font_size=30, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        lambdas = [0.3, 0.5, 0.4]

        # 初始概率质量
        flow_text = Tex("Initial probability mass = 1.0", font_size=20, color=FLOW_COLOR)
        flow_text.shift(UP * 1.5 + LEFT * 3.5)
        self.play(Write(flow_text), run_time=0.5)

        # ===== Loop 1 =====
        loop1 = LoopBlock("Loop 1", scale_factor=0.8)
        loop1.shift(LEFT * 3 + UP * 0.2)

        # 预先创建 Loop 2（用于计算箭头位置，稍后再显示）
        loop2 = LoopBlock("Loop 2", scale_factor=0.8)
        loop2.shift(RIGHT * 0.2 + UP * 0.2)

        self.play(FadeIn(loop1), run_time=0.4)

        lambda1 = MathTex(r"\lambda_1 = 0.3", font_size=24, color=EXIT_COLOR)
        lambda1.next_to(loop1, DOWN, buff=0.3)
        self.play(Write(lambda1), run_time=0.5)

        # 分流
        exit_arrow1 = Arrow(loop1.get_bottom() + DOWN * 0.2, loop1.get_bottom() + DOWN * 1.2, color=EXIT_COLOR, stroke_width=2)
        exit_lbl1 = MathTex(r"p_1 = 0.3", font_size=20, color=EXIT_COLOR)
        exit_lbl1.next_to(exit_arrow1, LEFT, buff=0.1)

        # 修复: 使用 loop2.get_left() 作为箭头终点，确保箭头正确连接两个 Loop
        surv_arrow1 = Arrow(loop1.get_right(), loop2.get_left(), buff=0.1, color=SURVIVE_COLOR, stroke_width=2, max_tip_length_to_length_ratio=0.1)
        surv_lbl1 = Tex("0.7 survives", font_size=16, color=SURVIVE_COLOR)
        surv_lbl1.next_to(surv_arrow1, UP, buff=0.05)

        self.play(
            GrowArrow(exit_arrow1), Write(exit_lbl1),
            GrowArrow(surv_arrow1), Write(surv_lbl1),
            run_time=0.8
        )

        # 条形图 - 位置往下调整，避免与求和公式重叠
        bar_base = Line(RIGHT * 3, RIGHT * 5.5, color=GREY_B, stroke_width=2)
        bar_base.shift(DOWN * 1.5)  # 往下移动更多
        bar_title = Tex("Exit Probabilities", font_size=16, color=GREY_B)
        bar_title.next_to(bar_base, UP, buff=1.6)

        self.play(Create(bar_base), Write(bar_title), run_time=0.4)

        bar1 = Rectangle(width=0.35, height=0.3 * 4, color=EXIT_COLOR, fill_opacity=0.8, stroke_width=1)
        bar1.next_to(bar_base, UP, buff=0).shift(LEFT * 0.6)
        bar1_lbl = MathTex(r"p_1", font_size=16)
        bar1_lbl.next_to(bar1, DOWN, buff=0.08)

        self.play(GrowFromEdge(bar1, DOWN), Write(bar1_lbl), run_time=0.5)

        self.wait(0.8)

        # ===== Loop 2 =====
        # loop2 已在前面创建，这里只显示它
        self.play(FadeIn(loop2), run_time=0.4)

        lambda2 = MathTex(r"\lambda_2 = 0.5", font_size=24, color=EXIT_COLOR)
        lambda2.next_to(loop2, DOWN, buff=0.3)
        self.play(Write(lambda2), run_time=0.5)

        # 条件概率说明
        cond_text = Tex("This 0.5 is CONDITIONAL!", font_size=20, color=HIGHLIGHT_COLOR)
        cond_text.to_edge(DOWN, buff=1.5)
        self.play(Write(cond_text), run_time=0.6)

        # 无条件计算
        uncond_formula = MathTex(
            r"p_2 = (1 - \lambda_1) \times \lambda_2 = 0.7 \times 0.5 = 0.35",
            font_size=22, color=HIGHLIGHT_COLOR
        )
        uncond_formula.next_to(cond_text, DOWN, buff=0.2)
        self.play(Write(uncond_formula), run_time=0.8)

        # 退出箭头
        exit_arrow2 = Arrow(loop2.get_bottom() + DOWN * 0.2, loop2.get_bottom() + DOWN * 1.2, color=EXIT_COLOR, stroke_width=2)
        exit_lbl2 = MathTex(r"p_2 = 0.35", font_size=20, color=EXIT_COLOR)
        exit_lbl2.next_to(exit_arrow2, LEFT, buff=0.1)

        self.play(GrowArrow(exit_arrow2), Write(exit_lbl2), run_time=0.6)

        # 更新条形图
        bar2 = Rectangle(width=0.35, height=0.35 * 4, color=HIGHLIGHT_COLOR, fill_opacity=0.8, stroke_width=1)
        bar2.next_to(bar_base, UP, buff=0)
        bar2_lbl = MathTex(r"p_2", font_size=16)
        bar2_lbl.next_to(bar2, DOWN, buff=0.08)

        self.play(GrowFromEdge(bar2, DOWN), Write(bar2_lbl), run_time=0.5)

        self.wait(0.8)

        # ===== 通用公式 =====
        self.play(FadeOut(cond_text), FadeOut(uncond_formula), run_time=0.4)

        general_formula = MathTex(
            r"p_n = \lambda_n \prod_{j=1}^{n-1}(1-\lambda_j)",
            font_size=30, color=FORMULA_COLOR
        )
        general_formula.to_edge(DOWN, buff=1)
        formula_box = SurroundingRectangle(general_formula, color=FORMULA_COLOR, buff=0.15)

        self.play(Write(general_formula), Create(formula_box), run_time=1)

        # p3 计算
        p3_text = MathTex(r"p_3 = 0.35 \times 0.4 = 0.14", font_size=22, color=SURVIVE_COLOR)
        p3_text.next_to(general_formula, UP, buff=0.5)
        self.play(Write(p3_text), run_time=0.6)

        bar3 = Rectangle(width=0.35, height=0.14 * 4, color=SURVIVE_COLOR, fill_opacity=0.8, stroke_width=1)
        bar3.next_to(bar_base, UP, buff=0).shift(RIGHT * 0.6)
        bar3_lbl = MathTex(r"p_3", font_size=16)
        bar3_lbl.next_to(bar3, DOWN, buff=0.08)

        self.play(GrowFromEdge(bar3, DOWN), Write(bar3_lbl), run_time=0.5)

        # 验证 - 修复: 将 sum_check 放置在柱状图下方，避免与柱状图重叠
        sum_check = MathTex(r"\sum = 0.79 < 1 \checkmark", font_size=22, color=SURVIVE_COLOR)
        sum_check.next_to(bar_base, DOWN, buff=0.3)
        self.play(Write(sum_check), run_time=0.6)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part5_final_step(self):
        """Part 5: Handling the Final Step (20-25 sec)"""
        title = Tex("Handling the Final Step", font_size=34, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.6)

        narration = Tex("What about the remaining probability mass?", font_size=24, color=GREY_B)
        narration.next_to(title, DOWN, buff=0.3)
        self.play(Write(narration), run_time=0.8)

        # 条形图
        bar_base = Line(LEFT * 2, RIGHT * 2, color=GREY_B, stroke_width=2)
        bar_base.shift(DOWN * 0.5)

        probs = [0.30, 0.35, 0.14]
        colors = [EXIT_COLOR, HIGHLIGHT_COLOR, SURVIVE_COLOR]
        bars = VGroup()
        lbls = VGroup()

        for i, (p, c) in enumerate(zip(probs, colors)):
            bar = Rectangle(width=0.45, height=p * 4, color=c, fill_opacity=0.8, stroke_width=1)
            bar.next_to(bar_base, UP, buff=0).shift(LEFT * 1.2 + RIGHT * i * 0.7)
            bars.add(bar)
            lbl = MathTex(f"p_{i+1}", font_size=18)
            lbl.next_to(bar, DOWN, buff=0.08)
            lbls.add(lbl)

        self.play(
            Create(bar_base),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in lbls], lag_ratio=0.1),
            run_time=1
        )

        # 缺口
        total = MathTex(r"\text{Total} = 0.79", font_size=26)
        total.shift(RIGHT * 3 + UP * 0.5)
        gap = MathTex(r"\text{Missing: } 0.21", font_size=24, color=EXIT_COLOR)
        gap.next_to(total, DOWN, buff=0.2)

        self.play(Write(total), Write(gap), run_time=0.8)

        # 解决方案
        solution = Tex("Force exit at max loops!", font_size=26, color=SURVIVE_COLOR)
        solution.shift(DOWN * 1.8)
        self.play(Write(solution), run_time=0.6)

        # p4 填充
        bar4 = Rectangle(width=0.45, height=0.21 * 4, color=LOOP_COLOR, fill_opacity=0.8, stroke_width=1)
        bar4.next_to(bar_base, UP, buff=0).shift(LEFT * 1.2 + RIGHT * 3 * 0.7)
        lbl4 = MathTex(r"p_4", font_size=18)
        lbl4.next_to(bar4, DOWN, buff=0.08)

        self.play(GrowFromEdge(bar4, DOWN), Write(lbl4), run_time=0.6)

        # 公式
        final_formula = MathTex(r"p_N = 1 - \sum_{n=1}^{N-1} p_n", font_size=26, color=LOOP_COLOR)
        final_formula.next_to(solution, DOWN, buff=0.3)
        self.play(Write(final_formula), run_time=0.6)

        # 验证
        self.play(FadeOut(total), FadeOut(gap), run_time=0.3)
        valid = MathTex(r"\sum p = 1.0 \checkmark", font_size=28, color=SURVIVE_COLOR)
        valid.shift(RIGHT * 3 + UP * 0.5)
        self.play(Write(valid), run_time=0.6)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part6_cdf_threshold(self):
        """Part 6: CDF Thresholding (30-40 sec)"""
        title = Tex("Inference: CDF Thresholding", font_size=34, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.6)

        cdf_values = [0.30, 0.65, 0.79, 1.00]
        labels = ["L1", "L2", "L3", "L4"]

        # CDF 图
        axes = Axes(
            x_range=[0, 5, 1], y_range=[0, 1.2, 0.2],
            x_length=7, y_length=4,
            axis_config={"color": GREY_B},
        )
        axes.shift(DOWN * 0.2)

        cdf_points = [(0, 0)]
        for i, cdf_val in enumerate(cdf_values):
            prev = cdf_values[i-1] if i > 0 else 0
            cdf_points.append((i + 1, prev))
            cdf_points.append((i + 1, cdf_val))

        cdf_line = VMobject(color=LOOP_COLOR, stroke_width=3)
        cdf_line.set_points_as_corners([axes.c2p(x, y) for x, y in cdf_points])

        cdf_dots = VGroup()
        cdf_lbls = VGroup()
        for i, cdf in enumerate(cdf_values):
            dot = Dot(axes.c2p(i + 1, cdf), color=HIGHLIGHT_COLOR, radius=0.06)
            lbl = MathTex(f"{cdf:.2f}", font_size=18, color=HIGHLIGHT_COLOR)
            lbl.next_to(dot, UR, buff=0.05)
            cdf_dots.add(dot)
            cdf_lbls.add(lbl)

        x_lbls = VGroup()
        for i, l in enumerate(labels):
            txt = Tex(l, font_size=18)
            txt.move_to(axes.c2p(i + 1, 0) + DOWN * 0.3)
            x_lbls.add(txt)

        self.play(Create(axes), run_time=0.6)
        self.play(Create(cdf_line), run_time=1)
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.3) for d in cdf_dots], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in cdf_lbls], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in x_lbls], lag_ratio=0.1),
            run_time=1
        )

        # 阈值线
        threshold_line = DashedLine(
            axes.c2p(0, 0.7), axes.c2p(5, 0.7),
            color=THRESHOLD_COLOR, stroke_width=3, dash_length=0.1
        )
        threshold_lbl = MathTex(r"q = 0.7", font_size=22, color=THRESHOLD_COLOR)
        threshold_lbl.next_to(threshold_line, RIGHT, buff=0.1)

        self.play(Create(threshold_line), Write(threshold_lbl), run_time=0.6)

        # 决策
        rule = Tex(r"Exit when CDF $\geq$ threshold", font_size=22, color=SURVIVE_COLOR)
        rule.to_edge(DOWN, buff=1.5)
        self.play(Write(rule), run_time=0.6)

        # 检查
        checks = VGroup()

        check1 = MathTex(r"L_1: 0.30 < 0.7 \rightarrow \text{Continue}", font_size=18)
        check1[-8:].set_color(SURVIVE_COLOR)
        check1.to_edge(DOWN, buff=0.9)

        check2 = MathTex(r"L_2: 0.65 < 0.7 \rightarrow \text{Continue}", font_size=18)
        check2[-8:].set_color(SURVIVE_COLOR)
        check2.next_to(check1, DOWN, buff=0.12)

        check3 = MathTex(r"L_3: 0.79 \geq 0.7 \rightarrow \textbf{EXIT!}", font_size=18)
        check3[-5:].set_color(EXIT_COLOR)
        check3.next_to(check2, DOWN, buff=0.12)

        self.play(Write(check1), run_time=0.5)
        self.play(Write(check2), run_time=0.5)
        self.play(Write(check3), run_time=0.5)

        # 高亮 L3
        exit_circle = Circle(radius=0.15, color=EXIT_COLOR, stroke_width=3)
        exit_circle.move_to(axes.c2p(3, 0.79))
        self.play(Create(exit_circle), run_time=0.4)
        self.play(exit_circle.animate.scale(1.5).set_opacity(0), run_time=0.5)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part7_recap(self):
        """Part 7: Recap (10-15 sec)"""
        title = Tex("Summary", font_size=40, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.6)

        # 公式
        formulas = VGroup(
            MathTex(r"p_n = \lambda_n \prod_{j=1}^{n-1}(1-\lambda_j)", font_size=28),
            MathTex(r"p_N = 1 - \sum_{n=1}^{N-1} p_n", font_size=28),
            Tex(r"Exit when CDF $\geq$ threshold", font_size=22, color=SURVIVE_COLOR),
        )
        formulas.arrange(DOWN, buff=0.3)
        formulas.shift(UP * 0.3)

        formula_box = SurroundingRectangle(formulas, color=FORMULA_COLOR, buff=0.25)

        self.play(
            LaggedStart(*[Write(f) for f in formulas], lag_ratio=0.2),
            run_time=1.5
        )
        self.play(Create(formula_box), run_time=0.5)

        # 总结
        summary_points = VGroup(
            Tex(r"$\checkmark$ Sequential gating with sigmoid", font_size=20, color=SURVIVE_COLOR),
            Tex(r"$\checkmark$ Automatic probability normalization", font_size=20, color=SURVIVE_COLOR),
            Tex(r"$\checkmark$ No future information needed", font_size=20, color=SURVIVE_COLOR),
        )
        summary_points.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        summary_points.to_edge(DOWN, buff=0.6)

        self.play(LaggedStart(*[Write(s) for s in summary_points], lag_ratio=0.2), run_time=1.2)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("PonderNet Early Exit Mechanism - Manim Animation")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql pondernet_early_exit.py PonderNetEarlyExit")
    print("  高质量:   manim -pqh pondernet_early_exit.py PonderNetEarlyExit")
    print("\n单独场景:")
    print("  manim -pql pondernet_early_exit.py Part1Setup")
    print("  manim -pql pondernet_early_exit.py Part2SigmoidProblem")
    print("  manim -pql pondernet_early_exit.py Part3WhyNotSoftmax")
    print("  manim -pql pondernet_early_exit.py Part4ConditionalToUnconditional")
    print("  manim -pql pondernet_early_exit.py Part5FinalStep")
    print("  manim -pql pondernet_early_exit.py Part6CDFThresholding")
    print("  manim -pql pondernet_early_exit.py Part7Recap")
    print("=" * 60)

