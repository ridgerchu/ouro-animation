"""
Knowledge Biography Animation - Simplified Version
Part 1: 随机选择 - All slots spin and stop simultaneously
Part 2: 数据集样本 - Multiple Q&A pairs with different names

运行命令:
  完整动画: manim -pql knowledge_biography_animation.py KnowledgeBiographyAnimation
  高质量:   manim -pqh knowledge_biography_animation.py KnowledgeBiographyAnimation
  1080p60:  manim -pqh --fps 60 knowledge_biography_animation.py KnowledgeBiographyAnimation
  4K:       manim -qk knowledge_biography_animation.py KnowledgeBiographyAnimation
"""

from manim import *
import random

# ==================== 辅助函数 ====================
def escape_latex(text):
    """转义 LaTeX 特殊字符"""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\\", "\\textbackslash{}")
    text = text.replace("&", "\\&")
    text = text.replace("%", "\\%")
    text = text.replace("$", "\\$")
    text = text.replace("#", "\\#")
    text = text.replace("^", "\\textasciicircum{}")
    text = text.replace("_", "\\_")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("~", "\\textasciitilde{}")
    return text

# ==================== 颜色配置 ====================
BACKGROUND_COLOR = BLACK
KEY_COLOR = "#6B8AFF"             # 亮蓝色 - Key (Name) - brighter
VALUE_COLOR = "#F4A261"           # 黄色/金色 - Value (Attributes)
TEXT_COLOR = WHITE
DIM_COLOR = GREY_B
SLOT_BG_COLOR = "#1a1a1a"

# ==================== 数据配置 ====================
# 随机滚动候选值
SLOT_CANDIDATES = {
    "Name": ["Anya Forger", "Loid Forger", "Yor Briar", "Damian Desmond", "Becky Blackbell", "Franky Franklin"],
    "Birth Date": ["Jan 15, 1994", "Mar 8, 1998", "Jul 22, 1995", "Oct 2, 1996", "Dec 3, 1997", "Sep 14, 1993"],
    "Birth City": ["Boston", "New York", "Princeton", "Chicago", "Seattle", "Austin", "Berlin", "Ostania"],
    "University": ["Stanford", "Harvard", "MIT", "Yale", "Berkeley", "Caltech", "Oxford", "Cambridge"],
    "Employer": ["Google", "Apple", "Meta", "Microsoft", "Amazon", "Netflix", "WISE", "City Hall"]
}


class SlotWheel(VGroup):
    """单个老虎机滚轮组件"""

    def __init__(self, label, candidates, final_value, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.candidates = candidates
        self.final_value = final_value

        # 滚轮外框
        color = KEY_COLOR if label == "Name" else VALUE_COLOR
        self.frame = RoundedRectangle(
            corner_radius=0.1,
            width=1.8,
            height=1.2,
            color=color,
            stroke_width=2,
            fill_color=SLOT_BG_COLOR,
            fill_opacity=0.9
        )
        self.add(self.frame)

        # 标签
        self.label_text = Tex(r"\texttt{" + escape_latex(label) + "}", font_size=18, color=DIM_COLOR)
        self.label_text.next_to(self.frame, UP, buff=0.1)
        self.add(self.label_text)

        # 当前显示的值
        self.current_value_text = Tex(r"\text{---}", font_size=16, color=TEXT_COLOR)
        self.current_value_text.move_to(self.frame.get_center())
        self.add(self.current_value_text)

        self.final_text = None

    def get_center_pos(self):
        return self.frame.get_center()

    def get_frame_width(self):
        return self.frame.width


class KnowledgeBiographyAnimation(Scene):
    """知识传记动画 - 简化版"""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # Part 1: 随机选择 - 所有滚轮同时滚动
        self.part1_random_selection()

        # Part 2: 显示自然文本样本，然后展示 Q&A
        self.part2_natural_text_and_qa()

    def part1_random_selection(self):
        """Part 1: 所有滚轮同时随机选择"""

        # 创建 5 个滚轮 (Name + 4 属性)
        slot_names = ["Name", "Birth Date", "Birth City", "University", "Employer"]
        final_values = ["Anya Forger", "Oct 2, 1996", "Princeton", "MIT", "Meta"]

        self.slot_wheels = VGroup()
        for i, name in enumerate(slot_names):
            wheel = SlotWheel(
                label=name,
                candidates=SLOT_CANDIDATES[name],
                final_value=final_values[i]
            )
            self.slot_wheels.add(wheel)

        # 排列滚轮
        self.slot_wheels.arrange(RIGHT, buff=0.4)
        self.slot_wheels.move_to(ORIGIN)

        # 显示所有滚轮
        self.play(
            LaggedStart(
                *[FadeIn(wheel, scale=0.9) for wheel in self.slot_wheels],
                lag_ratio=0.05
            ),
            run_time=0.8
        )

        self.wait(0.3)

        # 所有滚轮同时滚动
        self._spin_all_wheels_simultaneously()

        self.wait(1.0)

        # 淡出 Part 1 内容
        self.play(
            FadeOut(self.slot_wheels),
            run_time=0.8
        )

    def _spin_all_wheels_simultaneously(self):
        """所有滚轮同时滚动并停止"""

        # 准备每个滚轮的随机文本序列
        num_spins = 10
        all_spin_texts = []

        for wheel in self.slot_wheels:
            wheel_texts = []
            for _ in range(num_spins):
                random_val = random.choice(wheel.candidates)
                text = Tex(r"\text{" + escape_latex(random_val) + "}", font_size=16, color=TEXT_COLOR)
                text.move_to(wheel.get_center_pos())
                max_width = wheel.get_frame_width() - 0.2
                if text.width > max_width:
                    text.scale(max_width / text.width)
                wheel_texts.append(text)
            all_spin_texts.append(wheel_texts)

        # 移除初始占位符
        for wheel in self.slot_wheels:
            wheel.remove(wheel.current_value_text)

        self.play(
            *[FadeOut(wheel.current_value_text) for wheel in self.slot_wheels],
            run_time=0.1
        )

        # 显示第一帧
        current_texts = [texts[0] for texts in all_spin_texts]
        for text in current_texts:
            self.add(text)

        # 同时快速切换所有滚轮
        for i in range(1, num_spins):
            next_texts = [texts[i] for texts in all_spin_texts]
            anims = []
            for j, (curr, nxt) in enumerate(zip(current_texts, next_texts)):
                anims.append(FadeOut(curr, shift=UP * 0.1))
                anims.append(FadeIn(nxt, shift=UP * 0.1))

            self.play(*anims, run_time=0.08)
            current_texts = next_texts

        # 最终值 - 同时显示
        final_anims = []
        final_texts = []

        for j, wheel in enumerate(self.slot_wheels):
            color = KEY_COLOR if wheel.label == "Name" else VALUE_COLOR
            final_text = Tex(r"\textbf{" + escape_latex(wheel.final_value) + "}", font_size=16, color=color)
            final_text.move_to(wheel.get_center_pos())
            max_width = wheel.get_frame_width() - 0.2
            if final_text.width > max_width:
                final_text.scale(max_width / final_text.width)
            final_texts.append(final_text)

            final_anims.append(FadeOut(current_texts[j], shift=UP * 0.1))
            final_anims.append(FadeIn(final_text, scale=1.1))
            final_anims.append(Flash(wheel.frame, color=color, flash_radius=0.3, line_length=0.15))

        self.play(*final_anims, run_time=0.5)

        # 保存最终文本
        for j, wheel in enumerate(self.slot_wheels):
            wheel.final_text = final_texts[j]
            wheel.add(final_texts[j])

    def part2_natural_text_and_qa(self):
        """Part 2: 显示自然文本样本，然后展示一个 Q&A 对"""

        # 创建自然文本段落
        # "Anya Forger was born on Oct 2, 1996 in Princeton, NJ. She studied at MIT."
        natural_text = VGroup()

        # 第一句
        line1_parts = VGroup(
            Tex(r"\textbf{Anya Forger}", font_size=28, color=KEY_COLOR),
            Tex(r" was born on ", font_size=28, color=TEXT_COLOR),
            Tex(r"\textbf{Oct 2, 1996}", font_size=28, color=VALUE_COLOR),
            Tex(r" in ", font_size=28, color=TEXT_COLOR),
            Tex(r"\textbf{Princeton, NJ}", font_size=28, color=VALUE_COLOR),
            Tex(r".", font_size=28, color=TEXT_COLOR),
        )
        line1_parts.arrange(RIGHT, buff=0.08)

        # 第二句
        line2_parts = VGroup(
            Tex(r"She studied at ", font_size=28, color=TEXT_COLOR),
            Tex(r"\textbf{MIT}", font_size=28, color=VALUE_COLOR),
            Tex(r" and now works at ", font_size=28, color=TEXT_COLOR),
            Tex(r"\textbf{Meta}", font_size=28, color=VALUE_COLOR),
            Tex(r".", font_size=28, color=TEXT_COLOR),
        )
        line2_parts.arrange(RIGHT, buff=0.08)

        natural_text.add(line1_parts, line2_parts)
        natural_text.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        natural_text.move_to(ORIGIN)

        # 显示自然文本
        self.play(
            LaggedStart(
                *[FadeIn(part, shift=UP * 0.1) for part in line1_parts],
                lag_ratio=0.08
            ),
            run_time=1.2
        )
        self.play(
            LaggedStart(
                *[FadeIn(part, shift=UP * 0.1) for part in line2_parts],
                lag_ratio=0.08
            ),
            run_time=1.0
        )

        self.wait(1.0)

        # 将自然文本移到上方
        self.play(
            natural_text.animate.to_edge(UP, buff=1.0),
            run_time=0.8
        )

        self.wait(0.3)

        # 创建一个 Q&A 对
        qa_group = VGroup()

        # Question
        q_label = Tex(r"\textbf{Q:}", font_size=26, color=GREY_A)
        q_text = VGroup(
            Tex(r"When was ", font_size=26, color=TEXT_COLOR),
            Tex(r"\textbf{Anya Forger}", font_size=26, color=KEY_COLOR),
            Tex(r" born?", font_size=26, color=TEXT_COLOR),
        )
        q_text.arrange(RIGHT, buff=0.08)
        q_row = VGroup(q_label, q_text)
        q_row.arrange(RIGHT, buff=0.2)

        # Answer
        a_label = Tex(r"\textbf{A:}", font_size=26, color=GREY_A)
        a_text = Tex(r"\textbf{Oct 2, 1996}", font_size=26, color=VALUE_COLOR)
        a_row = VGroup(a_label, a_text)
        a_row.arrange(RIGHT, buff=0.2)

        qa_group.add(q_row, a_row)
        qa_group.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        qa_group.move_to(DOWN * 0.5)

        # 背景框
        qa_bg = RoundedRectangle(
            corner_radius=0.15,
            width=qa_group.width + 0.8,
            height=qa_group.height + 0.6,
            color=GREY_D,
            stroke_width=2,
            fill_color=GREY_E,
            fill_opacity=0.2
        )
        qa_bg.move_to(qa_group.get_center())

        # 显示 Q&A
        self.play(FadeIn(qa_bg, scale=0.95), run_time=0.4)
        self.play(
            LaggedStart(
                FadeIn(q_label, shift=RIGHT * 0.1),
                *[FadeIn(part, shift=RIGHT * 0.1) for part in q_text],
                lag_ratio=0.1
            ),
            run_time=0.8
        )

        self.wait(0.5)

        self.play(
            FadeIn(a_label, shift=RIGHT * 0.1),
            FadeIn(a_text, scale=1.1),
            run_time=0.6
        )

        self.wait(2)

        # 淡出所有
        self.play(
            FadeOut(natural_text),
            FadeOut(qa_bg),
            FadeOut(qa_group),
            run_time=1.0
        )

