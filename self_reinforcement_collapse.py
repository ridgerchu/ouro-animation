"""
Self-Reinforcement Collapse 可视化动画
运行命令:
  完整动画: manim -pql self_reinforcement_collapse.py SelfReinforcementCollapse
  单独场景: manim -pql self_reinforcement_collapse.py Part1Setup
           manim -pql self_reinforcement_collapse.py Part2Collapse
           manim -pql self_reinforcement_collapse.py Part3FalseHope
           manim -pql self_reinforcement_collapse.py Part4TrainingLoop
           manim -pql self_reinforcement_collapse.py Part5ViciousCycle
           manim -pql self_reinforcement_collapse.py Part6Evidence
           manim -pql self_reinforcement_collapse.py Part7Teaser
  高质量渲染: manim -pqh self_reinforcement_collapse.py SelfReinforcementCollapse
"""

from manim import *
import numpy as np

# ===== 颜色配置 =====
# 退出深度颜色 t=1 to t=5 (purple → blue → teal → green → yellow)
DEPTH_COLORS = [
    "#9B59B6",  # t=1 purple
    "#3498DB",  # t=2 blue
    "#1ABC9C",  # t=3 teal
    "#2ECC71",  # t=4 green
    "#F1C40F",  # t=5 yellow (dominant)
]

WARNING_COLOR = "#E74C3C"     # 红色 - 警告
HIGHLIGHT_COLOR = "#F39C12"   # 橙色 - 高亮
LOOP_COLOR = "#3498DB"        # 蓝色 - Loop方块
FORMULA_COLOR = "#9B59B6"     # 紫色 - 公式
GRADIENT_COLOR = "#E67E22"    # 梯度颜色
LOSS_COLOR = "#E74C3C"        # Loss 颜色
CELEBRATE_COLOR = "#F1C40F"   # 庆祝颜色


class LoopBlock(VGroup):
    """可复用的 Loop 方块组件"""
    def __init__(self, label_text, scale_factor=1.0, color=LOOP_COLOR, **kwargs):
        super().__init__(**kwargs)
        self.rect = RoundedRectangle(
            height=1.0 * scale_factor,
            width=1.3 * scale_factor,
            corner_radius=0.12 * scale_factor,
            color=color,
            fill_opacity=0.3,
            stroke_width=3
        )
        self.label = Tex(label_text, font_size=int(24 * scale_factor), color=WHITE)
        self.label.move_to(self.rect.get_center())
        self.add(self.rect, self.label)

    def highlight(self, color=HIGHLIGHT_COLOR):
        return self.rect.animate.set_stroke(color=color, width=5)

    def unhighlight(self):
        return self.rect.animate.set_stroke(color=LOOP_COLOR, width=3)


class ExitGate(VGroup):
    """Exit Gate 组件"""
    def __init__(self, scale_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.rect = RoundedRectangle(
            height=0.6 * scale_factor,
            width=0.8 * scale_factor,
            corner_radius=0.08 * scale_factor,
            color=HIGHLIGHT_COLOR,
            fill_opacity=0.2,
            stroke_width=2
        )
        self.label = MathTex(r"\sigma", font_size=int(20 * scale_factor))
        self.label.move_to(self.rect.get_center())
        self.add(self.rect, self.label)


class LossBox(VGroup):
    """Loss 方块组件"""
    def __init__(self, label_text, scale_factor=1.0, **kwargs):
        super().__init__(**kwargs)
        self.rect = RoundedRectangle(
            height=0.5 * scale_factor,
            width=0.7 * scale_factor,
            corner_radius=0.06 * scale_factor,
            color=LOSS_COLOR,
            fill_opacity=0.4,
            stroke_width=2
        )
        self.label = MathTex(label_text, font_size=int(18 * scale_factor), color=WHITE)
        self.label.move_to(self.rect.get_center())
        self.add(self.rect, self.label)


# ===== Part 1: Setting Up the Visualization =====
class Part1Setup(Scene):
    """Part 1: Setting Up the Visualization (15-20 sec)"""
    def construct(self):
        # 标题
        title = Tex(
            "Self-Reinforcement Collapse",
            font_size=40, color=WHITE
        )
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=1)

        # 旁白说明
        narration = Tex(
            "Training Iterations vs Exit Probability",
            font_size=24, color=GREY_B
        )
        narration.next_to(title, DOWN, buff=0.2)
        self.play(Write(narration), run_time=0.8)

        # ===== 创建坐标轴 =====
        axes = Axes(
            x_range=[0, 180, 30],
            y_range=[0, 1.1, 0.2],
            x_length=9,
            y_length=4.5,
            axis_config={"color": GREY_B, "include_tip": True},
            x_axis_config={"numbers_to_include": [0, 60, 120, 180]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        axes.shift(DOWN * 0.3 + LEFT * 0.5)

        # 轴标签
        x_label = Tex("Training Iterations", font_size=22, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.5)
        y_label = MathTex(r"p_\theta(t|x)", font_size=22, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1.5)

        # ===== 图例 =====
        legend_group = VGroup()
        legend_title = Tex("Exit Depth", font_size=18, color=GREY_B)
        legend_title.shift(RIGHT * 4.5 + UP * 2)
        legend_group.add(legend_title)

        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(color=color, radius=0.08)
            dot.shift(RIGHT * 4.2 + UP * (1.5 - i * 0.4))
            label = Tex(f"t={i+1}", font_size=16, color=color)
            label.next_to(dot, RIGHT, buff=0.15)
            legend_group.add(dot, label)

        self.play(FadeIn(legend_group), run_time=0.8)

        # ===== 初始状态：所有线从相似的低值开始 =====
        # 创建初始点
        initial_dots = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(axes.c2p(0, 0.2), color=color, radius=0.06)
            initial_dots.add(dot)

        self.play(
            LaggedStart(*[FadeIn(d, scale=1.5) for d in initial_dots], lag_ratio=0.1),
            run_time=0.8
        )

        # 说明文字
        explain = Tex(
            "All exit depths start with similar low probabilities",
            font_size=20, color=GREY_B
        )
        explain.to_edge(DOWN, buff=0.5)
        self.play(Write(explain), run_time=0.8)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Part 2: The Collapse Happens =====
class Part2Collapse(Scene):
    """Part 2: The Collapse Happens (20-25 sec)"""
    def construct(self):
        # 标题
        title = Tex("The Collapse Happens", font_size=36, color=WARNING_COLOR)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        # ===== 创建坐标轴 =====
        axes = Axes(
            x_range=[0, 180, 30],
            y_range=[0, 1.1, 0.2],
            x_length=9,
            y_length=4.5,
            axis_config={"color": GREY_B, "include_tip": True},
            x_axis_config={"numbers_to_include": [0, 60, 120, 180]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        axes.shift(DOWN * 0.3 + LEFT * 0.5)

        x_label = Tex("Training Iterations", font_size=20, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.5)
        y_label = MathTex(r"p_\theta(t|x)", font_size=20, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1)

        # ===== 图例 =====
        legend_group = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(color=color, radius=0.06)
            dot.shift(RIGHT * 4.2 + UP * (2 - i * 0.35))
            label = Tex(f"t={i+1}", font_size=14, color=color)
            label.next_to(dot, RIGHT, buff=0.1)
            legend_group.add(dot, label)

        self.play(FadeIn(legend_group), run_time=0.5)

        # ===== 定义概率曲线数据 =====
        # t=1 to t=4: 逐渐下降到接近0
        # t=5: 急剧上升到1.0
        def prob_curve(t_depth, x):
            """生成概率曲线"""
            if t_depth < 5:  # t=1,2,3,4
                # 指数衰减
                initial = 0.2
                decay_rate = 0.02 + (t_depth - 1) * 0.005
                return initial * np.exp(-decay_rate * x)
            else:  # t=5
                # S形上升
                midpoint = 80
                steepness = 0.05
                return 0.2 + 0.8 / (1 + np.exp(-steepness * (x - midpoint)))

        # 创建曲线
        curves = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            curve = axes.plot(
                lambda x, t=i+1: prob_curve(t, x),
                color=color,
                stroke_width=3
            )
            curves.add(curve)

        # ===== 动画：逐步绘制曲线 =====
        # 使用 ValueTracker 来动画化
        progress = ValueTracker(0)

        # 创建动态曲线
        dynamic_curves = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            def get_curve(i=i, color=color):
                x_max = progress.get_value()
                if x_max <= 0:
                    return VectorizedPoint(axes.c2p(0, prob_curve(i+1, 0)))
                curve = axes.plot(
                    lambda x, t=i+1: prob_curve(t, x),
                    x_range=[0, x_max],
                    color=color,
                    stroke_width=3
                )
                return curve

            dynamic_curve = always_redraw(get_curve)
            dynamic_curves.add(dynamic_curve)

        self.add(dynamic_curves)

        # 动画：从0到180
        self.play(progress.animate.set_value(180), run_time=5, rate_func=linear)

        # ===== 高亮 t=5 的主导 =====
        # 添加圆圈高亮
        highlight_circle = Circle(
            radius=0.3, color=CELEBRATE_COLOR, stroke_width=4
        )
        highlight_circle.move_to(axes.c2p(180, 1.0))

        # 主导深度标签
        dominant_badge = VGroup()
        badge_rect = RoundedRectangle(
            width=3.5, height=0.8, corner_radius=0.1,
            color=CELEBRATE_COLOR, fill_opacity=0.2, stroke_width=2
        )
        badge_text = Tex(
            r"Dominant: t=5, $p$ = 1.000",
            font_size=20, color=CELEBRATE_COLOR
        )
        badge_text.move_to(badge_rect.get_center())
        dominant_badge.add(badge_rect, badge_text)
        dominant_badge.shift(RIGHT * 3 + DOWN * 1.5)

        self.play(
            Create(highlight_circle),
            FadeIn(dominant_badge),
            run_time=0.8
        )

        # 说明
        explain = Tex(
            "The final loop absolutely dominates everything else!",
            font_size=22, color=WARNING_COLOR
        )
        explain.to_edge(DOWN, buff=0.4)
        self.play(Write(explain), run_time=0.8)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Part 3: The False Hope =====
class Part3FalseHope(Scene):
    """Part 3: The False Hope (10-15 sec)"""
    def construct(self):
        # ===== 庆祝部分 =====
        celebrate_text = Tex(
            "SOLVED DEEP LEARNING?",
            font_size=48, color=CELEBRATE_COLOR
        )
        celebrate_text.shift(UP * 1)

        self.play(FadeIn(celebrate_text, scale=1.5), run_time=0.8)

        # 问号
        question_text = Tex(
            "Everything needs many loops... Are we geniuses?",
            font_size=28, color=WHITE
        )
        question_text.next_to(celebrate_text, DOWN, buff=0.5)
        self.play(Write(question_text), run_time=1)

        # 简单的庆祝效果 - 用闪烁的点代替 confetti
        sparkles = VGroup()
        for _ in range(12):
            sparkle = Dot(
                point=np.array([
                    np.random.uniform(-5, 5),
                    np.random.uniform(-2, 2.5),
                    0
                ]),
                color=random_color(),
                radius=0.08
            )
            sparkles.add(sparkle)

        self.play(
            LaggedStart(*[FadeIn(s, scale=2) for s in sparkles], lag_ratio=0.05),
            run_time=0.8
        )

        self.wait(0.5)

        # ===== Record scratch - 一切停止 =====
        # 红色大X
        cross_line1 = Line(
            celebrate_text.get_corner(UL) + LEFT * 0.3 + UP * 0.2,
            celebrate_text.get_corner(DR) + RIGHT * 0.3 + DOWN * 0.2,
            color=WARNING_COLOR, stroke_width=8
        )
        cross_line2 = Line(
            celebrate_text.get_corner(UR) + RIGHT * 0.3 + UP * 0.2,
            celebrate_text.get_corner(DL) + LEFT * 0.3 + DOWN * 0.2,
            color=WARNING_COLOR, stroke_width=8
        )

        # "Nope" 文字
        nope_text = Tex(
            r"\textbf{Nope.}",
            font_size=60, color=WARNING_COLOR
        )
        nope_text.shift(DOWN * 1.5)

        # 动画：一切变灰，划掉
        self.play(
            celebrate_text.animate.set_opacity(0.3),
            question_text.animate.set_opacity(0.3),
            *[s.animate.set_opacity(0.1) for s in sparkles],
            Create(cross_line1),
            Create(cross_line2),
            run_time=0.6
        )

        self.play(FadeIn(nope_text, scale=1.5), run_time=0.5)

        # 但是...
        but_text = Tex(
            "Buuut it turns out that's not quite the case...",
            font_size=24, color=GREY_B
        )
        but_text.next_to(nope_text, DOWN, buff=0.4)
        self.play(Write(but_text), run_time=1)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Part 4: How Training Works =====
class Part4TrainingLoop(Scene):
    """Part 4: How Training Works (30-40 sec)"""
    def construct(self):
        # 标题
        title = Tex("How Training Works", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        # ===== 训练流程图 =====
        # 创建5个 Loop 方块
        loops = VGroup()
        for i in range(5):
            loop = LoopBlock(f"Loop {i+1}", scale_factor=0.8)
            loops.add(loop)
        loops.arrange(RIGHT, buff=0.6)
        loops.shift(UP * 1.2)

        # Input 箭头
        input_arrow = Arrow(
            loops[0].get_left() + LEFT * 1.2,
            loops[0].get_left() + LEFT * 0.1,
            color=GREY_B, stroke_width=2
        )
        input_label = Tex("Input", font_size=18, color=GREY_B)
        input_label.next_to(input_arrow, LEFT, buff=0.1)

        # Loop 之间的箭头
        loop_arrows = VGroup()
        for i in range(4):
            arrow = Arrow(
                loops[i].get_right() + RIGHT * 0.05,
                loops[i+1].get_left() + LEFT * 0.05,
                color=GREY_B, stroke_width=2, buff=0
            )
            loop_arrows.add(arrow)

        self.play(
            FadeIn(input_label), GrowArrow(input_arrow),
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.1),
            LaggedStart(*[GrowArrow(a) for a in loop_arrows], lag_ratio=0.1),
            run_time=1.5
        )

        # ===== Exit Gates =====
        exit_gates = VGroup()
        gate_arrows = VGroup()
        for i, loop in enumerate(loops):
            gate = ExitGate(scale_factor=0.7)
            gate.next_to(loop, DOWN, buff=0.3)
            exit_gates.add(gate)

            arrow = Arrow(
                loop.get_bottom(),
                gate.get_top(),
                color=HIGHLIGHT_COLOR, stroke_width=2, buff=0.05
            )
            gate_arrows.add(arrow)

        self.play(
            LaggedStart(*[FadeIn(g) for g in exit_gates], lag_ratio=0.08),
            LaggedStart(*[GrowArrow(a) for a in gate_arrows], lag_ratio=0.08),
            run_time=1
        )

        # ===== Loss boxes =====
        loss_boxes = VGroup()
        loss_arrows = VGroup()
        for i, gate in enumerate(exit_gates):
            loss = LossBox(f"L_{i+1}", scale_factor=0.9)
            loss.next_to(gate, DOWN, buff=0.3)
            loss_boxes.add(loss)

            arrow = Arrow(
                gate.get_bottom(),
                loss.get_top(),
                color=LOSS_COLOR, stroke_width=2, buff=0.05
            )
            loss_arrows.add(arrow)

        # 说明文字
        explain1 = Tex(
            "During training, we compute a loss at EVERY step",
            font_size=22, color=GREY_B
        )
        explain1.to_edge(DOWN, buff=1.8)
        self.play(Write(explain1), run_time=0.8)

        # 动画：所有 Loss 同时亮起
        self.play(
            LaggedStart(*[FadeIn(l, scale=1.2) for l in loss_boxes], lag_ratio=0.08),
            LaggedStart(*[GrowArrow(a) for a in loss_arrows], lag_ratio=0.08),
            run_time=1
        )

        # 全部高亮
        self.play(
            *[l.rect.animate.set_fill(LOSS_COLOR, opacity=0.7) for l in loss_boxes],
            run_time=0.5
        )

        self.wait(1)

        # ===== 权重公式 =====
        self.play(FadeOut(explain1), run_time=0.3)

        explain2 = Tex(
            "Each loss is weighted by exit probability",
            font_size=22, color=GREY_B
        )
        explain2.to_edge(DOWN, buff=1.8)
        self.play(Write(explain2), run_time=0.6)

        # 公式
        formula = MathTex(
            r"\mathcal{L} = \sum_{n=1}^{N} p_n \cdot L^{(n)}",
            font_size=36, color=FORMULA_COLOR
        )
        formula.to_edge(DOWN, buff=0.8)
        formula_box = SurroundingRectangle(formula, color=FORMULA_COLOR, buff=0.15)

        self.play(Write(formula), Create(formula_box), run_time=1.2)

        self.wait(1)

        # ===== 概率权重可视化 =====
        self.play(FadeOut(explain2), run_time=0.3)

        # 给每个 Loss 添加概率标签
        prob_values = [0.15, 0.15, 0.15, 0.15, 0.40]
        prob_labels = VGroup()
        for i, (loss, p) in enumerate(zip(loss_boxes, prob_values)):
            label = MathTex(f"p_{i+1}={p:.2f}", font_size=14, color=HIGHLIGHT_COLOR)
            label.next_to(loss, DOWN, buff=0.1)
            prob_labels.add(label)

        self.play(
            LaggedStart(*[Write(l) for l in prob_labels], lag_ratio=0.08),
            run_time=0.8
        )

        # 缩放 Loss boxes 来显示权重
        # p5=0.4 最大，其他较小
        scale_factors = [0.6, 0.6, 0.6, 0.6, 1.2]
        self.play(
            *[loss_boxes[i].animate.scale(sf) for i, sf in enumerate(scale_factors)],
            run_time=1
        )

        explain3 = Tex(
            r"Higher $p$ $\rightarrow$ larger loss contribution $\rightarrow$ dominates weight updates",
            font_size=20, color=GREY_B
        )
        explain3.next_to(formula_box, UP, buff=0.3)
        self.play(Write(explain3), run_time=1)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Part 5: The Vicious Cycle =====
class Part5ViciousCycle(Scene):
    """Part 5: The Vicious Cycle (45-55 sec)"""
    def construct(self):
        # 标题
        title = Tex("The Vicious Cycle", font_size=36, color=WARNING_COLOR)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        # ===== Part A: 初始状态 =====
        # 5个 Exit Gates，概率都约为0.2
        gates = VGroup()
        for i in range(5):
            gate = VGroup()
            rect = RoundedRectangle(
                width=1.2, height=0.8, corner_radius=0.1,
                color=DEPTH_COLORS[i], fill_opacity=0.3, stroke_width=2
            )
            label = MathTex(f"p_{i+1}", font_size=22, color=WHITE)
            label.move_to(rect.get_center())
            gate.add(rect, label)
            gates.add(gate)

        gates.arrange(RIGHT, buff=0.4)
        gates.shift(UP * 1.5)

        # 概率值标签
        prob_values = [0.20, 0.20, 0.20, 0.20, 0.20]
        prob_labels = VGroup()
        for i, (gate, p) in enumerate(zip(gates, prob_values)):
            label = MathTex(f"{p:.2f}", font_size=18, color=GREY_B)
            label.next_to(gate, DOWN, buff=0.15)
            prob_labels.add(label)

        self.play(
            LaggedStart(*[FadeIn(g) for g in gates], lag_ratio=0.08),
            LaggedStart(*[Write(l) for l in prob_labels], lag_ratio=0.08),
            run_time=1
        )

        # 说明
        explain1 = Tex(
            "Initially, all gates have similar probabilities",
            font_size=22, color=GREY_B
        )
        explain1.to_edge(DOWN, buff=2)
        self.play(Write(explain1), run_time=0.6)

        self.wait(0.8)

        # ===== Part B: 随机波动 =====
        self.play(FadeOut(explain1), run_time=0.3)

        explain2 = Tex(
            "One gate randomly increases slightly...",
            font_size=22, color=HIGHLIGHT_COLOR
        )
        explain2.to_edge(DOWN, buff=2)
        self.play(Write(explain2), run_time=0.6)

        # t=5 增加
        new_prob5 = MathTex("0.25", font_size=18, color=CELEBRATE_COLOR)
        new_prob5.move_to(prob_labels[4].get_center())

        # 高亮 t=5
        highlight_rect = SurroundingRectangle(gates[4], color=CELEBRATE_COLOR, buff=0.1)

        self.play(
            Transform(prob_labels[4], new_prob5),
            Create(highlight_rect),
            gates[4][0].animate.set_stroke(CELEBRATE_COLOR, width=4),
            run_time=0.8
        )

        # "Random fluctuation" 标注
        fluctuation_label = Tex("Random fluctuation", font_size=16, color=CELEBRATE_COLOR)
        fluctuation_label.next_to(highlight_rect, UP, buff=0.1)
        self.play(Write(fluctuation_label), run_time=0.5)

        self.wait(1)

        # ===== Part C: 更大的梯度贡献 =====
        self.play(FadeOut(explain2), FadeOut(fluctuation_label), run_time=0.3)

        explain3 = Tex(
            r"That loop-step gets MORE gradient contribution",
            font_size=22, color=GRADIENT_COLOR
        )
        explain3.to_edge(DOWN, buff=2)
        self.play(Write(explain3), run_time=0.6)

        # 梯度公式
        gradient_formula = MathTex(
            r"\nabla_\theta \propto p_\theta(t|x)",
            font_size=28, color=GRADIENT_COLOR
        )
        gradient_formula.next_to(gates, DOWN, buff=1)

        # 箭头指向 t=5
        grad_arrow = Arrow(
            gradient_formula.get_right() + RIGHT * 0.1,
            gates[4].get_bottom() + DOWN * 0.3,
            color=GRADIENT_COLOR, stroke_width=3
        )

        self.play(Write(gradient_formula), GrowArrow(grad_arrow), run_time=0.8)

        self.wait(1)

        # ===== Part D: 反馈循环图 =====
        self.play(
            FadeOut(gates), FadeOut(prob_labels), FadeOut(highlight_rect),
            FadeOut(gradient_formula), FadeOut(grad_arrow), FadeOut(explain3),
            run_time=0.6
        )

        # 创建循环图
        cycle_title = Tex("Self-Reinforcement Loop", font_size=28, color=WARNING_COLOR)
        cycle_title.to_edge(UP, buff=0.8)
        self.play(Transform(title, cycle_title), run_time=0.5)

        # 循环节点
        cycle_radius = 2
        center = ORIGIN + DOWN * 0.2

        node_texts = [
            r"Gate $\uparrow$" + "\n" + r"$p_\theta(t|x)$",
            r"More Gradient" + "\n" + r"$\nabla_\theta \propto p$",
            r"Loss $\downarrow$" + "\n" + r"$L^{(t)}$",
            r"Gate $\uparrow\uparrow$" + "\n" + r"$p_\theta(t|x)$",
        ]
        node_colors = [CELEBRATE_COLOR, GRADIENT_COLOR, LOSS_COLOR, WARNING_COLOR]

        nodes = VGroup()
        for i, (text, color) in enumerate(zip(node_texts, node_colors)):
            angle = PI/2 - i * PI/2  # 从顶部开始，顺时针
            pos = center + cycle_radius * np.array([np.cos(angle), np.sin(angle), 0])

            node_rect = RoundedRectangle(
                width=2.2, height=1, corner_radius=0.15,
                color=color, fill_opacity=0.2, stroke_width=3
            )
            node_rect.move_to(pos)

            node_text = Tex(text, font_size=18, color=WHITE)
            node_text.move_to(pos)

            node = VGroup(node_rect, node_text)
            nodes.add(node)

        # 箭头连接
        cycle_arrows = VGroup()
        for i in range(4):
            start_node = nodes[i]
            end_node = nodes[(i + 1) % 4]

            # 计算箭头位置
            start_angle = PI/2 - i * PI/2
            end_angle = PI/2 - ((i + 1) % 4) * PI/2

            start_pos = center + (cycle_radius - 0.6) * np.array([np.cos(start_angle - 0.3), np.sin(start_angle - 0.3), 0])
            end_pos = center + (cycle_radius - 0.6) * np.array([np.cos(end_angle + 0.3), np.sin(end_angle + 0.3), 0])

            arrow = CurvedArrow(
                start_pos, end_pos,
                color=GREY_B, stroke_width=3,
                angle=-PI/3
            )
            cycle_arrows.add(arrow)

        # 动画：显示循环
        self.play(
            LaggedStart(*[FadeIn(n, scale=0.8) for n in nodes], lag_ratio=0.2),
            run_time=1.5
        )
        self.play(
            LaggedStart(*[Create(a) for a in cycle_arrows], lag_ratio=0.2),
            run_time=1.2
        )

        # 中心标签
        center_label = Tex(
            "Current dominant:\n" + r"$t = 5$",
            font_size=20, color=CELEBRATE_COLOR
        )
        center_label.move_to(center)
        self.play(Write(center_label), run_time=0.6)

        # ===== 循环加速动画 =====
        # 让箭头闪烁来表示循环
        self.play(
            *[a.animate.set_color(WARNING_COLOR) for a in cycle_arrows],
            run_time=0.5
        )
        self.play(
            *[a.animate.set_color(GREY_B) for a in cycle_arrows],
            run_time=0.5
        )
        self.play(
            *[a.animate.set_color(WARNING_COLOR) for a in cycle_arrows],
            run_time=0.3
        )

        # 警告横幅
        warning_banner = VGroup()
        banner_rect = Rectangle(
            width=10, height=0.8,
            color=WARNING_COLOR, fill_opacity=0.3, stroke_width=3
        )
        banner_rect.to_edge(DOWN, buff=0.3)
        banner_text = Tex(
            r"\textbf{WARNING:} Without Entropy Regularization, model converges to single depth!",
            font_size=20, color=WARNING_COLOR
        )
        banner_text.move_to(banner_rect.get_center())
        warning_banner.add(banner_rect, banner_text)

        self.play(FadeIn(warning_banner, shift=UP * 0.3), run_time=0.8)

        # 让警告闪烁
        self.play(
            banner_rect.animate.set_fill(WARNING_COLOR, opacity=0.6),
            run_time=0.3
        )
        self.play(
            banner_rect.animate.set_fill(WARNING_COLOR, opacity=0.3),
            run_time=0.3
        )

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Part 6: Back to the Evidence =====
class Part6Evidence(Scene):
    """Part 6: Back to the Evidence (20-25 sec)"""
    def construct(self):
        # 标题
        title = Tex("Observing the Collapse", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        # ===== 重新创建概率图 =====
        axes = Axes(
            x_range=[0, 180, 30],
            y_range=[0, 1.1, 0.2],
            x_length=8,
            y_length=4,
            axis_config={"color": GREY_B, "include_tip": True},
            x_axis_config={"numbers_to_include": [0, 60, 120, 180]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        axes.shift(DOWN * 0.5 + LEFT * 0.5)

        x_label = Tex("Training Iterations", font_size=18, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.4)
        y_label = MathTex(r"p_\theta(t|x)", font_size=18, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.15)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1)

        # 图例
        legend = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(color=color, radius=0.05)
            dot.shift(RIGHT * 4.5 + UP * (1.5 - i * 0.3))
            label = Tex(f"t={i+1}", font_size=12, color=color)
            label.next_to(dot, RIGHT, buff=0.1)
            legend.add(dot, label)
        self.play(FadeIn(legend), run_time=0.4)

        # 定义曲线
        def prob_curve(t_depth, x):
            if t_depth < 5:
                initial = 0.2
                decay_rate = 0.02 + (t_depth - 1) * 0.005
                return initial * np.exp(-decay_rate * x)
            else:
                midpoint = 80
                steepness = 0.05
                return 0.2 + 0.8 / (1 + np.exp(-steepness * (x - midpoint)))

        # 动画绘制曲线
        progress = ValueTracker(0)

        dynamic_curves = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            def get_curve(i=i, color=color):
                x_max = progress.get_value()
                if x_max <= 0:
                    return VectorizedPoint(axes.c2p(0, prob_curve(i+1, 0)))
                curve = axes.plot(
                    lambda x, t=i+1: prob_curve(t, x),
                    x_range=[0, x_max],
                    color=color,
                    stroke_width=2.5
                )
                return curve
            dynamic_curve = always_redraw(get_curve)
            dynamic_curves.add(dynamic_curve)

        self.add(dynamic_curves)

        # ===== 标注说明 =====
        # 早期阶段标注
        early_annotation = Tex(
            "First batch favored t=5",
            font_size=16, color=CELEBRATE_COLOR
        )
        early_annotation.shift(LEFT * 2 + UP * 2)

        early_arrow = Arrow(
            early_annotation.get_bottom(),
            axes.c2p(20, 0.25),
            color=CELEBRATE_COLOR, stroke_width=2
        )

        self.play(progress.animate.set_value(40), run_time=1.5, rate_func=linear)
        self.play(Write(early_annotation), GrowArrow(early_arrow), run_time=0.6)

        # 继续动画
        self.play(progress.animate.set_value(100), run_time=2, rate_func=linear)

        # 中期标注
        mid_annotation = Tex(
            "Self-reinforcement kicks in",
            font_size=16, color=WARNING_COLOR
        )
        mid_annotation.shift(RIGHT * 1 + UP * 2.2)

        mid_arrow = Arrow(
            mid_annotation.get_bottom(),
            axes.c2p(80, 0.6),
            color=WARNING_COLOR, stroke_width=2
        )

        self.play(Write(mid_annotation), GrowArrow(mid_arrow), run_time=0.6)

        # 完成动画
        self.play(progress.animate.set_value(180), run_time=1.5, rate_func=linear)

        # 最终状态标签
        final_label = VGroup()
        final_rect = RoundedRectangle(
            width=3.5, height=0.7, corner_radius=0.1,
            color=WARNING_COLOR, fill_opacity=0.2, stroke_width=2
        )
        final_text = Tex(
            "Probability Collapse",
            font_size=18, color=WARNING_COLOR
        )
        final_text.move_to(final_rect.get_center())
        final_label.add(final_rect, final_text)
        final_label.shift(RIGHT * 3.5 + DOWN * 2)

        self.play(FadeIn(final_label), run_time=0.6)

        # 说明
        explain = Tex(
            "Whatever loop exited first in the first batch dominates the rest of training",
            font_size=18, color=GREY_B
        )
        explain.to_edge(DOWN, buff=0.3)
        self.play(Write(explain), run_time=1)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


# ===== Part 7: The Teaser for Solution =====
class Part7Teaser(Scene):
    """Part 7: The Teaser for Solution (5-10 sec)"""
    def construct(self):
        # 问号
        question = Tex(
            "So how do we fix this?",
            font_size=48, color=WHITE
        )
        question.shift(UP * 0.5)

        self.play(Write(question), run_time=1)

        self.wait(0.8)

        # 解决方案提示
        solutions = VGroup(
            Tex(r"$\rightarrow$ Entropy Regularization", font_size=32, color=FORMULA_COLOR),
            Tex(r"$\rightarrow$ KL Divergence", font_size=32, color=FORMULA_COLOR),
        )
        solutions.arrange(DOWN, buff=0.3)
        solutions.next_to(question, DOWN, buff=0.8)

        self.play(
            LaggedStart(*[FadeIn(s, shift=LEFT * 0.3) for s in solutions], lag_ratio=0.3),
            run_time=1.2
        )

        # Coming up
        coming_up = Tex(
            "Coming up next...",
            font_size=24, color=GREY_B
        )
        coming_up.to_edge(DOWN, buff=0.8)
        self.play(Write(coming_up), run_time=0.6)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


# ===== 完整动画: SelfReinforcementCollapse =====
class SelfReinforcementCollapse(Scene):
    """完整的 Self-Reinforcement Collapse 动画"""
    def construct(self):
        # Part 1: Setting Up the Visualization
        self.part1_setup()

        # Part 2: The Collapse Happens
        self.part2_collapse()

        # Part 3: The False Hope
        self.part3_false_hope()

        # Part 4: How Training Works
        self.part4_training_loop()

        # Part 5: The Vicious Cycle
        self.part5_vicious_cycle()

        # Part 6: Back to the Evidence
        self.part6_evidence()

        # Part 7: The Teaser for Solution
        self.part7_teaser()

    def part1_setup(self):
        """Part 1: Setting Up the Visualization"""
        title = Tex("Self-Reinforcement Collapse", font_size=38, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.8)

        narration = Tex("Training Iterations vs Exit Probability", font_size=22, color=GREY_B)
        narration.next_to(title, DOWN, buff=0.15)
        self.play(Write(narration), run_time=0.6)

        # 坐标轴
        axes = Axes(
            x_range=[0, 180, 30], y_range=[0, 1.1, 0.2],
            x_length=8, y_length=4,
            axis_config={"color": GREY_B, "include_tip": True},
            x_axis_config={"numbers_to_include": [0, 60, 120, 180]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        axes.shift(DOWN * 0.4 + LEFT * 0.5)

        x_label = Tex("Training Iterations", font_size=18, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.4)
        y_label = MathTex(r"p_\theta(t|x)", font_size=18, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.15)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1)

        # 图例
        legend = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(color=color, radius=0.05)
            dot.shift(RIGHT * 4.5 + UP * (1.5 - i * 0.3))
            label = Tex(f"t={i+1}", font_size=12, color=color)
            label.next_to(dot, RIGHT, buff=0.08)
            legend.add(dot, label)
        self.play(FadeIn(legend), run_time=0.5)

        # 初始点
        initial_dots = VGroup()
        for color in DEPTH_COLORS:
            dot = Dot(axes.c2p(0, 0.2), color=color, radius=0.05)
            initial_dots.add(dot)

        self.play(
            LaggedStart(*[FadeIn(d, scale=1.3) for d in initial_dots], lag_ratio=0.08),
            run_time=0.6
        )

        explain = Tex("All depths start with similar probabilities (~0.2)", font_size=18, color=GREY_B)
        explain.to_edge(DOWN, buff=0.4)
        self.play(Write(explain), run_time=0.6)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def part2_collapse(self):
        """Part 2: The Collapse Happens"""
        title = Tex("The Collapse Happens", font_size=32, color=WARNING_COLOR)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.6)

        # 坐标轴
        axes = Axes(
            x_range=[0, 180, 30], y_range=[0, 1.1, 0.2],
            x_length=8, y_length=4,
            axis_config={"color": GREY_B, "include_tip": True},
            x_axis_config={"numbers_to_include": [0, 60, 120, 180]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        axes.shift(DOWN * 0.4 + LEFT * 0.5)

        x_label = Tex("Training Iterations", font_size=18, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.4)
        y_label = MathTex(r"p_\theta(t|x)", font_size=18, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.15)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.8)

        # 图例
        legend = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(color=color, radius=0.05)
            dot.shift(RIGHT * 4.5 + UP * (1.5 - i * 0.3))
            label = Tex(f"t={i+1}", font_size=12, color=color)
            label.next_to(dot, RIGHT, buff=0.08)
            legend.add(dot, label)
        self.play(FadeIn(legend), run_time=0.4)

        # 概率曲线
        def prob_curve(t_depth, x):
            if t_depth < 5:
                initial = 0.2
                decay_rate = 0.02 + (t_depth - 1) * 0.005
                return initial * np.exp(-decay_rate * x)
            else:
                midpoint = 80
                steepness = 0.05
                return 0.2 + 0.8 / (1 + np.exp(-steepness * (x - midpoint)))

        progress = ValueTracker(0)

        dynamic_curves = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            def get_curve(i=i, color=color):
                x_max = progress.get_value()
                if x_max <= 0:
                    return VectorizedPoint(axes.c2p(0, prob_curve(i+1, 0)))
                curve = axes.plot(
                    lambda x, t=i+1: prob_curve(t, x),
                    x_range=[0, x_max],
                    color=color,
                    stroke_width=2.5
                )
                return curve
            dynamic_curve = always_redraw(get_curve)
            dynamic_curves.add(dynamic_curve)

        self.add(dynamic_curves)
        self.play(progress.animate.set_value(180), run_time=4, rate_func=linear)

        # 高亮
        highlight = Circle(radius=0.25, color=CELEBRATE_COLOR, stroke_width=3)
        highlight.move_to(axes.c2p(180, 1.0))

        badge = VGroup()
        badge_rect = RoundedRectangle(width=3, height=0.6, corner_radius=0.08, color=CELEBRATE_COLOR, fill_opacity=0.2, stroke_width=2)
        badge_text = Tex(r"t=5 dominates: $p$=1.0", font_size=16, color=CELEBRATE_COLOR)
        badge_text.move_to(badge_rect.get_center())
        badge.add(badge_rect, badge_text)
        badge.shift(RIGHT * 3 + DOWN * 1.5)

        self.play(Create(highlight), FadeIn(badge), run_time=0.6)

        explain = Tex("Final loop dominates everything!", font_size=20, color=WARNING_COLOR)
        explain.to_edge(DOWN, buff=0.4)
        self.play(Write(explain), run_time=0.6)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def part3_false_hope(self):
        """Part 3: The False Hope"""
        # 庆祝
        celebrate = Tex("SOLVED DEEP LEARNING?", font_size=42, color=CELEBRATE_COLOR)
        celebrate.shift(UP * 0.8)
        self.play(FadeIn(celebrate, scale=1.3), run_time=0.6)

        question = Tex("Are we geniuses?", font_size=26, color=WHITE)
        question.next_to(celebrate, DOWN, buff=0.4)
        self.play(Write(question), run_time=0.6)

        self.wait(0.5)

        # 划掉
        cross1 = Line(celebrate.get_corner(UL) + LEFT*0.2 + UP*0.1, celebrate.get_corner(DR) + RIGHT*0.2 + DOWN*0.1, color=WARNING_COLOR, stroke_width=6)
        cross2 = Line(celebrate.get_corner(UR) + RIGHT*0.2 + UP*0.1, celebrate.get_corner(DL) + LEFT*0.2 + DOWN*0.1, color=WARNING_COLOR, stroke_width=6)

        nope = Tex(r"\textbf{Nope.}", font_size=50, color=WARNING_COLOR)
        nope.shift(DOWN * 1.2)

        self.play(
            celebrate.animate.set_opacity(0.3),
            question.animate.set_opacity(0.3),
            Create(cross1), Create(cross2),
            run_time=0.5
        )
        self.play(FadeIn(nope, scale=1.3), run_time=0.4)

        but_text = Tex("That's not quite the case...", font_size=22, color=GREY_B)
        but_text.next_to(nope, DOWN, buff=0.3)
        self.play(Write(but_text), run_time=0.6)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def part4_training_loop(self):
        """Part 4: How Training Works"""
        title = Tex("How Training Works", font_size=32, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.6)

        # Loop 方块
        loops = VGroup()
        for i in range(5):
            loop = LoopBlock(f"L{i+1}", scale_factor=0.7)
            loops.add(loop)
        loops.arrange(RIGHT, buff=0.5)
        loops.shift(UP * 1.3)

        loop_arrows = VGroup()
        for i in range(4):
            arrow = Arrow(loops[i].get_right() + RIGHT*0.03, loops[i+1].get_left() + LEFT*0.03, color=GREY_B, stroke_width=2, buff=0)
            loop_arrows.add(arrow)

        self.play(
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.08),
            LaggedStart(*[GrowArrow(a) for a in loop_arrows], lag_ratio=0.08),
            run_time=1
        )

        # Loss boxes
        loss_boxes = VGroup()
        for i in range(5):
            loss = LossBox(f"L_{i+1}", scale_factor=0.8)
            loss.next_to(loops[i], DOWN, buff=0.6)
            loss_boxes.add(loss)

        self.play(
            LaggedStart(*[FadeIn(l, scale=1.1) for l in loss_boxes], lag_ratio=0.08),
            run_time=0.8
        )

        explain = Tex("Loss computed at EVERY step, weighted by exit probability", font_size=18, color=GREY_B)
        explain.to_edge(DOWN, buff=1.8)
        self.play(Write(explain), run_time=0.6)

        # 公式
        formula = MathTex(r"\mathcal{L} = \sum_{n=1}^{N} p_n \cdot L^{(n)}", font_size=30, color=FORMULA_COLOR)
        formula.to_edge(DOWN, buff=0.8)
        formula_box = SurroundingRectangle(formula, color=FORMULA_COLOR, buff=0.12)
        self.play(Write(formula), Create(formula_box), run_time=0.8)

        # 概率标签
        probs = [0.15, 0.15, 0.15, 0.15, 0.40]
        prob_labels = VGroup()
        for i, p in enumerate(probs):
            label = MathTex(f"p_{i+1}={p:.2f}", font_size=12, color=HIGHLIGHT_COLOR)
            label.next_to(loss_boxes[i], DOWN, buff=0.08)
            prob_labels.add(label)

        self.play(LaggedStart(*[Write(l) for l in prob_labels], lag_ratio=0.06), run_time=0.6)

        # 缩放显示权重
        scales = [0.65, 0.65, 0.65, 0.65, 1.15]
        self.play(*[loss_boxes[i].animate.scale(s) for i, s in enumerate(scales)], run_time=0.8)

        explain2 = Tex(r"Higher $p$ $\rightarrow$ dominates weight updates", font_size=16, color=GREY_B)
        explain2.next_to(formula_box, UP, buff=0.2)
        self.play(Write(explain2), run_time=0.5)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def part5_vicious_cycle(self):
        """Part 5: The Vicious Cycle"""
        title = Tex("The Vicious Cycle", font_size=32, color=WARNING_COLOR)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.6)

        # 初始 gates
        gates = VGroup()
        for i in range(5):
            rect = RoundedRectangle(width=1, height=0.6, corner_radius=0.08, color=DEPTH_COLORS[i], fill_opacity=0.3, stroke_width=2)
            label = MathTex(f"p_{i+1}", font_size=18, color=WHITE)
            label.move_to(rect.get_center())
            gate = VGroup(rect, label)
            gates.add(gate)
        gates.arrange(RIGHT, buff=0.3)
        gates.shift(UP * 1.5)

        probs = [0.20, 0.20, 0.20, 0.20, 0.20]
        prob_labels = VGroup()
        for i, (g, p) in enumerate(zip(gates, probs)):
            label = MathTex(f"{p:.2f}", font_size=14, color=GREY_B)
            label.next_to(g, DOWN, buff=0.1)
            prob_labels.add(label)

        self.play(
            LaggedStart(*[FadeIn(g) for g in gates], lag_ratio=0.06),
            LaggedStart(*[Write(l) for l in prob_labels], lag_ratio=0.06),
            run_time=0.8
        )

        explain = Tex("One gate randomly increases...", font_size=18, color=HIGHLIGHT_COLOR)
        explain.to_edge(DOWN, buff=2)
        self.play(Write(explain), run_time=0.5)

        # t=5 增加
        new_prob = MathTex("0.25", font_size=14, color=CELEBRATE_COLOR)
        new_prob.move_to(prob_labels[4].get_center())
        highlight = SurroundingRectangle(gates[4], color=CELEBRATE_COLOR, buff=0.08)

        self.play(
            Transform(prob_labels[4], new_prob),
            Create(highlight),
            gates[4][0].animate.set_stroke(CELEBRATE_COLOR, width=3),
            run_time=0.6
        )

        self.wait(0.8)

        # 切换到循环图
        self.play(FadeOut(gates), FadeOut(prob_labels), FadeOut(highlight), FadeOut(explain), run_time=0.4)

        # 循环图
        cycle_center = ORIGIN + DOWN * 0.2
        cycle_r = 1.8

        node_data = [
            (r"Gate $\uparrow$", CELEBRATE_COLOR),
            (r"More Gradient", GRADIENT_COLOR),
            (r"Loss $\downarrow$", LOSS_COLOR),
            (r"Gate $\uparrow\uparrow$", WARNING_COLOR),
        ]

        nodes = VGroup()
        for i, (text, color) in enumerate(node_data):
            angle = PI/2 - i * PI/2
            pos = cycle_center + cycle_r * np.array([np.cos(angle), np.sin(angle), 0])
            rect = RoundedRectangle(width=1.8, height=0.7, corner_radius=0.1, color=color, fill_opacity=0.2, stroke_width=2)
            rect.move_to(pos)
            txt = Tex(text, font_size=16, color=WHITE)
            txt.move_to(pos)
            nodes.add(VGroup(rect, txt))

        cycle_arrows = VGroup()
        for i in range(4):
            start_angle = PI/2 - i * PI/2
            end_angle = PI/2 - ((i+1) % 4) * PI/2
            start_pos = cycle_center + (cycle_r - 0.5) * np.array([np.cos(start_angle - 0.25), np.sin(start_angle - 0.25), 0])
            end_pos = cycle_center + (cycle_r - 0.5) * np.array([np.cos(end_angle + 0.25), np.sin(end_angle + 0.25), 0])
            arrow = CurvedArrow(start_pos, end_pos, color=GREY_B, stroke_width=2, angle=-PI/3)
            cycle_arrows.add(arrow)

        self.play(
            LaggedStart(*[FadeIn(n, scale=0.8) for n in nodes], lag_ratio=0.15),
            run_time=1
        )
        self.play(
            LaggedStart(*[Create(a) for a in cycle_arrows], lag_ratio=0.15),
            run_time=0.8
        )

        center_label = Tex(r"Dominant: $t=5$", font_size=16, color=CELEBRATE_COLOR)
        center_label.move_to(cycle_center)
        self.play(Write(center_label), run_time=0.4)

        # 闪烁
        self.play(*[a.animate.set_color(WARNING_COLOR) for a in cycle_arrows], run_time=0.3)
        self.play(*[a.animate.set_color(GREY_B) for a in cycle_arrows], run_time=0.3)

        # 警告
        warning = VGroup()
        w_rect = Rectangle(width=9, height=0.6, color=WARNING_COLOR, fill_opacity=0.2, stroke_width=2)
        w_rect.to_edge(DOWN, buff=0.3)
        w_text = Tex(r"\textbf{WARNING:} Without regularization, model collapses to single depth!", font_size=16, color=WARNING_COLOR)
        w_text.move_to(w_rect.get_center())
        warning.add(w_rect, w_text)

        self.play(FadeIn(warning, shift=UP*0.2), run_time=0.5)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def part6_evidence(self):
        """Part 6: Back to the Evidence"""
        title = Tex("Observing the Collapse", font_size=32, color=WHITE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title), run_time=0.6)

        # 坐标轴
        axes = Axes(
            x_range=[0, 180, 30], y_range=[0, 1.1, 0.2],
            x_length=7.5, y_length=3.8,
            axis_config={"color": GREY_B, "include_tip": True},
            x_axis_config={"numbers_to_include": [0, 60, 120, 180]},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0]},
        )
        axes.shift(DOWN * 0.5 + LEFT * 0.3)

        x_label = Tex("Training Iterations", font_size=16, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.35)
        y_label = MathTex(r"p_\theta(t|x)", font_size=16, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.1)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.8)

        # 图例
        legend = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            dot = Dot(color=color, radius=0.04)
            dot.shift(RIGHT * 4.3 + UP * (1.3 - i * 0.25))
            label = Tex(f"t={i+1}", font_size=10, color=color)
            label.next_to(dot, RIGHT, buff=0.06)
            legend.add(dot, label)
        self.play(FadeIn(legend), run_time=0.3)

        def prob_curve(t_depth, x):
            if t_depth < 5:
                initial = 0.2
                decay_rate = 0.02 + (t_depth - 1) * 0.005
                return initial * np.exp(-decay_rate * x)
            else:
                midpoint = 80
                steepness = 0.05
                return 0.2 + 0.8 / (1 + np.exp(-steepness * (x - midpoint)))

        progress = ValueTracker(0)

        dynamic_curves = VGroup()
        for i, color in enumerate(DEPTH_COLORS):
            def get_curve(i=i, color=color):
                x_max = progress.get_value()
                if x_max <= 0:
                    return VectorizedPoint(axes.c2p(0, prob_curve(i+1, 0)))
                curve = axes.plot(
                    lambda x, t=i+1: prob_curve(t, x),
                    x_range=[0, x_max],
                    color=color,
                    stroke_width=2
                )
                return curve
            dynamic_curve = always_redraw(get_curve)
            dynamic_curves.add(dynamic_curve)

        self.add(dynamic_curves)

        # 标注
        early_note = Tex("First batch favored t=5", font_size=14, color=CELEBRATE_COLOR)
        early_note.shift(LEFT * 2.5 + UP * 2)
        early_arrow = Arrow(early_note.get_bottom(), axes.c2p(20, 0.28), color=CELEBRATE_COLOR, stroke_width=1.5)

        self.play(progress.animate.set_value(40), run_time=1.2, rate_func=linear)
        self.play(Write(early_note), GrowArrow(early_arrow), run_time=0.5)

        self.play(progress.animate.set_value(100), run_time=1.5, rate_func=linear)

        mid_note = Tex("Self-reinforcement", font_size=14, color=WARNING_COLOR)
        mid_note.shift(RIGHT * 0.5 + UP * 2)
        mid_arrow = Arrow(mid_note.get_bottom(), axes.c2p(80, 0.55), color=WARNING_COLOR, stroke_width=1.5)
        self.play(Write(mid_note), GrowArrow(mid_arrow), run_time=0.5)

        self.play(progress.animate.set_value(180), run_time=1.2, rate_func=linear)

        # 结论
        final_label = VGroup()
        final_rect = RoundedRectangle(width=2.8, height=0.5, corner_radius=0.08, color=WARNING_COLOR, fill_opacity=0.2, stroke_width=2)
        final_text = Tex("Probability Collapse", font_size=14, color=WARNING_COLOR)
        final_text.move_to(final_rect.get_center())
        final_label.add(final_rect, final_text)
        final_label.shift(RIGHT * 3.2 + DOWN * 1.8)
        self.play(FadeIn(final_label), run_time=0.4)

        explain = Tex("Whichever loop exits first in the first batch dominates training", font_size=16, color=GREY_B)
        explain.to_edge(DOWN, buff=0.3)
        self.play(Write(explain), run_time=0.6)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def part7_teaser(self):
        """Part 7: The Teaser for Solution"""
        question = Tex("So how do we fix this?", font_size=42, color=WHITE)
        question.shift(UP * 0.5)
        self.play(Write(question), run_time=0.8)

        self.wait(0.6)

        solutions = VGroup(
            Tex(r"$\rightarrow$ Entropy Regularization", font_size=28, color=FORMULA_COLOR),
            Tex(r"$\rightarrow$ KL Divergence", font_size=28, color=FORMULA_COLOR),
        )
        solutions.arrange(DOWN, buff=0.25)
        solutions.next_to(question, DOWN, buff=0.6)

        self.play(
            LaggedStart(*[FadeIn(s, shift=LEFT*0.2) for s in solutions], lag_ratio=0.25),
            run_time=1
        )

        coming_up = Tex("Coming up next...", font_size=20, color=GREY_B)
        coming_up.to_edge(DOWN, buff=0.6)
        self.play(Write(coming_up), run_time=0.5)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("Self-Reinforcement Collapse - Manim Animation")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql self_reinforcement_collapse.py SelfReinforcementCollapse")
    print("  高质量:   manim -pqh self_reinforcement_collapse.py SelfReinforcementCollapse")
    print("\n单独场景:")
    print("  manim -pql self_reinforcement_collapse.py Part1Setup")
    print("  manim -pql self_reinforcement_collapse.py Part2Collapse")
    print("  manim -pql self_reinforcement_collapse.py Part3FalseHope")
    print("  manim -pql self_reinforcement_collapse.py Part4TrainingLoop")
    print("  manim -pql self_reinforcement_collapse.py Part5ViciousCycle")
    print("  manim -pql self_reinforcement_collapse.py Part6Evidence")
    print("  manim -pql self_reinforcement_collapse.py Part7Teaser")
    print("=" * 60)

