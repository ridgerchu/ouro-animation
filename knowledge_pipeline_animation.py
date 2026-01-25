"""
The Knowledge Pipeline Animation
展示知识生成流程：骨架(Skeleton) → 模板(Templating) → 合成(Synthesis)
核心例子: Anya Briar Forger

运行命令:
  完整动画: manim -pql knowledge_pipeline_animation.py KnowledgePipelineAnimation
  高质量:   manim -pqh knowledge_pipeline_animation.py KnowledgePipelineAnimation
  1080p60:  manim -pqh --fps 60 knowledge_pipeline_animation.py KnowledgePipelineAnimation
"""

from manim import *
import numpy as np
import random

# ==================== 颜色配置 ====================
BACKGROUND_COLOR = "#0D1117"      # 深色背景
PRIMARY_COLOR = "#4361EE"         # 主色 - 蓝色
SECONDARY_COLOR = "#2A9D8F"       # 次色 - 青色
ACCENT_COLOR = "#E63946"          # 强调色 - 红色
GOLD_COLOR = "#F4A261"            # 金色
PURPLE_COLOR = "#7B2CBF"          # 紫色
TEAL_COLOR = "#2A9D8F"            # 青色
CARD_BG_COLOR = "#1A1F2E"         # 卡片背景
SLOT_COLOR = "#2D3748"            # 槽位颜色
TEMPLATE_COLOR = "#4A5568"        # 模板颜色
TEXT_COLOR = WHITE                # 文字颜色
DIM_COLOR = GREY_B                # 弱化颜色
DEPENDENCY_COLOR = "#FF6B6B"      # 确定性依赖颜色

# ==================== 数据配置 ====================
# 人物属性数据
PROFILE_DATA = {
    "Name": "Anya Briar Forger",
    "Birth Date": "October 2, 1996",
    "Birth City": "Princeton, NJ",
    "University": "MIT",
    "Major": "Communications",
    "Company": "Meta Platforms",
    "Company City": "Menlo Park, CA"  # 确定性依赖
}

# 随机采样候选值（用于滚动动画）
SAMPLING_CANDIDATES = {
    "Name": ["Emma Watson", "Lena Chen", "Sofia Rodriguez", "Anya Briar Forger", "Yuki Tanaka", "Clara Schmidt"],
    "Birth Date": ["March 15, 1995", "July 8, 1998", "October 2, 1996", "December 21, 1997", "April 30, 1994"],
    "Birth City": ["Boston, MA", "San Francisco, CA", "Princeton, NJ", "Seattle, WA", "Austin, TX"],
    "University": ["Stanford", "Harvard", "MIT", "Caltech", "Berkeley"],
    "Major": ["Computer Science", "Communications", "Physics", "Economics", "Biology"],
    "Company": ["Google", "Apple", "Meta Platforms", "Microsoft", "Amazon"],
}

# 公司到城市的映射（确定性依赖）
COMPANY_TO_CITY = {
    "Google": "Mountain View, CA",
    "Apple": "Cupertino, CA",
    "Meta Platforms": "Menlo Park, CA",
    "Microsoft": "Redmond, WA",
    "Amazon": "Seattle, WA",
}

# 句子模板库
TEMPLATES = {
    "Name": [
        "[Name] was born on [Date].",
        "[Name] came into the world on [Date].",
        "On [Date], [Name] was born.",
    ],
    "Birth City": [
        "[Name] grew up in [City].",
        "[Name] was raised in [City].",
        "The hometown of [Name] is [City].",
    ],
    "University": [
        "[Name] received mentorship at [University].",
        "[Name] attended [University] for higher education.",
        "[Name] studied at [University].",
    ],
    "Major": [
        "[Name] majored in [Major].",
        "[Name] specialized in [Major].",
        "The field of study for [Name] was [Major].",
    ],
    "Company": [
        "[Name] works at [Company].",
        "[Name] is employed by [Company].",
        "[Name] joined [Company].",
    ],
    "Company City": [
        "[Name] is based in [City].",
        "[Name] works out of [City].",
        "The office of [Name] is located in [City].",
    ],
}

# 生成的句子（按顺序）
FINAL_SENTENCES = [
    "Anya Briar Forger was born on October 2, 1996.",
    "She grew up in Princeton, NJ.",
    "She received mentorship at MIT.",
    "She majored in Communications.",
    "She works at Meta Platforms.",
    "She is based in Menlo Park, CA.",
]


class ProfileCard(VGroup):
    """人物卡片组件（类似 RPG 属性面板）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 卡片主体
        self.card_bg = RoundedRectangle(
            corner_radius=0.2,
            width=4.5,
            height=5.2,
            color=PRIMARY_COLOR,
            stroke_width=3,
            fill_color=CARD_BG_COLOR,
            fill_opacity=0.95
        )
        self.add(self.card_bg)

        # 卡片标题
        self.title = Tex(r"\textbf{Character Profile}", font_size=28, color=GOLD_COLOR)
        self.title.next_to(self.card_bg.get_top(), DOWN, buff=0.25)
        self.add(self.title)

        # 创建槽位
        self.slots = {}
        self.slot_values = {}
        self.slot_labels = {}

        slot_names = ["Name", "Birth Date", "Birth City", "University", "Major", "Company"]
        start_y = self.card_bg.get_top()[1] - 0.9

        for i, name in enumerate(slot_names):
            y_pos = start_y - i * 0.65
            self._create_slot(name, y_pos)

        # 隐藏的第7个槽位（Company City）
        self.hidden_slot = None
        self.hidden_slot_y = start_y - 6 * 0.65

    def _create_slot(self, name, y_pos):
        """创建单个槽位"""
        # 标签
        label = Tex(f"\\texttt{{{name}}}:", font_size=16, color=DIM_COLOR)
        label.move_to(np.array([self.card_bg.get_left()[0] + 0.3, y_pos, 0]))
        label.align_to(self.card_bg.get_left() + RIGHT * 0.2, LEFT)

        # 槽位框
        slot = RoundedRectangle(
            corner_radius=0.08,
            width=2.6,
            height=0.4,
            color=SLOT_COLOR,
            stroke_width=1.5,
            fill_color=SLOT_COLOR,
            fill_opacity=0.3
        )
        slot.move_to(np.array([self.card_bg.get_right()[0] - 1.5, y_pos, 0]))

        # 空值占位符
        placeholder = Tex(r"---", font_size=14, color=GREY_D)
        placeholder.move_to(slot.get_center())

        self.slots[name] = slot
        self.slot_labels[name] = label
        self.slot_values[name] = placeholder

        self.add(label, slot, placeholder)

    def create_hidden_slot(self):
        """创建隐藏的 Company City 槽位"""
        # 扩展卡片
        new_height = 5.85
        new_bg = RoundedRectangle(
            corner_radius=0.2,
            width=4.5,
            height=new_height,
            color=PRIMARY_COLOR,
            stroke_width=3,
            fill_color=CARD_BG_COLOR,
            fill_opacity=0.95
        )
        new_bg.move_to(self.card_bg.get_center() + DOWN * 0.325)

        # 标签
        label = Tex(r"\texttt{Company City}:", font_size=16, color=DEPENDENCY_COLOR)
        label.move_to(np.array([self.card_bg.get_left()[0] + 0.3, self.hidden_slot_y, 0]))
        label.align_to(self.card_bg.get_left() + RIGHT * 0.2, LEFT)

        # 槽位框
        slot = RoundedRectangle(
            corner_radius=0.08,
            width=2.6,
            height=0.4,
            color=DEPENDENCY_COLOR,
            stroke_width=2,
            fill_color=DEPENDENCY_COLOR,
            fill_opacity=0.15
        )
        slot.move_to(np.array([self.card_bg.get_right()[0] - 1.5, self.hidden_slot_y, 0]))

        return new_bg, label, slot

    def get_slot_center(self, name):
        """获取槽位中心位置"""
        return self.slots[name].get_center()


class TemplateBox(VGroup):
    """句子模板组件"""

    def __init__(self, template_text, color=TEMPLATE_COLOR, **kwargs):
        super().__init__(**kwargs)

        self.bg = RoundedRectangle(
            corner_radius=0.1,
            width=7,
            height=0.6,
            color=color,
            stroke_width=1.5,
            fill_color=color,
            fill_opacity=0.2
        )

        self.text = Tex(template_text, font_size=18, color=TEXT_COLOR)
        self.text.move_to(self.bg.get_center())

        # 如果文本太长，缩放
        if self.text.width > self.bg.width - 0.3:
            self.text.scale((self.bg.width - 0.3) / self.text.width)

        self.add(self.bg, self.text)


class KnowledgePipelineAnimation(Scene):
    """知识流水线动画 - 主场景"""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # 运行三个阶段的动画
        self.phase1_skeleton()
        self.phase2_templating()
        self.phase3_synthesis()

    def phase1_skeleton(self):
        """Phase 1: 知识的"骨架" (The Skeleton)"""

        # 阶段标题
        phase_title = Tex(
            r"\textbf{Step 1: The Skeleton}",
            font_size=36,
            color=GOLD_COLOR
        )
        phase_title.to_edge(UP, buff=0.4)

        subtitle = Tex(
            r"\textit{Building the Knowledge Structure}",
            font_size=22,
            color=DIM_COLOR
        )
        subtitle.next_to(phase_title, DOWN, buff=0.15)

        self.play(
            FadeIn(phase_title, shift=DOWN * 0.3),
            FadeIn(subtitle, shift=DOWN * 0.2),
            run_time=1
        )

        # 创建人物卡片
        self.card = ProfileCard()
        self.card.move_to(LEFT * 3.5)

        self.play(
            FadeIn(self.card, scale=0.9),
            run_time=1
        )

        self.wait(0.5)

        # 采样说明
        sampling_label = Tex(
            r"\textbf{Random Sampling}",
            font_size=20,
            color=SECONDARY_COLOR
        )
        sampling_label.move_to(RIGHT * 3 + UP * 2)

        self.play(Write(sampling_label), run_time=0.5)

        # 依次对每个属性进行采样动画
        slot_names = ["Name", "Birth Date", "Birth City", "University", "Major", "Company"]

        for slot_name in slot_names:
            self._animate_sampling(slot_name)

        self.wait(0.5)

        # 显示确定性依赖
        dependency_label = Tex(
            r"\textbf{Deterministic Dependency}",
            font_size=20,
            color=DEPENDENCY_COLOR
        )
        dependency_label.move_to(RIGHT * 3 + UP * 1)

        self.play(
            Transform(sampling_label, dependency_label),
            run_time=0.6
        )

        # 创建隐藏槽位动画
        new_bg, company_city_label, company_city_slot = self.card.create_hidden_slot()

        # 从 Company 伸出箭头
        company_slot = self.card.slots["Company"]
        arrow = CurvedArrow(
            company_slot.get_right() + RIGHT * 0.1,
            company_city_slot.get_left() + LEFT * 0.1 + DOWN * 0.3,
            color=DEPENDENCY_COLOR,
            stroke_width=3,
            angle=-TAU / 4
        )

        # 动画：扩展卡片、显示新槽位
        self.play(
            Transform(self.card.card_bg, new_bg),
            run_time=0.6
        )

        self.play(
            FadeIn(company_city_label),
            FadeIn(company_city_slot),
            Create(arrow),
            run_time=0.8
        )

        # 自动填充 Company City
        city_value = Tex(
            r"\text{Menlo Park, CA}",
            font_size=14,
            color=DEPENDENCY_COLOR
        )
        city_value.move_to(company_city_slot.get_center())

        self.play(
            FadeIn(city_value, scale=1.2),
            Flash(company_city_slot, color=DEPENDENCY_COLOR, flash_radius=0.4),
            run_time=0.8
        )

        # 存储用于后续阶段
        self.card.slots["Company City"] = company_city_slot
        self.card.slot_values["Company City"] = city_value
        self.arrow = arrow
        self.company_city_label = company_city_label
        self.sampling_label = sampling_label
        self.phase_title = phase_title
        self.subtitle = subtitle

        self.wait(1)

        # 淡出采样标签
        self.play(FadeOut(self.sampling_label), run_time=0.3)

    def _animate_sampling(self, slot_name):
        """对单个槽位进行采样动画"""
        slot = self.card.slots[slot_name]
        placeholder = self.card.slot_values[slot_name]
        candidates = SAMPLING_CANDIDATES[slot_name]
        final_value = PROFILE_DATA[slot_name]

        # 创建滚动文本
        scroll_texts = VGroup()
        for candidate in candidates:
            text = Tex(f"\\text{{{candidate}}}", font_size=14, color=TEXT_COLOR)
            text.move_to(slot.get_center())
            scroll_texts.add(text)

        # 隐藏占位符
        self.play(FadeOut(placeholder), run_time=0.1)

        # 快速滚动效果
        current_idx = 0
        scroll_texts[current_idx].set_opacity(1)
        self.add(scroll_texts[current_idx])

        for _ in range(8):  # 滚动8次
            next_idx = (current_idx + 1) % len(candidates)
            self.play(
                scroll_texts[current_idx].animate.set_opacity(0).shift(UP * 0.2),
                FadeIn(scroll_texts[next_idx], shift=UP * 0.2),
                run_time=0.08
            )
            self.remove(scroll_texts[current_idx])
            current_idx = next_idx

        # 定格到最终值
        final_text = Tex(f"\\text{{{final_value}}}", font_size=14, color=GOLD_COLOR)
        final_text.move_to(slot.get_center())

        # 如果文本太长，缩放
        if final_text.width > slot.width - 0.2:
            final_text.scale((slot.width - 0.2) / final_text.width)

        self.play(
            FadeOut(scroll_texts[current_idx]),
            FadeIn(final_text, scale=1.1),
            slot.animate.set_stroke(color=GOLD_COLOR, width=2),
            run_time=0.3
        )

        self.card.slot_values[slot_name] = final_text

        self.wait(0.2)

    def phase2_templating(self):
        """Phase 2: 模版的"外衣" (The Templating)"""

        # 更新阶段标题
        new_title = Tex(
            r"\textbf{Step 2: The Templating}",
            font_size=36,
            color=GOLD_COLOR
        )
        new_title.to_edge(UP, buff=0.4)

        new_subtitle = Tex(
            r"\textit{Injecting Values into Templates}",
            font_size=22,
            color=DIM_COLOR
        )
        new_subtitle.next_to(new_title, DOWN, buff=0.15)

        self.play(
            Transform(self.phase_title, new_title),
            Transform(self.subtitle, new_subtitle),
            run_time=0.8
        )

        # 将卡片移到更左边
        self.play(
            self.card.animate.shift(LEFT * 0.5),
            FadeOut(self.arrow),
            run_time=0.6
        )

        # 模板库标签
        template_lib_label = Tex(
            r"\textbf{Template Library (50+ templates)}",
            font_size=18,
            color=SECONDARY_COLOR
        )
        template_lib_label.move_to(RIGHT * 2.5 + UP * 2)

        self.play(Write(template_lib_label), run_time=0.5)

        # 存储生成的句子
        self.generated_sentences = []

        # 对每个属性进行模板注入
        attributes = [
            ("Name", "Birth Date", "[Name] was born on [Date]."),
            ("Birth City", None, "[Name] grew up in [City]."),
            ("University", None, "[Name] received mentorship at [University]."),
            ("Major", None, "[Name] majored in [Major]."),
            ("Company", None, "[Name] works at [Company]."),
            ("Company City", None, "[Name] is based in [City]."),
        ]

        sentence_y_start = 1.5

        for i, (attr1, attr2, template) in enumerate(attributes):
            sentence = self._animate_templating(
                attr1, attr2, template,
                y_pos=sentence_y_start - i * 0.55,
                index=i
            )
            self.generated_sentences.append(sentence)

        self.template_lib_label = template_lib_label

        self.wait(0.5)

    def _animate_templating(self, attr1, attr2, template_text, y_pos, index):
        """对单个属性进行模板注入动画"""

        # 创建模板框（显示在中央）
        template_box = TemplateBox(template_text, color=TEMPLATE_COLOR)
        template_box.move_to(RIGHT * 2.5 + UP * y_pos)

        # 模板滚动效果（简化版）
        self.play(FadeIn(template_box, shift=LEFT * 0.3), run_time=0.3)

        # 高亮选中
        self.play(
            template_box.bg.animate.set_stroke(color=GOLD_COLOR, width=2),
            run_time=0.2
        )

        # 获取要注入的值
        if attr1 == "Name" and attr2 == "Birth Date":
            # 特殊情况：第一句包含 Name 和 Date
            name_value = self.card.slot_values["Name"].copy()
            date_value = self.card.slot_values["Birth Date"].copy()

            # 值飞入动画
            self.play(
                name_value.animate.move_to(template_box.get_center() + LEFT * 1.5).scale(0.8),
                date_value.animate.move_to(template_box.get_center() + RIGHT * 1).scale(0.8),
                run_time=0.5
            )

            # 合成最终句子
            final_sentence = Tex(
                FINAL_SENTENCES[index],
                font_size=16,
                color=TEXT_COLOR
            )
        else:
            # 其他属性
            value = self.card.slot_values[attr1].copy()

            self.play(
                value.animate.move_to(template_box.get_center()).scale(0.8),
                run_time=0.4
            )

            final_sentence = Tex(
                FINAL_SENTENCES[index],
                font_size=16,
                color=TEXT_COLOR
            )

        final_sentence.move_to(template_box.get_center())

        # 如果文本太长，缩放
        if final_sentence.width > 6.5:
            final_sentence.scale(6.5 / final_sentence.width)

        # 转换为最终句子
        self.play(
            FadeOut(template_box),
            FadeIn(final_sentence),
            run_time=0.4
        )

        # 清理飞入的值
        if attr1 == "Name" and attr2 == "Birth Date":
            self.remove(name_value, date_value)
        else:
            self.remove(value)

        return final_sentence

    def phase3_synthesis(self):
        """Phase 3: 最终的"合成" (The Synthesis)"""

        # 更新阶段标题
        new_title = Tex(
            r"\textbf{Step 3: The Synthesis}",
            font_size=36,
            color=GOLD_COLOR
        )
        new_title.to_edge(UP, buff=0.4)

        new_subtitle = Tex(
            r"\textit{Assembling the Final Paragraph}",
            font_size=22,
            color=DIM_COLOR
        )
        new_subtitle.next_to(new_title, DOWN, buff=0.15)

        self.play(
            Transform(self.phase_title, new_title),
            Transform(self.subtitle, new_subtitle),
            FadeOut(self.template_lib_label),
            run_time=0.8
        )

        # 淡出卡片
        self.play(
            FadeOut(self.card),
            FadeOut(self.company_city_label),
            run_time=0.6
        )

        # 重新排列句子（固定顺序）
        order_label = Tex(
            r"\textbf{Fixed Order: Date → City → Univ → Major → Company → Work City}",
            font_size=18,
            color=SECONDARY_COLOR
        )
        order_label.move_to(UP * 2.5)

        self.play(Write(order_label), run_time=0.6)

        # 将句子移动到屏幕中央，按顺序堆叠
        target_positions = []
        start_y = 1.5
        for i in range(6):
            target_positions.append(np.array([0, start_y - i * 0.5, 0]))

        # 动画：句子像积木一样堆叠
        animations = []
        for i, sentence in enumerate(self.generated_sentences):
            animations.append(sentence.animate.move_to(target_positions[i]))

        self.play(*animations, run_time=1.2)

        self.wait(0.5)

        # 合并动画：句子间距缩小
        merge_label = Tex(
            r"\textbf{Merging into Paragraph}",
            font_size=18,
            color=TEAL_COLOR
        )
        merge_label.move_to(UP * 2.5)

        self.play(
            Transform(order_label, merge_label),
            run_time=0.4
        )

        # 缩小间距
        merged_positions = []
        start_y = 1.0
        for i in range(6):
            merged_positions.append(np.array([0, start_y - i * 0.38, 0]))

        merge_anims = []
        for i, sentence in enumerate(self.generated_sentences):
            merge_anims.append(sentence.animate.move_to(merged_positions[i]))

        self.play(*merge_anims, run_time=0.8)

        self.wait(0.5)

        # 代词替换动画
        pronoun_label = Tex(
            r"\textbf{Pronoun Refinement: ``Anya Briar Forger'' → ``She''}",
            font_size=18,
            color=ACCENT_COLOR
        )
        pronoun_label.move_to(UP * 2.5)

        self.play(
            Transform(order_label, pronoun_label),
            run_time=0.4
        )

        # 替换后续句子中的名字
        new_sentences_text = [
            "Anya Briar Forger was born on October 2, 1996.",  # 保留全名
            "She grew up in Princeton, NJ.",
            "She received mentorship at MIT.",
            "She majored in Communications.",
            "She works at Meta Platforms.",
            "She is based in Menlo Park, CA.",
        ]

        # 对句子 2-6 进行代词替换动画
        for i in range(1, 6):
            old_sentence = self.generated_sentences[i]
            new_sentence = Tex(
                new_sentences_text[i],
                font_size=16,
                color=TEXT_COLOR
            )
            new_sentence.move_to(merged_positions[i])

            if new_sentence.width > 6.5:
                new_sentence.scale(6.5 / new_sentence.width)

            # 闪烁并替换
            self.play(
                old_sentence.animate.set_color(ACCENT_COLOR),
                run_time=0.15
            )
            self.play(
                Transform(old_sentence, new_sentence),
                run_time=0.25
            )

        self.wait(0.5)

        # 最终段落框
        final_bg = RoundedRectangle(
            corner_radius=0.15,
            width=7.5,
            height=3.0,
            color=GOLD_COLOR,
            stroke_width=2,
            fill_color=CARD_BG_COLOR,
            fill_opacity=0.8
        )
        final_bg.move_to(DOWN * 0.3)

        # 将所有句子组合
        all_sentences = VGroup(*self.generated_sentences)

        self.play(
            Create(final_bg),
            all_sentences.animate.move_to(final_bg.get_center()),
            run_time=0.8
        )

        # 完成标签
        complete_label = Tex(
            r"\textbf{Knowledge Generation Complete!}",
            font_size=24,
            color=GOLD_COLOR
        )
        complete_label.next_to(final_bg, DOWN, buff=0.5)

        self.play(
            FadeIn(complete_label, scale=1.2),
            Flash(final_bg, color=GOLD_COLOR, flash_radius=1.5),
            run_time=1
        )

        self.wait(2)

        # 淡出
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )


class KnowledgePipelineCompact(Scene):
    """紧凑版知识流水线动画（适合快速演示）"""

    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # 标题
        title = Tex(
            r"\textbf{The Knowledge Pipeline}",
            font_size=40,
            color=GOLD_COLOR
        )
        title.to_edge(UP, buff=0.5)

        self.play(Write(title), run_time=1)

        # 三个阶段的图标
        step1 = VGroup(
            RoundedRectangle(width=2.5, height=1.5, corner_radius=0.1, color=PRIMARY_COLOR, fill_opacity=0.2),
            Tex(r"\textbf{1. Skeleton}", font_size=18, color=PRIMARY_COLOR),
            Tex(r"\text{Sampling attributes}", font_size=12, color=DIM_COLOR),
        )
        step1[1].move_to(step1[0].get_center() + UP * 0.3)
        step1[2].move_to(step1[0].get_center() + DOWN * 0.2)

        step2 = VGroup(
            RoundedRectangle(width=2.5, height=1.5, corner_radius=0.1, color=SECONDARY_COLOR, fill_opacity=0.2),
            Tex(r"\textbf{2. Templating}", font_size=18, color=SECONDARY_COLOR),
            Tex(r"\text{Filling templates}", font_size=12, color=DIM_COLOR),
        )
        step2[1].move_to(step2[0].get_center() + UP * 0.3)
        step2[2].move_to(step2[0].get_center() + DOWN * 0.2)

        step3 = VGroup(
            RoundedRectangle(width=2.5, height=1.5, corner_radius=0.1, color=ACCENT_COLOR, fill_opacity=0.2),
            Tex(r"\textbf{3. Synthesis}", font_size=18, color=ACCENT_COLOR),
            Tex(r"\text{Merging \& Pronouns}", font_size=12, color=DIM_COLOR),
        )
        step3[1].move_to(step3[0].get_center() + UP * 0.3)
        step3[2].move_to(step3[0].get_center() + DOWN * 0.2)

        # 排列
        step1.move_to(LEFT * 4 + UP * 1)
        step2.move_to(ORIGIN + UP * 1)
        step3.move_to(RIGHT * 4 + UP * 1)

        # 箭头
        arrow1 = Arrow(step1.get_right(), step2.get_left(), buff=0.2, color=GREY_B)
        arrow2 = Arrow(step2.get_right(), step3.get_left(), buff=0.2, color=GREY_B)

        self.play(
            LaggedStart(
                FadeIn(step1, scale=0.9),
                Create(arrow1),
                FadeIn(step2, scale=0.9),
                Create(arrow2),
                FadeIn(step3, scale=0.9),
                lag_ratio=0.3
            ),
            run_time=2
        )

        # 示例人物
        example = Tex(
            r"\textit{Example: Anya Briar Forger}",
            font_size=20,
            color=GOLD_COLOR
        )
        example.move_to(DOWN * 0.5)

        self.play(Write(example), run_time=0.8)

        # 结果段落
        result_text = Tex(
            r"\text{``Anya Briar Forger was born on October 2, 1996. She grew up in...}",
            font_size=16,
            color=TEXT_COLOR
        )
        result_text.move_to(DOWN * 1.5)

        result_box = SurroundingRectangle(result_text, color=GOLD_COLOR, buff=0.15)

        self.play(
            Write(result_text),
            Create(result_box),
            run_time=1
        )

        self.wait(2)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)


if __name__ == "__main__":
    print("=" * 60)
    print("The Knowledge Pipeline Animation - Manim")
    print("=" * 60)
    print("\n运行命令:")
    print("  完整版: manim -pql knowledge_pipeline_animation.py KnowledgePipelineAnimation")
    print("  紧凑版: manim -pql knowledge_pipeline_animation.py KnowledgePipelineCompact")
    print("  高质量: manim -pqh knowledge_pipeline_animation.py KnowledgePipelineAnimation")
    print("  1080p60: manim -pqh --fps 60 knowledge_pipeline_animation.py KnowledgePipelineAnimation")
    print("=" * 60)

