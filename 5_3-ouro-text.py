from manim import *

class OuroModels(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        
        # Create the model name texts using Tex
        models = [
            Tex(r"Ouro-1.4B", font_size=56),
            Tex(r"Ouro-2.6B", font_size=56),
            Tex(r"Ouro-1.4B-Thinking", font_size=56),
            Tex(r"Ouro-2.6B-Thinking", font_size=56),
        ]
        
        # Arrange them vertically, center aligned
        model_group = VGroup(*models).arrange(DOWN, buff=0.5)
        model_group.move_to(ORIGIN)
        
        # Animate each one appearing
        for model in models:
            self.play(Write(model), run_time=1)
            self.wait(0.3)
        
        # Hold the final frame
        self.wait(2)
