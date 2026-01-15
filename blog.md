Extreme Optimization: Building a Mastermind Game in Pure i386 Assembly

Cover GIF Recommendation: Use a wide (5:2 aspect ratio) animated GIF of the register-packing animation (bits lighting up as the combination forms in one register). Render with high quality for best visual impact.

Why I Built This - A Personal Journey

My path into engineering started with a fascination for how things really work at the deepest level.

I began my university studies at the Medical Faculty in Novi Sad, diving into the intricate mechanics of the human body. I passed anatomy, histology, and embryology with perfect 10s, mastering the fundamentals of healthy human function. But something pulled me toward building systems rather than studying them. I switched to Software Engineering and Information Technologies at the Faculty of Technical Sciences.

There, I focused relentlessly on strong fundamentals: mathematics, algorithms, data structures, and core computer science. Those foundations opened doors to every branch of engineering, from embedded systems to distributed computing. In the end, I chose artificial intelligence, a field that felt like the ultimate fusion of rigor and creativity.

Seven years ago, in 2019 (long before AI tools could write code for us), I had just passed my Computer Architecture class. The grade was in, nothing left to prove for the transcript. But I could not let go of assembly.

Out of pure curiosity and a burning desire to truly understand the machine, I decided to build something ambitious: a complete Mastermind game (the Serbian "Skocko" variant with 6 symbols and 4 positions) entirely in 32-bit x86 assembly.

No deadlines, no requirements. Just me, the instruction set reference, and the joy of making every cycle count.

That project followed the exact learning philosophy Andrej Karpathy once described:

"How to become expert at thing: 
1 iteratively take on concrete projects and accomplish them depth wise, learning "on demand" 
2 teach/summarize everything you learn in your own words 
3 only compare yourself to younger you, never to others"

This was pure depth-first exploration. I learned bit tricks, stack manipulation, and syscalls only when I needed them. Now, writing this article is step 2, sharing the journey in my own words.

Today, as a teacher, I tell my students the same thing: your projects tell a story about you.

Every repository, every commit, every README is a chapter in your learning path. Do not be ashamed of the code you wrote while learning. It will never be perfect, and that is okay. Everyone who looks at it (if they even read the code) understands it was written during exploration and can probably be improved.

The truth is, almost nobody will read the actual code. Most people will glance at the project titles and make up their own story about what fascinated you. Those titles will follow you: from early experiments, through course projects, to your bachelor's, master's, and maybe even PhD thesis, documents that, let's be honest, very few people will ever read in full.

But all of it builds the foundation of your narrative. It gives you concrete artifacts to point to when you tell your story.

So go make those GitHub READMEs beautiful. Polish the descriptions, add screenshots, explain what you learned. Because one day, you will look back and see how far you have come, just like I do when I open this old assembly Mastermind project.

Section 1: The Core Trick - One Register Holds the Entire Combination

The single biggest optimization: the whole 4-symbol combination fits in one 32-bit register.

Each symbol is encoded as a single set bit in an 8-bit field:
- 1 → 0b10000000 (SKOCKO)
- 2 → 0b01000000 (TREF)
- 3 → 0b00100000 (PIK)
- 4 → 0b00010000 (HERC)
- 5 → 0b00001000 (KARO)
- 6 → 0b00000100 (ZVEZDA)

Four symbols → four bytes packed into one register. No arrays, almost no memory traffic.

In the simple C version I wrote for comparison (using int guess[4]), every combination requires four separate 32-bit loads/stores. My assembly needs only one 32-bit load per candidate.

Across the ~8,000-10,000 candidate checks in a full game, this saves roughly three-quarters of memory accesses in the hot path, a massive win on old i386 hardware.

Manim Animation Code for this Section (register packing execution - shows rorb/rorl instructions placing bits step-by-step):

from manim import *

class RegisterPackingExecution(Scene):
    def construct(self):
        title = Tex(r"Executing Bit Placement in Register").scale(0.8)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        ebx = Rectangle(width=4, height=0.8, color=BLUE)
        ebx_label = Tex(r"%ebx").next_to(ebx, UP)
        ebx_value = Integer(0b10000000100000001000000010000000, color=WHITE).move_to(ebx)  # initial mask

        code = Code(code=r"""
rorb %cl, %bl
rorl $8, %ebx
""", language="asm", font_size=24).to_corner(UL)

        self.play(Create(ebx), Write(ebx_label), Write(ebx_value), Write(code))

        for i in range(4):
            instr1 = code.code[0][0].copy().set_color(YELLOW)
            self.play(Transform(instr1, instr1), run_time=0.8)

            new_val = ebx_value.get_value() >> (3 * 8) | (ebx_value.get_value() & 0xFF) << (32 - 3 * 8) >> (i*8)
            ebx_value.become(Integer(new_val).move_to(ebx))
            self.play(ebx_value.animate.set_color(GREEN), run_time=1)

            instr2 = code.code[1][0].copy().set_color(YELLOW)
            self.play(Transform(instr2, instr2), run_time=0.8)
            self.play(ebx_value.animate.shift(RIGHT * 0.5), run_time=0.5)

        final = Tex(r"Full combination packed!").next_to(ebx, DOWN)
        self.play(Write(final))
        self.wait(2)

Section 2: Bit Magic - Feedback Calculation in Pure Registers

Feedback uses only bit operations and rotations, no array indexing.

Exact matches: AND guess & secret, count set bits while clearing.
Misplaced: XOR to remove exacts, then test-and-clear loop with 8-bit rotations.

In the C version, feedback uses frequency count arrays and loops, many branches and memory accesses.

My assembly version is ~35-45 instructions per comparison, almost entirely register-bound. Savings: roughly 2× fewer instructions per histogram call, plus zero cache misses.

Manim Animation Code for this Section (exact match execution - highlights AND, test, incl, shrl instructions with visual bit clearing):

from manim import *

class ExactMatchExecution(Scene):
    def construct(self):
        title = Tex(r"Executing Exact Matches (AND + Count)").scale(0.8)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        eax = Tex(r"%eax (guess): 10100000 ...").scale(0.7).to_corner(UL)
        ebx = Tex(r"%ebx (secret): 10000000 ...").scale(0.7).next_to(eax, DOWN)
        edx = Rectangle(width=5, height=0.8, color=YELLOW)
        edx_label = Tex(r"%edx (AND result)").next_to(edx, UP)
        edx_bits = VGroup(*[Circle(radius=0.2, color=RED if i%2==0 else WHITE) for i in range(8)]).arrange(RIGHT).move_to(edx)

        esi = Integer(0).next_to(edx, DOWN)
        esi_label = Tex(r"%esi (red count)")

        code = Code(code=r"""
andl %eax, %edx
testb %dl, %dl
jz end
incl %esi
shrl $8, %edx
""", language="asm", font_size=20).to_corner(UR)

        self.play(Write(eax), Write(ebx), Create(edx), Write(edx_label), Write(edx_bits), Write(esi), Write(esi_label), Write(code))

        for step in range(4):
            if step == 0:
                self.play(code.code[0][0].animate.set_color(YELLOW))

            if step % 2 == 0:
                self.play(code.code[1][0].animate.set_color(YELLOW))
                self.play(esi.animate.increment_value(1).set_color(GREEN))
                self.play(code.code[2][0].animate.set_color(YELLOW))

            self.play(code.code[3][0].animate.set_color(YELLOW))
            self.play(edx_bits.animate.shift(LEFT * 1), run_time=0.8)

        final = Tex(r"Red pegs counted in registers!").scale(0.8)
        self.play(Write(final))
        self.wait(2)

Section 3: Full Possibility Elimination - Entropy Reduction and Knuth's Insight

All 1296 possible codes are pre-generated. After each guess, filter to only those that would produce the exact same feedback.

Loads one packed 32-bit candidate at a time → extremely tight loop.

C version: 4 loads per candidate + frequency arrays.
Assembly: 1 load + register bit ops → ~2.5-3× faster elimination phase.

But the real beauty is deeper: this filtering reduces entropy step by step.

Initially: 1296 possibilities → log₂(1296) ≈ 10.34 bits of uncertainty.

Each guess partitions the remaining set based on the 14 possible feedback patterns. A good guess balances those partitions, maximizing information gain (i.e., minimizing expected remaining entropy).

Donald Knuth proved in 1977 that with optimal choices (minimax on worst-case remaining possibilities), the game can be solved in at most 5 guesses in the worst case.

My code already tracks remaining count. Adding one scoring pass would turn it into a perfect Knuth solver.

Manim Animation Code for this Section (elimination loop execution - shows movl load, call histogram, conditional keep/eliminate):

from manim import *

class EliminationLoopExecution(Scene):
    def construct(self):
        title = Tex(r"Elimination Loop Execution").scale(0.8)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        memory = VGroup(*[Rectangle(width=1, height=0.5, color=GREY) for _ in range(10)]).arrange(RIGHT, buff=0.2)
        memory_label = Tex(r"Memory array (candidates)").next_to(memory, UP)

        ebx = Rectangle(width=3, height=0.8, color=BLUE)
        ebx_label = Tex(r"%ebx (current candidate)").next_to(ebx, UP)

        ecx = Integer(0).next_to(ebx, DOWN)

        code = Code(code=r"""
movl sve_kombinacije(,%ecx,4), %ebx
call histogram
cmpl crveni, %esi
jne skip
""", language="asm", font_size=20).to_edge(RIGHT)

        self.play(Create(memory), Write(memory_label), Create(ebx), Write(ebx_label), Write(ecx), Write(code))

        for i in range(5):
            self.play(code.code[0][0].animate.set_color(YELLOW))
            cand = memory[i].copy().move_to(ebx)
            self.play(Transform(cand, cand.set_color(GREEN)))

            self.play(code.code[1][0].animate.set_color(YELLOW))
            if i % 2 == 0:
                self.play(memory[i].animate.set_color(GREEN))
            else:
                self.play(FadeOut(memory[i]))

            self.play(ecx.animate.increment_value(1))

        final = Tex(r"Remaining set filtered!").scale(0.8)
        self.play(Write(final))
        self.wait(2)

Manim Animation Code for this Section (entropy reduction - shrinking grid of dots with decreasing bit count):

from manim import *

class EntropyReduction(Scene):
    def construct(self):
        title = Tex(r"Entropy Reduction in Mastermind").scale(0.9)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        initial = Tex(r"Initial: 1296 possibilities $\\approx$ 10.34 bits").scale(0.8)
        self.play(Write(initial))

        grid = VGroup(*[Dot(radius=0.05, color=BLUE) for _ in range(1296)])
        grid.arrange_in_grid(rows=36, cols=36, buff=0.2)
        self.play(FadeIn(grid), run_time=2)

        remain_counts = [1296, 432, 144, 48, 12, 3, 1]
        bit_values = [10.34, 8.75, 7.17, 5.58, 3.58, 1.58, 0.0]

        for i in range(1, len(remain_counts)):
            to_fade = len(grid) - remain_counts[i]
            new_text = Tex(fr"After guess {i}: {remain_counts[i]} left $\\approx$ {bit_values[i]:.2f} bits").scale(0.8)
            entropy_bar = Rectangle(width=bit_values[i]/1.1, height=0.8, color=GREEN)
            bar_group = VGroup(entropy_bar, new_text.next_to(entropy_bar, UP))

            self.play(FadeOut(grid[:to_fade]), FadeOut(initial), FadeIn(bar_group), run_time=1.2)
            initial = new_text
            self.wait(0.8)

        final = Tex(r"Solved in $\leq$5 guesses (Knuth 1977)").scale(1).set_color(GOLD)
        self.play(Write(final))
        self.wait(3)

Section 4: The Wild Display Hack - Stack Overwriting for printf

Push 48 empty string pointers once, then overwrite only the needed slots for the current row before each printf. Empty pegs stay empty by skipping with subl $esp.

C version rebuilds all arguments fresh → dozens of pushes/writes per screen.
Assembly: ~7-8 pushes per turn → ~3-4× less display overhead.

Manim Animation Code for this Section (stack overwrite execution - highlights subl $esp skip and selective pushl for pegs/symbols):

from manim import *

class StackOverwriteExecution(Scene):
    def construct(self):
        title = Tex(r"Stack Overwrite Execution").scale(0.8)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        stack = VGroup(*[Rectangle(width=2, height=0.5, color=GREY).add(Tex("empty").move_to(rect)) for rect in range(15)]).arrange(DOWN, buff=0.1)
        esp = Arrow(start=stack[0].get_top(), end=stack[-1].get_bottom(), color=RED)
        esp_label = Tex(r"%esp $\downarrow$").next_to(esp, LEFT)

        code = Code(code=r"""
subl %eax, %esp  # skip empties
pushl $znak_zuti
pushl $znak_crveni
""", language="asm", font_size=20).to_edge(RIGHT)

        self.play(Create(stack), Create(esp), Write(esp_label), Write(code))

        self.play(code.code[0][0].animate.set_color(YELLOW))
        self.play(esp.animate.shift(DOWN * 3))

        self.play(code.code[1][0].animate.set_color(YELLOW))
        new_yellow = Tex(r"● yellow").move_to(stack[5])
        self.play(Transform(stack[5][0], new_yellow), stack[5].animate.set_color(YELLOW))

        self.play(code.code[2][0].animate.set_color(YELLOW))
        new_red = Tex(r"● red").move_to(stack[6])
        self.play(Transform(stack[6][0], new_red), stack[6].animate.set_color(RED))

        final = Tex(r"Only needed slots updated!").scale(0.8)
        self.play(Write(final))
        self.wait(2)

Section 5: Unrolling and Skipping Conventions

Six guess blocks fully unrolled with hardcoded offsets. No loop branches, no CDECL overhead in hot paths.

C version uses clean loops and functions → extra branches and stack work.
Assembly saves ~100-200 executed instructions per game.

Section 6: The Payoff - Benchmarks

Both versions compiled with -m32 -O3. Identical logic.

My assembly: ~2-3 ms per full game.
C: ~5-8 ms.

Overall ~2-2.5× faster, almost entirely from bit-packing and register-only operations.

Manim Animation Code for this Section (benchmark bar chart):

from manim import *

class BenchmarkChart(Scene):
    def construct(self):
        title = Tex(r"Benchmark: Assembly vs C").scale(0.8)
        self.play(Write(title))
        self.wait(1)

        axes = Axes(x_range=[0, 3], y_range=[0, 10, 2], axis_config={"color": BLUE})
        labels = axes.get_axis_labels(x_label="Version", y_label="Time (ms)")

        asm_bar = BarChart(values=[2.5], bar_colors=[GREEN], y_range=[0, 10, 2], x_length=4)
        c_bar = BarChart(values=[6.5], bar_colors=[RED], y_range=[0, 10, 2], x_length=4)

        asm_label = Tex("Assembly").next_to(asm_bar, DOWN)
        c_label = Tex("C").next_to(c_bar, DOWN)

        self.play(Create(axes), Write(labels))
        self.play(Create(asm_bar), Write(asm_label))
        self.play(Create(c_bar), Write(c_label))
        self.wait(2)

Conclusion: Hand-Crafting Code in the Age of AI

Hand-written assembly largely vanished once compilers became excellent. Productivity won over the last few percent of performance.

We are now at the same turning point with AI coding tools. Soon, most production code will be generated, not hand-written.

I finished my bachelor's (average 9.96) and master's (perfect 10.00) in software engineering without any AI help. In fact, I started exploring AI topics toward the end of each degree, with theses on graph neural networks for drug interaction prediction and recommendation systems. Now, in my PhD, AI is central to my research. Yet another layer of abstraction has appeared: we program with natural language, describing what we want instead of how to do it.

Still, I believe there is profound value in occasionally dropping down to the lower layers, writing assembly, tweaking bits, feeling the machine breathe.

Learning across different levels of abstraction, and especially learning how to fluidly move up and down that ladder, builds a sharper engineering mindset. You understand trade-offs deeply: when to abstract for speed of development, when to dive low for performance or control.

As Elon Musk has often implied, engineering is magic, turning ideas into reality through sheer will and ingenuity. But AI software engineering feels like the purest form of that magic today. Solving hard problems in AI does not just advance computing; it unlocks solutions across engineering disciplines and beyond, especially in medicine, the field I first studied before switching paths. I look forward to the day when AI helps crack challenges like personalized treatment or disease prediction at scale.

In today's world, engineering is magic. Keep exploring all layers. Build personal projects that push you outside your comfort zone. One day you will look back, like I do with this seven-year-old assembly game, and see how far you have come.

Thanks for reading!
Full code: https://github.com/njmarko/i386-assembly-mastermind-game
Try it, share it, tell me what you think. 🚀

