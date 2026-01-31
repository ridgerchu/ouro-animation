"""
Special Thanks Animation
展示论文作者和贡献者的致谢动画

运行命令:
  预览:     manim -pql 15_special_thanks.py SpecialThanks
  高质量:   manim -pqh 15_special_thanks.py SpecialThanks
  1080p60:  manim -pqh --fps 60 15_special_thanks.py SpecialThanks
  4K100fps: manim -pqk --fps 100 15_special_thanks.py SpecialThanks
"""

from manim import *
import numpy as np

# ==================== 颜色配置 ====================
BG_COLOR = BLACK
TITLE_COLOR = "#FFD700"  # 金色标题
CORE_COLOR = "#E63946"   # 红色 - Core Contributors
CONTRIB_COLOR = "#3498DB"  # 蓝色 - Contributors
SUPER_COLOR = "#2ECC71"  # 绿色 - Supervision
AFFIL_COLOR = "#9B59B6"  # 紫色 - Affiliations
TEXT_COLOR = WHITE
ACCENT_COLOR = "#64b5f6"


class SpecialThanks(Scene):
    """Special Thanks 结尾动画"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # ==================== Phase 1: Special Thanks 标题 ====================
        title = Tex(r"\textbf{Special Thanks}", font_size=72)
        title.set_color(TITLE_COLOR)
        title.move_to(ORIGIN)

        # 添加发光效果
        glow = title.copy()
        glow.set_stroke(color=TITLE_COLOR, width=8, opacity=0.3)

        self.play(
            Write(title),
            run_time=1.5
        )
        self.play(
            FadeIn(glow, scale=1.02),
            run_time=0.5
        )
        self.play(
            FadeOut(glow, scale=1.05),
            run_time=0.5
        )
        self.wait(0.5)

        # 标题移到顶部
        self.play(
            title.animate.scale(0.6).to_edge(UP, buff=0.3),
            run_time=0.8
        )

        # ==================== Phase 2: Core Contributors ====================
        core_title = Tex(r"\textbf{Core Contributors}", font_size=36)
        core_title.set_color(CORE_COLOR)
        core_title.next_to(title, DOWN, buff=0.5)

        core_authors = [
            "Rui-Jie Zhu", "Zixuan Wang", "Kai Hua", "Tianyu Zhang", "Ziniu Li",
            "Haoran Que", "Boyi Wei", "Zixin Wen", "Fan Yin", "He Xing"
        ]

        # 分两行显示 Core Contributors
        core_row1 = VGroup(*[
            Tex(name, font_size=24, color=TEXT_COLOR)
            for name in core_authors[:5]
        ]).arrange(RIGHT, buff=0.5)

        core_row2 = VGroup(*[
            Tex(name, font_size=24, color=TEXT_COLOR)
            for name in core_authors[5:]
        ]).arrange(RIGHT, buff=0.5)

        core_group = VGroup(core_row1, core_row2).arrange(DOWN, buff=0.25)
        core_group.next_to(core_title, DOWN, buff=0.3)

        self.play(Write(core_title), run_time=0.6)
        self.play(
            LaggedStart(*[FadeIn(name, shift=UP*0.2) for name in core_row1], lag_ratio=0.1),
            run_time=1.2
        )
        self.play(
            LaggedStart(*[FadeIn(name, shift=UP*0.2) for name in core_row2], lag_ratio=0.1),
            run_time=1.0
        )
        self.wait(0.5)

        # ==================== Phase 3: Contributors ====================
        contrib_title = Tex(r"\textbf{Contributors}", font_size=32)
        contrib_title.set_color(CONTRIB_COLOR)
        contrib_title.next_to(core_group, DOWN, buff=0.4)

        contributors = [
            "Lu Li", "Jiajun Shi", "Kaijing Ma", "Shanda Li", "Taylor Kergan",
            "Andrew Smith", "Xingwei Qu", "Mude Hui", "Bohong Wu", "Qiyang Min",
            "Hongzhi Huang", "Xun Zhou", "Wei Ye", "Jiaheng Liu", "Jian Yang",
            "Yunfeng Shi", "Chenghua Lin", "Enduo Zhao", "Tianle Cai"
        ]

        # 分三行显示 Contributors
        contrib_row1 = VGroup(*[
            Tex(name, font_size=18, color=GREY_B)
            for name in contributors[:7]
        ]).arrange(RIGHT, buff=0.35)

        contrib_row2 = VGroup(*[
            Tex(name, font_size=18, color=GREY_B)
            for name in contributors[7:13]
        ]).arrange(RIGHT, buff=0.35)

        contrib_row3 = VGroup(*[
            Tex(name, font_size=18, color=GREY_B)
            for name in contributors[13:]
        ]).arrange(RIGHT, buff=0.35)

        contrib_group = VGroup(contrib_row1, contrib_row2, contrib_row3).arrange(DOWN, buff=0.2)
        contrib_group.next_to(contrib_title, DOWN, buff=0.25)

        self.play(Write(contrib_title), run_time=0.5)
        self.play(
            LaggedStart(
                *[FadeIn(name, shift=UP*0.15) for name in contrib_row1],
                *[FadeIn(name, shift=UP*0.15) for name in contrib_row2],
                *[FadeIn(name, shift=UP*0.15) for name in contrib_row3],
                lag_ratio=0.03
            ),
            run_time=1.5
        )
        self.wait(0.5)

        # ==================== Phase 4: Supervision ====================
        super_title = Tex(r"\textbf{Supervision}", font_size=32)
        super_title.set_color(SUPER_COLOR)
        super_title.next_to(contrib_group, DOWN, buff=0.4)

        supervisors = ["Ge Zhang", "Wenhao Huang", "Yoshua Bengio", "Jason Eshraghian"]

        super_row = VGroup(*[
            Tex(r"\textbf{" + name + "}", font_size=26, color=TEXT_COLOR)
            for name in supervisors
        ]).arrange(RIGHT, buff=0.6)
        super_row.next_to(super_title, DOWN, buff=0.25)

        self.play(Write(super_title), run_time=0.5)
        self.play(
            LaggedStart(*[FadeIn(name, shift=UP*0.2, scale=0.8) for name in super_row], lag_ratio=0.15),
            run_time=1.2
        )
        self.wait(1)

        # ==================== Phase 5: 淡出所有内容，显示机构 ====================
        all_content = VGroup(title, core_title, core_group, contrib_title, contrib_group, super_title, super_row)

        self.play(
            FadeOut(all_content),
            run_time=1
        )

        # ==================== Phase 6: Affiliations ====================
        affil_title = Tex(r"\textbf{Affiliations}", font_size=48)
        affil_title.set_color(AFFIL_COLOR)
        affil_title.to_edge(UP, buff=0.5)

        affiliations = [
            ("ByteDance Seed", "#FF6B6B"),
            ("UC Santa Cruz", "#4ECDC4"),
            ("Princeton University", "#FF9F1C"),
            ("Mila - Quebec AI Institute", "#E63946"),
            ("University of Montreal", "#457B9D"),
            ("Peking University", "#A8DADC"),
            ("Carnegie Mellon University", "#E9C46A"),
            ("University of Pennsylvania", "#264653"),
            ("Conscium", "#2A9D8F"),
            ("University of Manchester", "#F4A261"),
            ("M-A-P", "#E76F51"),
        ]

        self.play(Write(affil_title), run_time=0.8)

        # 创建机构列表
        affil_items = VGroup()
        for name, color in affiliations:
            item = VGroup(
                Dot(color=color, radius=0.08),
                Tex(name, font_size=22, color=TEXT_COLOR)
            ).arrange(RIGHT, buff=0.15)
            affil_items.add(item)

        # 分两列显示
        col1 = VGroup(*affil_items[:6]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        col2 = VGroup(*affil_items[6:]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)

        cols = VGroup(col1, col2).arrange(RIGHT, buff=1.5)
        cols.next_to(affil_title, DOWN, buff=0.6)

        self.play(
            LaggedStart(*[FadeIn(item, shift=LEFT*0.3) for item in affil_items], lag_ratio=0.08),
            run_time=2
        )
        self.wait(1.5)

        # ==================== Phase 7: Final Message ====================
        self.play(
            FadeOut(affil_title),
            FadeOut(cols),
            run_time=0.8
        )

        # 最终感谢语
        final_text = VGroup(
            Tex(r"\textbf{Thank You for Watching}", font_size=56, color=TITLE_COLOR),
            Tex(r"Scaling Latent Reasoning via Looped Language Models", font_size=28, color=GREY_B),
        ).arrange(DOWN, buff=0.4)
        final_text.move_to(ORIGIN)

        self.play(
            FadeIn(final_text[0], shift=UP*0.3, scale=0.9),
            run_time=1
        )
        self.play(
            FadeIn(final_text[1], shift=UP*0.2),
            run_time=0.8
        )

        # 添加发光脉冲效果
        self.play(
            final_text.animate.scale(1.03),
            rate_func=there_and_back,
            run_time=1
        )

        self.wait(2)

        # 最终淡出
        self.play(
            FadeOut(final_text),
            run_time=1.5
        )
        self.wait(0.5)


class SpecialThanksCompact(Scene):
    """紧凑版 Special Thanks（单屏展示）"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # 标题
        title = Tex(r"\textbf{Special Thanks}", font_size=52)
        title.set_color(TITLE_COLOR)
        title.to_edge(UP, buff=0.4)

        # Core Contributors 标题
        core_label = Tex(r"\textbf{Core Contributors}", font_size=22, color=CORE_COLOR)

        core_names = r"Rui-Jie Zhu \cdot Zixuan Wang \cdot Kai Hua \cdot Tianyu Zhang \cdot Ziniu Li \\ Haoran Que \cdot Boyi Wei \cdot Zixin Wen \cdot Fan Yin \cdot He Xing"
        core_text = Tex(core_names, font_size=18, color=TEXT_COLOR)

        core_group = VGroup(core_label, core_text).arrange(DOWN, buff=0.15)

        # Contributors 标题
        contrib_label = Tex(r"\textbf{Contributors}", font_size=20, color=CONTRIB_COLOR)

        contrib_names = r"Lu Li \cdot Jiajun Shi \cdot Kaijing Ma \cdot Shanda Li \cdot Taylor Kergan \cdot Andrew Smith \\ Xingwei Qu \cdot Mude Hui \cdot Bohong Wu \cdot Qiyang Min \cdot Hongzhi Huang \cdot Xun Zhou \\ Wei Ye \cdot Jiaheng Liu \cdot Jian Yang \cdot Yunfeng Shi \cdot Chenghua Lin \cdot Enduo Zhao \cdot Tianle Cai"
        contrib_text = Tex(contrib_names, font_size=14, color=GREY_B)

        contrib_group = VGroup(contrib_label, contrib_text).arrange(DOWN, buff=0.1)

        # Supervision 标题
        super_label = Tex(r"\textbf{Supervision}", font_size=20, color=SUPER_COLOR)
        super_names = r"\textbf{Ge Zhang} \cdot \textbf{Wenhao Huang} \cdot \textbf{Yoshua Bengio} \cdot \textbf{Jason Eshraghian}"
        super_text = Tex(super_names, font_size=20, color=TEXT_COLOR)

        super_group = VGroup(super_label, super_text).arrange(DOWN, buff=0.15)

        # 机构
        affil_label = Tex(r"\textbf{Affiliations}", font_size=18, color=AFFIL_COLOR)
        affil_names = r"ByteDance Seed \cdot UC Santa Cruz \cdot Princeton \cdot Mila \cdot U. Montreal \\ Peking U. \cdot CMU \cdot U. Penn \cdot Conscium \cdot U. Manchester \cdot M-A-P"
        affil_text = Tex(affil_names, font_size=12, color=GREY)

        affil_group = VGroup(affil_label, affil_text).arrange(DOWN, buff=0.1)

        # 整体布局
        content = VGroup(core_group, contrib_group, super_group, affil_group)
        content.arrange(DOWN, buff=0.35)
        content.next_to(title, DOWN, buff=0.4)

        # 动画
        self.play(Write(title), run_time=1)
        self.wait(0.3)

        self.play(FadeIn(core_group, shift=UP*0.2), run_time=0.8)
        self.wait(0.3)

        self.play(FadeIn(contrib_group, shift=UP*0.2), run_time=0.8)
        self.wait(0.3)

        self.play(FadeIn(super_group, shift=UP*0.2), run_time=0.8)
        self.wait(0.3)

        self.play(FadeIn(affil_group, shift=UP*0.2), run_time=0.8)
        self.wait(2)

        # 淡出
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


class SpecialThanksScrolling(Scene):
    """滚动式 Special Thanks（类似电影结尾字幕）"""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # 构建完整的致谢内容
        sections = []

        # 标题
        title = Tex(r"\textbf{Special Thanks}", font_size=64, color=TITLE_COLOR)
        sections.append(title)
        sections.append(Tex("", font_size=20))  # 空行

        # Core Contributors
        core_title = Tex(r"\textbf{Core Contributors}", font_size=36, color=CORE_COLOR)
        sections.append(core_title)

        core_authors = [
            "Rui-Jie Zhu", "Zixuan Wang", "Kai Hua", "Tianyu Zhang", "Ziniu Li",
            "Haoran Que", "Boyi Wei", "Zixin Wen", "Fan Yin", "He Xing"
        ]
        for name in core_authors:
            sections.append(Tex(name, font_size=26, color=TEXT_COLOR))

        sections.append(Tex("", font_size=30))  # 空行

        # Contributors
        contrib_title = Tex(r"\textbf{Contributors}", font_size=32, color=CONTRIB_COLOR)
        sections.append(contrib_title)

        contributors = [
            "Lu Li", "Jiajun Shi", "Kaijing Ma", "Shanda Li", "Taylor Kergan",
            "Andrew Smith", "Xingwei Qu", "Mude Hui", "Bohong Wu", "Qiyang Min",
            "Hongzhi Huang", "Xun Zhou", "Wei Ye", "Jiaheng Liu", "Jian Yang",
            "Yunfeng Shi", "Chenghua Lin", "Enduo Zhao", "Tianle Cai"
        ]
        for name in contributors:
            sections.append(Tex(name, font_size=22, color=GREY_B))

        sections.append(Tex("", font_size=30))  # 空行

        # Supervision
        super_title = Tex(r"\textbf{Supervision}", font_size=32, color=SUPER_COLOR)
        sections.append(super_title)

        supervisors = ["Ge Zhang", "Wenhao Huang", "Yoshua Bengio", "Jason Eshraghian"]
        for name in supervisors:
            sections.append(Tex(r"\textbf{" + name + "}", font_size=28, color=TEXT_COLOR))

        sections.append(Tex("", font_size=40))  # 空行

        # Affiliations
        affil_title = Tex(r"\textbf{Affiliations}", font_size=32, color=AFFIL_COLOR)
        sections.append(affil_title)

        affiliations = [
            "ByteDance Seed", "UC Santa Cruz", "Princeton University",
            "Mila - Quebec AI Institute", "University of Montreal", "Peking University",
            "Carnegie Mellon University", "University of Pennsylvania",
            "Conscium", "University of Manchester", "M-A-P"
        ]
        for name in affiliations:
            sections.append(Tex(name, font_size=20, color=GREY))

        sections.append(Tex("", font_size=60))  # 空行

        # 最终感谢
        final1 = Tex(r"\textbf{Thank You for Watching}", font_size=48, color=TITLE_COLOR)
        final2 = Tex(r"Scaling Latent Reasoning via Looped Language Models", font_size=24, color=GREY_B)
        sections.append(final1)
        sections.append(final2)

        # 组合所有内容
        all_content = VGroup(*sections).arrange(DOWN, buff=0.2)
        all_content.move_to(ORIGIN)
        all_content.shift(DOWN * (all_content.get_height() / 2 + 4))  # 从屏幕下方开始

        # 滚动动画
        scroll_distance = all_content.get_height() + 10

        self.play(
            all_content.animate.shift(UP * scroll_distance),
            run_time=25,
            rate_func=linear
        )

        self.wait(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Special Thanks Animation")
    print("=" * 60)
    print("\nCommands:")
    print("  Standard:  manim -pql 15_special_thanks.py SpecialThanks")
    print("  Compact:   manim -pql 15_special_thanks.py SpecialThanksCompact")
    print("  Scrolling: manim -pql 15_special_thanks.py SpecialThanksScrolling")
    print("  HQ:        manim -pqh 15_special_thanks.py SpecialThanks")
    print("  4K:        manim -pqk --fps 60 15_special_thanks.py SpecialThanks")
    print("=" * 60)

