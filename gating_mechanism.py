"""
Adaptive Exit Gate Mechanism 可视化动画
运行命令:
  完整动画: manim -pql gating_mechanism.py GatingMechanism
  单独场景: manim -pql gating_mechanism.py IntroScene
           manim -pql gating_mechanism.py StepByStepScene
           manim -pql gating_mechanism.py WhyNotProbDistScene  (新增!)
           manim -pql gating_mechanism.py ProbabilityDistScene
           manim -pql gating_mechanism.py CDFThresholdScene
           manim -pql gating_mechanism.py SummaryScene
  高质量渲染: manim -pqh gating_mechanism.py GatingMechanism
"""

from manim import *
import numpy as np

# 颜色配置
EXIT_COLOR = "#E74C3C"      # 红色 - 退出
SURVIVE_COLOR = "#2ECC71"   # 绿色 - 继续
HIGHLIGHT_COLOR = "#F39C12" # 橙色 - 高亮
LOOP_COLOR = "#3498DB"      # 蓝色 - Loop方块
FORMULA_COLOR = "#9B59B6"   # 紫色 - 公式

class LoopBlock(VGroup):
    """可复用的 Loop 方块组件"""
    def __init__(self, label_text, **kwargs):
        super().__init__(**kwargs)
        self.rect = RoundedRectangle(
            height=1.2, width=1.5,
            corner_radius=0.15,
            color=LOOP_COLOR,
            fill_opacity=0.3,
            stroke_width=3
        )
        self.label = Text(label_text, font_size=28, color=WHITE)
        self.label.move_to(self.rect.get_center())
        self.add(self.rect, self.label)

    def highlight(self, color=HIGHLIGHT_COLOR):
        return self.rect.animate.set_stroke(color=color, width=5)

    def unhighlight(self):
        return self.rect.animate.set_stroke(color=LOOP_COLOR, width=3)


class ProbabilityBar(VGroup):
    """概率条组件 - 显示退出/继续概率"""
    def __init__(self, exit_prob, width=1.5, height=0.3, **kwargs):
        super().__init__(**kwargs)
        self.exit_prob = exit_prob
        self.survive_prob = 1 - exit_prob

        # 退出部分（红色）
        self.exit_bar = Rectangle(
            height=height, width=width * exit_prob,
            color=EXIT_COLOR, fill_opacity=0.8,
            stroke_width=0
        )

        # 继续部分（绿色）
        self.survive_bar = Rectangle(
            height=height, width=width * self.survive_prob,
            color=SURVIVE_COLOR, fill_opacity=0.8,
            stroke_width=0
        )

        # 排列
        self.exit_bar.move_to(ORIGIN)
        self.survive_bar.next_to(self.exit_bar, RIGHT, buff=0)

        # 整体居中
        bars = VGroup(self.exit_bar, self.survive_bar)
        bars.move_to(ORIGIN)

        self.add(self.exit_bar, self.survive_bar)


class IntroScene(Scene):
    """Scene 1: 问题引入"""
    def construct(self):
        # 标题
        title = Text("Why can't we just use Softmax?", font_size=42, color=WHITE)
        title.to_edge(UP, buff=0.5)

        # 创建4个 Loop 方块
        loops = VGroup(*[LoopBlock(f"Loop {i+1}") for i in range(4)])
        loops.arrange(RIGHT, buff=0.8)
        loops.shift(UP * 0.5)

        # 箭头连接
        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops[i].get_right(),
                loops[i+1].get_left(),
                buff=0.1,
                color=GREY_B,
                stroke_width=3
            )
            arrows.add(arrow)

        # 问号标签
        question_marks = VGroup()
        for loop in loops:
            qmark = Text("?", font_size=36, color=HIGHLIGHT_COLOR)
            qmark.next_to(loop, UP, buff=0.3)
            question_marks.add(qmark)

        # Sigmoid 输出标签（占位）
        sigma_labels = VGroup()
        for i, loop in enumerate(loops):
            sigma = MathTex(r"\sigma_" + str(i+1) + " = ?", font_size=28)
            sigma.next_to(loop, UP, buff=0.3)
            sigma_labels.add(sigma)

        # 问题说明文字
        problem_text = Text(
            "We can't forecast the future —\nwe don't know P(exit at loop 1) until all loops complete",
            font_size=26,
            color=GREY_B,
            line_spacing=1.2
        )
        problem_text.to_edge(DOWN, buff=1)

        # ===== 动画序列 =====
        self.play(Write(title), run_time=1)
        self.wait(0.5)

        # 依次显示 Loop 方块
        for i, loop in enumerate(loops):
            if i > 0:
                self.play(
                    FadeIn(loop, shift=RIGHT*0.3),
                    GrowArrow(arrows[i-1]),
                    run_time=0.5
                )
            else:
                self.play(FadeIn(loop, shift=RIGHT*0.3), run_time=0.5)

        self.wait(0.3)

        # 显示问号
        self.play(
            LaggedStart(*[FadeIn(qm, scale=1.5) for qm in question_marks], lag_ratio=0.2),
            run_time=1
        )

        self.wait(0.5)

        # 显示问题文字
        self.play(Write(problem_text), run_time=2)
        self.wait(2)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class StepByStepScene(Scene):
    """Scene 2: Step-by-Step 概率计算"""
    def construct(self):
        # 标题
        title = Text("Step-by-Step Probability Calculation", font_size=36)
        title.to_edge(UP, buff=0.4)

        # Lambda 值设定
        lambdas = [0.3, 0.5, 0.4, None]  # 最后一个是强制退出

        # 创建4个 Loop 方块
        loops = VGroup(*[LoopBlock(f"Loop {i+1}") for i in range(4)])
        loops.arrange(RIGHT, buff=0.8)
        loops.shift(UP * 1.5)

        # 箭头连接
        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops[i].get_right(),
                loops[i+1].get_left(),
                buff=0.1,
                color=SURVIVE_COLOR,
                stroke_width=3
            )
            arrows.add(arrow)

        # 概率条位置（在 loops 下方）
        prob_bar_group = VGroup()

        # ===== 动画序列 =====
        self.play(Write(title))
        self.play(
            LaggedStart(*[FadeIn(loop) for loop in loops], lag_ratio=0.15),
            LaggedStart(*[GrowArrow(arrow) for arrow in arrows], lag_ratio=0.15),
            run_time=1.5
        )

        # 追踪累计生存概率和无条件退出概率
        survival_prob = 1.0
        unconditional_probs = []

        # ===== Step 2a: Loop 1 =====
        self.play(loops[0].highlight())

        # Sigmoid 动画
        sigma_text = MathTex(r"\sigma(x) \rightarrow \lambda_1 = 0.3", font_size=30)
        sigma_text.next_to(loops[0], DOWN, buff=0.5)
        self.play(Write(sigma_text), run_time=1)

        # 概率条
        prob_bar_1 = ProbabilityBar(0.3, width=2, height=0.35)
        prob_bar_1.next_to(sigma_text, DOWN, buff=0.4)

        exit_label_1 = Text("Exit: 0.3", font_size=20, color=EXIT_COLOR)
        survive_label_1 = Text("Survive: 0.7", font_size=20, color=SURVIVE_COLOR)
        exit_label_1.next_to(prob_bar_1.exit_bar, DOWN, buff=0.15)
        survive_label_1.next_to(prob_bar_1.survive_bar, DOWN, buff=0.15)

        self.play(
            FadeIn(prob_bar_1.exit_bar, shift=UP*0.2),
            FadeIn(prob_bar_1.survive_bar, shift=UP*0.2),
            run_time=0.8
        )
        self.play(Write(exit_label_1), Write(survive_label_1), run_time=0.6)

        # 说明文字
        explain_1 = Text("Unconditional exit probability = 0.3", font_size=24, color=GREY_B)
        explain_1.to_edge(DOWN, buff=0.8)
        self.play(Write(explain_1))

        survival_prob = 0.7
        unconditional_probs.append(0.3)

        self.wait(1.5)
        self.play(
            FadeOut(sigma_text), FadeOut(prob_bar_1),
            FadeOut(exit_label_1), FadeOut(survive_label_1),
            FadeOut(explain_1),
            loops[0].unhighlight()
        )

        # ===== Step 2b: Loop 2 =====
        # 显示生存流动
        flow_arrow = Arrow(
            loops[0].get_bottom() + DOWN*0.3,
            loops[1].get_bottom() + DOWN*0.3,
            color=SURVIVE_COLOR, stroke_width=4
        )
        flow_label = Text("Surviving 70%", font_size=20, color=SURVIVE_COLOR)
        flow_label.next_to(flow_arrow, DOWN, buff=0.1)

        self.play(GrowArrow(flow_arrow), Write(flow_label), run_time=0.8)
        self.play(loops[1].highlight())

        # Sigmoid 输出
        sigma_text_2 = MathTex(r"\lambda_2 = 0.5", font_size=30)
        sigma_text_2.next_to(loops[1], DOWN, buff=0.5)
        self.play(Write(sigma_text_2))

        # 条件概率说明
        cond_prob = MathTex(
            r"P(\text{exit at } L_2 \mid \text{survived } L_1) = 0.5",
            font_size=26
        )
        cond_prob.next_to(sigma_text_2, DOWN, buff=0.4)
        self.play(Write(cond_prob))

        # 无条件概率计算
        formula_box = VGroup()
        formula_line1 = MathTex(
            r"P(\text{exit at } L_2) = P(\text{survive } L_1) \times P(\text{exit} \mid \text{survive})",
            font_size=24
        )
        formula_line2 = MathTex(
            r"= 0.7 \times 0.5 = 0.35",
            font_size=28, color=HIGHLIGHT_COLOR
        )
        formula_line1.to_edge(DOWN, buff=1.2)
        formula_line2.next_to(formula_line1, DOWN, buff=0.2)

        self.play(Write(formula_line1), run_time=1)
        self.play(Write(formula_line2), run_time=1)

        unconditional_probs.append(0.35)
        survival_prob = 0.7 * 0.5  # 0.35

        self.wait(1.5)
        self.play(
            FadeOut(flow_arrow), FadeOut(flow_label),
            FadeOut(sigma_text_2), FadeOut(cond_prob),
            FadeOut(formula_line1), FadeOut(formula_line2),
            loops[1].unhighlight()
        )

        # ===== Step 2c: Loop 3 =====
        flow_arrow_2 = Arrow(
            loops[1].get_bottom() + DOWN*0.3,
            loops[2].get_bottom() + DOWN*0.3,
            color=SURVIVE_COLOR, stroke_width=4
        )
        flow_label_2 = Text("Surviving 35%", font_size=20, color=SURVIVE_COLOR)
        flow_label_2.next_to(flow_arrow_2, DOWN, buff=0.1)

        self.play(GrowArrow(flow_arrow_2), Write(flow_label_2), run_time=0.8)
        self.play(loops[2].highlight())

        sigma_text_3 = MathTex(r"\lambda_3 = 0.4", font_size=30)
        sigma_text_3.next_to(loops[2], DOWN, buff=0.5)
        self.play(Write(sigma_text_3))

        formula_line1_3 = MathTex(
            r"P(\text{exit at } L_3) = 0.35 \times 0.4 = 0.14",
            font_size=26, color=HIGHLIGHT_COLOR
        )
        formula_line1_3.to_edge(DOWN, buff=1)
        self.play(Write(formula_line1_3))

        unconditional_probs.append(0.14)
        survival_prob = 0.35 * 0.6  # 0.21

        self.wait(1.5)
        self.play(
            FadeOut(flow_arrow_2), FadeOut(flow_label_2),
            FadeOut(sigma_text_3), FadeOut(formula_line1_3),
            loops[2].unhighlight()
        )

        # ===== Step 2d: Loop 4 (强制退出) =====
        self.play(loops[3].highlight())

        # 计算剩余概率
        remaining = 1 - sum(unconditional_probs)  # 0.21
        remaining_text = MathTex(
            r"\text{Remaining mass} = 1 - (0.3 + 0.35 + 0.14) = 0.21",
            font_size=26
        )
        remaining_text.next_to(loops[3], DOWN, buff=0.5)
        self.play(Write(remaining_text))

        # 动画：将剩余质量"倾倒"到 Loop 4
        pour_arrow = Arrow(UP*0.5, DOWN*0.5, color=EXIT_COLOR, stroke_width=4)
        pour_arrow.next_to(loops[3], UP, buff=0.2)

        final_text = Text("Forced exit: 0.21", font_size=24, color=EXIT_COLOR)
        final_text.to_edge(DOWN, buff=1)

        self.play(GrowArrow(pour_arrow))
        self.play(Write(final_text))
        self.play(FadeOut(pour_arrow))

        unconditional_probs.append(0.21)

        self.wait(2)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class WhyNotProbDistScene(Scene):
    """Scene 2.5: 为什么不保证是概率分布？"""
    def construct(self):
        # Part A: 数学直觉 - 无穷级数
        self.part_a_math_intuition()

        # Part B: Case 1 - λ 太小
        self.part_b_lambda_too_small()

        # Part C: Case 2 - λ 太大
        self.part_c_lambda_too_large()

        # Part D: 解决方案
        self.part_d_solution()

    def part_a_math_intuition(self):
        """Part A: 数学直觉 - 无穷 vs 有限"""
        title = Text("Why might Σp̃ₜ ≠ 1?", font_size=42)
        title.to_edge(UP, buff=0.5)

        self.play(Write(title), run_time=1)

        # 无穷级数公式
        infinite_formula = MathTex(
            r"\text{If } T_{max} \to \infty \text{ and } \lambda_t = \lambda:",
            font_size=30
        )
        infinite_formula.shift(UP * 1.5)

        series_formula = MathTex(
            r"\sum_{t=1}^{\infty} \tilde{p}_t = \sum_{t=1}^{\infty} \lambda(1-\lambda)^{t-1} = 1",
            font_size=36, color=SURVIVE_COLOR
        )
        series_formula.next_to(infinite_formula, DOWN, buff=0.5)

        self.play(Write(infinite_formula), run_time=1)
        self.play(Write(series_formula), run_time=1.5)

        # 说明文字
        explain_text = Text(
            "In the infinite case, geometric series sums to 1",
            font_size=26, color=GREY_B
        )
        explain_text.next_to(series_formula, DOWN, buff=0.5)
        self.play(Write(explain_text))

        self.wait(1)

        # "但是..."的转折
        but_text = Text("But...", font_size=40, color=EXIT_COLOR)
        but_text.next_to(explain_text, DOWN, buff=0.6)
        self.play(Write(but_text), run_time=0.5)

        # 问题揭示
        problem_text = Text(
            "We only have Tmax steps!",
            font_size=32, color=EXIT_COLOR
        )
        problem_text.next_to(but_text, DOWN, buff=0.4)

        # 红色框强调
        problem_box = SurroundingRectangle(problem_text, color=EXIT_COLOR, buff=0.2)

        self.play(Write(problem_text), Create(problem_box), run_time=1)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part_b_lambda_too_small(self):
        """Part B: Case 1 - λ 太小导致概率泄漏"""
        title = Text("Case 1: λ too small → Probability Leakage", font_size=34, color=EXIT_COLOR)
        title.to_edge(UP, buff=0.4)

        self.play(Write(title), run_time=1)

        # 设置场景说明
        setup_text = MathTex(
            r"\lambda_1 = \lambda_2 = \lambda_3 = \lambda_4 = 0.1",
            font_size=30
        )
        setup_text.shift(UP * 2)
        self.play(Write(setup_text))

        # 创建4个小 Loop 方块
        loops = VGroup(*[LoopBlock(f"L{i+1}") for i in range(4)])
        loops.arrange(RIGHT, buff=0.5)
        loops.scale(0.7)
        loops.shift(UP * 0.8)

        # 每个 loop 下方显示 λ=0.1
        lambda_labels = VGroup()
        for loop in loops:
            lbl = MathTex(r"\lambda=0.1", font_size=20)
            lbl.next_to(loop, DOWN, buff=0.15)
            lambda_labels.add(lbl)

        self.play(
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in lambda_labels], lag_ratio=0.1),
            run_time=1
        )

        # 计算过程
        calc_lines = VGroup(
            MathTex(r"\tilde{p}_1 = 0.1", font_size=26),
            MathTex(r"\tilde{p}_2 = 0.9 \times 0.1 = 0.09", font_size=26),
            MathTex(r"\tilde{p}_3 = 0.81 \times 0.1 = 0.081", font_size=26),
            MathTex(r"\tilde{p}_4 = 0.729 \times 0.1 = 0.073", font_size=26),
        )
        calc_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        calc_lines.shift(DOWN * 0.8 + LEFT * 2)

        for line in calc_lines:
            self.play(Write(line), run_time=0.5)

        # 分隔线
        sep_line = Line(LEFT * 1.5, RIGHT * 1.5, color=GREY_B)
        sep_line.next_to(calc_lines, DOWN, buff=0.15)
        self.play(Create(sep_line))

        # 求和结果
        sum_result = MathTex(
            r"\sum = 0.344 \ll 1",
            font_size=30, color=EXIT_COLOR
        )
        sum_result.next_to(sep_line, DOWN, buff=0.15)

        cross_mark = Text("❌", font_size=36, color=EXIT_COLOR)
        cross_mark.next_to(sum_result, RIGHT, buff=0.3)

        self.play(Write(sum_result), FadeIn(cross_mark, scale=1.5), run_time=1)

        # 概率桶可视化
        bucket_group = VGroup()

        # 桶的轮廓
        bucket_outline = Rectangle(
            height=3, width=1.2,
            color=WHITE, stroke_width=3, fill_opacity=0
        )
        bucket_outline.shift(RIGHT * 3.5)

        # 填充部分 (34.4%)
        filled_part = Rectangle(
            height=3 * 0.344, width=1.2,
            color=LOOP_COLOR, fill_opacity=0.7, stroke_width=0
        )
        filled_part.align_to(bucket_outline, DOWN)
        filled_part.shift(RIGHT * 3.5)

        # 空的部分标注
        empty_label = Text("65.6%\nempty!", font_size=18, color=EXIT_COLOR)
        empty_label.move_to(bucket_outline.get_center() + UP * 0.8)

        filled_label = Text("34.4%", font_size=18, color=WHITE)
        filled_label.move_to(filled_part.get_center())

        bucket_title = Text("Probability\nBucket", font_size=18, color=GREY_B)
        bucket_title.next_to(bucket_outline, UP, buff=0.2)

        self.play(
            Create(bucket_outline),
            Write(bucket_title),
            run_time=0.8
        )
        self.play(
            GrowFromEdge(filled_part, DOWN),
            Write(filled_label),
            run_time=1
        )
        self.play(Write(empty_label), run_time=0.5)

        # 剩余质量说明
        survival_text = MathTex(
            r"S_4 = 0.9^4 = 0.656",
            font_size=26, color=SURVIVE_COLOR
        )
        survival_text.to_edge(DOWN, buff=0.8)

        survival_explain = Text(
            '"Survival mass" that leaks beyond Tmax',
            font_size=22, color=GREY_B
        )
        survival_explain.next_to(survival_text, DOWN, buff=0.2)

        self.play(Write(survival_text), Write(survival_explain), run_time=1)

        # 问题总结
        problem_summary = Text(
            "Model too hesitant to exit → probability leaks!",
            font_size=24, color=EXIT_COLOR
        )
        problem_summary.next_to(survival_explain, DOWN, buff=0.3)
        self.play(Write(problem_summary))

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part_c_lambda_too_large(self):
        """Part C: Case 2 - λ 太大"""
        title = Text("Case 2: λ too large → Early Concentration", font_size=34, color=HIGHLIGHT_COLOR)
        title.to_edge(UP, buff=0.4)

        self.play(Write(title), run_time=1)

        # 设置场景说明
        setup_text = MathTex(
            r"\lambda_1 = \lambda_2 = \lambda_3 = \lambda_4 = 0.9",
            font_size=30
        )
        setup_text.shift(UP * 2)
        self.play(Write(setup_text))

        # 创建4个小 Loop 方块
        loops = VGroup(*[LoopBlock(f"L{i+1}") for i in range(4)])
        loops.arrange(RIGHT, buff=0.5)
        loops.scale(0.7)
        loops.shift(UP * 0.8)

        lambda_labels = VGroup()
        for loop in loops:
            lbl = MathTex(r"\lambda=0.9", font_size=20)
            lbl.next_to(loop, DOWN, buff=0.15)
            lambda_labels.add(lbl)

        self.play(
            LaggedStart(*[FadeIn(l) for l in loops], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in lambda_labels], lag_ratio=0.1),
            run_time=1
        )

        # 计算过程
        calc_lines = VGroup(
            MathTex(r"\tilde{p}_1 = 0.9", font_size=26),
            MathTex(r"\tilde{p}_2 = 0.1 \times 0.9 = 0.09", font_size=26),
            MathTex(r"\tilde{p}_3 = 0.01 \times 0.9 = 0.009", font_size=26),
            MathTex(r"\tilde{p}_4 = 0.001 \times 0.9 = 0.0009", font_size=26),
        )
        calc_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        calc_lines.shift(DOWN * 0.8 + LEFT * 2)

        for line in calc_lines:
            self.play(Write(line), run_time=0.4)

        # 分隔线
        sep_line = Line(LEFT * 1.8, RIGHT * 1.8, color=GREY_B)
        sep_line.next_to(calc_lines, DOWN, buff=0.15)
        self.play(Create(sep_line))

        # 求和结果
        sum_result = MathTex(
            r"\sum = 0.9999 \approx 1",
            font_size=30, color=SURVIVE_COLOR
        )
        sum_result.next_to(sep_line, DOWN, buff=0.15)

        check_mark = Text("✓", font_size=36, color=SURVIVE_COLOR)
        check_mark.next_to(sum_result, RIGHT, buff=0.3)

        self.play(Write(sum_result), FadeIn(check_mark, scale=1.5), run_time=1)

        # 概率桶可视化 - 几乎满了
        bucket_outline = Rectangle(
            height=3, width=1.2,
            color=WHITE, stroke_width=3, fill_opacity=0
        )
        bucket_outline.shift(RIGHT * 3.5)

        filled_part = Rectangle(
            height=3 * 0.9999, width=1.2,
            color=SURVIVE_COLOR, fill_opacity=0.7, stroke_width=0
        )
        filled_part.align_to(bucket_outline, DOWN)
        filled_part.shift(RIGHT * 3.5)

        filled_label = Text("≈100%", font_size=18, color=WHITE)
        filled_label.move_to(filled_part.get_center())

        bucket_title = Text("Probability\nBucket", font_size=18, color=GREY_B)
        bucket_title.next_to(bucket_outline, UP, buff=0.2)

        self.play(
            Create(bucket_outline),
            Write(bucket_title),
            run_time=0.8
        )
        self.play(
            GrowFromEdge(filled_part, DOWN),
            Write(filled_label),
            run_time=1
        )

        # 说明文字
        explain_text = Text(
            "Almost all mass at early steps, S₄ ≈ 0",
            font_size=24, color=GREY_B
        )
        explain_text.to_edge(DOWN, buff=1)
        self.play(Write(explain_text))

        note_text = Text(
            "This case is actually fine — no leaked probability!",
            font_size=22, color=SURVIVE_COLOR
        )
        note_text.next_to(explain_text, DOWN, buff=0.2)
        self.play(Write(note_text))

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def part_d_solution(self):
        """Part D: 解决方案 - 强制分配剩余质量"""
        title = Text("Solution: Force Exit at Final Step", font_size=36, color=SURVIVE_COLOR)
        title.to_edge(UP, buff=0.4)

        self.play(Write(title), run_time=1)

        # 回顾 Case 1 的问题
        problem_recap = Text("Recall Case 1: λ = 0.1", font_size=26, color=GREY_B)
        problem_recap.shift(UP * 2.2)
        self.play(Write(problem_recap))

        # 原始计算（左侧）
        original_title = Text("Before Fix", font_size=24, color=EXIT_COLOR)
        original_title.shift(UP * 1.5 + LEFT * 3)

        original_calc = VGroup(
            MathTex(r"p_1 = 0.1", font_size=24),
            MathTex(r"p_2 = 0.09", font_size=24),
            MathTex(r"p_3 = 0.081", font_size=24),
            MathTex(r"p_4 = 0.073", font_size=24, color=EXIT_COLOR),
            MathTex(r"\sum = 0.344", font_size=24, color=EXIT_COLOR),
        )
        original_calc.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        original_calc.next_to(original_title, DOWN, buff=0.3)

        self.play(Write(original_title))
        self.play(LaggedStart(*[Write(l) for l in original_calc], lag_ratio=0.15), run_time=1.5)

        # 箭头指向修复
        fix_arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, color=SURVIVE_COLOR, stroke_width=4)
        fix_arrow.shift(UP * 0.3)
        self.play(GrowArrow(fix_arrow))

        # 修复后的计算（右侧）
        fixed_title = Text("After Fix", font_size=24, color=SURVIVE_COLOR)
        fixed_title.shift(UP * 1.5 + RIGHT * 3)

        fixed_calc = VGroup(
            MathTex(r"p_1 = 0.1", font_size=24),
            MathTex(r"p_2 = 0.09", font_size=24),
            MathTex(r"p_3 = 0.081", font_size=24),
            MathTex(r"p_4 = S_3 = 0.729", font_size=24, color=SURVIVE_COLOR),
            MathTex(r"\sum = 1.0", font_size=24, color=SURVIVE_COLOR),
        )
        fixed_calc.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        fixed_calc.next_to(fixed_title, DOWN, buff=0.3)

        self.play(Write(fixed_title))

        # 逐行显示修复后的计算，高亮变化的行
        for i, (orig, fixed) in enumerate(zip(original_calc, fixed_calc)):
            if i < 3:
                self.play(Write(fixed), run_time=0.3)
            else:
                # 高亮显示关键变化
                self.play(Write(fixed), run_time=0.6)

        # 动画：将剩余质量"倾倒"到 Loop 4
        pour_text = Text("Assign remaining mass to L₄", font_size=22, color=HIGHLIGHT_COLOR)
        pour_text.next_to(fixed_calc[-2], RIGHT, buff=0.3)

        # 强调箭头指向 p_4
        highlight_arrow = Arrow(
            pour_text.get_left() + LEFT * 0.1,
            fixed_calc[3].get_right() + RIGHT * 0.1,
            color=HIGHLIGHT_COLOR, stroke_width=3
        )

        self.play(Write(pour_text), GrowArrow(highlight_arrow), run_time=0.8)

        # 显示最终公式
        self.wait(1)

        formula_box = VGroup()
        formula_title = Text("Final Formula:", font_size=26, color=WHITE)
        formula_title.to_edge(DOWN, buff=1.8)

        # 分段函数
        piecewise_formula = MathTex(
            r"p(t) = \begin{cases} "
            r"\tilde{p}_t = \lambda_t \cdot S_{t-1}, & t < T_{max} \\"
            r"S_{T_{max}-1}, & t = T_{max}"
            r"\end{cases}",
            font_size=28
        )
        piecewise_formula.next_to(formula_title, DOWN, buff=0.3)

        # 框住公式
        formula_rect = SurroundingRectangle(
            piecewise_formula, color=FORMULA_COLOR, buff=0.2
        )

        self.play(Write(formula_title), run_time=0.5)
        self.play(Write(piecewise_formula), run_time=1.5)
        self.play(Create(formula_rect))

        # 结论文字
        conclusion = Text(
            "Force exit at final step → Valid probability distribution!",
            font_size=22, color=SURVIVE_COLOR
        )
        conclusion.next_to(piecewise_formula, DOWN, buff=0.4)

        check_mark = Text("✓", font_size=30, color=SURVIVE_COLOR)
        check_mark.next_to(conclusion, RIGHT, buff=0.2)

        self.play(Write(conclusion), FadeIn(check_mark, scale=1.5), run_time=1)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)


class ProbabilityDistScene(Scene):
    """Scene 3: 概率分布可视化"""
    def construct(self):
        # 标题
        title = Text("Exit Probability Distribution", font_size=38)
        title.to_edge(UP, buff=0.5)

        # 数据
        probs = [0.30, 0.35, 0.14, 0.21]
        labels = ["Loop 1", "Loop 2", "Loop 3", "Loop 4"]

        # 创建坐标轴
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 0.5, 0.1],
            x_length=10,
            y_length=5,
            axis_config={
                "color": GREY_B,
                "include_tip": False,
                "include_numbers": False,
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": [0.1, 0.2, 0.3, 0.4, 0.5],
                "font_size": 24,
            },
        )
        axes.shift(DOWN * 0.3)

        # Y轴标签
        y_label = Text("Probability", font_size=24, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        # X轴标签
        x_labels = VGroup()
        for i, label in enumerate(labels):
            x_text = Text(label, font_size=22)
            x_text.move_to(axes.c2p(i + 1, 0) + DOWN * 0.4)
            x_labels.add(x_text)

        # 创建柱子
        bars = VGroup()
        bar_width = 0.6
        colors = [EXIT_COLOR, HIGHLIGHT_COLOR, SURVIVE_COLOR, LOOP_COLOR]

        for i, (prob, color) in enumerate(zip(probs, colors)):
            bar = Rectangle(
                height=prob * 10,  # 缩放到可视高度
                width=bar_width,
                color=color,
                fill_opacity=0.8,
                stroke_width=2
            )
            # 定位柱子底部对齐 x 轴
            bar.move_to(axes.c2p(i + 1, prob / 2))
            bars.add(bar)

        # 柱子上方的数值标签
        value_labels = VGroup()
        for i, (prob, bar) in enumerate(zip(probs, bars)):
            val_text = Text(f"{prob:.2f}", font_size=24, color=WHITE)
            val_text.next_to(bar, UP, buff=0.1)
            value_labels.add(val_text)

        # ===== 动画序列 =====
        self.play(Write(title))
        self.play(Create(axes), Write(y_label), run_time=1)
        self.play(
            LaggedStart(*[Write(label) for label in x_labels], lag_ratio=0.15),
            run_time=1
        )

        # 柱子依次升起
        for bar, val_label in zip(bars, value_labels):
            self.play(
                GrowFromEdge(bar, DOWN),
                FadeIn(val_label, shift=DOWN*0.2),
                run_time=0.6
            )

        self.wait(0.5)

        # 显示总和验证
        sum_text = MathTex(
            r"\sum P = 0.30 + 0.35 + 0.14 + 0.21 = 1.0 \checkmark",
            font_size=30, color=SURVIVE_COLOR
        )
        sum_text.to_edge(DOWN, buff=0.6)

        # 高亮动画
        self.play(
            *[bar.animate.set_stroke(color=WHITE, width=4) for bar in bars],
            run_time=0.5
        )
        self.play(Write(sum_text), run_time=1)

        # 附加说明
        note_text = Text("Automatically bounded between 0 & 1", font_size=24, color=GREY_B)
        note_text.next_to(sum_text, DOWN, buff=0.3)
        self.play(Write(note_text))

        self.wait(2)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class CDFThresholdScene(Scene):
    """Scene 4: CDF 与阈值决策"""
    def construct(self):
        # 标题
        title = Text("CDF & Threshold Decision", font_size=38)
        title.to_edge(UP, buff=0.5)

        # 数据
        probs = [0.30, 0.35, 0.14, 0.21]
        cdf_values = [0.30, 0.65, 0.79, 1.00]
        labels = ["L1", "L2", "L3", "L4"]

        # 创建坐标轴
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1.2, 0.2],
            x_length=9,
            y_length=5,
            axis_config={
                "color": GREY_B,
                "include_tip": True,
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": [0.2, 0.4, 0.6, 0.8, 1.0],
                "font_size": 22,
            },
        )
        axes.shift(DOWN * 0.2 + LEFT * 0.5)

        # 轴标签
        x_label = Text("Loop", font_size=22, color=GREY_B)
        x_label.next_to(axes.x_axis, RIGHT, buff=0.2)
        y_label = Text("CDF", font_size=22, color=GREY_B)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        # X轴标签
        x_tick_labels = VGroup()
        for i, label in enumerate(labels):
            x_text = Text(label, font_size=20)
            x_text.move_to(axes.c2p(i + 1, 0) + DOWN * 0.35)
            x_tick_labels.add(x_text)

        # 创建阶梯状 CDF
        cdf_points = [(0, 0)]
        for i, cdf_val in enumerate(cdf_values):
            cdf_points.append((i + 1, cdf_values[i-1] if i > 0 else 0))
            cdf_points.append((i + 1, cdf_val))

        cdf_line = VMobject(color=LOOP_COLOR, stroke_width=4)
        cdf_line.set_points_as_corners([axes.c2p(x, y) for x, y in cdf_points])

        # CDF 点
        cdf_dots = VGroup()
        cdf_labels = VGroup()
        for i, cdf_val in enumerate(cdf_values):
            dot = Dot(axes.c2p(i + 1, cdf_val), color=HIGHLIGHT_COLOR, radius=0.1)
            label = MathTex(f"{cdf_val:.2f}", font_size=22, color=HIGHLIGHT_COLOR)
            label.next_to(dot, UR, buff=0.1)
            cdf_dots.add(dot)
            cdf_labels.add(label)

        # ===== 动画序列 =====
        self.play(Write(title))
        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1)
        self.play(
            LaggedStart(*[Write(label) for label in x_tick_labels], lag_ratio=0.1),
            run_time=0.8
        )

        # 绘制 CDF 曲线
        self.play(Create(cdf_line), run_time=2)
        self.play(
            LaggedStart(*[FadeIn(dot, scale=1.5) for dot in cdf_dots], lag_ratio=0.2),
            LaggedStart(*[Write(label) for label in cdf_labels], lag_ratio=0.2),
            run_time=1.5
        )

        self.wait(1)

        # ===== 阈值线 =====
        threshold = 0.6
        threshold_line = DashedLine(
            axes.c2p(0, threshold),
            axes.c2p(5, threshold),
            color=EXIT_COLOR,
            stroke_width=3,
            dash_length=0.15
        )
        threshold_label = MathTex(r"q = 0.6", font_size=26, color=EXIT_COLOR)
        threshold_label.next_to(threshold_line, RIGHT, buff=0.2)

        self.play(Create(threshold_line), Write(threshold_label), run_time=1)

        # ===== 决策演示 =====
        decision_box = VGroup()

        # L1 检查
        check_1 = MathTex(r"L_1: CDF(0.30) < 0.6 \rightarrow \text{Continue}", font_size=24)
        check_1[0][0:2].set_color(LOOP_COLOR)
        check_1[0][-8:].set_color(SURVIVE_COLOR)

        # L2 检查
        check_2 = MathTex(r"L_2: CDF(0.65) \geq 0.6 \rightarrow \textbf{EXIT}", font_size=24)
        check_2[0][0:2].set_color(LOOP_COLOR)
        check_2[0][-4:].set_color(EXIT_COLOR)

        decision_box = VGroup(check_1, check_2)
        decision_box.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        decision_box.to_edge(DOWN, buff=0.8)

        # L1 检查动画
        check_dot_1 = Dot(axes.c2p(1, 0.3), color=SURVIVE_COLOR, radius=0.15)
        self.play(FadeIn(check_dot_1, scale=2), run_time=0.5)
        self.play(Write(check_1), run_time=1)
        self.play(check_dot_1.animate.set_color(SURVIVE_COLOR), run_time=0.3)

        # L2 检查动画
        check_dot_2 = Dot(axes.c2p(2, 0.65), color=EXIT_COLOR, radius=0.15)
        self.play(FadeIn(check_dot_2, scale=2), run_time=0.5)
        self.play(Write(check_2), run_time=1)

        # 高亮 L2 作为退出点
        exit_highlight = Circle(radius=0.25, color=EXIT_COLOR, stroke_width=4)
        exit_highlight.move_to(axes.c2p(2, 0.65))
        self.play(Create(exit_highlight), run_time=0.5)
        self.play(
            exit_highlight.animate.scale(1.5).set_opacity(0),
            run_time=0.8
        )

        self.wait(1)

        # ===== 交互式展示不同阈值 =====
        # 清除之前的决策文字
        self.play(FadeOut(decision_box), FadeOut(check_dot_1), FadeOut(check_dot_2))

        # 展示不同阈值效果
        thresholds_demo = [
            (0.2, "L1", EXIT_COLOR),
            (0.6, "L2", HIGHLIGHT_COLOR),
            (0.9, "L4", LOOP_COLOR),
        ]

        demo_text = Text("Varying threshold q:", font_size=26)
        demo_text.to_edge(DOWN, buff=1.5)
        self.play(Write(demo_text))

        for q_val, exit_loop, color in thresholds_demo:
            # 移动阈值线
            new_threshold_line = DashedLine(
                axes.c2p(0, q_val),
                axes.c2p(5, q_val),
                color=color,
                stroke_width=3,
                dash_length=0.15
            )
            new_label = MathTex(f"q = {q_val}", font_size=26, color=color)
            new_label.next_to(new_threshold_line, RIGHT, buff=0.2)

            result_text = Text(f"→ Exit at {exit_loop}", font_size=24, color=color)
            result_text.next_to(demo_text, DOWN, buff=0.3)

            self.play(
                Transform(threshold_line, new_threshold_line),
                Transform(threshold_label, new_label),
                run_time=0.8
            )
            self.play(Write(result_text), run_time=0.5)
            self.wait(1)
            self.play(FadeOut(result_text))

        self.wait(1)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class SummaryScene(Scene):
    """Scene 5: 总结公式"""
    def construct(self):
        # 标题
        title = Text("Summary: The Gating Formula", font_size=40)
        title.to_edge(UP, buff=0.6)

        # 核心公式
        main_formula = MathTex(
            r"\tilde{p}_t(x) = \lambda_t(x) \cdot \prod_{j=1}^{t-1}(1 - \lambda_j(x))",
            font_size=48
        )
        main_formula.shift(UP * 0.5)

        # 公式分解框
        formula_box = SurroundingRectangle(main_formula, color=FORMULA_COLOR, buff=0.3)

        # 具体例子
        example_title = Text("Example: Exit at Loop 2", font_size=28, color=GREY_B)
        example_title.next_to(main_formula, DOWN, buff=1)

        example_formula = MathTex(
            r"\tilde{p}_2 = 0.5 \times (1 - 0.3) = 0.35",
            font_size=36
        )
        example_formula.next_to(example_title, DOWN, buff=0.4)

        # 标注
        exit_arrow = Arrow(
            example_formula.get_bottom() + LEFT * 1.8,
            example_formula.get_bottom() + LEFT * 1.8 + DOWN * 0.8,
            color=EXIT_COLOR, stroke_width=3
        )
        exit_label = Text("exit rate λ₂", font_size=20, color=EXIT_COLOR)
        exit_label.next_to(exit_arrow, DOWN, buff=0.1)

        survival_arrow = Arrow(
            example_formula.get_bottom() + RIGHT * 0.8,
            example_formula.get_bottom() + RIGHT * 0.8 + DOWN * 0.8,
            color=SURVIVE_COLOR, stroke_width=3
        )
        survival_label = Text("survival from L1", font_size=20, color=SURVIVE_COLOR)
        survival_label.next_to(survival_arrow, DOWN, buff=0.1)

        # ===== 动画序列 =====
        self.play(Write(title), run_time=1)
        self.wait(0.5)

        # 显示核心公式
        self.play(Write(main_formula), run_time=2)
        self.play(Create(formula_box), run_time=0.8)

        self.wait(1)

        # 显示例子
        self.play(Write(example_title), run_time=0.8)
        self.play(Write(example_formula), run_time=1.5)

        # 显示标注
        self.play(
            GrowArrow(exit_arrow), Write(exit_label),
            GrowArrow(survival_arrow), Write(survival_label),
            run_time=1
        )

        self.wait(2)

        # 最终总结
        final_text = VGroup(
            Text("✓ Sequential gating with sigmoid outputs", font_size=24, color=SURVIVE_COLOR),
            Text("✓ Automatic probability normalization", font_size=24, color=SURVIVE_COLOR),
            Text("✓ No need to know future loop outputs", font_size=24, color=SURVIVE_COLOR),
        )
        final_text.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        final_text.to_edge(DOWN, buff=0.5)

        self.play(
            LaggedStart(*[Write(text) for text in final_text], lag_ratio=0.3),
            run_time=2
        )

        self.wait(3)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


class GatingMechanism(Scene):
    """完整的 Gating Mechanism 动画 - 包含所有场景"""
    def construct(self):
        # Scene 1: 问题引入
        self.intro_problem()

        # Scene 2: Step-by-Step 概率计算
        self.step_by_step()

        # Scene 2.5: 为什么不保证是概率分布？
        self.why_not_prob_dist()

        # Scene 3: 概率分布可视化
        self.probability_dist()

        # Scene 4: CDF 与阈值决策
        self.cdf_threshold()

        # Scene 5: 总结公式
        self.summary()

    def intro_problem(self):
        """Scene 1: 问题引入"""
        # 标题
        title = Text("Why can't we just use Softmax?", font_size=42, color=WHITE)
        title.to_edge(UP, buff=0.5)

        # 创建4个 Loop 方块
        loops = VGroup(*[LoopBlock(f"Loop {i+1}") for i in range(4)])
        loops.arrange(RIGHT, buff=0.8)
        loops.shift(UP * 0.5)

        # 箭头连接
        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops[i].get_right(),
                loops[i+1].get_left(),
                buff=0.1,
                color=GREY_B,
                stroke_width=3
            )
            arrows.add(arrow)

        # 问号标签
        question_marks = VGroup()
        for loop in loops:
            qmark = Text("?", font_size=36, color=HIGHLIGHT_COLOR)
            qmark.next_to(loop, UP, buff=0.3)
            question_marks.add(qmark)

        # 问题说明文字
        problem_text = Text(
            "We can't forecast the future —\nwe don't know P(exit) until all loops complete",
            font_size=24,
            color=GREY_B,
            line_spacing=1.2
        )
        problem_text.to_edge(DOWN, buff=1)

        # 动画
        self.play(Write(title), run_time=1)

        for i, loop in enumerate(loops):
            if i > 0:
                self.play(
                    FadeIn(loop, shift=RIGHT*0.3),
                    GrowArrow(arrows[i-1]),
                    run_time=0.4
                )
            else:
                self.play(FadeIn(loop, shift=RIGHT*0.3), run_time=0.4)

        self.play(
            LaggedStart(*[FadeIn(qm, scale=1.5) for qm in question_marks], lag_ratio=0.15),
            run_time=0.8
        )

        self.play(Write(problem_text), run_time=1.5)
        self.wait(1.5)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def step_by_step(self):
        """Scene 2: Step-by-Step 概率计算"""
        title = Text("Step-by-Step Probability Calculation", font_size=36)
        title.to_edge(UP, buff=0.4)

        lambdas = [0.3, 0.5, 0.4]

        loops = VGroup(*[LoopBlock(f"Loop {i+1}") for i in range(4)])
        loops.arrange(RIGHT, buff=0.7)
        loops.shift(UP * 1.5)
        loops.scale(0.9)

        arrows = VGroup()
        for i in range(3):
            arrow = Arrow(
                loops[i].get_right(),
                loops[i+1].get_left(),
                buff=0.1,
                color=SURVIVE_COLOR,
                stroke_width=2
            )
            arrows.add(arrow)

        self.play(Write(title))
        self.play(
            LaggedStart(*[FadeIn(loop) for loop in loops], lag_ratio=0.1),
            LaggedStart(*[GrowArrow(arrow) for arrow in arrows], lag_ratio=0.1),
            run_time=1
        )

        unconditional_probs = []

        # Loop 1
        self.play(loops[0].highlight())
        sigma_1 = MathTex(r"\lambda_1 = 0.3", font_size=28).next_to(loops[0], DOWN, buff=0.4)
        self.play(Write(sigma_1), run_time=0.6)

        result_1 = MathTex(r"P(\text{exit at } L_1) = 0.3", font_size=24, color=HIGHLIGHT_COLOR)
        result_1.to_edge(DOWN, buff=1)
        self.play(Write(result_1))
        unconditional_probs.append(0.3)
        self.wait(1)
        self.play(FadeOut(sigma_1), FadeOut(result_1), loops[0].unhighlight())

        # Loop 2
        self.play(loops[1].highlight())
        sigma_2 = MathTex(r"\lambda_2 = 0.5", font_size=28).next_to(loops[1], DOWN, buff=0.4)
        self.play(Write(sigma_2), run_time=0.6)

        formula_2 = MathTex(r"P(\text{exit at } L_2) = 0.7 \times 0.5 = 0.35", font_size=24, color=HIGHLIGHT_COLOR)
        formula_2.to_edge(DOWN, buff=1)
        self.play(Write(formula_2))
        unconditional_probs.append(0.35)
        self.wait(1)
        self.play(FadeOut(sigma_2), FadeOut(formula_2), loops[1].unhighlight())

        # Loop 3
        self.play(loops[2].highlight())
        sigma_3 = MathTex(r"\lambda_3 = 0.4", font_size=28).next_to(loops[2], DOWN, buff=0.4)
        self.play(Write(sigma_3), run_time=0.6)

        formula_3 = MathTex(r"P(\text{exit at } L_3) = 0.35 \times 0.4 = 0.14", font_size=24, color=HIGHLIGHT_COLOR)
        formula_3.to_edge(DOWN, buff=1)
        self.play(Write(formula_3))
        unconditional_probs.append(0.14)
        self.wait(1)
        self.play(FadeOut(sigma_3), FadeOut(formula_3), loops[2].unhighlight())

        # Loop 4
        self.play(loops[3].highlight())
        remaining_text = MathTex(r"\text{Remaining} = 1 - 0.79 = 0.21", font_size=24, color=EXIT_COLOR)
        remaining_text.to_edge(DOWN, buff=1)
        self.play(Write(remaining_text))
        self.wait(1)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def why_not_prob_dist(self):
        """Scene 2.5: 为什么不保证是概率分布？"""
        # Part A: 数学直觉
        self._why_part_a()
        # Part B: λ 太小
        self._why_part_b()
        # Part C: λ 太大
        self._why_part_c()
        # Part D: 解决方案
        self._why_part_d()

    def _why_part_a(self):
        """Part A: 数学直觉 - 无穷 vs 有限"""
        title = Text("Why might Σp̃ₜ ≠ 1?", font_size=38)
        title.to_edge(UP, buff=0.5)

        self.play(Write(title), run_time=0.8)

        infinite_formula = MathTex(
            r"\text{If } T_{max} \to \infty \text{ and } \lambda_t = \lambda:",
            font_size=28
        )
        infinite_formula.shift(UP * 1.5)

        series_formula = MathTex(
            r"\sum_{t=1}^{\infty} \tilde{p}_t = \sum_{t=1}^{\infty} \lambda(1-\lambda)^{t-1} = 1",
            font_size=32, color=SURVIVE_COLOR
        )
        series_formula.next_to(infinite_formula, DOWN, buff=0.4)

        self.play(Write(infinite_formula), run_time=0.8)
        self.play(Write(series_formula), run_time=1)

        explain_text = Text("Geometric series sums to 1", font_size=24, color=GREY_B)
        explain_text.next_to(series_formula, DOWN, buff=0.4)
        self.play(Write(explain_text))

        self.wait(0.8)

        but_text = Text("But...", font_size=36, color=EXIT_COLOR)
        but_text.next_to(explain_text, DOWN, buff=0.5)
        self.play(Write(but_text), run_time=0.4)

        problem_text = Text("We only have Tmax steps!", font_size=28, color=EXIT_COLOR)
        problem_text.next_to(but_text, DOWN, buff=0.3)
        problem_box = SurroundingRectangle(problem_text, color=EXIT_COLOR, buff=0.15)

        self.play(Write(problem_text), Create(problem_box), run_time=0.8)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def _why_part_b(self):
        """Part B: Case 1 - λ 太小"""
        title = Text("Case 1: λ too small", font_size=32, color=EXIT_COLOR)
        title.to_edge(UP, buff=0.4)

        self.play(Write(title), run_time=0.6)

        setup_text = MathTex(r"\lambda_1 = \lambda_2 = \lambda_3 = \lambda_4 = 0.1", font_size=26)
        setup_text.shift(UP * 2)
        self.play(Write(setup_text), run_time=0.6)

        # 计算
        calc_lines = VGroup(
            MathTex(r"\tilde{p}_1 = 0.1", font_size=24),
            MathTex(r"\tilde{p}_2 = 0.9 \times 0.1 = 0.09", font_size=24),
            MathTex(r"\tilde{p}_3 = 0.81 \times 0.1 = 0.081", font_size=24),
            MathTex(r"\tilde{p}_4 = 0.729 \times 0.1 = 0.073", font_size=24),
        )
        calc_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        calc_lines.shift(LEFT * 2 + UP * 0.3)

        self.play(LaggedStart(*[Write(l) for l in calc_lines], lag_ratio=0.2), run_time=1.5)

        sep_line = Line(LEFT * 1.2, RIGHT * 1.2, color=GREY_B)
        sep_line.next_to(calc_lines, DOWN, buff=0.12)
        self.play(Create(sep_line), run_time=0.3)

        sum_result = MathTex(r"\sum = 0.344 \ll 1", font_size=26, color=EXIT_COLOR)
        sum_result.next_to(sep_line, DOWN, buff=0.12)
        cross_mark = Text("❌", font_size=28, color=EXIT_COLOR)
        cross_mark.next_to(sum_result, RIGHT, buff=0.2)

        self.play(Write(sum_result), FadeIn(cross_mark, scale=1.3), run_time=0.6)

        # 概率桶
        bucket_outline = Rectangle(height=2.5, width=1, color=WHITE, stroke_width=2, fill_opacity=0)
        bucket_outline.shift(RIGHT * 3 + DOWN * 0.3)

        filled_part = Rectangle(height=2.5 * 0.344, width=1, color=LOOP_COLOR, fill_opacity=0.7, stroke_width=0)
        filled_part.align_to(bucket_outline, DOWN)
        filled_part.shift(RIGHT * 3 + DOWN * 0.3)

        empty_label = Text("65.6%\nempty!", font_size=16, color=EXIT_COLOR)
        empty_label.move_to(bucket_outline.get_center() + UP * 0.6)

        self.play(Create(bucket_outline), run_time=0.4)
        self.play(GrowFromEdge(filled_part, DOWN), run_time=0.6)
        self.play(Write(empty_label), run_time=0.4)

        leak_text = Text("Probability leaks beyond Tmax!", font_size=22, color=EXIT_COLOR)
        leak_text.to_edge(DOWN, buff=0.6)
        self.play(Write(leak_text), run_time=0.6)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def _why_part_c(self):
        """Part C: Case 2 - λ 太大"""
        title = Text("Case 2: λ too large", font_size=32, color=HIGHLIGHT_COLOR)
        title.to_edge(UP, buff=0.4)

        self.play(Write(title), run_time=0.6)

        setup_text = MathTex(r"\lambda_1 = \lambda_2 = \lambda_3 = \lambda_4 = 0.9", font_size=26)
        setup_text.shift(UP * 2)
        self.play(Write(setup_text), run_time=0.6)

        calc_lines = VGroup(
            MathTex(r"\tilde{p}_1 = 0.9", font_size=24),
            MathTex(r"\tilde{p}_2 = 0.1 \times 0.9 = 0.09", font_size=24),
            MathTex(r"\tilde{p}_3 = 0.01 \times 0.9 = 0.009", font_size=24),
            MathTex(r"\tilde{p}_4 = 0.001 \times 0.9 = 0.0009", font_size=24),
        )
        calc_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        calc_lines.shift(LEFT * 2 + UP * 0.3)

        self.play(LaggedStart(*[Write(l) for l in calc_lines], lag_ratio=0.15), run_time=1.2)

        sep_line = Line(LEFT * 1.5, RIGHT * 1.5, color=GREY_B)
        sep_line.next_to(calc_lines, DOWN, buff=0.12)
        self.play(Create(sep_line), run_time=0.3)

        sum_result = MathTex(r"\sum = 0.9999 \approx 1", font_size=26, color=SURVIVE_COLOR)
        sum_result.next_to(sep_line, DOWN, buff=0.12)
        check_mark = Text("✓", font_size=28, color=SURVIVE_COLOR)
        check_mark.next_to(sum_result, RIGHT, buff=0.2)

        self.play(Write(sum_result), FadeIn(check_mark, scale=1.3), run_time=0.6)

        # 概率桶 - 几乎满
        bucket_outline = Rectangle(height=2.5, width=1, color=WHITE, stroke_width=2, fill_opacity=0)
        bucket_outline.shift(RIGHT * 3 + DOWN * 0.3)

        filled_part = Rectangle(height=2.5 * 0.9999, width=1, color=SURVIVE_COLOR, fill_opacity=0.7, stroke_width=0)
        filled_part.align_to(bucket_outline, DOWN)
        filled_part.shift(RIGHT * 3 + DOWN * 0.3)

        self.play(Create(bucket_outline), run_time=0.4)
        self.play(GrowFromEdge(filled_part, DOWN), run_time=0.6)

        ok_text = Text("This case is fine — no leakage!", font_size=22, color=SURVIVE_COLOR)
        ok_text.to_edge(DOWN, buff=0.6)
        self.play(Write(ok_text), run_time=0.6)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def _why_part_d(self):
        """Part D: 解决方案"""
        title = Text("Solution: Force Exit at Final Step", font_size=32, color=SURVIVE_COLOR)
        title.to_edge(UP, buff=0.4)

        self.play(Write(title), run_time=0.6)

        # 对比：修复前 vs 修复后
        before_title = Text("Before", font_size=22, color=EXIT_COLOR)
        before_title.shift(UP * 1.8 + LEFT * 3)

        before_calc = VGroup(
            MathTex(r"p_1 = 0.1", font_size=22),
            MathTex(r"p_2 = 0.09", font_size=22),
            MathTex(r"p_3 = 0.081", font_size=22),
            MathTex(r"p_4 = 0.073", font_size=22, color=EXIT_COLOR),
            MathTex(r"\sum = 0.344", font_size=22, color=EXIT_COLOR),
        )
        before_calc.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        before_calc.next_to(before_title, DOWN, buff=0.2)

        after_title = Text("After", font_size=22, color=SURVIVE_COLOR)
        after_title.shift(UP * 1.8 + RIGHT * 3)

        after_calc = VGroup(
            MathTex(r"p_1 = 0.1", font_size=22),
            MathTex(r"p_2 = 0.09", font_size=22),
            MathTex(r"p_3 = 0.081", font_size=22),
            MathTex(r"p_4 = S_3 = 0.729", font_size=22, color=SURVIVE_COLOR),
            MathTex(r"\sum = 1.0", font_size=22, color=SURVIVE_COLOR),
        )
        after_calc.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        after_calc.next_to(after_title, DOWN, buff=0.2)

        self.play(Write(before_title), Write(after_title), run_time=0.5)
        self.play(
            LaggedStart(*[Write(l) for l in before_calc], lag_ratio=0.1),
            LaggedStart(*[Write(l) for l in after_calc], lag_ratio=0.1),
            run_time=1.5
        )

        # 箭头
        fix_arrow = Arrow(LEFT * 0.8, RIGHT * 0.8, color=HIGHLIGHT_COLOR, stroke_width=3)
        fix_arrow.shift(UP * 0.3)
        self.play(GrowArrow(fix_arrow), run_time=0.4)

        # 公式
        formula_text = Text("Final formula:", font_size=22, color=WHITE)
        formula_text.to_edge(DOWN, buff=1.5)

        piecewise = MathTex(
            r"p(t) = \begin{cases} \lambda_t \cdot S_{t-1}, & t < T_{max} \\ S_{T_{max}-1}, & t = T_{max} \end{cases}",
            font_size=26
        )
        piecewise.next_to(formula_text, DOWN, buff=0.2)

        self.play(Write(formula_text), run_time=0.4)
        self.play(Write(piecewise), run_time=1)

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.6)

    def probability_dist(self):
        """Scene 3: 概率分布可视化"""
        title = Text("Exit Probability Distribution", font_size=36)
        title.to_edge(UP, buff=0.5)

        probs = [0.30, 0.35, 0.14, 0.21]
        labels = ["L1", "L2", "L3", "L4"]
        colors = [EXIT_COLOR, HIGHLIGHT_COLOR, SURVIVE_COLOR, LOOP_COLOR]

        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 0.5, 0.1],
            x_length=9,
            y_length=4.5,
            axis_config={"color": GREY_B, "include_tip": False},
        )
        axes.shift(DOWN * 0.3)

        x_labels = VGroup()
        for i, label in enumerate(labels):
            x_text = Text(label, font_size=22)
            x_text.move_to(axes.c2p(i + 1, 0) + DOWN * 0.4)
            x_labels.add(x_text)

        bars = VGroup()
        value_labels = VGroup()
        for i, (prob, color) in enumerate(zip(probs, colors)):
            bar = Rectangle(
                height=prob * 9,
                width=0.6,
                color=color,
                fill_opacity=0.8,
                stroke_width=2
            )
            bar.move_to(axes.c2p(i + 1, prob / 2))
            bars.add(bar)

            val_text = Text(f"{prob:.2f}", font_size=22, color=WHITE)
            val_text.next_to(bar, UP, buff=0.1)
            value_labels.add(val_text)

        self.play(Write(title))
        self.play(Create(axes), run_time=0.8)
        self.play(LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1))

        for bar, val in zip(bars, value_labels):
            self.play(GrowFromEdge(bar, DOWN), FadeIn(val), run_time=0.5)

        sum_text = MathTex(r"\sum P = 1.0 \checkmark", font_size=30, color=SURVIVE_COLOR)
        sum_text.to_edge(DOWN, buff=0.6)
        self.play(Write(sum_text))

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def cdf_threshold(self):
        """Scene 4: CDF 与阈值决策"""
        title = Text("CDF & Threshold Decision", font_size=36)
        title.to_edge(UP, buff=0.5)

        cdf_values = [0.30, 0.65, 0.79, 1.00]
        labels = ["L1", "L2", "L3", "L4"]

        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 1.2, 0.2],
            x_length=8,
            y_length=4.5,
            axis_config={"color": GREY_B},
        )
        axes.shift(DOWN * 0.2)

        x_labels = VGroup()
        for i, label in enumerate(labels):
            x_text = Text(label, font_size=20)
            x_text.move_to(axes.c2p(i + 1, 0) + DOWN * 0.35)
            x_labels.add(x_text)

        # CDF 阶梯线
        cdf_points = [(0, 0)]
        for i, cdf_val in enumerate(cdf_values):
            cdf_points.append((i + 1, cdf_values[i-1] if i > 0 else 0))
            cdf_points.append((i + 1, cdf_val))

        cdf_line = VMobject(color=LOOP_COLOR, stroke_width=4)
        cdf_line.set_points_as_corners([axes.c2p(x, y) for x, y in cdf_points])

        cdf_dots = VGroup()
        cdf_labels = VGroup()
        for i, cdf_val in enumerate(cdf_values):
            dot = Dot(axes.c2p(i + 1, cdf_val), color=HIGHLIGHT_COLOR, radius=0.08)
            label = MathTex(f"{cdf_val:.2f}", font_size=20, color=HIGHLIGHT_COLOR)
            label.next_to(dot, UR, buff=0.08)
            cdf_dots.add(dot)
            cdf_labels.add(label)

        self.play(Write(title))
        self.play(Create(axes), run_time=0.8)
        self.play(LaggedStart(*[Write(l) for l in x_labels], lag_ratio=0.1))
        self.play(Create(cdf_line), run_time=1.5)
        self.play(
            LaggedStart(*[FadeIn(d, scale=1.5) for d in cdf_dots], lag_ratio=0.15),
            LaggedStart(*[Write(l) for l in cdf_labels], lag_ratio=0.15),
            run_time=1
        )

        # 阈值线
        threshold_line = DashedLine(
            axes.c2p(0, 0.6), axes.c2p(5, 0.6),
            color=EXIT_COLOR, stroke_width=3, dash_length=0.15
        )
        threshold_label = MathTex(r"q = 0.6", font_size=24, color=EXIT_COLOR)
        threshold_label.next_to(threshold_line, RIGHT, buff=0.15)

        self.play(Create(threshold_line), Write(threshold_label))

        # 决策
        decision = Text("CDF(L2) = 0.65 ≥ 0.6 → Exit at L2", font_size=24, color=EXIT_COLOR)
        decision.to_edge(DOWN, buff=0.8)
        self.play(Write(decision))

        exit_circle = Circle(radius=0.2, color=EXIT_COLOR, stroke_width=3)
        exit_circle.move_to(axes.c2p(2, 0.65))
        self.play(Create(exit_circle))

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

    def summary(self):
        """Scene 5: 总结公式"""
        title = Text("The Gating Formula", font_size=40)
        title.to_edge(UP, buff=0.6)

        main_formula = MathTex(
            r"\tilde{p}_t(x) = \lambda_t(x) \cdot \prod_{j=1}^{t-1}(1 - \lambda_j(x))",
            font_size=44
        )
        main_formula.shift(UP * 0.8)

        formula_box = SurroundingRectangle(main_formula, color=FORMULA_COLOR, buff=0.25)

        example = MathTex(
            r"\tilde{p}_2 = 0.5 \times (1 - 0.3) = 0.35",
            font_size=32
        )
        example.next_to(main_formula, DOWN, buff=0.8)

        final_text = VGroup(
            Text("✓ Sequential gating with sigmoid", font_size=22, color=SURVIVE_COLOR),
            Text("✓ Automatic normalization to [0,1]", font_size=22, color=SURVIVE_COLOR),
            Text("✓ No future information needed", font_size=22, color=SURVIVE_COLOR),
        )
        final_text.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        final_text.to_edge(DOWN, buff=0.6)

        self.play(Write(title))
        self.play(Write(main_formula), run_time=1.5)
        self.play(Create(formula_box))
        self.play(Write(example), run_time=1)
        self.play(LaggedStart(*[Write(t) for t in final_text], lag_ratio=0.3), run_time=1.5)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("Adaptive Exit Gate Mechanism - Manim 动画")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整动画: manim -pql gating_mechanism.py GatingMechanism")
    print("  高质量:   manim -pqh gating_mechanism.py GatingMechanism")
    print("\n单独场景:")
    print("  manim -pql gating_mechanism.py IntroScene")
    print("  manim -pql gating_mechanism.py StepByStepScene")
    print("  manim -pql gating_mechanism.py WhyNotProbDistScene  (新增!)")
    print("  manim -pql gating_mechanism.py ProbabilityDistScene")
    print("  manim -pql gating_mechanism.py CDFThresholdScene")
    print("  manim -pql gating_mechanism.py SummaryScene")
    print("=" * 60)

