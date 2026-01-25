from manim import *

class ReasoningProblems(Scene):
    def construct(self):
        # Title
        title = Text("Problems with Reasoning", color=WHITE, font_size=44)
        title.to_edge(UP, buff=0.8)
        
        self.play(Write(title))
        self.wait(0.5)
        
        # Point 1 - centered
        point1 = Text("1) Extends context", color=WHITE, font_size=32)
        point1.next_to(title, DOWN, buff=0.7)
        
        self.play(Write(point1))
        self.wait(0.5)
        
        # Point 2 - centered
        # point2 = Text("2) Pretrained model still needs at least one correct answer", color=WHITE, font_size=32)
        point2 = Text("2) Pretrained model sets upper-limit on reasoning performance", color=WHITE, font_size=32)
        point2.next_to(point1, DOWN, buff=0.5)
        
        self.play(Write(point2))
        self.wait(0.5)
        
        # Question after point 2 - centered
        question = Text(
            "What can we do to increase the chance of getting that correct answer?",
            color=WHITE,
            font_size=28
        )
        question.next_to(point2, DOWN, buff=0.6)
        
        self.play(Write(question))
        self.wait(1)
        
        # Answer - centered
        answer = Text("Increase model size/dataset size. Catch-22.", color=WHITE, font_size=28)
        answer.next_to(question, DOWN, buff=0.4)
        
        self.play(Write(answer))
        self.wait(1)
        
        # Fade out question and answer
        self.play(FadeOut(question), FadeOut(answer))
        self.wait(0.3)
        
        # Point 3 - centered
        point3 = Text("3) Operates on your vocabulary", color=WHITE, font_size=32)
        point3.next_to(point2, DOWN, buff=0.5)
        
        self.play(Write(point3))
        self.wait(2)
