import re
import math
import ast
import operator
from fractions import Fraction

_SAFE_MATH_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_MATH_FUNCS = {
    "math.sqrt": math.sqrt,
    "math.log": math.log,
    "math.sin": math.sin,
    "math.cos": math.cos,
    "math.tan": math.tan,
    "math.gcd": math.gcd,
    "sqrt": math.sqrt,
    "log": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "gcd": math.gcd,
    "abs": abs,
    "round": round,
}

_SAFE_MATH_CONSTS = {
    "math.pi": math.pi,
    "math.e": math.e,
    "pi": math.pi,
    "e": math.e,
}

def _safe_eval_math(expr_str, extra_funcs=None):
    """Safely parse and evaluate mathematical expressions using AST.
    Restricts nodes strictly to numbers, math operators, constants, and whitelisted functions.
    Rejects any code execution, attributes, imports, or statements.
    """
    funcs = dict(_SAFE_MATH_FUNCS)
    if extra_funcs:
        funcs.update(extra_funcs)

    tree = ast.parse(expr_str, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, complex)):
                return node.value
            raise ValueError("Only numeric literals are allowed")
        elif isinstance(node, ast.Name):
            if node.id in _SAFE_MATH_CONSTS:
                return _SAFE_MATH_CONSTS[node.id]
            raise ValueError(f"Unknown or disallowed identifier: {node.id}")
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                full_name = f"{node.value.id}.{node.attr}"
                if full_name in _SAFE_MATH_CONSTS:
                    return _SAFE_MATH_CONSTS[full_name]
            raise ValueError("Unsupported attribute access")
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) in _SAFE_MATH_OPERATORS:
                return _SAFE_MATH_OPERATORS[type(node.op)](_eval(node.operand))
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        elif isinstance(node, ast.BinOp):
            if type(node.op) in _SAFE_MATH_OPERATORS:
                left = _eval(node.left)
                right = _eval(node.right)
                if isinstance(node.op, ast.Pow):
                    if isinstance(right, (int, float)) and right > 10000:
                        raise ValueError("Exponent too large")
                return _SAFE_MATH_OPERATORS[type(node.op)](left, right)
            raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
        elif isinstance(node, ast.Call):
            if node.keywords:
                raise ValueError("Keyword arguments are not allowed")
            fn = None
            if isinstance(node.func, ast.Name) and node.func.id in funcs:
                fn = funcs[node.func.id]
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                full_name = f"{node.func.value.id}.{node.func.attr}"
                if full_name in funcs:
                    fn = funcs[full_name]
            if fn is None:
                raise ValueError("Function call is not permitted")
            args = [_eval(a) for a in node.args]
            return fn(*args)
        else:
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")

    return _eval(tree)

# FIX (bug found via testing): functions that need a real Python call with
# parentheses around their argument(s), e.g. math.sqrt(16) instead of the
# old broken "math.sqrt16" (which crashed on every use).
FUNC_ARITY = {
    "math.sqrt": 1,
    "math.log": 1,
    "math.sin": 1,
    "math.cos": 1,
    "math.tan": 1,
    "math.gcd": 2,
    "lcm": 2,
}


def _build_safe_expression(tokens):
    """
    FIX: previously tokens were joined with "".join(expression), which
    glued function names directly onto numbers (e.g. "math.sqrt" + "16"
    became "math.sqrt16" — not valid Python, and not even a valid function
    call). This rebuilds a proper, parenthesized expression instead, e.g.
    "math.sqrt(16)" or "math.gcd(12, 8)", so eval() actually works.
    """
    parts = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in FUNC_ARITY:
            arity = FUNC_ARITY[tok]
            args = []
            i += 1
            while len(args) < arity and i < len(tokens):
                if re.match(r'^[\d.]+$', tokens[i]):
                    args.append(tokens[i])
                    i += 1
                elif tokens[i] in ('+', '-', '*', '/', '(', ')'):
                    i += 1  # skip stray connector tokens between arguments
                else:
                    break
            parts.append(f"{tok}({', '.join(args)})")
        else:
            parts.append(tok)
            i += 1
    return "".join(parts)


def calculate_expression(command):
    """Evaluate mathematical expressions, including advanced functions, from voice commands."""
    try:
        # Normalize the command
        command = command.lower()

        # Map number words to digits
        number_words = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
            "ten": "10"
        }
        for word, digit in number_words.items():
            command = re.sub(rf'\b{word}\b', digit, command)

        # Replace operators and keywords
        command = command.replace("plus", "+").replace("minus", "-")
        command = command.replace("times", "*").replace("into", "*")
        command = command.replace("divided by", "/").replace("over", "/")
        command = command.replace("what is", "").replace("calculate", "").strip()
        command = command.replace("average of", "average")
        command = command.replace("problems on numbers", "numbers_problem")
        command = command.replace("problems on ages", "ages_problem")
        command = command.replace("surds and indices", "surds_indices")
        command = command.replace("chain rule", "chain_rule")
        command = command.replace("time and work", "time_work")
        command = command.replace("area of", "area")
        command = command.replace("volume of", "volume")
        command = command.replace("problem on trains", "train_problem")
        command = command.replace("calendar problem", "calendar_problem")
        command = command.replace("clock problem", "clock_problem")
        command = command.replace("stocks and shares", "stocks_shares")
        command = command.replace("races", "race_problem")
        command = command.replace("partnership", "partnership_problem")
        command = command.replace("permutation of", "permutation")
        command = command.replace("combination of", "combination")
        command = command.replace("solve quadratic", "quadratic")
        command = command.replace("percentage of", "percentage")
        command = command.replace("convert", "convert_unit")

        # Replace advanced math terms with Python functions
        command = command.replace("square root of", "math.sqrt")
        command = command.replace("power of", "**").replace("to the power of", "**")
        command = command.replace("log of", "math.log").replace("log base", "math.log")
        command = command.replace("sin of", "math.sin").replace("cos of", "math.cos").replace("tan of", "math.tan")
        command = command.replace("hcf of", "math.gcd")
        command = command.replace("lcm of", "lcm")
        command = command.replace("fraction of", "Fraction")
        command = command.replace("simplify", "Fraction")

        # FIX (bug found via testing): the old code did
        #   command.replace("pi", "math.pi").replace("e", "math.e")
        # which replaced every single letter "e" anywhere in the string —
        # corrupting almost any normal English word ("area" -> "armath.ea",
        # "circle" -> "circlmath.e", etc.). Now we only replace "pi" and "e"
        # when they appear as their own standalone word.
        command = re.sub(r'\bpi\b', 'math.pi', command)
        command = re.sub(r'\be\b', 'math.e', command)

        # Define helper functions
        def average(*args):
            return sum(args) / len(args)

        def numbers_problem(*args):
            # Placeholder for problems on numbers logic
            return "Problems on numbers logic not implemented."

        def ages_problem(*args):
            # Placeholder for problems on ages logic
            return "Problems on ages logic not implemented."

        def surds_indices(expression):
            # Placeholder for surds and indices logic
            return "Surds and indices logic not implemented."

        def chain_rule(*args):
            # Placeholder for chain rule logic
            return "Chain rule logic not implemented."

        def time_work(*args):
            # Placeholder for time and work logic
            return "Time and work logic not implemented."

        def area(shape, *dimensions):
            if shape == "circle":
                return math.pi * dimensions[0] ** 2
            elif shape == "rectangle":
                return dimensions[0] * dimensions[1]
            elif shape == "triangle":
                return 0.5 * dimensions[0] * dimensions[1]
            else:
                return "Area calculation for this shape is not implemented."

        def volume(shape, *dimensions):
            if shape == "sphere":
                return (4 / 3) * math.pi * dimensions[0] ** 3
            elif shape == "cube":
                return dimensions[0] ** 3
            elif shape == "cylinder":
                return math.pi * dimensions[0] ** 2 * dimensions[1]
            else:
                return "Volume calculation for this shape is not implemented."

        def train_problem(*args):
            # Placeholder for problems on trains logic
            return "Problems on trains logic not implemented."

        def calendar_problem(*args):
            # Placeholder for calendar problems logic
            return "Calendar problems logic not implemented."

        def clock_problem(*args):
            # Placeholder for clock problems logic
            return "Clock problems logic not implemented."

        def stocks_shares(*args):
            # Placeholder for stocks and shares logic
            return "Stocks and shares logic not implemented."

        def race_problem(*args):
            # Placeholder for races logic
            return "Races logic not implemented."

        def partnership_problem(*args):
            # Placeholder for partnership logic
            return "Partnership logic not implemented."

        # Define LCM function
        def lcm(a, b):
            return abs(a * b) // math.gcd(a, b)

        def permutation(n, r):
            return math.factorial(n) // math.factorial(n - r)

        def combination(n, r):
            return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))

        def quadratic(a, b, c):
            discriminant = b**2 - 4*a*c
            if discriminant < 0:
                return "No real roots."
            elif discriminant == 0:
                root = -b / (2*a)
                return f"One root: {root}"
            else:
                root1 = (-b + math.sqrt(discriminant)) / (2*a)
                root2 = (-b - math.sqrt(discriminant)) / (2*a)
                return f"Two roots: {root1} and {root2}"

        def percentage(value, total):
            return (value / total) * 100

        def convert_unit(value, from_unit, to_unit):
            conversions = {
                "meters to kilometers": lambda x: x / 1000,
                "kilometers to meters": lambda x: x * 1000,
                "grams to kilograms": lambda x: x / 1000,
                "kilograms to grams": lambda x: x * 1000,
                "celsius to fahrenheit": lambda x: (x * 9/5) + 32,
                "fahrenheit to celsius": lambda x: (x - 32) * 5/9
            }
            key = f"{from_unit} to {to_unit}"
            if key in conversions:
                return conversions[key](value)
            else:
                return "Conversion not supported."

        # Extract numbers, operators, and allowed math functions
        expression = re.findall(r'[\d.]+|[\+\-\*/\(\)\^,]|math\.\w+|Fraction|lcm', command)
        if not expression:
            return "I couldn't understand the mathematical expression."

        # Check for specific keywords and call corresponding helper functions
        if "average" in command:
            numbers = [float(num) for num in re.findall(r'[\d.]+', command)]
            return f"The result is {average(*numbers)}"
        elif "area" in command:
            parts = command.split()
            shape = parts[1]  # Assuming the shape is the second word
            dimensions = [float(num) for num in re.findall(r'[\d.]+', command)]
            return f"The result is {area(shape, *dimensions)}"
        elif "volume" in command:
            parts = command.split()
            shape = parts[1]  # Assuming the shape is the second word
            dimensions = [float(num) for num in re.findall(r'[\d.]+', command)]
            return f"The result is {volume(shape, *dimensions)}"
        elif "train_problem" in command:
            return train_problem()
        elif "calendar_problem" in command:
            return calendar_problem()
        elif "clock_problem" in command:
            return clock_problem()
        elif "stocks_shares" in command:
            return stocks_shares()
        elif "race_problem" in command:
            return race_problem()
        elif "partnership_problem" in command:
            return partnership_problem()
        elif "permutation" in command:
            numbers = [int(num) for num in re.findall(r'\d+', command)]
            return f"The result is {permutation(*numbers)}"
        elif "combination" in command:
            numbers = [int(num) for num in re.findall(r'\d+', command)]
            return f"The result is {combination(*numbers)}"
        elif "quadratic" in command:
            coefficients = [float(num) for num in re.findall(r'[\d.]+', command)]
            return quadratic(*coefficients)
        elif "percentage" in command:
            values = [float(num) for num in re.findall(r'[\d.]+', command)]
            return f"The result is {percentage(*values)}%"
        elif "convert_unit" in command or "convert" in command:
            match = re.search(r'([\d.]+)\s*([a-zA-Z]+)\s+to\s+([a-zA-Z]+)', command)
            if match:
                value = float(match.group(1))
                from_unit = match.group(2).lower()
                to_unit = match.group(3).lower()
                return f"The result is {convert_unit(value, from_unit, to_unit)}"
            parts = command.split()
            try:
                numeric_candidates = [p for p in parts if re.match(r'^[\d.]+$', p)]
                if numeric_candidates and "to" in parts:
                    value = float(numeric_candidates[0])
                    to_idx = parts.index("to")
                    from_unit = parts[to_idx - 1]
                    to_unit = parts[to_idx + 1]
                    return f"The result is {convert_unit(value, from_unit, to_unit)}"
            except Exception:
                pass
            return "Please use the format: convert 10 meters to kilometers."

        # Join the extracted parts and evaluate safely via AST
        safe_expression = _build_safe_expression(expression)
        result = _safe_eval_math(safe_expression, extra_funcs={"lcm": lcm, "Fraction": Fraction})
        return f"The result is {result}"

    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except SyntaxError:
        return "Error: There seems to be a syntax error in your expression."
    except NameError:
        return "Error: The expression contains undefined terms or variables."
    except ValueError:
        return "Error: Invalid value encountered in the calculation."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"