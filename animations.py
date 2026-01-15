"""
Parameterized Manim Animation Script for Mastermind Assembly Blog
Generates GIFs for different sections of the blog with configurable parameters.
"""

from manim import *
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class BaseAnimation(Scene):
    """
    Base class for all Mastermind assembly animations.
    Provides common functionality and configuration management.
    """

    def __init__(self, config: Dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or self.get_default_config()

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Return default configuration for this animation."""
        return {
            'width': 16,  # 16:9 aspect ratio
            'height': 9,
            'fps': 30,
            'background_color': '#1a1a1a',  # Dark theme
            'text_color': WHITE,
            'highlight_color': YELLOW,
            'success_color': GREEN,
            'error_color': RED,
            'font_size': 36,
            'animation_speed': 1.0,
            'wait_time': 1.0,
        }

    def setup_scene(self):
        """Setup common scene elements like title, background, etc."""
        # Set background color
        self.camera.background_color = self.config['background_color']

        # Configure text defaults
        Text.set_default(color=self.config['text_color'])
        Tex.set_default(color=self.config['text_color'])

    def create_register_visualization(self, register_name: str, width: float = 4,
                                   height: float = 0.8, color: str = BLUE) -> Tuple[Rectangle, Text, Text]:
        """Create a visual representation of a CPU register."""
        reg_rect = Rectangle(width=width, height=height, color=color)
        reg_label = Text(register_name, font_size=self.config['font_size'] * 0.8).next_to(reg_rect, UP)
        reg_value = Text("", font_size=self.config['font_size'] * 0.6).move_to(reg_rect)

        return reg_rect, reg_label, reg_value

    def animate_code_highlight(self, code_obj, line_index: int,
                             highlight_color: str = None) -> Animation:
        """Highlight a specific line of code."""
        highlight_color = highlight_color or self.config['highlight_color']
        if hasattr(code_obj, 'submobjects') and line_index < len(code_obj.submobjects):
            # For VGroup of Text objects
            line = code_obj.submobjects[line_index].copy()
            return line.animate.set_color(highlight_color)
        elif hasattr(code_obj, 'code') and line_index < len(code_obj.code):
            # For Code objects (fallback)
            line = code_obj.code[line_index][0].copy()
            return line.animate.set_color(highlight_color)
        return Wait(0.1)

    def create_bit_visualization(self, value: int, bits: int = 32,
                               spacing: float = 0.1) -> VGroup:
        """Create a visual representation of bits in a register."""
        bit_squares = VGroup()
        for i in range(bits):
            bit = (value >> i) & 1
            color = GREEN if bit else GRAY
            square = Square(side_length=0.3, color=color, fill_opacity=0.7)
            square.shift(RIGHT * (i - bits/2) * (square.side_length + spacing))
            bit_squares.add(square)
        return bit_squares

    def animate_bit_change(self, bit_squares: VGroup, bit_index: int,
                          new_value: int, color: str = None) -> Animation:
        """Animate a bit changing value."""
        color = color or (GREEN if new_value else GRAY)
        return bit_squares[bit_index].animate.set_color(color)

    def add_title_and_wait(self, title_text: str, wait_time: float = None):
        """Add a title to the scene and wait."""
        wait_time = wait_time or self.config['wait_time']
        title = Text(title_text, font_size=self.config['font_size']).to_edge(UP)
        self.play(Write(title))
        self.wait(wait_time)
        return title

    def cleanup_scene(self, title: Text = None):
        """Clean up scene elements."""
        animations = []
        if title:
            animations.append(FadeOut(title))
        if animations:
            self.play(*animations)


class RegisterPackingExecution(BaseAnimation):
    """Animation showing register packing execution with rorb/rorl instructions."""

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        config = super().get_default_config()
        config.update({
            'symbols': ['SKOCKO', 'TREF', 'PIK', 'HERC'],  # 4 symbols for combination
            'symbol_bits': [0b10000000, 0b01000000, 0b00100000, 0b00010000],  # 8-bit encodings
            'initial_mask': 0b10000000100000001000000010000000,
            'register_width': 4,
            'bit_animation_delay': 0.5,
        })
        return config

    def construct(self):
        self.setup_scene()

        title = self.add_title_and_wait("Executing Bit Placement in Register")

        # Create register visualization
        ebx_rect, ebx_label, ebx_value = self.create_register_visualization("%ebx")
        ebx_value_text = Text(f"0x{self.config['initial_mask']:08X}", font_size=24)
        ebx_value_text.move_to(ebx_rect)

        # Simple assembly code display
        code_text = Text("rorb %cl, %bl\nrorl $8, %ebx", font_size=20, font="Monospace")
        code_text.to_corner(UL)

        self.play(Create(ebx_rect), Write(ebx_label), Write(ebx_value_text), Write(code_text))

        current_value = self.config['initial_mask']

        for i in range(4):
            # Simple highlight effect
            self.play(code_text.animate.set_color(YELLOW), run_time=0.8)

            # Animate bit rotation
            # rorb %cl, %bl - rotate bottom byte right by cl positions
            rotated_byte = ((current_value & 0xFF) >> 3) | (((current_value & 0xFF) << 5) & 0xFF)
            new_value = (current_value & ~0xFF) | rotated_byte

            # Update display
            new_value_text = Text(f"0x{new_value:08X}", font_size=24, color=GREEN)
            new_value_text.move_to(ebx_rect)
            self.play(Transform(ebx_value_text, new_value_text), run_time=self.config['bit_animation_delay'])

            # Reset code color
            self.play(code_text.animate.set_color(WHITE), run_time=0.8)

            # rorl $8, %ebx - rotate entire register left by 8 bits
            new_value = ((new_value << 8) & 0xFFFFFFFF) | (new_value >> 24)
            current_value = new_value

            # Update display with shift animation
            final_value_text = Text(f"0x{current_value:08X}", font_size=24)
            final_value_text.move_to(ebx_rect)
            self.play(Transform(ebx_value_text, final_value_text),
                     run_time=0.5)

        # Final message
        final_msg = Text("Full combination packed!", font_size=30, color=GREEN).next_to(ebx_rect, DOWN)
        self.play(Write(final_msg))
        self.wait(2)

        self.cleanup_scene(title)


class RegisterPackingDetailed(Scene):
    def construct(self):
        # Title
        title = Tex(r"Packing the Combination into One 32-bit Register").scale(0.9)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Main register - 32 bits divided into 4 colored bytes
        register = VGroup()
        byte_colors = [BLUE_D, TEAL_D, GREEN_D, PURPLE_D]
        bit_groups = []
        for byte_idx in range(4):
            start_bit = byte_idx * 8
            end_bit = start_bit + 8
            byte_bits = VGroup(*[
                Square(side_length=0.4, color=byte_colors[byte_idx], fill_opacity=0.2, stroke_width=2)
                for _ in range(8)
            ]).arrange(RIGHT, buff=0)
            byte_bits.shift(RIGHT * (byte_idx * 3.6 - 6.3))
            bit_groups.append(byte_bits)
            register.add(byte_bits)

        register.move_to(ORIGIN + UP * 1.5)

        reg_label = Tex(r"32-bit Register (\%ebx)").next_to(register, UP, buff=0.8)
        byte_labels = VGroup(
            Tex(r"Byte 3").next_to(bit_groups[0], DOWN, buff=0.5),
            Tex(r"Byte 2").next_to(bit_groups[1], DOWN, buff=0.5),
            Tex(r"Byte 1").next_to(bit_groups[2], DOWN, buff=0.5),
            Tex(r"Byte 0").next_to(bit_groups[3], DOWN, buff=0.5),
        )

        self.play(
            FadeIn(register),
            Write(reg_label),
            Write(byte_labels)
        )

        # Legend on the right
        legend_title = Tex(r"Symbol Encoding").scale(0.8).to_corner(UR)
        legend = VGroup(legend_title)
        symbols = ["SKOCKO (1)", "TREF (2)", "PIK (3)", "HERC (4)", "KARO (5)", "ZVEZDA (6)"]
        patterns = ["10000000", "01000000", "00100000", "00010000", "00001000", "00000100"]
        legend_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

        for sym, pat, col in zip(symbols, patterns, legend_colors):
            row = VGroup(
                Tex(sym).scale(0.7),
                Tex(pat).scale(0.7).set_color(col)
            ).arrange(RIGHT, buff=1)
            legend.add(row)

        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(legend_title, DOWN, buff=0.6)
        self.play(Write(legend))

        # Initial explanation
        expl = Tex(r"Initial mask: all positions ready").scale(0.7).to_edge(DOWN)
        self.play(Write(expl))

        # Example placement order (e.g., symbols 1, 3, 5, 6)
        placement_order = [0, 2, 4, 5]  # indices in legend: SKOCKO, PIK, KARO, ZVEZDA
        byte_targets = [3, 2, 1, 0]    # which byte to fill (right to left)

        current_expl = expl

        for step, (sym_idx, target_byte) in enumerate(zip(placement_order, byte_targets)):
            # Highlight legend row
            legend_row = legend[step + 1]
            self.play(legend_row.animate.set_color(YELLOW))

            # Show incoming byte block below, aligned to target
            incoming_byte = VGroup(*[
                Square(side_length=0.4, color=byte_colors[target_byte], fill_opacity=0.4)
                for _ in range(8)
            ]).arrange(RIGHT, buff=0)
            incoming_byte.next_to(bit_groups[target_byte], DOWN, buff=1)

            pattern = patterns[sym_idx]
            for i, bit in enumerate(pattern):
                if bit == "1":
                    incoming_byte[i].set_fill(legend_colors[sym_idx], opacity=1)

            incoming_label = Tex(symbols[sym_idx]).scale(0.7).next_to(incoming_byte, DOWN)

            self.play(FadeIn(incoming_byte, incoming_label))

            # Explanation: rorb to place bit in low byte
            new_expl = Tex(r"Step {}: rorb \%cl, \%bl - rotate low byte to place bit".format(step+1)).scale(0.7).to_edge(DOWN)
            self.play(ReplacementTransform(current_expl, new_expl))
            current_expl = new_expl

            # Animate rotation into low byte (visual swirl)
            low_byte = bit_groups[3]  # always low byte before shift
            self.play(Rotate(incoming_byte, angle=PI, about_point=low_byte.get_center()), run_time=1.2)
            self.play(FadeOut(incoming_byte, incoming_label))

            # Light the correct bit in low byte
            bit_pos = pattern.find("1")
            low_byte[bit_pos].set_fill(legend_colors[sym_idx], opacity=1)
            self.play(low_byte[bit_pos].animate.scale(1.3), run_time=0.4)
            self.play(low_byte[bit_pos].animate.scale(1/1.3))

            # Explanation: rorl $8 to shift whole register left by 8 bits
            new_expl = Tex(r"rorl \$8, \%ebx - shift everything left by 8 bits").scale(0.7).to_edge(DOWN)
            self.play(ReplacementTransform(current_expl, new_expl))
            current_expl = new_expl

            # Animate full register shift left (bits move left)
            self.play(register.animate.shift(LEFT * 3.6), run_time=1.5)  # visual shift of one byte
            # Reset position for next iteration
            self.play(register.animate.shift(RIGHT * 3.6), run_time=0.01)

            # Unhighlight legend
            self.play(legend_row.animate.set_color(WHITE))

        # Final state
        final_expl = Tex(r"Full 4-symbol combination packed in one register!").scale(0.8).set_color(GREEN).to_edge(DOWN)
        self.play(ReplacementTransform(current_expl, final_expl))
        self.wait(3)


class ExactMatchExecution(BaseAnimation):
    """Animation showing exact match calculation with bit operations."""

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        config = super().get_default_config()
        config.update({
            'guess_value': 0x80A02040,  # Example guess
            'secret_value': 0x80102040,  # Example secret (3 exact matches)
            'bit_operations': ['AND', 'TEST', 'INCL', 'SHRL'],
        })
        return config

    def construct(self):
        self.setup_scene()

        title = self.add_title_and_wait("Exact Match Calculation")

        # Simple demonstration
        initial_text = Text("AND operation: guess & secret", font_size=24)
        self.play(Write(initial_text))

        # Show the calculation
        guess_val = self.config['guess_value']
        secret_val = self.config['secret_value']
        result = guess_val & secret_val

        calc_text = Text(f"0x{guess_val:08X} & 0x{secret_val:08X} = 0x{result:08X}", font_size=20)
        calc_text.next_to(initial_text, DOWN)
        self.play(Write(calc_text))

        # Count set bits
        bit_count = bin(result).count('1')
        result_text = Text(f"Number of exact matches: {bit_count}", font_size=24, color=GREEN)
        result_text.next_to(calc_text, DOWN)
        self.play(Write(result_text))

        self.wait(3)
        self.cleanup_scene(title)


class EliminationLoopExecution(BaseAnimation):
    """Animation showing elimination loop execution with candidate filtering."""

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        config = super().get_default_config()
        config.update({
            'num_candidates': 10,
            'candidates_to_keep': [0, 2, 4, 6, 8],  # Which candidates pass the test
            'memory_width': 1.0,
            'memory_height': 0.5,
            'memory_spacing': 0.2,
        })
        return config

    def construct(self):
        self.setup_scene()

        title = self.add_title_and_wait("Elimination Loop Execution")

        # Create memory array visualization
        memory_blocks = VGroup(*[
            Rectangle(width=self.config['memory_width'],
                     height=self.config['memory_height'],
                     color=GREY, fill_opacity=0.3)
            for _ in range(self.config['num_candidates'])
        ]).arrange(RIGHT, buff=self.config['memory_spacing'])

        memory_label = Text("Memory array (candidates)", font_size=24).next_to(memory_blocks, UP)

        # Create register visualization
        ebx_rect, ebx_label, ebx_value = self.create_register_visualization("%ebx", color=BLUE)
        ebx_group = VGroup(ebx_rect, ebx_label, ebx_value).shift(DOWN * 1.5)

        # Counter for current index
        ecx_counter = Text("0", font_size=30).next_to(ebx_group, DOWN)
        ecx_label = Text("%ecx (index)", font_size=20).next_to(ecx_counter, DOWN)

        # Assembly code
        code_lines = [
            "movl sve_kombinacije(,%ecx,4), %ebx",
            "call histogram",
            "cmpl crveni, %esi",
            "jne skip",
            "movl %ebx, rezultat(,%edx,4)",
            "incl %edx",
            "skip:"
        ]
        code = VGroup(*[Text(line, font_size=16, font="Monospace").align_to(code_lines[0], LEFT) for line in code_lines]).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)

        # Position elements
        memory_group = VGroup(memory_blocks, memory_label).shift(UP * 1.5)

        self.play(Create(memory_group), Create(ebx_group), Write(ecx_counter),
                 Write(ecx_label), Write(code))

        # Elimination loop
        result_index = 0

        for i in range(self.config['num_candidates']):
            # Load candidate from memory
            self.play(self.animate_code_highlight(code, 0), run_time=0.5)

            # Animate loading into EBX
            candidate_copy = memory_blocks[i].copy()
            candidate_copy.generate_target()
            candidate_copy.target.move_to(ebx_rect).set_color(BLUE)
            self.play(MoveToTarget(candidate_copy), run_time=0.8)

            # Update EBX display
            candidate_value = Text(f"0x{(i * 0x11111111) & 0xFFFFFFFF:08X}", font_size=16)
            candidate_value.move_to(ebx_rect)
            self.play(Write(candidate_value), run_time=0.5)

            # Call histogram function
            self.play(self.animate_code_highlight(code, 1), run_time=0.5)
            histogram_call = Text("histogram()", font_size=20, color=YELLOW).to_edge(LEFT)
            self.play(Write(histogram_call), run_time=0.8)
            self.play(FadeOut(histogram_call), run_time=0.3)

            # Compare and decide
            self.play(self.animate_code_highlight(code, 2), run_time=0.5)

            if i in self.config['candidates_to_keep']:
                # Keep candidate - highlight as green and move to result area
                self.play(self.animate_code_highlight(code, 3), run_time=0.3)  # movl to result
                self.play(self.animate_code_highlight(code, 4), run_time=0.3)  # incl %edx

                # Mark as kept
                self.play(memory_blocks[i].animate.set_color(GREEN), run_time=0.5)

                result_index += 1
            else:
                # Eliminate candidate
                self.play(self.animate_code_highlight(code, 5), run_time=0.3)  # jne skip

                # Fade out eliminated candidate
                self.play(FadeOut(memory_blocks[i]), run_time=0.8)

            # Update counter
            new_counter = Text(str(i + 1), font_size=30)
            new_counter.move_to(ecx_counter)
            self.play(Transform(ecx_counter, new_counter), run_time=0.3)

            # Clean up candidate visualization
            self.play(FadeOut(candidate_copy), FadeOut(candidate_value), run_time=0.3)

        # Final result
        final_msg = Text(f"Elimination complete! {result_index} candidates remaining",
                        font_size=28, color=GREEN).to_edge(DOWN)
        self.play(Write(final_msg))
        self.wait(2)

        self.cleanup_scene(title)


class EntropyReduction(BaseAnimation):
    """Animation showing entropy reduction through the solving process."""

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        config = super().get_default_config()
        config.update({
            'initial_possibilities': 1296,  # 6^4 = 1296 for Mastermind
            'remaining_counts': [1296, 432, 144, 48, 12, 3, 1],
            'entropy_bits': [10.34, 8.75, 7.17, 5.58, 3.58, 1.58, 0.0],
            'grid_rows': 36,  # sqrt(1296) ≈ 36
            'grid_cols': 36,
            'dot_radius': 0.03,
            'dot_buff': 0.15,
            'bar_max_width': 12.0,
            'guess_descriptions': [
                "Initial possibilities",
                "After first guess",
                "After second guess",
                "After third guess",
                "After fourth guess",
                "After fifth guess",
                "Solution found!"
            ]
        })
        return config

    def construct(self):
        self.setup_scene()

        title = self.add_title_and_wait("Entropy Reduction in Mastermind")

        # Initial state
        initial_text = Text(f"Initial: {self.config['initial_possibilities']} possibilities ≈ {self.config['entropy_bits'][0]:.2f} bits",
                           font_size=28)
        self.play(Write(initial_text))

        # Create grid of dots representing possibilities
        grid = VGroup(*[
            Dot(radius=self.config['dot_radius'], color=BLUE, fill_opacity=0.8)
            for _ in range(self.config['initial_possibilities'])
        ])
        grid.arrange_in_grid(
            rows=self.config['grid_rows'],
            cols=self.config['grid_cols'],
            buff=self.config['dot_buff']
        ).scale(0.8)

        self.play(FadeIn(grid), run_time=2)
        self.wait(1)

        current_text = initial_text

        # Animate entropy reduction through guesses
        for i in range(1, len(self.config['remaining_counts'])):
            remaining = self.config['remaining_counts'][i]
            entropy = self.config['entropy_bits'][i]

            # Calculate how many dots to remove
            dots_to_remove = len(grid) - remaining

            # Create new text and entropy bar
            new_text = Text(f"{self.config['guess_descriptions'][i]}: {remaining} left ≈ {entropy:.2f} bits",
                           font_size=28)

            # Entropy bar visualization
            bar_width = (entropy / self.config['entropy_bits'][0]) * self.config['bar_max_width']
            entropy_bar = Rectangle(
                width=max(bar_width, 0.5),  # Minimum width
                height=0.6,
                color=GREEN if entropy > 0 else GOLD,
                fill_opacity=0.7
            )

            # Position bar below the grid
            bar_group = VGroup(entropy_bar, new_text).arrange(DOWN, buff=0.3).shift(DOWN * 2)

            # Animate the transition
            animations = [FadeOut(current_text)]

            if dots_to_remove > 0:
                # Remove dots representing eliminated possibilities
                animations.append(FadeOut(grid[:dots_to_remove], run_time=1.5))

                # Update grid to only show remaining dots
                remaining_grid = grid[dots_to_remove:].copy()
                grid = remaining_grid

            animations.append(FadeIn(bar_group))

            self.play(*animations, run_time=1.5)
            self.wait(0.8)

            current_text = new_text

        # Final message
        final_text = Text("Solved in ≤5 guesses (Knuth 1977)", font_size=36, color=GOLD)
        final_text.shift(DOWN * 1.5)

        self.play(Write(final_text), run_time=2)
        self.wait(3)

        self.cleanup_scene(title)


class StackOverwriteExecution(BaseAnimation):
    """Animation showing stack overwrite execution for printf display."""

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        config = super().get_default_config()
        config.update({
            'stack_slots': 15,
            'stack_width': 2.0,
            'stack_height': 0.5,
            'stack_buff': 0.1,
            'esp_arrow_color': RED,
            'skip_slots': 3,  # How many empty slots to skip
            'symbols_to_push': [
                {'name': 'yellow', 'symbol': '●', 'color': YELLOW},
                {'name': 'red', 'symbol': '●', 'color': RED},
                {'name': 'blue', 'symbol': '●', 'color': BLUE},
            ],
            'push_positions': [5, 6, 7],  # Which stack positions to update
        })
        return config

    def construct(self):
        self.setup_scene()

        title = self.add_title_and_wait("Stack Overwrite Execution")

        # Create stack visualization (growing downward)
        stack_slots = []
        for i in range(self.config['stack_slots']):
            slot = Rectangle(
                width=self.config['stack_width'],
                height=self.config['stack_height'],
                color=GREY,
                fill_opacity=0.2
            )
            label = Text("empty", font_size=16)
            label.move_to(slot)
            stack_slots.append(VGroup(slot, label))

        stack = VGroup(*stack_slots).arrange(DOWN, buff=self.config['stack_buff'])

        # ESP pointer (stack pointer)
        esp_arrow = Arrow(
            start=stack[0].get_top() + UP * 0.2,
            end=stack[0].get_bottom(),
            color=self.config['esp_arrow_color'],
            buff=0
        )
        esp_label = Text("%esp →", font_size=20).next_to(esp_arrow, LEFT)

        # Assembly code
        code_lines = [
            "subl %eax, %esp     # skip empty slots",
            "pushl $znak_zuti    # push yellow peg",
            "pushl $znak_crveni   # push red peg",
            "pushl $znak_plavi    # push blue peg"
        ]
        code = VGroup(*[Text(line, font_size=16, font="Monospace").align_to(code_lines[0], LEFT) for line in code_lines]).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)

        # Initial setup
        self.play(Create(stack), Create(esp_arrow), Write(esp_label), Write(code))

        # Skip empty slots with subl
        self.play(self.animate_code_highlight(code, 0), run_time=0.8)

        skip_distance = self.config['skip_slots'] * (self.config['stack_height'] + self.config['stack_buff'])
        self.play(
            esp_arrow.animate.shift(DOWN * skip_distance),
            esp_label.animate.shift(DOWN * skip_distance),
            run_time=1.5
        )

        # Push symbols onto stack
        current_stack_top = self.config['skip_slots']

        for i, symbol_info in enumerate(self.config['symbols_to_push']):
            self.play(self.animate_code_highlight(code, i + 1), run_time=0.8)

            # Update stack slot with symbol
            slot_index = self.config['push_positions'][i]
            new_symbol = Text(f"{symbol_info['symbol']} {symbol_info['name']}",
                             font_size=16, color=symbol_info['color'])
            new_symbol.move_to(stack[slot_index])

            # Animate the push
            self.play(
                stack[slot_index][1].animate.become(new_symbol),
                stack[slot_index][0].animate.set_color(symbol_info['color']),
                run_time=0.8
            )

            # Move ESP up for push
            self.play(
                esp_arrow.animate.shift(UP * (self.config['stack_height'] + self.config['stack_buff'])),
                esp_label.animate.shift(UP * (self.config['stack_height'] + self.config['stack_buff'])),
                run_time=0.5
            )

        # Final message
        final_msg = Text("Only needed slots updated! Stack optimized.",
                        font_size=28, color=GREEN).to_edge(DOWN)
        self.play(Write(final_msg))
        self.wait(2)

        self.cleanup_scene(title)


class BenchmarkChart(BaseAnimation):
    """Animation showing benchmark comparison between Assembly and C versions."""

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        config = super().get_default_config()
        config.update({
            'assembly_time': 2.5,  # ms per game
            'c_time': 6.5,  # ms per game
            'max_time': 10.0,  # max y-axis
            'bar_width': 0.8,
            'bar_spacing': 1.5,
            'chart_height': 6.0,
            'assembly_color': GREEN,
            'c_color': RED,
            'axis_color': BLUE,
            'show_percentage': True,
        })
        return config

    def construct(self):
        self.setup_scene()

        title = self.add_title_and_wait("Benchmark: Assembly vs C Performance")

        # Create axes
        axes = Axes(
            x_range=[0, 3, 1],
            y_range=[0, self.config['max_time'], 2],
            axis_config={"color": self.config['axis_color']},
            x_length=6,
            y_length=self.config['chart_height']
        )

        x_label = Text("Implementation", font_size=24).next_to(axes.x_axis, DOWN)
        y_label = Text("Time (ms)", font_size=24).next_to(axes.y_axis, LEFT).rotate(90 * DEGREES)

        # Create bars
        assembly_height = (self.config['assembly_time'] / self.config['max_time']) * self.config['chart_height']
        c_height = (self.config['c_time'] / self.config['max_time']) * self.config['chart_height']

        # Assembly bar (left)
        assembly_bar = Rectangle(
            width=self.config['bar_width'],
            height=assembly_height,
            color=self.config['assembly_color'],
            fill_opacity=0.8
        )
        assembly_bar.move_to(axes.coords_to_point(0.7, assembly_height/2))

        # C bar (right)
        c_bar = Rectangle(
            width=self.config['bar_width'],
            height=c_height,
            color=self.config['c_color'],
            fill_opacity=0.8
        )
        c_bar.move_to(axes.coords_to_point(2.3, c_height/2))

        # Labels
        assembly_label = Text("Assembly", font_size=24, color=self.config['assembly_color'])
        assembly_label.next_to(assembly_bar, DOWN)

        c_label = Text("C", font_size=24, color=self.config['c_color'])
        c_label.next_to(c_bar, DOWN)

        # Value labels on bars
        assembly_value = Text(".2f", font_size=20, color=WHITE)
        assembly_value.move_to(assembly_bar.get_center())

        c_value = Text(".1f", font_size=20, color=WHITE)
        c_value.move_to(c_bar.get_center())

        # Performance comparison text
        speedup = self.config['c_time'] / self.config['assembly_time']
        comparison_text = Text(f"Assembly is {speedup:.1f}× faster than C!", font_size=28, color=GOLD)
        comparison_text.to_edge(DOWN)

        # Animate chart creation
        self.play(Create(axes), Write(x_label), Write(y_label))

        # Animate bars appearing
        self.play(FadeIn(assembly_bar), run_time=1.0)
        self.play(Write(assembly_label), Write(assembly_value))

        self.play(FadeIn(c_bar), run_time=1.0)
        self.play(Write(c_label), Write(c_value))

        # Show comparison
        self.play(Write(comparison_text), run_time=2)
        self.wait(2)

        # Additional optimization note
        optimization_note = Text("~2-2.5× faster from bit-packing and register operations",
                                font_size=24, color=GREEN).to_edge(DOWN)
        self.play(FadeOut(comparison_text), FadeIn(optimization_note), run_time=1.0)
        self.wait(2)

        self.cleanup_scene(title)


def create_animation(animation_name: str, config: Dict[str, Any] = None):
    """Factory function to create animation instances."""
    # Scene-based animations (don't inherit from BaseAnimation)
    scene_animations = {
        'register_packing_detailed': RegisterPackingDetailed,
    }

    # BaseAnimation-based animations
    base_animations = {
        'register_packing': RegisterPackingExecution,
        'exact_match': ExactMatchExecution,
        'elimination_loop': EliminationLoopExecution,
        'entropy_reduction': EntropyReduction,
        'stack_overwrite': StackOverwriteExecution,
        'benchmark_chart': BenchmarkChart,
    }

    all_animations = {**scene_animations, **base_animations}

    if animation_name not in all_animations:
        raise ValueError(f"Unknown animation: {animation_name}. Available: {list(all_animations.keys())}")

    animation_class = all_animations[animation_name]

    # Scene-based animations don't take config parameter
    if animation_name in scene_animations:
        return animation_class()
    else:
        return animation_class(config)


def main():
    """Main function to parse arguments and run animations."""
    parser = argparse.ArgumentParser(description='Generate GIFs for Mastermind Assembly Blog')
    parser.add_argument('animation', choices=[
        'register_packing', 'exact_match', 'elimination_loop',
        'entropy_reduction', 'stack_overwrite', 'benchmark_chart'
    ], help='Which animation to generate')
    parser.add_argument('--config', type=str, help='JSON config file path')
    parser.add_argument('--output', type=str, default='media',
                       help='Output directory for rendered files')
    parser.add_argument('--format', choices=['gif', 'mp4'], default='gif',
                       help='Output format')
    parser.add_argument('--quality', choices=['low', 'medium', 'high'], default='high',
                       help='Render quality')

    args = parser.parse_args()

    # Load config if provided
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)

    # Set render quality
    quality_settings = {
        'low': {'pixel_height': 480, 'pixel_width': 854},
        'medium': {'pixel_height': 720, 'pixel_width': 1280},
        'high': {'pixel_height': 1080, 'pixel_width': 1920},
    }

    # Create animation instance
    animation = create_animation(args.animation, config)

    # Configure output
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Render animation
    scene_config = quality_settings[args.quality]
    scene_config.update({
        'output_file_path': str(output_dir / f"{args.animation}.{args.format}"),
        'format': args.format,
    })

    # Render the animation using manim command line
    print(f"Rendering {args.animation} animation...")
    print(f"Output: {scene_config['output_file_path']}")
    print(f"Quality: {args.quality} ({scene_config['pixel_width']}x{scene_config['pixel_height']})")

    import subprocess
    import sys
    import os

    # Set environment variables for manim configuration
    env = os.environ.copy()
    env['MANIM_CONFIG_FILE'] = ''  # Don't use config file

    # Build manim command
    cmd = [
        sys.executable, "-m", "manim",
        "--format", args.format,
        "--media_dir", str(output_dir),
        "--custom_folders",
        "-v", "WARNING"  # Reduce verbosity
    ]

    # Add quality settings
    if args.quality == "low":
        cmd.extend(["-ql"])
    elif args.quality == "medium":
        cmd.extend(["-qm"])
    else:  # high
        cmd.extend(["-qh"])

    # Add the animation class and output name
    cmd.extend(["animations.py", args.animation])

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, env=env, cwd=Path(__file__).parent, capture_output=True, text=True)
        if result.returncode == 0:
            print("Animation rendering completed successfully!")

            # Check if the output file was created
            expected_file = output_dir / f"{args.animation}.{args.format}"
            if expected_file.exists():
                print(f"Output file created: {expected_file}")
            else:
                print(f"Warning: Expected output file not found: {expected_file}")
                # List what files were actually created
                print("Files in output directory:")
                for file in output_dir.glob("*"):
                    print(f"  {file.name}")

        else:
            print(f"Animation rendering failed with exit code: {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return 1
    except Exception as e:
        print(f"Animation rendering failed: {e}")
        return 1


if __name__ == "__main__":
    main()