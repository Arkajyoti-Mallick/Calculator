"""
Interactive CLI Calculator Interface
Provides an interactive command-line REPL for calculating expressions, managing memory, and viewing history.
"""

import os
import sys
from typing import List, Optional
from calculator_engine import CalculatorEngine, CalculationError


# ANSI Color Codes for terminal styling
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner(angle_mode: str) -> None:
    """Print the welcome banner for CLI mode."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}======================================================
               PYTHON CALCULATOR (CLI)
======================================================{Colors.RESET}
 {Colors.DIM}Type any math expression or command. Type 'help' for info.
 Angle Mode: {Colors.YELLOW}{angle_mode}{Colors.RESET}{Colors.DIM} | Exit: 'exit' or 'quit'{Colors.RESET}
{Colors.CYAN}------------------------------------------------------{Colors.RESET}
"""
    print(banner)


def print_help() -> None:
    """Display help information for CLI commands and math syntax."""
    help_text = f"""
{Colors.BOLD}Available Math Functions & Operators:{Colors.RESET}
  {Colors.CYAN}Basic Arithmetic:{Colors.RESET}  + , - , * , / , // (floor div) , % (mod or pct) , ^ or ** (power)
  {Colors.CYAN}Trigonometry:{Colors.RESET}      sin, cos, tan, asin, acos, atan, sinh, cosh, tanh
  {Colors.CYAN}Advanced Math:{Colors.RESET}     sqrt, cbrt, log (base 10), ln (natural log), log2, exp, abs, fact / !
  {Colors.CYAN}Constants:{Colors.RESET}         pi, e, tau, ans (last result)

{Colors.BOLD}Memory & Mode Commands:{Colors.RESET}
  {Colors.YELLOW}mode [deg|rad]{Colors.RESET}  - View or toggle angle mode (degrees / radians)
  {Colors.YELLOW}mem{Colors.RESET}             - Display current memory value
  {Colors.YELLOW}mc{Colors.RESET}              - Clear memory
  {Colors.YELLOW}mr{Colors.RESET}              - Recall memory value
  {Colors.YELLOW}ms <value>{Colors.RESET}      - Store value into memory
  {Colors.YELLOW}m+ <value>{Colors.RESET}      - Add value to memory
  {Colors.YELLOW}m- <value>{Colors.RESET}      - Subtract value from memory

{Colors.BOLD}General Commands:{Colors.RESET}
  {Colors.GREEN}history{Colors.RESET}         - View calculation history
  {Colors.GREEN}clear{Colors.RESET}           - Clear the terminal screen
  {Colors.GREEN}help{Colors.RESET}            - Show this help message
  {Colors.RED}exit / quit{Colors.RESET}     - Exit the calculator
"""
    print(help_text)


def show_history(engine: CalculatorEngine) -> None:
    """Display history of calculations."""
    history = engine.get_history()
    if not history:
        print(f"{Colors.DIM}No calculation history yet.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}Calculation History ({len(history)} items):{Colors.RESET}")
    print(f"{Colors.DIM}{'#':<4} {'Time':<10} {'Expression':<30} {'Result':<20}{Colors.RESET}")
    print("-" * 65)
    for idx, item in enumerate(history, 1):
        expr = item['expression']
        res = CalculatorEngine.format_number(item['result'])
        ts = item.get('timestamp', '')
        print(f"{idx:<4} {ts:<10} {Colors.CYAN}{expr:<30}{Colors.RESET} = {Colors.GREEN}{res:<20}{Colors.RESET}")
    print()


def run_cli() -> None:
    """Start the interactive CLI REPL session."""
    # Enable ANSI color support on Windows
    if os.name == "nt":
        os.system("color")

    engine = CalculatorEngine(angle_mode="DEG")
    print_banner(engine.angle_mode)

    while True:
        try:
            prompt = f"{Colors.BOLD}{Colors.BLUE}calc [{engine.angle_mode}] > {Colors.RESET}"
            user_input = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.DIM}Exiting calculator. Goodbye!{Colors.RESET}")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # Exit
        if cmd in ("exit", "quit", "q"):
            print(f"{Colors.DIM}Exiting calculator. Goodbye!{Colors.RESET}")
            break

        # Help
        if cmd == "help":
            print_help()
            continue

        # Clear screen
        if cmd in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            print_banner(engine.angle_mode)
            continue

        # History
        if cmd == "history":
            show_history(engine)
            continue

        # Angle mode toggle / view
        if cmd.startswith("mode"):
            parts = user_input.split()
            if len(parts) == 1:
                new_mode = engine.toggle_angle_mode()
                print(f"{Colors.YELLOW}Angle mode switched to: {new_mode}{Colors.RESET}")
            else:
                target = parts[1].upper()
                try:
                    engine.set_angle_mode(target)
                    print(f"{Colors.YELLOW}Angle mode set to: {engine.angle_mode}{Colors.RESET}")
                except CalculationError as err:
                    print(f"{Colors.RED}Error: {err}{Colors.RESET}")
            continue

        # Memory commands
        if cmd == "mem":
            print(f"{Colors.YELLOW}Memory = {CalculatorEngine.format_number(engine.memory_recall())}{Colors.RESET}")
            continue

        if cmd == "mc":
            engine.memory_clear()
            print(f"{Colors.YELLOW}Memory Cleared (0.0){Colors.RESET}")
            continue

        if cmd == "mr":
            val = engine.memory_recall()
            print(f"{Colors.YELLOW}Memory Recall = {CalculatorEngine.format_number(val)}{Colors.RESET}")
            continue

        if cmd.startswith("ms "):
            expr = user_input[3:].strip()
            try:
                val = engine.evaluate(expr)
                engine.memory_store(val)
                print(f"{Colors.YELLOW}Stored in Memory: {CalculatorEngine.format_number(val)}{Colors.RESET}")
            except CalculationError as err:
                print(f"{Colors.RED}Error: {err}{Colors.RESET}")
            continue

        if cmd.startswith("m+ "):
            expr = user_input[3:].strip()
            try:
                val = engine.evaluate(expr)
                new_mem = engine.memory_add(val)
                print(f"{Colors.YELLOW}Added {CalculatorEngine.format_number(val)} to Memory -> {CalculatorEngine.format_number(new_mem)}{Colors.RESET}")
            except CalculationError as err:
                print(f"{Colors.RED}Error: {err}{Colors.RESET}")
            continue

        if cmd.startswith("m- "):
            expr = user_input[3:].strip()
            try:
                val = engine.evaluate(expr)
                new_mem = engine.memory_subtract(val)
                print(f"{Colors.YELLOW}Subtracted {CalculatorEngine.format_number(val)} from Memory -> {CalculatorEngine.format_number(new_mem)}{Colors.RESET}")
            except CalculationError as err:
                print(f"{Colors.RED}Error: {err}{Colors.RESET}")
            continue

        # Evaluate standard expression
        try:
            result = engine.evaluate(user_input)
            formatted = CalculatorEngine.format_number(result)
            print(f"{Colors.GREEN}{Colors.BOLD}= {formatted}{Colors.RESET}")
        except CalculationError as err:
            print(f"{Colors.RED}Error: {err}{Colors.RESET}")
        except Exception as err:
            print(f"{Colors.RED}Unexpected Error: {err}{Colors.RESET}")


def evaluate_single_expression(expr: str, angle_mode: str = "DEG") -> int:
    """Evaluate a single expression from command line arguments and print output."""
    engine = CalculatorEngine(angle_mode=angle_mode)
    try:
        result = engine.evaluate(expr)
        print(CalculatorEngine.format_number(result))
        return 0
    except CalculationError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(evaluate_single_expression(" ".join(sys.argv[1:])))
    else:
        run_cli()
