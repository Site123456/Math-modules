# This is a Test of existing voice models (latest test with: pyttsx3)
# CORSPRITE HAS it's own voice input and output model
# This is a test for math calculation with basic math model
# Find the complete and better model at: https://github.com/Site123456/CORSPRITE

# To run this just run:
# pip install pyttsx3
# python main.py


import re
import threading
import queue
import pyttsx3
from math_modules import (
    add, subtract, multiply, divide,
    power, square_root, mod,
    make_fraction, add_fractions,
    subtract_fractions, multiply_fractions,
    divide_fractions
)

# pyttsx3 + QUEUE

engine = pyttsx3.init()
_speech_queue = queue.Queue()
_speech_thread = None
_speech_thread_started = False
_speech_lock = threading.Lock()

def _speech_worker():
    while True:
        text = _speech_queue.get()
        if text is None:
            break
        with _speech_lock:
            print(f"[VOICE] {text}")
            engine.say(text)
            engine.runAndWait()
        _speech_queue.task_done()

def _ensure_speech_thread():
    global _speech_thread_started, _speech_thread
    if not _speech_thread_started:
        _speech_thread_started = True
        _speech_thread = threading.Thread(target=_speech_worker, daemon=True)
        _speech_thread.start()

def speak(text: str):
    _ensure_speech_thread()
    _speech_queue.put(text)

def shutdown_speech():
    _speech_queue.put(None)
    if _speech_thread is not None:
        _speech_thread.join()

# NUMBER → WORDS (SMART)
num_words = {
    0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",
    10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",
    17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"forty",50:"fifty",
    60:"sixty",70:"seventy",80:"eighty",90:"ninety"
}

def number_to_words(n):
    if isinstance(n, float):
        return float_to_words(n)

    n = int(n)
    if n < 0:
        return "negative " + number_to_words(-n)

    if n < 20:
        return num_words[n]

    if n < 100:
        if n % 10 == 0:
            return num_words[n]
        return num_words[n - n % 10] + " " + num_words[n % 10]

    if n < 1000:
        if n % 100 == 0:
            return num_words[n // 100] + " hundred"
        return num_words[n // 100] + " hundred " + number_to_words(n % 100)

    return str(n)

def float_to_words(f):
    s = str(f).rstrip("0").rstrip(".")
    if "." not in s:
        return number_to_words(int(s))

    whole, dec = s.split(".")
    whole_words = number_to_words(int(whole))
    dec_words = " ".join(num_words[int(d)] for d in dec)
    return f"{whole_words} point {dec_words}"

# FRACTION → WORDS
fraction_names = {
    2:"half",3:"third",4:"fourth",5:"fifth",6:"sixth",7:"seventh",8:"eighth",9:"ninth",10:"tenth"
}

def fraction_to_words(frac):
    num = frac.numerator
    den = frac.denominator

    if num > den:
        whole = num // den
        rem = num % den
        if rem == 0:
            return number_to_words(whole)
        return f"{number_to_words(whole)} and {fraction_to_words(make_fraction(rem, den))}"

    if den in fraction_names:
        if num == 1:
            return f"one {fraction_names[den]}"
        return f"{number_to_words(num)} {fraction_names[den]}s"

    return f"{number_to_words(num)} over {number_to_words(den)}"

# OPERATOR → WORDS
op_words = {
    "+": "plus",
    "-": "minus",
    "*": "times",
    "/": "divided by",
    "%": "modulo",
    "^": "to the power of",
    "sqrt": "square root of"
}

# TOKENIZER
def tokenize(expr):
    expr = expr.replace(" ", "")
    expr = expr.replace("√", "sqrt")
    pattern = r'\d+/\d+|\d+\.?\d*|sqrt|\+|\-|\*|\/|\^|\%|\(|\)'
    return re.findall(pattern, expr)

# EXPRESSION CLEANUP
OPERATORS = {"+", "-", "*", "/", "%", "^"}

def clean_expression(expr: str) -> str:
    expr = expr.strip()
    while expr and expr[-1] in OPERATORS:
        expr = expr[:-1].rstrip()
    return expr

# VALUE PARSER
def parse_value(token):
    if "/" in token:
        num, den = token.split("/")
        return make_fraction(int(num), int(den))
    if token == "sqrt":
        return "sqrt"
    return float(token)

# PRECEDENCE
precedence = {
    "sqrt": 4,
    "^": 3,
    "*": 2,
    "/": 2,
    "%": 2,
    "+": 1,
    "-": 1
}

# SHUNTING-YARD → RPN
def to_rpn(tokens):
    output = []
    stack = []

    for t in tokens:
        if re.match(r'\d', t) or "/" in t:
            output.append(t)

        elif t == "sqrt":
            stack.append(t)

        elif t in precedence:
            while stack and stack[-1] in precedence and precedence[stack[-1]] >= precedence[t]:
                output.append(stack.pop())
            stack.append(t)

        elif t == "(":
            stack.append(t)

        elif t == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses.")
            stack.pop()

    while stack:
        top = stack.pop()
        if top in ("(", ")"):
            raise ValueError("Mismatched parentheses.")
        output.append(top)

    return output

# EXPRESSION TREE
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

def build_tree(rpn):
    stack = []
    for t in rpn:
        if t not in precedence and t != "sqrt":
            stack.append(Node(t))
        else:
            if t == "sqrt":
                a = stack.pop()
                stack.append(Node("sqrt", a, None))
            else:
                b = stack.pop()
                a = stack.pop()
                stack.append(Node(t, a, b))
    if len(stack) != 1:
        raise ValueError("Invalid expression.")
    return stack[0]

# PRETTY PRINT
def print_expr(node, parent_prec=0):
    if node.value == "sqrt":
        return f"√({print_expr(node.left, precedence['sqrt'])})"

    if node.left is None:
        return str(node.value)

    my_prec = precedence[node.value]
    left = print_expr(node.left, my_prec)
    right = print_expr(node.right, my_prec)

    expr = f"{left} {node.value} {right}"
    return f"({expr})" if my_prec < parent_prec else expr

# VALUE → WORDS
def value_to_words(v):
    if hasattr(v, "numerator"):
        return fraction_to_words(v)
    if isinstance(v, float):
        return float_to_words(v)
    return number_to_words(v)

# EVALUATION (WITH STEP ORDER)
def is_fraction(x):
    return hasattr(x, "numerator")

def eval_node(node, steps, spoken_steps):
    if node.left is None and node.right is None and node.value != "sqrt":
        return parse_value(node.value)

    if node.value == "sqrt":
        a = eval_node(node.left, steps, spoken_steps)
        res = square_root(a)
        steps.append(f"√({a}) = {res}")
        spoken_steps.append(f"{op_words['sqrt']} {value_to_words(a)} equals {value_to_words(res)}.")
        return res

    a = eval_node(node.left, steps, spoken_steps)
    b = eval_node(node.right, steps, spoken_steps)

    if is_fraction(a) or is_fraction(b):
        if node.value == "+": res = add_fractions(a, b)
        elif node.value == "-": res = subtract_fractions(a, b)
        elif node.value == "*": res = multiply_fractions(a, b)
        elif node.value == "/": res = divide_fractions(a, b)
        else: raise ValueError("Unsupported fraction operator.")
    else:
        if node.value == "+": res = add(a, b)
        elif node.value == "-": res = subtract(a, b)
        elif node.value == "*": res = multiply(a, b)
        elif node.value == "/": res = divide(a, b)
        elif node.value == "^": res = power(a, b)
        elif node.value == "%": res = mod(a, b)
        else: raise ValueError("Unknown operator.")

    steps.append(f"{a} {node.value} {b} = {res}")
    spoken_steps.append(
        f"{value_to_words(a)} {op_words[node.value]} {value_to_words(b)} equals {value_to_words(res)}."
    )
    return res

# The CORSPRITE architecture has been updated.
# Instead of streaming intermediate steps, only the final computation result is sent to the C++ application, and all voice is now handled entirely on the GPU, not the CPU.
def calculate_expression(expr: str, speak_steps=False):
    expr = clean_expression(expr)

    if not expr:
        speak("Impossible to calculate.")
        return None, [], [], ""

    try:
        tokens = tokenize(expr)
        rpn = to_rpn(tokens)
        tree = build_tree(rpn)

        pretty = print_expr(tree)

        steps = []
        spoken_steps = []
        result = eval_node(tree, steps, spoken_steps)

        spoken_expr = pretty.replace("sqrt", "square root of") \
                            .replace("*", " times ") \
                            .replace("/", " divided by ") \
                            .replace("%", " modulo ")
        speak(f"{spoken_expr}. The final result is {value_to_words(result)}.")

        if speak_steps:
            speak("Here are the steps. " + " ".join(spoken_steps))

        return result, steps, spoken_steps, pretty

    except Exception:
        speak("Impossible to calculate.")
        return None, [], [], ""

# MULTI-EXPRESSION SUPPORT
def split_expressions(raw: str):
    # Accept ; , and newlines as separators, mixed
    # Replace newlines with semicolons, then commas with semicolons, then split
    normalized = raw.replace("\n", ";").replace(",", ";")
    parts = [p.strip() for p in normalized.split(";")]
    return [p for p in parts if p]

def calculate_multiple(raw: str, speak_steps=True):
    expressions = split_expressions(raw)
    results = []

    for idx, expr in enumerate(expressions, start=1):
        print(f"\nExpression {idx}: {expr}")
        result, steps, spoken_steps, pretty = calculate_expression(expr, speak_steps=speak_steps)

        if result is None:
            print("  Error: Impossible to calculate.")
            results.append((expr, None, steps, pretty))
            continue

        # Print steps in clean block format
        for i, step in enumerate(steps, start=1):
            print(f"  Step {i}: {step}")
        print(f"Final result: {result}")

        results.append((expr, result, steps, pretty))

    return results

# OPTIONAL CLI
if __name__ == "__main__":
    try:
        while True:
            print("\nEnter one or more expressions.")
            print("You can separate them with ';', ',' or newlines.")
            raw = []
            line = input("Expression (or 'exit'): ")
            if line.lower().strip() in ["exit", "quit", "stop"]:
                break

            # Allow multi-line input until blank line
            raw.append(line)
            while True:
                more = input()
                if more.strip() == "":
                    break
                raw.append(more)

            full_input = "\n".join(raw)
            calculate_multiple(full_input, speak_steps=True)
    finally:
        shutdown_speech()
