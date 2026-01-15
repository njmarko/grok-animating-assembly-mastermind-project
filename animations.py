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

    def animate_code_highlight(self, code_obj: Code, line_index: int,
                             highlight_color: str = None) -> Animation:
        """Highlight a specific line of code."""
        highlight_color = highlight_color or self.config['highlight_color']
        if hasattr(code_obj, 'code') and line_index < len(code_obj.code):
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

        # Assembly code
        code = Code(code=r"""
rorb %cl, %bl
rorl $8, %ebx
""", language="asm", font_size=24).to_corner(UL)

        self.play(Create(ebx_rect), Write(ebx_label), Write(ebx_value_text), Write(code))

        current_value = self.config['initial_mask']

        for i in range(4):
            # Highlight first instruction
            self.play(self.animate_code_highlight(code, 0), run_time=0.8)

            # Animate bit rotation
            # rorb %cl, %bl - rotate bottom byte right by cl positions
            rotated_byte = ((current_value & 0xFF) >> 3) | (((current_value & 0xFF) << 5) & 0xFF)
            new_value = (current_value & ~0xFF) | rotated_byte

            # Update display
            new_value_text = Text(f"0x{new_value:08X}", font_size=24, color=GREEN)
            new_value_text.move_to(ebx_rect)
            self.play(Transform(ebx_value_text, new_value_text), run_time=self.config['bit_animation_delay'])

            # Highlight second instruction
            self.play(self.animate_code_highlight(code, 1), run_time=0.8)

            # rorl $8, %ebx - rotate entire register left by 8 bits
            new_value = ((new_value << 8) & 0xFFFFFFFF) | (new_value >> 24)
            current_value = new_value

            # Update display with shift animation
            final_value_text = Text(f"0x{current_value:08X}", font_size=24)
            final_value_text.move_to(ebx_rect)
            self.play(Transform(ebx_value_text, final_value_text),
                     ebx_value_text.animate.shift(RIGHT * 0.5), run_time=0.5)

        # Final message
        final_msg = Text("Full combination packed!", font_size=30, color=GREEN).next_to(ebx_rect, DOWN)
        self.play(Write(final_msg))
        self.wait(2)

        self.cleanup_scene(title)


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

        # Create register visualizations
        guess_rect, guess_label, guess_value = self.create_register_visualization("%eax", color=BLUE)
        secret_rect, secret_label, secret_value = self.create_register_visualization("%ebx", color=RED)
        result_rect, result_label, result_value = self.create_register_visualization("%ecx", color=GREEN)

        guess_value_text = Text(f"0x{self.config['guess_value']:08X}", font_size=20)
        guess_value_text.move_to(guess_rect)
        secret_value_text = Text(f"0x{self.config['secret_value']:08X}", font_size=20)
        secret_value_text.move_to(secret_rect)

        # Position registers
        guess_group = VGroup(guess_rect, guess_label, guess_value_text).shift(UP * 1.5)
        secret_group = VGroup(secret_rect, secret_label, secret_value_text).shift(UP * 0.5)
        result_group = VGroup(result_rect, result_label, result_value).shift(DOWN * 0.5)

        # Assembly code
        code = Code(code=r"""
andl %ebx, %eax    # AND guess & secret
xorl %ecx, %ecx    # Clear counter
test_loop:
testb $1, %al      # Test LSB
jz skip_inc        # If zero, skip
incl %ecx          # Increment counter
skip_inc:
shrl $1, %eax      # Shift right
jnz test_loop      # Loop if not zero
""", language="asm", font_size=18).to_corner(UL)

        self.play(Create(guess_group), Create(secret_group), Create(result_group), Write(code))

        # AND operation
        self.play(self.animate_code_highlight(code, 0), run_time=0.8)
        and_result = self.config['guess_value'] & self.config['secret_value']
        and_text = Text(f"0x{and_result:08X}", font_size=20, color=YELLOW)
        and_text.move_to(guess_rect)
        self.play(Transform(guess_value_text, and_text))

        # Clear counter
        self.play(self.animate_code_highlight(code, 1), run_time=0.8)
        counter_text = Text("0", font_size=20)
        counter_text.move_to(result_rect)
        self.play(Write(counter_text))

        # Bit counting loop
        current_value = and_result
        bit_count = 0

        for bit_pos in range(32):
            if current_value & 1:
                self.play(self.animate_code_highlight(code, 2), run_time=0.3)  # testb
                self.play(self.animate_code_highlight(code, 4), run_time=0.3)  # incl
                bit_count += 1
                counter_text_new = Text(str(bit_count), font_size=20, color=GREEN)
                counter_text_new.move_to(result_rect)
                self.play(Transform(counter_text, counter_text_new))
            else:
                self.play(self.animate_code_highlight(code, 3), run_time=0.3)  # jz skip

            self.play(self.animate_code_highlight(code, 5), run_time=0.3)  # shrl
            current_value >>= 1

            if current_value == 0:
                break

        final_msg = Text(f"Exact matches: {bit_count}", font_size=30, color=GREEN).to_edge(DOWN)
        self.play(Write(final_msg))
        self.wait(2)

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
        code = Code(code=r"""
movl sve_kombinacije(,%ecx,4), %ebx
call histogram
cmpl crveni, %esi
jne skip
movl %ebx, rezultat(,%edx,4)
incl %edx
skip:
""", language="asm", font_size=18).to_edge(RIGHT)

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
                kept_copy = memory_blocks[i].copy().set_color(GREEN)
                kept_copy.move_to(memory_blocks[i])
                self.play(Transform(memory_blocks[i], kept_copy), run_time=0.5)

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
        code = Code(code=r"""
subl %eax, %esp     # skip empty slots
pushl $znak_zuti    # push yellow peg
pushl $znak_crveni   # push red peg
pushl $znak_plavi    # push blue peg
""", language="asm", font_size=18).to_edge(RIGHT)

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
                Transform(stack[slot_index][1], new_symbol),
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

        # Animate bars growing
        self.play(
            assembly_bar.animate.scale([1, 1, 0]).scale([1, 1, 1]),  # Start from zero height
            run_time=1.5
        )
        self.play(Write(assembly_label), Write(assembly_value))

        self.play(
            c_bar.animate.scale([1, 1, 0]).scale([1, 1, 1]),  # Start from zero height
            run_time=1.5
        )
        self.play(Write(c_label), Write(c_value))

        # Show comparison
        self.play(Write(comparison_text), run_time=2)
        self.wait(2)

        # Additional optimization note
        optimization_note = Text("~2-2.5× faster from bit-packing and register operations",
                                font_size=24, color=GREEN).to_edge(DOWN)
        self.play(Transform(comparison_text, optimization_note))
        self.wait(2)

        self.cleanup_scene(title)


def create_animation(animation_name: str, config: Dict[str, Any] = None) -> BaseAnimation:
    """Factory function to create animation instances."""
    animations = {
        'register_packing': RegisterPackingExecution,
        'exact_match': ExactMatchExecution,
        'elimination_loop': EliminationLoopExecution,
        'entropy_reduction': EntropyReduction,
        'stack_overwrite': StackOverwriteExecution,
        'benchmark_chart': BenchmarkChart,
    }

    if animation_name not in animations:
        raise ValueError(f"Unknown animation: {animation_name}. Available: {list(animations.keys())}")

    return animations[animation_name](config)


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

    # This would normally render the animation, but for now we'll just print the config
    print(f"Would render {args.animation} animation with config:")
    print(f"Output: {scene_config['output_file_path']}")
    print(f"Quality: {args.quality} ({scene_config['pixel_width']}x{scene_config['pixel_height']})")

    # In a real implementation, you'd call:
    # animation.render(**scene_config)


if __name__ == "__main__":
    main()