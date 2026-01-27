"""
Knowledge Manipulation Animation - Multi-hop Reasoning
展示模型如何进行多跳推理，超越简单检索

运行命令:
  完整动画: manim -pql knowledge_manipulation_animation.py MultiHopReasoning
  高质量:   manim -pqh knowledge_manipulation_animation.py MultiHopReasoning
  1080p60:  manim -pqh --fps 60 knowledge_manipulation_animation.py MultiHopReasoning
  4K:       manim -qk knowledge_manipulation_animation.py MultiHopReasoning
"""

from manim import *

# ==================== 颜色配置 ====================
BACKGROUND_COLOR = BLACK
KEY_COLOR = "#64B5F6"        # 浅蓝色 - Key (Name)
VALUE_COLOR = "#F4A261"      # 金色 - Value (Attributes)
REASON_COLOR = "#2A9D8F"     # 青色 - Reasoning
ANSWER_COLOR = "#E63946"     # 红色 - Answer
TEXT_COLOR = WHITE
DIM_COLOR = GREY_B
BOX_BG_COLOR = "#1a1a1a"


class ReasoningBox(VGroup):
    """推理步骤框"""

    def __init__(self, label, content_lines, color, width=2.8, **kwargs):
        super().__init__(**kwargs)

        # 计算高度
        height = 0.5 + len(content_lines) * 0.4

        # 主框
        self.box = RoundedRectangle(
            corner_radius=0.12,
            width=width,
            height=height,
            color=color,
            stroke_width=2.5,
            fill_color=BOX_BG_COLOR,
            fill_opacity=0.9
        )
        self.add(self.box)

        # 标签（顶部）
        self.label = Tex(r"\textbf{" + label + "}", font_size=18, color=color)
        self.label.next_to(self.box.get_top(), DOWN, buff=0.12)
        self.add(self.label)

        # 内容
        self.content = VGroup()
        for i, line in enumerate(content_lines):
            text = Tex(line, font_size=16, color=TEXT_COLOR)
            text.move_to(self.box.get_center() + DOWN * (i * 0.35 - 0.05))
            self.content.add(text)
        self.add(self.content)


class MultiHopReasoning(Scene):
    """多跳推理动画 - 展示知识操作"""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # ===== 1. Question =====
        # "Is Anya Forger's age an odd number?"
        q_prefix = Tex(r'``Is ', font_size=28, color=TEXT_COLOR)
        q_name = Tex(r"Anya Forger", font_size=28, color=KEY_COLOR)
        q_suffix = Tex(r"'s age an odd number?''", font_size=28, color=TEXT_COLOR)

        question = VGroup(q_prefix, q_name, q_suffix)
        question.arrange(RIGHT, buff=0.08)
        question.move_to(UP * 2.5)

        # Question 出现
        self.play(
            Write(q_prefix),
            Write(q_name),
            Write(q_suffix),
            run_time=1.2
        )

        self.wait(0.5)

        # ===== 2. Flow: Three boxes in a row =====
        # Hop 1: Retrieve
        hop1 = ReasoningBox(
            label="Hop 1: Retrieve",
            content_lines=[r"Birth date: \textbf{Oct 2, 1996}"],
            color=VALUE_COLOR,
            width=3.0
        )
        hop1.move_to(LEFT * 4 + DOWN * 0.3)

        # Hop 2: Reason
        hop2 = ReasoningBox(
            label="Hop 2: Reason",
            content_lines=[r"$2026 - 1996 = 30$", r"Birthday not yet $\rightarrow$ \textbf{29}"],
            color=REASON_COLOR,
            width=3.5
        )
        hop2.move_to(ORIGIN + DOWN * 0.3)

        # Answer box
        answer_box = RoundedRectangle(
            corner_radius=0.12,
            width=2.2,
            height=1.2,
            color=ANSWER_COLOR,
            stroke_width=3,
            fill_color=BOX_BG_COLOR,
            fill_opacity=0.9
        )
        answer_box.move_to(RIGHT * 4 + DOWN * 0.3)

        answer_label = Tex(r"\textbf{Answer}", font_size=18, color=ANSWER_COLOR)
        answer_label.next_to(answer_box.get_top(), DOWN, buff=0.12)

        answer_text = Tex(r"\textbf{Yes}", font_size=32, color=ANSWER_COLOR)
        answer_text.move_to(answer_box.get_center() + DOWN * 0.1)

        answer_reason = Tex(r"(29 is odd)", font_size=14, color=DIM_COLOR)
        answer_reason.next_to(answer_text, DOWN, buff=0.1)

        answer_group = VGroup(answer_box, answer_label, answer_text, answer_reason)

        # ===== Arrows =====
        # Question to Hop 1
        arrow_q_to_h1 = Arrow(
            question.get_bottom() + DOWN * 0.1,
            hop1.get_top() + UP * 0.1,
            color=DIM_COLOR,
            stroke_width=2,
            buff=0.15,
            max_tip_length_to_length_ratio=0.15
        )

        # Hop 1 to Hop 2
        arrow_h1_to_h2 = Arrow(
            hop1.get_right(),
            hop2.get_left(),
            color=VALUE_COLOR,
            stroke_width=3,
            buff=0.15,
            max_tip_length_to_length_ratio=0.2
        )

        # Hop 2 to Answer
        arrow_h2_to_a = Arrow(
            hop2.get_right(),
            answer_box.get_left(),
            color=REASON_COLOR,
            stroke_width=3,
            buff=0.15,
            max_tip_length_to_length_ratio=0.2
        )

        # ===== Animate the flow =====
        # Arrow to Hop 1
        self.play(Create(arrow_q_to_h1), run_time=0.5)

        # Hop 1 appears
        self.play(
            FadeIn(hop1.box, scale=0.9),
            Write(hop1.label),
            run_time=0.6
        )
        self.play(
            Write(hop1.content),
            run_time=0.8
        )

        # Highlight the retrieved value
        value_highlight = SurroundingRectangle(
            hop1.content[0],
            color=VALUE_COLOR,
            buff=0.08,
            stroke_width=2
        )
        self.play(Create(value_highlight), run_time=0.4)
        self.play(FadeOut(value_highlight), run_time=0.3)

        self.wait(0.3)

        # Arrow to Hop 2
        self.play(Create(arrow_h1_to_h2), run_time=0.5)

        # Hop 2 appears
        self.play(
            FadeIn(hop2.box, scale=0.9),
            Write(hop2.label),
            run_time=0.6
        )
        self.play(
            Write(hop2.content[0]),  # 1996 → 2024
            run_time=0.6
        )
        self.play(
            Write(hop2.content[1]),  # Age = 28 years
            run_time=0.6
        )

        self.wait(0.3)

        # Arrow to Answer
        self.play(Create(arrow_h2_to_a), run_time=0.5)

        # Answer appears with emphasis
        self.play(
            FadeIn(answer_box, scale=0.9),
            Write(answer_label),
            run_time=0.5
        )
        self.play(
            FadeIn(answer_text, scale=1.3),
            run_time=0.6
        )
        self.play(
            FadeIn(answer_reason),
            run_time=0.4
        )

        # Final highlight pulse on answer
        # pulse = answer_box.copy()
        # pulse.set_stroke(width=6, opacity=0.6)
        # self.play(
        #     pulse.animate.scale(1.15).set_stroke(opacity=0),
        #     run_time=0.7
        # )
        # self.remove(pulse)

        self.wait(1.5)

        # Fade out everything
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1
        )


if __name__ == "__main__":
    print("=" * 60)
    print("Knowledge Manipulation Animation - Multi-hop Reasoning")
    print("=" * 60)
    print("\n运行命令:")
    print("  预览:   manim -pql knowledge_manipulation_animation.py MultiHopReasoning")
    print("  高质量: manim -pqh knowledge_manipulation_animation.py MultiHopReasoning")
    print("  1080p60: manim -pqh --fps 60 knowledge_manipulation_animation.py MultiHopReasoning")
    print("=" * 60)

