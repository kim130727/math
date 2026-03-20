from manim import *

class LatexTest(Scene):
    def construct(self):
        eq = MathTex(r"\frac{a}{b} = c")
        self.play(Write(eq))
        self.wait()