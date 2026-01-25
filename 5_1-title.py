from manim import *

class HeaderAnimation(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = BLACK
        
        # Create the header text using Tex for proper LaTeX rendering
        line1 = Tex(r"Scaling Latent Reasoning via Looped", font_size=56)
        line2 = Tex(r"Language Models", font_size=56)
        
        # Arrange the lines vertically
        header = VGroup(line1, line2).arrange(DOWN, buff=0.4)
        header.move_to(ORIGIN)
        
        # Animation sequence
        # First, write the first line with a typewriter effect
        self.play(Write(line1), run_time=2)
        self.wait(0.3)
        
        # Then write the second line
        self.play(Write(line2), run_time=1.5)
        self.wait(0.5)
        
        # Add a subtle pulse effect
        self.play(
            header.animate.scale(1.05),
            rate_func=there_and_back,
            run_time=0.6
        )
        
        # Add a glow/emphasis effect by creating a copy
        glow = header.copy()
        glow.set_stroke(color=WHITE, width=2, opacity=0.3)
        
        self.play(
            FadeIn(glow, scale=1.02),
            run_time=0.5
        )
        self.play(
            FadeOut(glow, scale=1.05),
            run_time=0.5
        )
        
        # Hold the final frame
        self.wait(2)


class HeaderAnimationFancy(Scene):
    """More elaborate animation with underline effect"""
    def construct(self):
        self.camera.background_color = BLACK
        
        # Create the text using Tex
        line1 = Tex(r"Scaling Latent Reasoning via Looped", font_size=54)
        line2 = Tex(r"Language Models", font_size=54)
        
        header = VGroup(line1, line2).arrange(DOWN, buff=0.5)
        header.move_to(ORIGIN)
        
        # Create underline
        # underline = Line(
        #     start=line2.get_left() + DOWN * 0.3,
        #     end=line2.get_right() + DOWN * 0.3,
        #     color="#64b5f6",
        #     stroke_width=3
        # )
        
        # Animation: Fade in from below
        header.shift(DOWN * 0.5)
        header.set_opacity(0)
        
        self.play(
            header.animate.shift(UP * 0.5).set_opacity(1),
            run_time=1.2,
            rate_func=smooth
        )
        
        self.wait(0.3)
        
        # # Draw underline
        # self.play(Create(underline), run_time=0.8)
        
        # Subtle breathing animation
        self.play(
            header.animate.scale(1.02),
            # underline.animate.scale(1.02),
            rate_func=there_and_back_with_pause,
            run_time=1.5
        )
        
        self.wait(2)

