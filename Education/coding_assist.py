from utils import speak
responses = {
    "what is python": "Python is a popular programming language used for web development, data analysis, machine learning, and automation. It is known for its readability and simplicity. Example: print('Hello, World!')",
    "features of python": "Python features include simple syntax, dynamic typing, automatic memory management, extensive libraries, and cross-platform support.",
    "advantages of python": "Python is easy to learn, highly readable, and has vast community support. It also supports multiple paradigms like procedural, object-oriented, and functional programming.",
    "disadvantages of python": "Python is slower than compiled languages, consumes more memory, and has limitations in mobile computing.",
    "applications of python": "Python is used in web development, AI, data science, automation, cybersecurity, and gaming.",
    "syntax of python": "Python syntax is simple and uses indentation for code blocks. Example: def greet(): print('Hello!')",
    "data types in python": "Python has several data types including int, float, str, list, tuple, dict, and set.",
    "control statements in python": "Python control statements include if-else, loops (for, while), and break, continue, pass statements.",
    "functions in python": "Functions in Python are defined using the def keyword. Example: def add(a, b): return a + b",
    "classes in python": "Python supports object-oriented programming with classes and objects. Example: class Car: def __init__(self, brand): self.brand = brand",
    "inheritance in python": "Python supports single, multiple, and multilevel inheritance using class-based hierarchies.",
    "modules in python": "Python modules allow code reusability. Example: import math; print(math.sqrt(16))",
    "file handling in python": "Python supports file operations like reading, writing, and appending using open() function. Example: with open('file.txt', 'r') as f: print(f.read())",
    "exception handling in python": "Python handles errors using try-except blocks. Example: try: x = 1/0 except ZeroDivisionError: print('Cannot divide by zero')",
    "decorators in python": "Decorators in Python modify functions dynamically using @decorator syntax. Example: @staticmethod",
    "generators in python": "Generators in Python use the yield keyword to return values lazily. Example: def gen(): yield 1; yield 2",
    "list comprehension in python": "List comprehensions provide concise ways to create lists. Example: squares = [x*x for x in range(10)]",
    "lambda function in python": "Lambda functions are anonymous functions written in one line. Example: add = lambda x, y: x + y",
    "difference between list and tuple in python": "Lists are mutable while tuples are immutable. Lists use square brackets [], tuples use parentheses ()",
    "difference between deep copy and shallow copy in python": "Shallow copy creates a new object but references nested objects, while deep copy creates a new object with copies of nested objects.",
    "difference between python 2 and python 3": "Python 3 has improved syntax, better Unicode support, and different print function usage compared to Python 2.",
    "what is java": "Java is a widely-used programming language known for its portability, efficiency, and object-oriented design. Example: System.out.println('Hello, World!')",
    "features of java": "Java features include platform independence, automatic memory management, strong security, and multi-threading support.",
    "advantages of java": "Java is platform-independent, has strong security, automatic garbage collection, and a rich set of APIs.",
    "disadvantages of java": "Java is slower than natively compiled languages, consumes more memory, and has verbose syntax.",
    "applications of java": "Java is used in enterprise applications, mobile development (Android), cloud computing, and web development.",
    "what is c++": "C++ is a high-performance programming language used for system/software development, game development, and in performance-critical applications. Example: std::cout << 'Hello, World!';",
    "features of c++": "C++ features include low-level memory manipulation, object-oriented programming, generic programming, and support for multiple inheritance.",
    "advantages of c++": "C++ offers high performance, close-to-hardware programming, and extensive library support.",
    "disadvantages of c++": "C++ can be complex and difficult to learn, has manual memory management, and lacks some modern features of other languages.",
    "applications of c++": "C++ is used in game development, systems programming, real-time simulations, and high-performance applications.",
    "what is html": "HTML (HyperText Markup Language) is the standard markup language for creating web pages. Example: <p>Hello, World!</p>",
    "features of html": "HTML features include the ability to structure content, support multimedia elements, and provide a foundation for web development.",
    "advantages of html": "HTML is easy to learn, widely supported, and forms the basis of web development.",
    "disadvantages of html": "HTML alone does not have dynamic capabilities, lacks advanced functionalities without CSS or JavaScript, and can become complex for large websites.",
    "applications of html": "HTML is used in web development to structure and display content, create web documents, and build user interfaces.",
# Python Installation
    "how to install python": "To install Python, follow these steps: 1) Visit the official Python website at python.org. 2) Download the installer for your operating system (Windows, macOS, or Linux). 3) Run the installer and follow the instructions. 4) Add Python to your PATH environment variable for easy access.",
     # Python Basics
    "python variables": "In Python, variables are used to store data. Example: x = 10; y = 'Hello'; z = 3.14",        "python operators": "Python operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (and, or, not), and assignment (=, +=, -=) operators.",
        "python import": "The `import` statement in Python is used to include external modules and libraries. Example: import math; print(math.sqrt(16))",
        # Java Installation
        "how to install java": "To install Java, follow these steps: 1) Visit the official Java website at oracle.com/java. 2) Download the JDK (Java Development Kit) for your operating system. 3) Run the installer and follow the instructions. 4) Set the JAVA_HOME environment variable and add Java to your PATH.",
        # Java Basics
        "java variables": "In Java, variables are used to store data. Example: int x = 10; String y = 'Hello'; double z = 3.14",
        "java operators": "Java operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "java import": "The `import` statement in Java is used to include external classes and packages. Example: import java.util.ArrayList; ArrayList<String> list = new ArrayList<>();",
        # C++ Installation
        "how to install c++": "To install C++, follow these steps: 1) Download and install a C++ compiler like GCC (for Linux) or MinGW (for Windows). 2) Install an IDE (Integrated Development Environment) like Code::Blocks or Visual Studio. 3) Set up your development environment and create a new C++ project.",
        # C++ Basics
        "c++ variables": "In C++, variables are used to store data. Example: int x = 10; std::string y = 'Hello'; double z = 3.14;",
        "c++ operators": "C++ operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "c++ import": "In C++, the `#include` directive is used to include external libraries and headers. Example: #include <iostream>; std::cout << 'Hello, World!';",
        # HTML Basics
        "html syntax": "HTML uses tags to structure content. Example: <html><head><title>Page Title</title></head><body><p>Hello, World!</p></body></html>",
        "html attributes": "HTML attributes provide additional information about elements. Example: <a href='https://example.com'>Link</a>",
        # JavaScript Basics
        "javascript variables": "In JavaScript, variables are used to store data. Example: let x = 10; let y = 'Hello'; let z = 3.14;",
        "javascript operators": "JavaScript operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "javascript import": "The `import` statement in JavaScript is used to include modules. Example: import {myFunction} from './myModule.js'; myFunction();",
        # Ruby Basics
        "ruby variables": "In Ruby, variables are used to store data. Example: x = 10; y = 'Hello'; z = 3.14",
        "ruby operators": "Ruby operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "ruby import": "The `require` statement in Ruby is used to include external libraries. Example: require 'date'; puts Date.today",
        # PHP Basics
        "php variables": "In PHP, variables are used to store data. Example: $x = 10; $y = 'Hello'; $z = 3.14;",
        "php operators": "PHP operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "php import": "The `include` and `require` statements in PHP are used to include external files. Example: include 'header.php';",
        # Swift Basics
        "swift variables": "In Swift, variables are used to store data. Example: var x = 10; var y = 'Hello'; var z = 3.14;",
        "swift operators": "Swift operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "swift import": "The `import` statement in Swift is used to include modules. Example: import Foundation; print(Date())",
        # Kotlin Basics
        "kotlin variables": "In Kotlin, variables are used to store data. Example: var x = 10; var y = 'Hello'; var z = 3.14;",
        "kotlin operators": "Kotlin operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "kotlin import": "The `import` statement in Kotlin is used to include modules. Example: import java.util.Date; println(Date())",
        # SQL Basics
        "sql syntax": "SQL is used to query and manipulate databases. Example: SELECT * FROM users;",
        "sql data types": "SQL data types include INT, VARCHAR, DATE, BOOLEAN, and FLOAT.",
        "sql commands": "Common SQL commands include SELECT, INSERT, UPDATE, DELETE, and CREATE.",
        # R Basics
        "r variables": "In R, variables are used to store data. Example: x <- 10; y <- 'Hello'; z <- 3.14",
        "r operators": "R operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (<-, =, <<-) operators.",
        "r import": "The `library` function in R is used to include packages. Example: library(ggplot2); ggplot(data, aes(x, y)) + geom_point()",
        # MATLAB Basics
        "matlab variables": "In MATLAB, variables are used to store data. Example: x = 10; y = 'Hello'; z = 3.14;",
        "matlab operators": "MATLAB operators include arithmetic (+, -, *, /), comparison (==, ~=, >, <), logical (&&, ||, ~), and assignment (=, +=, -=) operators.",
        "matlab import": "The `import` statement in MATLAB is used to include packages. Example: import matplotlib.pyplot as plt; plt.plot(x, y)",
        # Go Basics
        "go variables": "In Go, variables are used to store data. Example: var x int = 10; var y string = 'Hello'; var z float64 = 3.14",
        "go operators": "Go operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "go import": "The `import` statement in Go is used to include packages. Example: import 'fmt'; fmt.Println('Hello, World!')",
        # Rust Basics
        "rust variables": "In Rust, variables are used to store data. Example: let x = 10; let y = 'Hello'; let z = 3.14;",
        "rust operators": "Rust operators include arithmetic (+, -, *, /), comparison (==, !=, >, <), logical (&&, ||, !), and assignment (=, +=, -=) operators.",
        "rust import": "The `use` statement in Rust is used to include modules. Example: use std::io; println!('Hello, World!')",

    "what is css": "CSS (Cascading Style Sheets) is a stylesheet language used to describe the presentation of a document written in HTML or XML. It controls the layout, colors, fonts, and overall visual appearance of web pages.",
    "features of css": "CSS features include styling elements, layout control, responsive design, animation, and support for various media types.",
    "advantages of css": "CSS allows for separation of content and presentation, making it easier to maintain and update web pages. It also improves page load times and enables responsive design.",
    "disadvantages of css": "CSS can be challenging to debug, has inconsistent support across different browsers, and may lead to performance issues if not optimized.",
    "applications of css": "CSS is used in web design to control the visual appearance of web pages, create responsive designs, and enhance user experience.",
    "css syntax": "CSS syntax consists of selectors and declarations. Example: body { color: blue; font-size: 16px; }",
    "css selectors": "CSS selectors are used to target HTML elements. Example: element selector (p), class selector (.class), ID selector (#id), attribute selector (input[type='text'])",
    "css box model": "The CSS box model describes the rectangular boxes generated for elements. It includes content, padding, border, and margin.",
    "css positioning": "CSS positioning includes static, relative, absolute, fixed, and sticky positioning. Example: position: absolute;",
    "css flexbox": "CSS Flexbox is a layout model that provides an easy and efficient way to arrange items within a container. Example: display: flex; justify-content: center;",
    "css grid": "CSS Grid is a layout system that provides a way to create complex, responsive grid layouts. Example: display: grid; grid-template-columns: repeat(3, 1fr);",
    "css media queries": "CSS media queries are used to apply styles based on the characteristics of the device. Example: @media (max-width: 600px) { body { font-size: 14px; } }",
    "css transitions": "CSS transitions allow for smooth changes between property values. Example: transition: background-color 0.5s ease;",
    "css animations": "CSS animations enable complex animations with keyframes. Example: @keyframes slide { from { left: 0; } to { left: 100px; } }",
    "css variables": "CSS variables are custom properties that store values for reuse. Example: :root { --main-color: blue; } body { color: var(--main-color); }",
    "css frameworks": "CSS frameworks like Bootstrap, Foundation, and Tailwind CSS provide pre-designed components and styles to streamline web development.",
    "difference between css and css3": "CSS3 is the latest version of CSS with new features like animations, transitions, and enhanced layout options.",
    "css pseudo-classes": "CSS pseudo-classes are used to define the special states of an element. Example: a:hover { color: red; }",
    "css pseudo-elements": "CSS pseudo-elements are used to style specific parts of an element. Example: p::first-line { font-weight: bold; }",
    "how to include css": "CSS can be included in HTML using inline styles, internal stylesheets, or external stylesheets. Example: <link rel='stylesheet' href='styles.css'>",


        # If statement
        "if statement": "What is the syntax of an `if` statement in Python?",
        # If else statement
        "if else statement": "How does an `if else` statement work in Python?",
        # Elif statement
        "elif statement": "What is the purpose of the `elif` statement in Python?",
        # For loop
        "for loop": "How do you use a `for` loop in Python?",
        # While loop
        "while loop": "How do you use a `while` loop in Python?",
        # Nested loops
        "nested loops": "What are nested loops and how are they used in Python?",
        # Break statement
        "break statement": "What is the function of the `break` statement in Python?",
        # Continue statement
        "continue statement": "When would you use the `continue` statement in Python?",
        # Pass statement
        "pass statement": "What is the purpose of the `pass` statement in Python?",
        # Try except block
        "try except block": "How does a `try except` block work in Python?",
        # Functions
        "python functions": "How do you define and call a function in Python?",
        # Lambda functions
        "lambda functions": "What are lambda functions and how are they used in Python?",
        # Classes
        "python classes": "How do you define a class in Python?",
        # Inheritance
        "inheritance in python": "What is inheritance and how is it implemented in Python?",
        # Modules
        "python modules": "How do you import and use modules in Python?",
        # File handling
        "file handling in python": "How do you read from and write to files in Python?",
        # Arithmetic operators
        "arithmetic operators": "What are arithmetic operators in Python and how are they used?",
        # Comparison operators
        "comparison operators": "What are comparison operators in Python and how are they used?",
        # Logical operators
        "logical operators": "What are logical operators in Python and how are they used?",
        # Assignment operators
        "assignment operators": "What are assignment operators in Python and how are they used?",
        # Identity operators
        "identity operators": "What are identity operators in Python and how are they used?",
        # Membership operators
        "membership operators": "What are membership operators in Python and how are they used?",
        # Bitwise operators
        "bitwise operators": "What are bitwise operators in Python and how are they used?",
        # Tkinter
        "what is tkinter": "What is Tkinter and how is it used in Python?",
        "tkinter widgets": "What are some common widgets available in Tkinter?",
        "tkinter layout management": "How do you manage the layout of widgets in Tkinter?",
        "tkinter events": "How do you handle events in Tkinter?",
        # JWT
        "what is jwt": "What is JWT (JSON Web Token) and how is it used?",
        "jwt structure": "What is the structure of a JWT?",
        "jwt use cases": "What are some common use cases for JWT?",
        "jwt security": "How does JWT ensure security?",
        # GUI
        "what is gui": "What is a GUI (Graphical User Interface)?",
        "gui elements": "What are some common elements of a GUI?",
        "gui design principles": "What are some key principles of GUI design?",
        "gui frameworks": "What are some popular GUI frameworks for Python?"
   

      
}

def programming_help(command):
    command = command.lower()

    for key in responses.keys():
        if key in command:
            response = responses[key]
            speak(response)  
            return True
    return False

"""# Example usage
user_input = "Tell me about the features of Java."
programming_help(user_input)
"""