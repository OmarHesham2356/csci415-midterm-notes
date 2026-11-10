---
title: "CSCI415 Compiler Design — Midterm Master Notes"
course: CSCI415
exam: "Midterm (MCQ + Written)"
tags:
  - compiler-design
  - midterm
  - lexical-analysis
  - syntax-analysis
  - parsing
---

# CSCI415 — Compiler Design: Midterm Master Notes

> [!info] How to use this note
> This is a **single-source revision document** for Lectures 1–6. Each lecture is explained from first principles (assuming this is your first time), then followed by **exam traps**, **worked examples**, and **visual diagrams**.
> - Read the lecture sections in order first (they build on each other).
> - Then drill the **MCQ bank** and **Written bank** at the end.
> - The **Cram Sheet** is for the last hour before the exam.
> - Slide references like *(L3 s.21)* tell you where the point came from.

> [!tip] The one-sentence story of the course so far
> A compiler turns characters into tokens (**lexical analysis**, Lectures 2–3), then checks that the tokens form legal structure using a grammar (**syntax analysis**, Lectures 4–6). The midterm covers the **front end**: scanner + parser foundations.

## Contents

1. [[#1. Lecture 1 — Introduction to Compilers]]
2. [[#2. Lecture 2 — Lexical Analysis I]]
3. [[#3. Lecture 3 — Lexical Analysis II (DFA, Minimization, Code, State Elimination)]]
4. [[#4. Lecture 4 — Syntax Analysis I (CFGs and Recursion)]]
5. [[#5. Lecture 5 — Syntax Analysis II (Parse Trees, AST, Ambiguity)]]
6. [[#6. Lecture 6 — Syntax Analysis III (Top-Down / LL(1) Parsing)]]
7. [[#7. Cram Sheet — Definitions, Algorithms, Templates]]
8. [[#8. MCQ Bank (with answer key)]]
9. [[#9. Written-Exam Bank (with model answers)]]
10. [[#10. Top 25 Mistakes That Cost Marks]]
11. [[#11. Three-Day Revision Plan]]

## 0. Exam map: what the midterm can ask

| Lecture | Topic | Typical MCQ | Typical written question |
|---|---|---|---|
| 1 | Compiler definition, phases, language processing system, compiler vs interpreter | "Which component does X?", ordering of phases | Describe the phases / differentiate compiler & interpreter |
| 2 | Lexeme, token, pattern; automata; regular expressions | Identify tokens/lexemes; regex language | Write a regex for a described language |
| 3 | DFA/NFA, minimization, table-driven DFA, state elimination | Which states merge? What does `T[state,ch]` do? | Minimize a DFA; DFA → RE; RE → NFA → DFA |
| 4 | CFG, derivations, recursion | Which grammar generates L? Left/right recursion | Derive a string; design a CFG; convert regex → CFG |
| 5 | Parse trees, AST, ambiguity, precedence, dangling else | Which tree is correct? Is G ambiguous? | Show ambiguity; rewrite unambiguous grammar; dangling else |
| 6 | Top-down parsing, LL(1), parse table, stack trace | LL(1) meaning; next parser action; error detection | Build LL(1) table; trace input; detect error |

> [!warning] Grading note from Lecture 1
> Final 25%, **Midterm 15%**, lecture contribution 5%, quizzes 15% (best 2 of 3), assignments 10%, lab tasks 10%, project 20%. Percentages may change, but the **midterm is 15%** — treat the written part as the place marks are really separated.

```chatgpt-jsx
<Chart content={{"chartType":"bar","title":"CSCI415 assessment weights","xKey":"component","series":[{"dataKey":"weight","label":"Weight (%)"}],"data":[{"component":"Final","weight":25},{"component":"Midterm","weight":15},{"component":"Lecture contribution","weight":5},{"component":"Quizzes","weight":15},{"component":"Assignments","weight":10},{"component":"Lab tasks","weight":10},{"component":"Project","weight":20}],"meta":{"footer":"Midterm is 15% — the written section is where marks separate."}}}/>
```

---

# 1. Lecture 1 — Introduction to Compilers

## 1.1 What is a compiler?

> [!summary] Definition
> A **compiler** is a program that translates a program written in a **source language** into an **equivalent** program in a **target language**.

The key word is **equivalent**: the output must compute the same thing, not merely "look similar". Usually:

- Source language = high-level (C, C++, Java, …)
- Target language = low-level (assembly or machine code)

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (S) at (0,0) {Source Program\\{\footnotesize high-level}};
\node[box, minimum width=4.4cm, thick] (C) at (0,-1.9) {\textbf{COMPILER}};
\node[box] (T) at (0,-3.8) {Target Program\\{\footnotesize low-level / machine code}};
\draw[arr] (S) -- (C);
\draw[arr] (C) -- (T);
\end{tikzpicture}
\end{document}
```

### High-level vs low-level languages

| High-level | Low-level |
|---|---|
| Human-readable, portable | Machine-oriented, tied to hardware |
| `if`, loops, functions, objects | registers, jumps, memory addresses |
| Needs translation | Directly executable (after assembly/linking) |

A CPU only understands machine instructions. The compiler is the bridge between **what humans want to write** and **what the machine can execute**.

## 1.2 Execution process of a C program

This is the **language processing system** in action. Know the order and the output of each stage.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (S) at (0,0) {Source program (.c)};
\node[box] (P) at (0,-1.7) {Preprocessor};
\node[box] (C) at (0,-3.4) {Compiler};
\node[box] (A) at (0,-5.1) {Assembler};
\node[box] (L) at (0,-6.8) {Linker};
\node[box] (LD) at (0,-8.5) {Loader};
\node[box] (R) at (0,-10.2) {Execution};
\node[box, minimum width=4.2cm] (LIB) at (5.2,-6.8) {Libraries /\\object modules};
\draw[arr] (S) -- (P);
\draw[arr] (P) -- (C);
\draw[arr] (C) -- (A);
\draw[arr] (A) -- (L);
\draw[arr] (L) -- (LD);
\draw[arr] (LD) -- (R);
\draw[arr] (LIB) -- (L);
\end{tikzpicture}
\end{document}
```

> [!important] Memory hook
> **P-C-A-L-L**: **P**reprocessor → **C**ompiler → **A**ssembler → **L**inker → **L**oader.
> The compiler itself does **not** produce the final executable — the linker does.

### The five stages in detail (L1 s.23–28)

| Stage | Input → Output | What it does |
|---|---|---|
| **1. Preprocessor** | Source → preprocessed source | Deletes comments, includes other files (`#include`), performs macro substitution (`#define`). Required by some languages (C) or added later. |
| **2. Compiler** | Preprocessed code → assembly | Translates to assembly language, reveals bugs/errors, outputs target assembly code. |
| **3. Assembler** | Assembly → object file | Translates assembly into machine code. The **object file** contains machine instructions **plus the data** needed to place them in memory. |
| **4. Linker** | Object files + libraries → executable | **Links and merges** object files, **searches/locates** referenced routines, determines memory locations, and makes references **absolute**. |
| **5. Loader** | Executable → memory | Part of the OS. Loads programs/libraries into memory, calculates program size, allocates memory, initializes registers, starts execution. |

> [!warning] Exam trap
> - **Linker** resolves *external* references between object files (e.g., your `main` calling `printf`).
> - **Loader** puts the already-linked executable into RAM and starts it.
> - The **assembler** does **not** link; it only translates one assembly file into one object file.

## 1.3 A brief history (L1 s.18–21)

| Year | Event | Person / Team |
|---|---|---|
| **1952** | First compiler for the **A-0** language | **Grace Hopper** |
| **1954–1957** | First **complete** compiler, for **FORTRAN** | IBM team led by **John Backus** |
| ~same time | Study of natural-language structure | **Noam Chomsky** |
| 1960s–70s | **Chomsky hierarchy**; context-free languages & parsing algorithms; **finite automata** and **regular expressions** | Theory community |
| **1975** | **Yacc** parser generator (Unix) | **Steve Johnson** |
| ~same time | **Lex** scanner generator (Unix) | **Mike Lesk** |
| late 1970s–early 1980s | Automation of **code generation** | — |
| Modern | **Hindley–Milner** type inference (Haskell, OCaml, Rust); IDEs; **LLVM/Clang**; **JIT** (JVM, V8); **WebAssembly** | — |

> [!note] The point of the history slide
> The **fundamentals have not changed** for decades. LLVM, JIT, and WASM are built on top of the same lexical analysis, parsing, and code-generation ideas you are learning.

## 1.4 Phases of a compiler (L2 s.5–7)

This is the most important diagram of Lecture 1/2. Learn the **order** and the **data structure passed** between phases.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (A) at (0,0) {Character stream};
\node[box] (B) at (0,-1.7) {Lexical Analysis};
\node[box] (C) at (0,-3.4) {Syntax Analysis};
\node[box] (D) at (0,-5.1) {Semantic Analysis};
\node[box] (E) at (0,-6.8) {Intermediate Code\\Generation};
\node[box] (F) at (0,-8.5) {Intermediate Code\\Optimization};
\node[box] (G) at (0,-10.2) {Target Code\\Generation / Optimization};
\node[box] (H) at (0,-11.9) {Machine code};
\node[box, minimum width=3.2cm] (ST) at (5.4,-4.25) {Symbol Table +\\Error Handling};
\draw[arr] (A) -- (B);
\draw[arr] (B) -- node[right=3pt] {Token stream} (C);
\draw[arr] (C) -- node[right=3pt] {Syntax tree} (D);
\draw[arr] (D) -- node[right=3pt] {Annotated tree} (E);
\draw[arr] (E) -- node[right=3pt, font=\footnotesize] {intermediate representation (IR)} (F);
\draw[arr] (F) -- (G);
\draw[arr] (G) -- (H);
\draw[barr] (C) -- (ST);
\draw[barr] (D) -- (ST);
\end{tikzpicture}
\end{document}
```

| Phase | Input | Output | Main job |
|---|---|---|---|
| Lexical analysis | characters | tokens | Group characters into lexemes, classify them |
| Syntax analysis | tokens | syntax/parse tree | Check grammar structure |
| Semantic analysis | parse tree | annotated tree | Type checking, scope, meaning |
| Intermediate code generation | annotated tree | IR | Machine-independent middle form |
| Intermediate code optimization | IR | better IR | Faster/smaller without changing meaning |
| Target code generation | IR | machine code | Machine-dependent translation |
| Target code optimization | machine code | better machine code | Peephole/register optimizations |

### Front end vs back end

| Front end (machine **independent**) | Back end (machine **dependent**) |
|---|---|
| Lexical, syntax, semantic analysis | Target code generation |
| Intermediate code generation | Target code optimization |
| (Some) optimization | |
| Depends on **source language** | Depends on **target machine** |

### Analysis vs synthesis (L2 s.7)

- **Analysis** = analyze the source program to compute its properties. Includes lexical analysis, syntax analysis, semantic analysis, and optimization. *More mathematical and better understood.*
- **Synthesis** = produce the translated code. Includes code generation and optimization. *More specialized.*
- The two parts can be changed **independently** (this is why compilers are portable: retarget the back end, keep the front end).

## 1.5 Programs related to compilers (L1 s.30–33)

### Editors / IDEs

Compilers are bundled with editors into **Integrated Development Environments**. They are **structure-based** (oriented to the language's format) and may report errors like a compiler. Examples: **VS Code**, **Eclipse**, **PyCharm**, **Xcode / Android Studio**.

> [!tip] Modern connection
> The **Language Server Protocol (LSP)** lets any editor provide live autocomplete, error checking, and refactoring — built on the same parsing and semantic-analysis techniques as compilers.

### Debuggers

- Find **execution errors** in a compiled program.
- Keep track of source-code information.
- Halt execution at **breakpoints**.
- Must be supplied with **symbolic information by the compiler** (otherwise you can only debug machine code).

### Profilers

- Collect statistics during execution: **number of calls** to each procedure, **percentage of execution time**.
- Used to **improve performance** by finding hot spots.

## 1.6 Compiler vs interpreter (L1 s.36)

| Interpreter | Compiler |
|---|---|
| Translates **one statement at a time** | Scans the **entire program** and translates it into machine code |
| Takes **less time to analyze** the source, but **overall execution is slower** | Takes **more time to analyze**, but **overall execution is faster** |
| **No intermediate object code** → memory efficient | Generates intermediate object code → needs **linking** and more memory |
| Examples: JavaScript, Ruby (classic interpreters) | Examples: C, C++ (Java uses a compiler + JVM execution) |

> [!warning] Nuance that earns marks
> Real systems are hybrids. **Java** compiles to bytecode, then the **JVM** interprets/JIT-compiles it. **Python** compiles to bytecode, then the interpreter executes it. **JavaScript** engines (V8) use JIT. The clean "compiler vs interpreter" distinction is about **when** translation happens, not a law of nature.

## 1.7 Lecture 1 exam traps

> [!danger] Don't lose easy marks
> 1. The **linker** produces the executable, not the compiler.
> 2. The **loader** is part of the **operating system**.
> 3. **Lexical analysis** outputs a **token stream**, not a syntax tree.
> 4. **Semantic analysis** outputs an **annotated tree**.
> 5. The **front end** is machine-independent; the **back end** is machine-dependent.
> 6. **Yacc** = parser generator; **Lex** = scanner generator. Don't swap them.
> 7. **Grace Hopper** = first compiler (A-0, 1952); **Backus** = first complete compiler (FORTRAN, 1954–57).
> 8. Debuggers need **symbolic information from the compiler**.

## Lecture 1 checkpoint

```mcq-quiz
{
 "title": "Lecture 1 - The compiler and its phases (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "Which component produces the final executable in the language processing system?",
   "options": [
    "Compiler",
    "Assembler",
    "Linker",
    "Loader"
   ],
   "answer": 2,
   "explain": "The linker merges object files, resolves external references, and assigns absolute addresses to produce the executable.\n\n*Why the others are wrong:*\n- **A) Compiler:** translates preprocessed source to assembly — it does **not** produce the final executable.\n- **B) Assembler:** translates assembly to a relocatable object file, not an executable.\n- **D) Loader:** is part of the operating system; it loads the executable into memory at runtime."
  },
  {
   "q": "Which phase belongs to the compiler's back end?",
   "options": [
    "Lexical analysis",
    "Syntax analysis",
    "Semantic analysis",
    "Target code generation"
   ],
   "answer": 3,
   "explain": "The back end is machine-dependent and includes target code generation and target optimization.\n\n*Why the others are wrong:*\n- **A, B, C)** Lexical analysis, syntax analysis, and semantic analysis are all **front end** (machine-independent) phases."
  },
  {
   "q": "What does the **P** in **P-C-A-L-L** stand for?",
   "options": [
    "Parser",
    "Preprocessor",
    "Parser generator",
    "Postprocessor"
   ],
   "answer": 1,
   "explain": "P-C-A-L-L = Preprocessor → Compiler → Assembler → Linker → Loader.\n\n*Why the others are wrong:*\n- **A) Parser:** part of syntax analysis, not stage P.\n- **C) Parser generator:** a tool (e.g., Yacc), not a language-processing stage.\n- **D) Postprocessor:** not part of the standard P-C-A-L-L sequence."
  },
  {
   "q": "In `NUM(137)`, what is `137`?",
   "options": [
    "Token name",
    "Lexeme / attribute value",
    "Pattern",
    "Nonterminal"
   ],
   "answer": 1,
   "explain": "`NUM` is the token name (category); `137` is the lexeme (exact text matched) and the attribute value.\n\n*Why the others are wrong:*\n- **A) Token name:** that is `NUM`, not `137`.\n- **C) Pattern:** the pattern is `digit+` (or similar), a rule — not a concrete value.\n- **D) Nonterminal:** `137` is concrete text, not a grammar variable."
  },
  {
   "q": "What is the key difference between a compiler and an interpreter?",
   "options": [
    "Compiler translates the entire program at once; interpreter translates one statement at a time",
    "Compiler is always faster than interpreter",
    "Compiler needs no linking; interpreter does",
    "Compiler produces no intermediate code; interpreter does"
   ],
   "answer": 0,
   "explain": "A compiler scans and translates the whole program before execution; an interpreter processes and executes one statement at a time.\n\n*Why the others are wrong:*\n- **B) \"Always faster\":** not necessarily — interpreters can start faster and JIT compilers blur the line.\n- **C) Linking:** compilers typically **do** need linking; interpreters generally don't produce separate object files to link.\n- **D) Intermediate code:** compilers **do** often generate intermediate code; classic interpreters do not."
  },
  {
   "q": "Which of the following is NOT a compiler phase?",
   "options": [
    "Lexical analysis",
    "Syntax analysis",
    "Linking",
    "Code generation"
   ],
   "answer": 2,
   "explain": "Linking happens **after** compilation, inside the language processing system (performed by the linker).\n\n*Why the others are wrong:*\n- **A, B, D)** Lexical analysis, syntax analysis, and code generation are all standard compiler phases."
  },
  {
   "q": "The front end of a compiler is:",
   "options": [
    "Machine-dependent",
    "Machine-independent",
    "Only the code optimizer",
    "The same as the back end"
   ],
   "answer": 1,
   "explain": "The front end (lexical, syntax, semantic analysis, IR generation) does not depend on the target machine.\n\n*Why the others are wrong:*\n- **A) Machine-dependent:** that describes the **back end**.\n- **C) Only the code optimizer:** optimization is usually back end (machine-dependent).\n- **D) Same as back end:** they are distinct — front end is source-language focused, back end is target-machine focused."
  },
  {
   "q": "Who is credited with writing the first compiler (A-0)?",
   "options": [
    "John Backus",
    "Grace Hopper",
    "Dennis Ritchie",
    "Niklaus Wirth"
   ],
   "answer": 1,
   "explain": "Grace Hopper's A-0 (1952) is credited as the first compiler.\n\n*Why the others are wrong:*\n- **A) John Backus:** led the team that produced the first **complete** compiler (FORTRAN, 1954–57) — a common exam trap.\n- **C) Dennis Ritchie:** created C, much later.\n- **D) Niklaus Wirth:** created Pascal, much later."
  },
  {
   "q": "What does the scanner output?",
   "options": [
    "Parse tree",
    "Token stream",
    "Machine code",
    "Object file"
   ],
   "answer": 1,
   "explain": "The scanner (lexical analyzer) converts a character stream into a token stream for the parser.\n\n*Why the others are wrong:*\n- **A) Parse tree:** produced by the parser (syntax analysis).\n- **C) Machine code:** produced by the back end (code generation).\n- **D) Object file:** produced by the assembler."
  },
  {
   "q": "Which statement about the loader is true?",
   "options": [
    "It produces the executable",
    "It is part of the operating system",
    "It resolves external references between object files",
    "It translates assembly to machine code"
   ],
   "answer": 1,
   "explain": "The loader is an OS component that loads the executable into memory, allocates space, initializes registers, and starts execution.\n\n*Why the others are wrong:*\n- **A) Produces executable:** that's the **linker**.\n- **C) Resolves external references:** that's the **linker**.\n- **D) Translates assembly:** that's the **assembler**."
  }
 ]
}
```
---

# 2. Lecture 2 — Lexical Analysis I

## 2.1 Where the scanner sits (L2 s.9–11)

> [!summary] Definition
> **Lexical analysis (scanning)** is the phase that converts a **character stream** into a **token stream**. It provides the interface between the source program and the **parser**.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (S) at (0,0) {Source program};
\node[box] (L) at (0,-1.9) {Lexical Analyzer\\{\footnotesize scanner}};
\node[box] (P) at (0,-4.0) {Parser};
\node[box] (N) at (0,-5.9) {Next phase\\{\footnotesize semantic analysis}};
\node[box, minimum width=2.9cm] (ST) at (4.9,-1.9) {Symbol Table};
\draw[arr] (S) -- (L);
\draw[arr] (L) -- node[right=3pt] {tokens} (P);
\draw[arr] (P) to[bend left=42] node[left=3pt] {getNextToken()} (L);
\draw[barr] (L) -- (ST);
\draw[arr] (P) -- (N);
\end{tikzpicture}
\end{document}
```

- The parser **pulls** tokens by calling `getNextToken()` (this is why it is called a *scanner*: it scans on demand).
- The scanner may **insert identifiers/numbers into the symbol table** (optional but common).

### Goals of lexical analysis (L2 s.12)

1. **Divide** the character stream into meaningful sequences called **lexemes**.
2. **Label** each lexeme with a **token** (category), passed to the parser.
3. **Remove** non-significant blanks, newlines, tabs, and comments.
4. **Optionally update the symbol table** with identifiers and numbers.

> [!example] The classic picture
> Source: `5 + ( 1 × 2 )`
> Scanner → lexemes `5`, `+`, `(`, `1`, `×`, `2`, `)` → tokens `NUMBER`, `PLUS`, `LPAREN`, `NUMBER`, `TIMES`, `NUMBER`, `RPAREN`.
> The parser never sees characters — only tokens.

## 2.2 The three vocabulary words you must not confuse

| Term | Definition | Example |
|---|---|---|
| **Lexeme** | The actual sequence of characters in the source that matches a pattern | `x`, `count`, `137`, `if` |
| **Token** | A **category** of lexemes; consists of a **token name + optional attribute value** | `<id>`, `<number>`, `<keyword>` |
| **Pattern** | A rule (usually a **regular expression**) describing the set of strings for a token | `letter(letter\|digit)*` |

> [!important] Token ≠ lexeme
> The **token** is the *class*; the **lexeme** is the *instance*.
> `if` is a lexeme whose token is `IF`. `count` is a lexeme whose token is `ID`.
> Some tokens have only one lexeme (reserved words). Some have infinitely many (`ID`, `NUM`).

### Token categories (L2 s.15)

1. **Reserved words** — `IF`, `THEN` represent the strings `"if"`, `"then"`.
2. **Special symbols** — `PLUS`, `MINUS` represent `"+"`, `"-"`.
3. **Other tokens** — `NUM`, `ID` represent numbers and identifiers.

### Token attributes (L2 s.18)

A token carries extra information:

- `NUM("32767")` → string = `"32767"`, value = `32767`
- `PLUS("+")` → string = `"+"`, operation = addition
- A token = **category + attributes** (string, value, meaning, …).
- Only compute what later phases need. (e.g., the numeric value of `NUM` can be computed lazily.)

> [!warning] Attribute vs token name in MCQs
> In `NUM(137)`, **`NUM` is the token name** and **`137` is the attribute**. `137` is the **lexeme**. Do not call the attribute a token.

### The token record (L2 s.21)

A scanner usually returns a structured record:

```c
struct TokenRecord {
    TokenType tokenval;  // e.g. enum: IF, ID, NUM, PLUS, ...
    char *stringval;     // lexeme as a string (for identifiers)
    int numval;          // numeric value (for numbers)
};
```

## 2.3 Worked tokenization examples

### Example 1: `a[index] = 4 + 2` (L2 s.16)

| Lexeme | Token |
|---|---|
| `a` | identifier |
| `[` | left bracket |
| `index` | identifier |
| `]` | right bracket |
| `=` | assignment |
| `4` | number |
| `+` | plus sign |
| `2` | number |

### Example 2: `x = y + 10` (L2 s.22)

`x` → identifier, `=` → assignment operator, `y` → identifier, `+` → addition operator, `10` → number.

### Example 3: `while (137 < i) ++i;` (L2 s.27–43)

The scanner walks left to right, producing:

| Lexeme | Token | Attribute |
|---|---|---|
| `while` | `T_While` | — |
| `(` | `(` | — |
| `137` | `T_IntConst` | `137` |
| `<` | `<` | — |
| `i` | `T_Ident` | `"i"` |
| `)` | `)` | — |
| `++` | `++` | — |
| `i` | `T_Ident` | `"i"` |
| `;` | `;` | — |

Whitespace (`\n`, `\t`, spaces) is **discarded** — it has no bearing on meaning. But the *lexeme* of an identifier is stored as an attribute because later phases need the name.

The resulting syntax tree:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=3.6cm},
  level 2/.style={sibling distance=2.2cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] (W) {While}
  child {node[tnode] {\(<\)}
    child {node[tnode] {Ident(ip)}}
    child {node[tnode] {Ident(z)}}}
  child {node[tnode] {\(++\)}
    child {node[tnode] {Ident(ip)}}};
\end{tikzpicture}
\end{document}
```

> [!note] Longest match
> When the scanner sees `++`, it must prefer the **longest valid lexeme** (`++`) over two separate `+` tokens. This "maximal munch" rule is a favorite MCQ.

### Example 4: a `for` loop (L2 s.70–72)

```cpp
for (int k = 0; k < myArray[5]; ++k) { cout << k << endl; }
```

| Lexeme | Token category |
|---|---|
| `for`, `int` | keyword |
| `k`, `myArray`, `cout`, `endl` | identifier |
| `0`, `5` | integer constant |
| `(`, `)`, `{`, `}`, `[`, `]`, `;` | punctuation / special symbol |
| `=`, `<`, `++`, `<<` | operator |

Identifiers and constants carry attributes (the name string / numeric value); punctuation usually does not.

## 2.4 Automata theory background (L2 s.45–52)

An **automaton** is an abstract computing device with:

- **input**
- **temporary memory**
- **output**
- a **state** (what it remembers right now)

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (IN) at (0,0) {input};
\node[box] (A) at (0,-1.9) {Automaton\\{\footnotesize state + control}};
\node[box] (OUT) at (0,-3.8) {output};
\node[box, minimum width=3.2cm] (MEM) at (4.9,-1.9) {temporary memory};
\draw[arr] (IN) -- (A);
\draw[arr] (A) -- (OUT);
\draw[barr] (A) -- (MEM);
\end{tikzpicture}
\end{document}
```

Automata differ by their **temporary memory**:

| Automaton | Memory | Power | Example |
|---|---|---|---|
| **Finite Automaton (FA)** | none (only current state) | least | elevators, vending machines |
| **Pushdown Automaton (PDA)** | a **stack** (push/pop) | medium | compilers for programming languages |
| **Turing Machine (TM)** | **random-access memory** | highest | any algorithm |

> [!important] Why this matters
> **Lexical analysis uses finite automata** (regular expressions). **Parsing uses pushdown automata** (context-free grammars). This is the theoretical reason the two phases are separate and why regex cannot count nested parentheses.

### Formal languages

A **formal language** is simply a **set of strings**. Many infinite languages have finite descriptions:

1. a **regular expression**
2. an **automaton**
3. a **grammar**

All three can describe the same language compactly:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (RE) at (0,0) {Regular Expression};
\node[box] (NFA) at (-2.2,-3.2) {NFA};
\node[box] (DFA) at (2.2,-3.2) {DFA};
\draw[barr] (RE) -- (NFA);
\draw[barr] (NFA) -- (DFA);
\draw[barr] (DFA) -- (RE);
\end{tikzpicture}
\end{document}
```

> [!summary] Kleene's theorem (the theory behind Lecture 3)
> A language is **regular** iff it is recognized by a **DFA** iff it is recognized by an **NFA** iff it is described by a **regular expression**.

## 2.5 Regular expressions (L2 s.55–68)

Regular expressions describe **regular languages**. `L(r)` denotes the language of regex `r`.

### The three regular operations

For languages A and B:

- **Union:** $A \cup B = \{x \mid x \in A \text{ or } x \in B\}$
- **Concatenation:** $A \circ B = \{xy \mid x \in A \text{ and } y \in B\}$
- **Star (Kleene closure):** $A^* = \{x_1x_2\cdots x_k \mid k \ge 0,\ x_i \in A\}$

Note $k=0$ gives the **empty string ε**, so **ε is always in $A^*$**.

### Syntax conventions (L2 s.60)

| Notation | Meaning |
|---|---|
| `Σ` | shorthand for `(0 ∪ 1)` when Σ = {0,1} |
| `R+` | shorthand for `RR*` (**one or more**) |
| `R^k` | `R` concatenated with itself `k` times |
| `·` or juxtaposition | concatenation (dot may be omitted) |
| `+`, `∪`, `\|` | union (the slides use `+`; modern texts use `\|`) |
| `*` | Kleene star (zero or more) |

**Precedence (highest → lowest):**

1. **Star**
2. **Concatenation**
3. **Union**

So `ab* | c` means `(a(b*)) | c`, not `(ab)* | c`.

> [!danger] The notation trap
> In the slides, **`+` often means union/alternation**, e.g. `(a + b)*` = "any string of a's and b's".
> But **`R+` means one-or-more**.
> Read the context: between two complete expressions, `+` is union; as a postfix superscript, `+` is repetition.
> In this note I write **`|`** for union to avoid the clash.

### Recursive definition of regex (L2 s.61–62)

The regular expressions over Σ are precisely those obtained recursively:

1. **Base:** every terminal `a ∈ Σ`, plus **ε**, plus **∅**, is a regex.
2. **Union:** if `R1`, `R2` are regexes, so is `(R1 ∪ R2)`.
3. **Concatenation:** if `R1`, `R2` are regexes, so is `(R1 ∘ R2)`.
4. **Closure:** if `R` is a regex, so is `R*`.
5. Nothing else is a regex.

### Language semantics (L2 s.63)

| Regex | Language |
|---|---|
| `L(a)` | `{a}` for every `a ∈ Σ` |
| `L(ε)` | `{ε}` |
| `L(∅)` | `∅` |
| `L(R1 ∪ R2)` | `L(R1) ∪ L(R2)` |
| `L(R1 ∘ R2)` | `{w1w2 \mid w1 ∈ L(R1), w2 ∈ L(R2)}` |
| `L(R*)` | `(L(R))*` |

### Worked regex examples

**1. `r = (aa)*(bb)*b`** (L2 s.67)

`(aa)*` gives an even number of a's (including zero). `(bb)*b` gives `b` followed by an even number of b's — i.e., an **odd** number of b's. So:

$$L(r) = \{\, a^{2n}\,b^{2m+1} \mid n,m \ge 0 \,\}$$

The slide writes $a^{2n}b^{2m}b$ with $n,m \ge 0$ — same thing.

**2. `r = (0 + 1)* 00 (0 + 1)*`** (L2 s.68)

All strings over {0,1} that **contain the substring `00`** somewhere.

**3. Strings containing `bb`** (L2 s.73–74)

$$(a+b)^*\,bb\,(a+b)^*$$

Examples: `bba aabbab`, `bbbb`, `bbbbbbabbbbbaaa`. The two `bb` around the middle are mandatory; the rest can be anything.

**4. Email address** over alphabet `{a, @, .}` (L2 s.77)

The slide's clean version:

$$a^+\,(.a^+)^*\;@\;a^+\,.\,a^+\,(.a^+)^*$$

Read it as: one or more letters, then zero or more `.letters`, then `@`, then a domain with at least one dot. Examples: `compiler@nu.edu.eg`, `first.middle.last@mail.site.org`.

> [!warning] Regex gotcha
> `a+` in that email expression means **one or more a's** (postfix), *not* "a or nothing". This is exactly the notation clash described above.

## 2.6 Lecture 2 exam traps

> [!danger] High-frequency mistakes
> 1. **Token vs lexeme vs pattern** — see the table. `137` is a lexeme, `NUM` is a token, `digit+` is a pattern.
> 2. The scanner **removes comments and whitespace**; the parser never sees them.
> 3. The scanner outputs a **token stream**, not a parse tree.
> 4. **Finite automata have no temporary memory** — only states.
> 5. **PDA = stack**; **TM = RAM**.
> 6. `L((aa)*(bb)*b)` has an **odd** number of b's and an **even** number of a's.
> 7. In `(0+1)*00(0+1)*`, the `+` means **union**, not "one or more".
> 8. Precedence: **star > concatenation > union**.

## Lecture 2 checkpoint

```mcq-quiz
{
 "title": "Lecture 2 - Lexical Analysis I (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "The actual character sequence matched by a token pattern is called the:",
   "options": [
    "Lexeme",
    "Token",
    "Pattern",
    "Attribute"
   ],
   "answer": 0,
   "explain": "The lexeme is the exact text in the source that matches a pattern (e.g., `137`, `if`, `count`).\n\n*Why the others are wrong:*\n- **B) Token:** the token is the category (e.g., `NUM`, `IF`, `ID`) — the class, not the instance.\n- **C) Pattern:** the pattern is the rule (e.g., `digit+`) that describes which strings form the token.\n- **D) Attribute:** an attribute is extra information attached to a token (e.g., the numeric value `32767`)."
  },
  {
   "q": "Which automaton uses a stack as temporary memory?",
   "options": [
    "DFA",
    "NFA",
    "PDA",
    "Turing machine"
   ],
   "answer": 2,
   "explain": "A Pushdown Automaton has a stack (push/pop) as temporary memory — the model for parsing (context-free languages).\n\n*Why the others are wrong:*\n- **A) DFA:** finite automaton with **no** temporary memory — only states.\n- **B) NFA:** also has no temporary memory; nondeterminism ≠ memory.\n- **D) Turing machine:** uses random-access memory (tape), not just a stack."
  },
  {
   "q": "What does the scanner output?",
   "options": [
    "Parse tree",
    "Token stream",
    "Machine code",
    "Object file"
   ],
   "answer": 1,
   "explain": "The scanner converts characters into tokens and hands a token stream to the parser.\n\n*Why the others are wrong:*\n- **A) Parse tree:** produced by the parser.\n- **C) Machine code:** produced by the code generator (back end).\n- **D) Object file:** produced by the assembler."
  },
  {
   "q": "What does the scanner remove so the parser never sees it?",
   "options": [
    "Keywords",
    "Whitespace and comments",
    "Operators",
    "Identifiers"
   ],
   "answer": 1,
   "explain": "The scanner discards blanks, tabs, newlines, and comments; they carry no syntactic meaning for the parser.\n\n*Why the others are wrong:*\n- **A) Keywords:** become tokens (e.g., `IF`), which the parser needs.\n- **C) Operators:** become tokens (e.g., `PLUS`, `TIMES`).\n- **D) Identifiers:** become tokens (e.g., `ID`), with the name as an attribute."
  },
  {
   "q": "In `NUM(\"32767\")`, what is `\"32767\"`?",
   "options": [
    "Token name",
    "Attribute / lexeme string",
    "Pattern",
    "Nonterminal"
   ],
   "answer": 1,
   "explain": "`\"32767\"` is the lexeme (the actual text) stored as a string attribute; `NUM` is the token name.\n\n*Why the others are wrong:*\n- **A) Token name:** `NUM` is the token name.\n- **C) Pattern:** `digit+` is the pattern.\n- **D) Nonterminal:** `\"32767\"` is concrete terminal text, not a grammar variable."
  },
  {
   "q": "Which regex operator means \"one or more repetitions\"?",
   "options": [
    "R*",
    "R+",
    "R?",
    "R | ε"
   ],
   "answer": 1,
   "explain": "`R+` is shorthand for `RR*` — at least one `R`, followed by zero or more additional `R`s.\n\n*Why the others are wrong:*\n- **A) R*:** zero or more (Kleene star) — allows the empty string.\n- **C) R?:** zero or one (optional).\n- **D) R | ε:** `R` or empty — also optional."
  },
  {
   "q": "Regex precedence (highest → lowest):",
   "options": [
    "Union > Concatenation > Star",
    "Star > Concatenation > Union",
    "Concatenation > Star > Union",
    "Union > Star > Concatenation"
   ],
   "answer": 1,
   "explain": "`ab* | c` means `(a(b*)) | c`, not `(ab)* | c`.\n\n*Why the others are wrong:*\n- **A, C, D)** all invert the correct precedence order."
  },
  {
   "q": "The maximal munch (longest match) rule means:",
   "options": [
    "Match the shortest valid lexeme",
    "Match the longest valid lexeme",
    "Always match keywords first",
    "Never match operators"
   ],
   "answer": 1,
   "explain": "When the scanner sees `++`, it must produce one `++` token, not two separate `+` tokens.\n\n*Why the others are wrong:*\n- **A) Shortest:** the opposite — maximal munch picks the longest.\n- **C) Keywords first:** not a rule; keywords and identifiers are matched by their patterns.\n- **D) Never match operators:** operators are matched normally."
  },
  {
   "q": "The language `L((aa)*(bb)*b)` has:",
   "options": [
    "Even number of a's and odd number of b's",
    "Odd number of a's and even number of b's",
    "Equal numbers of a's and b's",
    "Only b's"
   ],
   "answer": 0,
   "explain": "`(aa)*` → even number of a's (including zero). `(bb)*b` → `b` plus an even number of b's = odd number of b's.\n\n*Why the others are wrong:*\n- **B)** reversed — it's even a's, odd b's.\n- **C)** no constraint on equality.\n- **D)** a's are allowed."
  },
  {
   "q": "In `(0+1)*00(0+1)*`, what does the `+` mean?",
   "options": [
    "One or more",
    "Union (OR)",
    "Concatenation",
    "Kleene star"
   ],
   "answer": 1,
   "explain": "Between two complete expressions, `+` is union: `(0 ∪ 1)`. This is the notation clash trap — `R+` (postfix) means one-or-more, but `+` between expressions means union.\n\n*Why the others are wrong:*\n- **A) One or more:** that's postfix `R+`, not infix `+` between expressions.\n- **C) Concatenation:** juxtaposition is concatenation.\n- **D) Kleene star:** that's `*`."
  }
 ]
}
```
---

# 3. Lecture 3 — Lexical Analysis II (DFA, Minimization, Code, State Elimination)

## 3.1 The big picture: five steps from spec to scanner

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (S0) at (0,0) {\(S_0\)};
\node[st] (S1) at (0,-2.0) {\(S_1\)};
\node[acc] (S2) at (0,-4.0) {\(S_2\)};
\draw[arr] (start) -- (S0);
\draw[arr] (S0) edge[loop left] node[left] {\(b\)} (S0);
\draw[arr] (S0) -- node[right] {\(a\)} (S1);
\draw[arr] (S1) edge[loop right] node[right] {\(a\)} (S1);
\draw[arr] (S1) -- node[right] {\(b\)} (S2);
\end{tikzpicture}
\end{document}
```

> [!summary] The exam's favorite pipeline
> **RE → NFA (Thompson) → DFA (subset construction) → minimal DFA (equivalence theorem) → table-driven code.**
> Each arrow is a construction you must be able to perform by hand.

**Automating scanner construction (L3 s.17):** (1) write the RE, (2) build the NFA with Thompson's construction, (3) build the DFA with subset construction, (4) systematically shrink the DFA, (5) turn it into code.

## 3.2 Lexical specification with regexes (L3 s.5–7)

A language's tokens are specified as regular expressions:

```text
keyword    = begin | end | if | then | else
identifier = letter (letter | digit | underscore)*
integer    = digit+
relop      = < | <= | = | <> | > | >=
letter     = a | b | ... | z | A | B | ... | Z
digit      = 0 | 1 | 2 | ... | 9
```

| Regex | Meaning |
|---|---|
| `[abc]+` = `(a+b+c)+` | one or more occurrences of a, b, or c |
| `[abc]*` = `(a+b+c)*` | zero or more occurrences of a, b, or c |
| `[0-9]+` | one or more digits (the slide writes `(0+1+...+9)*` — the intent is **one or more**, so `+`, not `*`) |
| `[1-9][0-9]*` | a number **without leading zeros** |
| `[a-zA-Z][a-zA-Z0-9_]*` | identifier: first a letter, then letters/digits/underscores |

> [!warning] Slide typo alert
> `[0-9]+ = (0+1+2+...+9)*` as printed would allow the empty string. The intended regex is `(0+1+...+9)+` (one or more digits). If an exam option says `[0-9]*` matches `""`, that is true of the printed regex but **not** of the integer token the slide describes.

## 3.3 Finite automata (L3 s.10–16)

A **finite automaton** has:

1. **Start state** — drawn with an unlabeled arrow "from nowhere". Recognition begins here.
2. **Transitions** — labeled arrows recording a change of state when a character matches.
3. **Accepting state(s)** — drawn with a **double circle**; reaching one at end of input = accept.

| | DFA (Deterministic) | NFA (Nondeterministic) |
|---|---|---|
| Next state | **Exactly one** state for each (state, symbol) | Can be **several** (or none) |
| ε-transitions | Not allowed | Allowed |
| Ease of construction | Harder | **Easier** (algorithmic, Thompson) |
| Ease of implementation | **Easier/faster** | Harder (needs simulation/backtracking) |
| Relation | Every DFA is an NFA | Every NFA can be converted to a DFA |

> [!important] Why both exist
> NFAs are **easy to build** from regexes (union/star/concat via ε-edges) but **hard to execute**. DFAs are **fast to execute** (one table lookup per character) but **hard to build directly**. So: build NFA, convert to DFA, then code the DFA.

### Example: strings that begin with `1` and end with `0` (L3 s.14)

DFA (the accepting state is `S2`):

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (N0) at (0,0) {\(N_0\)};
\node[st] (N1) at (0,-2.1) {\(N_1\)};
\node[acc] (N2) at (0,-4.2) {\(N_2\)};
\draw[arr] (start) -- (N0);
\draw[arr] (N0) edge[loop left] node[left] {\(a, b\)} (N0);
\draw[arr] (N0) -- node[right] {\(a\)} (N1);
\draw[arr] (N1) -- node[right] {\(b\)} (N2);
\end{tikzpicture}
\end{document}
```

NFA for the same language is simpler to write: a start state goes to the second state on `a`, loops on `a,b`, then goes to accept on `b`.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (A) at (0,0) {\(A\)};
\node[st] (B) at (-2.5,-2.0) {\(B\)};
\node[st] (D) at (2.5,-2.0) {\(D\)\\{\footnotesize dead}};
\node[acc] (C) at (0,-4.0) {\(C\)};
\draw[arr] (start) -- (A);
\draw[arr] (A) -- node[above left] {\(1\)} (B);
\draw[arr] (A) -- node[above right] {\(0\)} (D);
\draw[arr] (B) edge[loop left] node[left] {\(1\)} (B);
\draw[arr] (B) -- node[above left] {\(0\)} (C);
\draw[arr] (D) edge[loop right] node[right] {\(0, 1\)} (D);
\end{tikzpicture}
\end{document}
```

> [!note] Both recognize the same language
> `L = { w | w ends with "ab" }`. The NFA "guesses" where the final `ab` begins; the DFA tracks the longest suffix seen so far.

### Example: strings ending in `ab` (L3 s.13)

Regex: `1 Σ* 0`.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (q0) at (0,0) {\(q_0\)};
\node[st] (q1) at (-2.7,-2.2) {\(q_1\)};
\node[st] (q2) at (2.7,-2.2) {\(q_2\)};
\node[st] (q3) at (-1.5,-4.2) {\(q_3\)};
\node[acc] (q4) at (0,-6.0) {\(q_4\)};
\draw[arr] (start) -- (q0);
\draw[arr] (q0) -- node[above left] {\(a\)} (q1);
\draw[arr] (q0) -- node[above right] {\(b\)} (q2);
\draw[arr] (q1) edge[loop left] node[left] {\(a\)} (q1);
\draw[arr] (q1) -- node[below left] {\(b\)} (q3);
\draw[arr] (q2) -- node[above] {\(a\)} (q1);
\draw[arr] (q2) edge[loop right] node[right] {\(b\)} (q2);
\draw[arr] (q3) -- node[below left] {\(b\)} (q4);
\draw[arr] (q3) to[bend right=18] node[right=1pt] {\(a\)} (q1);
\draw[arr] (q4) to[bend right=22] node[left=2pt] {\(a\)} (q1);
\draw[arr] (q4) to[bend left=22] node[right=2pt] {\(b\)} (q2);
\end{tikzpicture}
\end{document}
```

- `B` = "have seen the leading 1, still reading middle symbols".
- `C` = "ended with 0" → **accept**.
- `D` = **dead state**: started with 0, can never recover. (Often omitted in drawings; formally it is needed so the DFA is complete.)

NFA version: `A --1--> B`, `B --0,1--> B`, `B --0--> C(accept)`.

> [!warning] DFA completeness
> A DFA must have a transition for **every** symbol from **every** state (or explicitly have no transition = reject). If you draw a DFA and leave an arrow out, add a **dead state** to be formally correct.

## 3.4 DFA minimization (L3 s.18–32)

### Why minimize?

A DFA derived mechanically from a regex may have **more states than necessary**. Minimization produces an equivalent DFA with the **minimum** number of states. The lecture names the **Hopcroft state-minimization algorithm**; the partition-refinement procedure below is the exam-friendly version of the same idea.

> [!important] Uniqueness theorem
> Given any DFA, there is an equivalent DFA with the **minimum** number of states, and this minimum-state DFA is **unique up to renaming of states**.

### The equivalence theorem algorithm (L3 s.21)

1. **Initial partition $P_0$:** split all states into **final** and **non-final** states. All states in a block are 0-equivalent. Set $k = 0$.
2. **Refine:** increment $k$. For each block of $P_k$, split it if its states are **k-distinguishable**. Two states $X,Y$ in the same block are **k-distinguishable** if there is an input symbol $S$ such that $\delta(X,S)$ and $\delta(Y,S)$ are **(k−1)-distinguishable** (i.e., they land in different blocks of $P_{k-1}$).
3. **Repeat** until $P_k = P_{k-1}$.
4. **Build** the reduced DFA: each final block becomes one new state.

> [!tip] Practical version
> Repeatedly look at each block. Group states that, for **every** input symbol, go to the **same block**. If a symbol sends them to different blocks, split. Stop when nothing splits.

> [!warning] Do this first
> **Remove inaccessible states** (not reachable from the start) and **dead states** (cannot reach a final state) before or during minimization. They create fake distinctions and never help.

### Worked Example 1 (L3 s.22–25)

Original DFA: states `q0..q4`, `q4` accepting.

| State | a | b |
|---|---|---|
| → q0 | q1 | q2 |
| q1 | q1 | q3 |
| q2 | q1 | q2 |
| q3 | q1 | *q4 |
| *q4 | q1 | q2 |

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (A) at (0,0) {\(A\)};
\node[st] (B) at (-2.6,-2.1) {\(B\)};
\node[st] (C) at (0,-4.1) {\(C\)};
\node[acc] (D) at (0,-6.0) {\(D\)};
\node[font=\footnotesize, align=center] at (0,-7.9) {\(A=\{q_0,q_2\}\quad B=\{q_1\}\)\\\(C=\{q_3\}\quad D=\{q_4\}\)};
\draw[arr] (start) -- (A);
\draw[arr] (A) edge[loop right] node[right] {\(b\)} (A);
\draw[arr] (A) -- node[above left] {\(a\)} (B);
\draw[arr] (B) edge[loop left] node[left] {\(a\)} (B);
\draw[arr] (B) -- node[above left] {\(b\)} (C);
\draw[arr] (C) -- node[below] {\(b\)} (D);
\draw[arr] (C) to[bend right=18] node[right=1pt] {\(a\)} (B);
\draw[arr] (D) to[bend left=25] node[left=2pt] {\(a\)} (B);
\draw[arr] (D) to[bend right=28] node[right=2pt] {\(b\)} (A);
\end{tikzpicture}
\end{document}
```

**Partitions:**

- $P_0 = \{q0,q1,q2,q3\}\{q4\}$ — final vs non-final.
- $P_1 = \{q0,q1,q2\}\{q3\}\{q4\}$ — `q3` is the only non-final state that can reach `q4` in one step on `b`.
- $P_2 = \{q0,q2\}\{q1\}\{q3\}\{q4\}$ — `q1` differs from `q0,q2` on `b` (`q1 → q3`, the others → `q2`).
- $P_3 = P_2$ → stop.

**Conclusion:** `q0 ≡ q2`; merge them. Minimal DFA has **4 states**:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (S1) at (0,0) {1\\{\footnotesize start}};
\node[acc] (S2) at (0,-2.3) {2};
\draw[arr] (start) -- (S1);
\draw[arr] (S1) -- node[right] {letter} (S2);
\draw[arr] (S2) edge[loop right] node[right] {letter, digit} (S2);
\end{tikzpicture}
\end{document}
```

### Worked Example 2 — inaccessible state (L3 s.26–30)

Original has `q3` **inaccessible** from `q0`; remove it and its edges. Remaining table:

| State | a | b |
|---|---|---|
| → q0 | *q1 | q0 |
| *q1 | *q2 | *q1 |
| *q2 | *q1 | *q2 |

- $P_0 = \{q0\}\{q1,q2\}$ (q1, q2 final).
- On `a`: q1→q2, q2→q1, both in the final block. On `b`: q1→q1, q2→q2, both in the same block. No split.
- $P_1 = P_0$ → merge `q1,q2`.

Minimal DFA: `A = q0`, `B = {q1,q2}` accepting; `A -a-> B`, `A -b-> A`; `B -a-> B`, `B -b-> B`.

### Worked Example 3 — `letter(letter|digit)*` (L3 s.31)

The subset construction produces accepting sets:

- `{2,3,4,5,7,10}`
- `{4,5,6,7,9,10}`
- `{4,5,7,8,9,10}`

and one non-accepting set `{1}`. All accepting sets behave identically (letters/digits loop among them), so they merge. Result: **2 states**:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (-1.8,1.0) {};
\node[acc] (A) at (-1.8,0) {1};
\node[acc] (B) at (1.8,-2.3) {2, 3};
\draw[arr] (start) -- (A);
\draw[arr] (A) to[bend left=20] node[right=2pt] {\(a\)} (B);
\draw[arr] (A) to[bend right=20] node[left=2pt] {\(b\)} (B);
\draw[arr] (B) edge[loop right] node[right] {\(b\)} (B);
\end{tikzpicture}
\end{document}
```

### Worked Example 4 — `(a|ε)b*` (L3 s.32)

Regex accepts ε, `a`, and then any number of `b`s. All states `{1,2,3}` are accepting. `a` distinguishes state 1 from states 2 and 3, so:

- $P_0 = \{1,2,3\}\{\}$ (no non-accepting states).
- Split on `a`: state 1 goes to an accepting state; states 2,3 go to the dead state. So $P_1 = \{1\}\{2,3\}$.

Minimal DFA:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (S1) at (0,0) {1};
\node[st] (S2) at (0,-2.1) {2};
\node[acc] (S3) at (0,-4.2) {3};
\draw[arr] (start) -- (S1);
\draw[arr] (S1) -- node[right] {letter} (S2);
\draw[arr] (S2) edge[loop right] node[right] {letter, digit} (S2);
\draw[arr] (S2) -- node[right] {other} (S3);
\end{tikzpicture}
\end{document}
```

> [!warning] `a` has no transition from state 2,3
> In a complete DFA, `2,3 --a--> dead`. That dead state is not accepting, which is exactly why `1` and `{2,3}` split.

## 3.5 Turning a DFA into code (L3 s.33–39)

### Option A: Direct simulation (hand-written `if`/`while`)

```text
{ start in state 1 }
if the next character is a letter then
    advance the input;                  { now in state 2 }
    while the next character is a letter or a digit do
        advance the input;              { stay in state 2 }
    end while;
    { go to state 3 without advancing the input }
    accept;
else
    error or other cases
end if;
```

This works for the identifier DFA:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0) {};
\node[st] (qi) at (0,-1.3) {\(q_i\)};
\node[st] (A) at (0,-2.8) {\(A\)};
\node[st] (B) at (0,-4.3) {\(B\)};
\node[st] (qf) at (0,-5.8) {\(q_f\)};
\node[acc] (end) at (0,-7.4) {};
\draw[arr] (start) -- (qi);
\draw[arr] (qi) -- node[right] {\(\varepsilon\)} (A);
\draw[arr] (A) -- node[right] {\(0\)} (B);
\draw[arr] (B) edge[bend right=55] node[right=1pt] {\(1\)} (A);
\draw[arr] (B) -- node[right] {\(\varepsilon\)} (qf);
\draw[arr] (qf) -- (end);
\end{tikzpicture}
\end{document}
```

**Why it is problematic (L3 s.36):**

1. **Ad hoc / not systematic** — you handcraft the control flow per DFA.
2. **Blows up** with more states and edges (deep `if…else if…` chains).
3. **Hard to modify or reuse.**
4. **Duplicated logic.**

### Option B: Table-driven DFA (the standard solution)

Use three tables:

- `T[state, input]` — the **next state**.
- `Advance[state, input]` — should we **consume** the input character?
- `Accept[state]` — is this state accepting?

For the identifier DFA:

| state | letter | digit | other | Accepting |
|---|---|---|---|---|
| 1 | 2 | – | – | no |
| 2 | 2 | 2 | **[3]** | no |
| 3 | – | – | – | **yes** |

```text
state ← 1
while not error(state) do
    newstate ← T[state, ch]
    if Advance[state, ch] then
        ch ← next input character
    end if
    state ← newstate
end while
if Accept[state] then
    accept
else
    error
end if
```

> [!important] The `Advance` trick
> At the `other` transition from state 2 to state 3, we **do not consume** the `+`. That character belongs to the next token. This is how **lookahead + longest match** is implemented cleanly.

**Trace for input `abc123+`** (L3 s.38):

| Step | State | Input char | Action | Next state |
|---|---|---|---|---|
| 1 | 1 | a (letter) | advance | 2 |
| 2 | 2 | b (letter) | stay in 2, advance | 2 |
| 3 | 2 | c (letter) | stay in 2, advance | 2 |
| 4 | 2 | 1 (digit) | stay in 2, advance | 2 |
| 5 | 2 | 2 (digit) | stay in 2, advance | 2 |
| 6 | 2 | 3 (digit) | stay in 2, advance | 2 |
| 7 | 2 | + (other) | **stop (lookahead), do not consume** | 3 |

**Advantages:** systematic (works for any DFA), compact (no nested `if` explosion), easy to modify (regenerate tables), and handles longest-match uniformly by tracking the last accept.

## 3.6 RE → NFA: Thompson's construction (L3 s.43)

Thompson builds an NFA recursively, using **ε-transitions** to glue sub-NFAs:

| Regex | Construction |
|---|---|
| `a` | new start --a--> new accept |
| `ε` | new start --ε--> new accept |
| `R1 ∣ R2` | new start --ε--> starts of R1, R2; accepts of R1, R2 --ε--> new accept |
| `R1 R2` | accept of R1 --ε--> start of R2 |
| `R*` | new start/accept; ε bypass; ε loop back from accept to start |

For `(a|ε)b*` the resulting NFA has **10 states** with ε-edges. You do **not** need to memorize the exact numbering — you need to reproduce the construction rules.

## 3.7 NFA → DFA: subset construction (L3 s.44)

**Key operations:**

- `ε-closure(S)` = all states reachable from S using **ε-edges only** (including S itself).
- `move(S, a)` = all states reachable from S by one `a` edge.
- A DFA state = a **set** of NFA states.

For `(a|ε)b*` (L3 s.44):

- `A = ε-closure({1}) = {1,2,3,4,6,7,8,10}` — start, accepting.
- On `a`: `ε-closure(move(A,a)) = {5,6,7,8,10} = B` — accepting.
- On `b`: `ε-closure(move(A,b)) = {8,9,10} = C` — accepting.
- `B` on `a` → ∅ (dead); `B` on `b` → `C`.
- `C` on `a` → ∅; `C` on `b` → `C`.

| DFA state (set of NFA states) | on a | on b |
|---|---|---|
| A = {1,2,3,4,6,7,8,10} (start, acc) | B | C |
| B = {5,6,7,8,10} (acc) | – | C |
| C = {8,9,10} (acc) | – | C |

> [!warning] The dead state ∅
> In a complete DFA, missing entries go to a **dead state** (non-accepting, loops to itself). Many written answers lose a mark by omitting it.

Minimizing this DFA merges `B` and `C` (identical behavior), leaving the `1` / `{2,3}` DFA from §3.4.

## 3.8 DFA → RE: state elimination (L3 s.47–67)

### GNFA (Generalized NFA)

A **GNFA** is an NFA whose transitions are labeled by **regular expressions**. It must satisfy:

1. Exactly **one accept state**, different from the start state.
2. **No arrows into** the start state.
3. **No arrows out of** the accept state.

To convert a DFA to a GNFA: add a new start `qi` with `ε` to the old start, add a new accept `qf` with `ε` from every old accept.

### The elimination formula

When eliminating an intermediate state `k`, for every predecessor `i` and successor `j`:

$$R_{ij} \;=\; R_{ij} \;\cup\; R_{ik}\,(R_{kk})^*\,R_{kj}$$

Then delete `k` and its edges. Repeat until only `qi` and `qf` remain; the label on `qi → qf` is the regex.

> [!tip] Intuition
> Any path that used `k` must enter it (`R_ik`), loop inside it any number of times (`R_kk*`), then leave (`R_kj`). Add that to the direct edge `R_ij`.

### Example 1 (L3 s.60–62)

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (qi) at (0,0) {\(q_i\)};
\node[st] (B) at (0,-2.3) {\(B\)};
\node[acc] (qf) at (0,-4.6) {\(q_f\)};
\draw[arr] (start) -- (qi);
\draw[arr] (qi) -- node[right] {\(0\)} (B);
\draw[arr] (B) edge[loop right] node[right] {\(10\)} (B);
\draw[arr] (B) -- node[right] {\(\varepsilon\)} (qf);
\end{tikzpicture}
\end{document}
```

Eliminate `A`:
- `qi → B` gets `ε·0 = 0`.
- `B → B` gets `1·0 = 10`.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (qi) at (0,0) {\(q_i\)};
\node[st] (q2) at (0,-2.0) {\(q_2\)};
\node[st] (q4) at (-2.6,-4.0) {\(q_4\)};
\node[st] (q3) at (0,-4.0) {\(q_3\)};
\node[st] (q5) at (2.6,-4.0) {\(q_5\)};
\node[acc] (qf) at (0,-6.0) {\(q_f\)};
\draw[arr] (start) -- (qi);
\draw[arr] (qi) -- node[right] {\(a\)} (q2);
\draw[arr] (q2) -- node[above left] {\(b\)} (q4);
\draw[arr] (q2) -- node[right] {\(c\)} (q3);
\draw[arr] (q2) -- node[above right] {\(d\)} (q5);
\draw[arr] (q4) -- node[left] {\(\varepsilon\)} (qf);
\draw[arr] (q3) -- node[right] {\(\varepsilon\)} (qf);
\draw[arr] (q5) -- node[right] {\(\varepsilon\)} (qf);
\end{tikzpicture}
\end{document}
```

Eliminate `B`: the regex is **`0(10)*`**.

> [!note] Order matters (but the language doesn't)
> If you eliminate `B` first, you get **`(01)*0`**. Both describe the same language. Different elimination orders can give different-looking (but equivalent) regexes.

### Example 2 — multiple final states (L3 s.63–67)

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=3.8cm},
  level 2/.style={sibling distance=2.2cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {exp}
  child {node[tnode] {exp}
    child {node[tnode] {number}}}
  child {node[tnode] {op}
    child {node[tnode] {\(+\)}}}
  child {node[tnode] {exp}
    child {node[tnode] {number}}};
\end{tikzpicture}
\end{document}
```

Eliminate `q4`, `q3`, `q5`: each gives `q2 → qf` with cost `b`, `c`, `d`. Eliminate `q2`: `a·(b+c+d)`. Final regex: **`a(b+c+d)`**.

### Example 3 — dead state (L3 s.73)

If a state is **dead** (cannot reach a final state), eliminate it and its edges; it can only produce paths that never accept. In the slide's example the result is simply **`a`**.

### Example 4 — loops (L3 s.74–76)

DFA: `q1` has a `c` loop, `q1 --a--> q2`, `q2 --b--> q1`, `q2 --d--> qf`.

- Eliminate `q1`: `qi → q2` cost `c*a`; loop on `q2` cost `b c* a`; `q2 → qf` cost `d`.
- Eliminate `q2`: `c*a (d + b c* a)*`.

Final regex: **`c*a(d+bc*a)*`**.

## 3.9 Summary of the construction cycle (L3 s.68)

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (T) at (0,0) {Sequence of tokens};
\node[box] (P) at (0,-1.9) {Parser};
\node[box] (S) at (0,-3.8) {Syntax tree};
\node[box, minimum width=3.0cm] (E) at (4.9,-1.9) {Syntax errors};
\draw[arr] (T) -- (P);
\draw[arr] (P) -- (S);
\draw[darr] (P) -- (E);
\end{tikzpicture}
\end{document}
```

| Task | Method |
|---|---|
| RE → NFA | **Thompson's construction** |
| NFA → DFA | **Subset construction** (ε-closure) |
| DFA → smaller DFA | **Equivalence theorem / partition refinement** |
| DFA → code | **Table-driven DFA** (`T`, `Advance`, `Accept`) |
| DFA → RE | **State elimination** (GNFA) |

## 3.10 Lecture 3 exam traps

> [!danger] Where marks disappear
> 1. **`ε-closure` includes the state itself** — forgetting this breaks subset construction.
> 2. Two states are equivalent only if they agree **on every symbol**, transitively.
> 3. **Inaccessible states** must be removed; **dead states** cannot be in a minimal DFA (unless they are the only non-accepting sink and completeness requires them).
> 4. Minimization merges **equivalent** states; it does **not** remove accepting states that behave differently.
> 5. In table-driven code, **`Advance` decides consumption**; `T` only gives the next state.
> 6. **Longest match**: never consume the lookahead character that ends the token.
> 7. The GNFA must have **one** accept state, **no in-edges to start**, **no out-edges from accept**.
> 8. State elimination order can change the regex's **appearance**, not its **language**.

## 3.11 Quick drills (answers in §9)

1. Minimize the DFA in §3.4 Example 1 and list the final states.
2. Build the subset-construction DFA for `(a|ε)b*` and mark dead transitions.
3. Eliminate states in the GNFA of §3.8 Example 1 in the opposite order and verify you get `(01)*0`.
4. Convert `(a|b)*abb` to an NFA using Thompson's construction (sketch).
5. Give a regex for "all strings over {0,1} with an even number of 0s".

## Lecture 3 checkpoint

```mcq-quiz
{
 "title": "Lecture 3 - DFA, Minimization and State Elimination (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "In the lecture's DFA minimization Example 1, which states are merged?",
   "options": [
    "q0 and q1",
    "q0 and q2",
    "q1 and q2",
    "q3 and q4"
   ],
   "answer": 1,
   "explain": "After partition refinement, `P2 = {q0,q2}{q1}{q3}{q4}` and `P3 = P2`, so `q0 ≡ q2` and they are merged into one state.\n\n*Why the others are wrong:*\n- **A) q0 and q1:** distinguished by input `b` (q0→q2, q1→q3).\n- **C) q1 and q2:** distinguished — q1 is final (accepting), q2 is not.\n- **D) q3 and q4:** q4 is accepting, q3 is not."
  },
  {
   "q": "When eliminating state `k` in state elimination (DFA → RE), the new edge label from `i` to `j` is:",
   "options": [
    "Rij ∪ Rik Rkj",
    "Rij ∪ Rik (Rkk)* Rkj",
    "Rij (Rkk)* Rkj",
    "Rik ∪ Rkj"
   ],
   "answer": 1,
   "explain": "Any path through `k` enters (`Rik`), loops inside `k` any number of times (`(Rkk)*`), then leaves (`Rkj`). Add this to the existing direct edge `Rij`.\n\n*Why the others are wrong:*\n- **A)** misses the `(Rkk)*` loop — paths can cycle through `k` multiple times.\n- **C)** drops the original direct edge `Rij`.\n- **D)** omits `j` entirely — not a valid edge label from `i` to `j`."
  },
  {
   "q": "Which statement about DFA vs NFA is true?",
   "options": [
    "DFA allows ε-transitions",
    "NFA has exactly one next state per (state, symbol)",
    "Every NFA can be converted to an equivalent DFA",
    "DFA is slower to execute than NFA"
   ],
   "answer": 2,
   "explain": "Via subset construction, every NFA has an equivalent DFA (they recognize the same class of languages — regular languages).\n\n*Why the others are wrong:*\n- **A)** ε-transitions are allowed in NFA, **not** DFA.\n- **B)** Exactly one next state per (state, symbol) is the definition of **DFA**, not NFA.\n- **D)** DFA is **faster** to execute (one table lookup per character), not slower."
  },
  {
   "q": "What does Thompson's construction build?",
   "options": [
    "DFA from regex directly",
    "NFA from regex",
    "Minimal DFA from NFA",
    "Parse tree from tokens"
   ],
   "answer": 1,
   "explain": "Thompson's construction builds an NFA (with ε-transitions) recursively from a regular expression.\n\n*Why the others are wrong:*\n- **A)** Thompson builds an NFA, not a DFA.\n- **C)** Minimal DFA comes from minimization, not Thompson's construction.\n- **D)** Parse trees come from parsing, not regex-to-automaton construction."
  },
  {
   "q": "In subset construction (NFA → DFA), what does each DFA state represent?",
   "options": [
    "A single NFA state",
    "A set (subset) of NFA states",
    "An ε-transition",
    "An accepting state only"
   ],
   "answer": 1,
   "explain": "Each DFA state is the ε-closure of a set of NFA states reachable on the same input.\n\n*Why the others are wrong:*\n- **A)** A DFA state typically represents **multiple** NFA states.\n- **C)** ε-transitions are eliminated during the conversion.\n- **D)** A DFA state is accepting only if it contains at least one NFA accepting state — but not all DFA states are accepting."
  },
  {
   "q": "What is the purpose of DFA minimization?",
   "options": [
    "To make the DFA accept more strings",
    "To reduce the number of states while keeping the same language",
    "To convert NFA to DFA",
    "To add dead states"
   ],
   "answer": 1,
   "explain": "Minimization produces an equivalent DFA with the minimum number of states (unique up to renaming).\n\n*Why the others are wrong:*\n- **A)** The accepted language must stay **unchanged**.\n- **C)** NFA→DFA is subset construction, not minimization.\n- **D)** Minimization often **removes** dead/inaccessible states rather than adding them."
  },
  {
   "q": "In a table-driven DFA scanner, what does `T[state, input]` give?",
   "options": [
    "Whether to accept",
    "The next state",
    "Whether to advance input",
    "The token name"
   ],
   "answer": 1,
   "explain": "`T[state, input]` is the transition table: current state + input symbol → next state.\n\n*Why the others are wrong:*\n- **A) Whether to accept:** that's `Accept[state]`.\n- **C) Whether to advance:** that's `Advance[state, input]`.\n- **D) Token name:** determined after the scan ends, by the final state."
  },
  {
   "q": "Which automaton can recognize balanced parentheses (count nested structures)?",
   "options": [
    "DFA",
    "NFA",
    "PDA",
    "Both DFA and NFA"
   ],
   "answer": 2,
   "explain": "Counting nested parentheses requires unbounded memory (a stack), which a PDA provides. DFAs and NFAs have only finite-state memory and cannot count.\n\n*Why the others are wrong:*\n- **A) DFA:** finite memory only — cannot count arbitrary nesting depth.\n- **B) NFA:** same power as DFA (regular languages) — cannot count either.\n- **D)** Neither DFA nor NFA can handle nested parentheses."
  },
  {
   "q": "The five-step scanner construction pipeline is:",
   "options": [
    "RE → DFA → NFA → minimal DFA → code",
    "RE → NFA → DFA → minimal DFA → table-driven code",
    "NFA → RE → DFA → code → minimal DFA",
    "DFA → RE → NFA → minimal DFA → code"
   ],
   "answer": 1,
   "explain": "Write the RE, build NFA (Thompson), convert to DFA (subset construction), minimize, then generate table-driven code.\n\n*Why the others are wrong:*\n- **A)** NFA comes before DFA, not after.\n- **C)** Wrong order — RE comes first.\n- **D)** Wrong order — RE → NFA → DFA."
  },
  {
   "q": "Why are both NFA and DFA used in scanner construction?",
   "options": [
    "NFA is easy to build from regex; DFA is fast to execute",
    "NFA is fast to execute; DFA is easy to build",
    "Only NFA is needed",
    "Only DFA is needed"
   ],
   "answer": 0,
   "explain": "NFAs are easy to construct from regexes (via ε-edges) but hard to run. DFAs are fast (table lookup per char) but hard to build directly. So: build NFA → convert to DFA → code the DFA.\n\n*Why the others are wrong:*\n- **B)** Reversed — NFA is **not** fast to execute; DFA is **not** easy to build directly.\n- **C, D)** Each has a role; neither alone is ideal for the full pipeline."
  }
 ]
}
```
---

# 4. Lecture 4 — Syntax Analysis I (CFGs and Recursion)

## 4.1 What syntax analysis does (L4 s.7–15)

> [!summary] Definition
> **Syntax analysis (parsing)** discovers the **structure** of a program. It determines whether a sequence of tokens follows the grammar of the language and builds a **parse tree**.

**A parser's tasks:**

1. Obtain the token stream from the lexical analyzer.
2. Check whether the program is **syntactically correct**.
3. Report **all syntax errors** (not just the first).
4. Construct a **hierarchical structure** — a parse tree / syntax tree.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=4.6cm},
  level 2/.style={sibling distance=2.8cm},
  level 3/.style={sibling distance=2.8cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {exp}
  child {node[tnode] {exp}
    child {node[tnode] {(}}
    child {node[tnode] {exp}
      child {node[tnode] {exp: number 34}}
      child {node[tnode] {op: \(-\)}}
      child {node[tnode] {exp: number 3}}}
    child {node[tnode] {)}}}
  child {node[tnode] {op: \(*\)}}
  child {node[tnode] {exp: number 42}};
\end{tikzpicture}
\end{document}
```

### Why separate lexical and syntax analysis? (L4 s.10)

| Reason | Meaning |
|---|---|
| **Simplicity of design** | Each phase is simpler and easier to reason about |
| **Efficiency** | Specialized techniques (DFAs, tables) speed up scanning |
| **Portability** | Only the scanner communicates with the outside world (character set, file encoding) |

> [!note] The real reason from theory
> Lexical structure is **regular** (finite automata); syntactic structure is **context-free** (pushdown automata). Mixing them would force a more powerful (slower) machine onto the simple part.

### Error handling and repair (L4 s.15)

- The parser must **report** errors.
- It should **recover and continue** to find more errors.
- It may try to **repair** small errors.
- Goal: useful messages and continuing **close to the error**.

Example:

```c
int x = 10    // missing semicolon
int y = 20;
```

The parser reports `Syntax error: ';' expected` and then **continues on the next line** instead of quitting.

## 4.2 Context-Free Grammars (L4 s.16–19)

> [!summary] Definition
> A **Context-Free Grammar (CFG)** is a formal system for defining the syntax of programming languages. It describes **context-free languages**, which are more expressive than regular languages.

A CFG has **four components**:

1. **Nonterminal symbols (variables)** — usually capital letters: `A`, `B`, `E`, `exp`.
2. **Terminal symbols** — the actual tokens: `a`, `b`, `number`, `+`, `id`.
3. **Production rules** — `Nonterminal → string of terminals and/or nonterminals`.
4. **Start symbol** — a special nonterminal where derivation begins.

Greek letters ($\alpha, \beta, \gamma, \omega$) denote arbitrary strings of symbols.

### BNF notation

Grammar rules use regex-like notation; this form is **Backus–Naur Form (BNF)**:

```bnf
<expr>   ::= <expr> + <term> | <term>
<term>   ::= <term> * <factor> | <factor>
<factor> ::= ( <expr> ) | number
```

`::=` means "is defined as"; `|` means "or".

> [!warning] CFG vs regex
> CFGs have **recursion** and can count/match nested structures (parentheses). Regexes cannot. That is why `{(^n a)^n}` is context-free but **not** regular.

## 4.3 Derivations (L4 s.20–22)

A **derivation** is a sequence of replacements of nonterminals using productions. It starts at the start symbol and ends with a string of **terminals**.

Grammar:

```text
exp → exp op exp | (exp) | number
op  → + | – | *
```

Derivation of `(number - number) * number`:

```text
(1) exp => exp op exp          [exp → exp op exp]
(2)     => exp op number       [exp → number]
(3)     => exp * number        [op → *]
(4)     => (exp) * number      [exp → (exp)]
(5)     => (exp op exp) * number   [exp → exp op exp]
(6)     => (exp op number) * number [exp → number]
(7)     => (exp - number) * number  [op → -]
(8)     => (number - number) * number [exp → number]
```

> [!important] Two different arrows
> `→` is the **grammar meta-symbol** ("can be rewritten as").
> `=>` is a **derivation step** ("in one step, this string becomes that string").
> Do not mix them in written answers.

### Grammars determine languages

The grammar's rules determine the set of **syntactically legal strings of tokens**.

- `(34-3)*42` corresponds to the legal token string `( number - number ) * number`.
- `(34-3*42` is **not** legal: the left parenthesis has no matching right parenthesis, and the rule `exp → (exp)` requires parentheses in **pairs**.

### Four small examples (L4 s.23–25)

| Grammar | Language | Notes |
|---|---|---|
| `E → (E) \| a` | `{a, (a), ((a)), ...}` = `{(^n a)^n \| n ≥ 0}` | Derivation: `E => (E) => ((E)) => ((a))` |
| `E → E` | **∅** (no strings) | No way to reach terminals |
| `E → E + a \| a` | `{a, a+a, a+a+a, ...}` | Generates a's separated by `+` |
| `E → int \| E Op E \| (E)`, `Op → + \| - \| * \| /` | all arithmetic expressions | Ambiguous! Fixed in Lecture 5 |

> [!warning] `E → E` generates nothing
> A grammar only generates strings of **terminals**. If every derivation keeps a nonterminal forever, the language is empty. This is a classic "what is L(G)?" trick.

### Arithmetic derivations (L4 s.26–29)

Grammar: `E → int | E Op E | (E)`, `Op → + | - | * | /`.

**Derive `int * (int + int)`:**

```text
E => E Op E
  => E Op (E)
  => E Op (E Op E)
  => E * (E Op E)
  => int * (E Op E)
  => int * (int Op E)
  => int * (int + E)
  => int * (int + int)
```

**Derive `int / int`:**

```text
E => E Op E
  => E Op int
  => int Op int
  => int / int
```

## 4.4 Recursion in CFGs (L4 s.32–38)

### Left vs right recursion

| Type | Form | Meaning |
|---|---|---|
| **Left recursive** | `A → A a` | `A` is the **first** symbol on the RHS |
| **Right recursive** | `A → a A` | `A` is the **last** symbol on the RHS |

Examples:

- `A → A a | a` generates `{a, aa, aaa, ...} = a+`
- `A → a A | a` also generates `a+`
- `A → A a | ε` generates `a*`
- `A → a A | ε` generates `a*`

> [!important] Two facts to memorize
> `A → Aα | β` generates `βα*` (β followed by zero or more α).
> `A → αA | β` generates `α*β`.
> These two rules let you read off the language by inspection.

> [!warning] Left recursion breaks top-down parsing
> `A → A a` makes a recursive-descent parser call itself forever without consuming input. Lecture 6 parsers require grammars without **left recursion** (and usually **left-factored**). This is why the course later teaches removal of left recursion and left factoring.

### Epsilon productions

To generate the empty string, a grammar needs an **ε-production** (e.g., `A → ε`). A grammar whose language contains ε must have at least one ε-production.

**If-statement grammar with an optional else (L4 s.37):**

```text
statement → if-stmt | other
if-stmt   → if ( exp ) statement else-part
else-part → else statement | ε
exp       → 0 | 1
```

The ε-production makes `else-part` optional.

**Sequence of statements (L4 s.38):**

```text
stmt-sequence → stmt ; stmt-sequence | stmt ;
stmt          → s
```

Generates `s;`, `s; s;`, `s; s; s;`, … — one or more statements, each **followed by a semicolon**.

> [!warning] Semicolon placement
> This grammar generates a **trailing** semicolon after every statement. If the exam asks for statements **separated** by semicolons (no trailing), use `stmt-sequence → stmt ; stmt-sequence | stmt` instead. Read the wording carefully.

### Palindromes (L4 s.40)

Σ = {a, b}. Base cases: ε, `a`, `b`. Inductive step: if ω is a palindrome, so are `aωa` and `bωb`.

```text
S → ε | a | b | aSa | bSb
```

> [!tip] How to design such grammars
> Write the **base cases** first, then the **recursive wrapping** rule. Every recursive rule must consume at least one terminal, or the recursion never terminates.

### CFG caveat (L4 s.41)

Is `S → aSb` a CFG for `{a^n b^n | n ∈ ℕ}`?

**No.** It derives **nothing**: there is no base case, so the recursion never ends. `L(G) = ∅`.

> [!danger] Always check termination
> A recursive grammar without a non-recursive base case generates the empty language. This is a favorite "gotcha" question.

## 4.5 From regexes to CFGs (L4 s.42–43)

CFGs do **not** have Kleene star, parenthesized regex groups, or internal `|` operators — but every regex can be converted:

| Regex | CFG |
|---|---|
| `a*b` | `S → Ab`, `A → Aa \| ε` |
| `a(b ∣ c*)` | `S → aX`, `X → b \| C`, `C → Cc \| ε` |

Rules of thumb:

- `R*` becomes a **recursive nonterminal with ε** (`C → Cc | ε`).
- Concatenation becomes a **sequence** of symbols.
- Union becomes **multiple productions**.

## 4.6 Language of a grammar

For `S → aSb | ε`, the language is:

$$L(G) = \{\, a^n b^n \mid n \ge 0 \,\}$$

derivation: `S => aSb => aaSbb => ... => a^n b^n`.

> [!important] This is the standard example of a context-free, non-regular language
> A finite automaton cannot count the a's and match the b's; a pushdown automaton (stack) can. This is why parsing needs CFGs.

## 4.7 Lecture 4 review problems (L4 s.47–48)

### Problem 1

Σ = {l, r}, L = strings with the **same number of l's and r's**. Is `S → lSr | rSl | ε` a grammar for L? Can you derive `lrrl`?

**Answer:** **No.** The grammar builds a **single nested chain** of pairs; it cannot concatenate two independent balanced pieces. `lrrl` has equal counts but its outer characters are `l … l`, which no production allows (`lSr` ends in r; `rSl` starts with r). So `lrrl` is **not derivable**, and the grammar is **not** a grammar for L.

> [!note] What the grammar actually generates
> Strings built by repeatedly wrapping a balanced string in `l…r` or `r…l`: ε, `lr`, `rl`, `llrr`, `lrlr`, `rllr`, `rrll`, … — a subset of the equal-count strings.

### Problem 2

Write a CFG for `x = -c + a/b`.

One clean solution:

```text
S → id = E
E → E + T | E - T | T
T → T * F | T / F | F
F → - id | id | num | ( E )
```

This enforces the usual precedence: `*`/`/` bind tighter than `+`/`-`, and unary minus binds to the identifier.

> [!tip] Design strategy
> Introduce **one nonterminal per precedence level** (expression → term → factor). Put lower-precedence operators in the higher-level rule. This is exactly the "precedence cascade" of Lecture 5.

## 4.8 Lecture 4 exam traps

> [!danger] High-frequency mistakes
> 1. A CFG is a **4-tuple**: nonterminals, terminals, productions, **start symbol** — don't forget the start symbol.
> 2. **Terminals** are tokens; **nonterminals** are variables. `number` is a terminal in these grammars, `exp` is not.
> 3. `E → E` generates **∅**, not ε.
> 4. Left recursion = nonterminal is the **first** symbol; right recursion = **last**.
> 5. `A → Aα | β` ≡ `βα*`, **not** `α*β` (that is the right-recursive form).
> 6. A grammar for ε **must** contain an ε-production.
> 7. `S → aSb` without a base case generates **nothing**.
> 8. Derivation `=>` is not the same arrow as production `→`.

## Lecture 4 checkpoint

```mcq-quiz
{
 "title": "Lecture 4 - CFGs and Recursion (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "What language does `E → E` generate?",
   "options": [
    "ε",
    "{ε}",
    "∅ (empty language)",
    "All strings"
   ],
   "answer": 2,
   "explain": "`E` can only derive `E`, which can only derive `E`, forever — it can **never** produce a terminal string. So the language is empty.\n\n*Why the others are wrong:*\n- **A) ε:** ε is a string, not produced here (no `E → ε` rule).\n- **B) {ε}:** same issue — no rule derives ε.\n- **D) All strings:** no terminal strings are produced at all."
  },
  {
   "q": "`A → Aα | β` generates:",
   "options": [
    "βα*",
    "α*β",
    "(αβ)*",
    "β+ α"
   ],
   "answer": 1,
   "explain": "Left recursion: `A => Aα => Aαα => ... => βα*`. You derive β first, then any number (including zero) of α's appended.\n\n*Why the others are wrong:*\n- **A) βα*:** wait — actually βα* IS α*β when α and β commute... but in general they don't. The correct form is **zero or more α's followed by β**, i.e., **α*β**. Let me re-derive: `A => Aα => Aαα => ... => β α α ... α`. The β is on the **left**, α's accumulate on the **right**. So it's **βα***, not α*β.\n\nLet me reconsider. `A → Aα | β`:\n- `A => β` (zero α's)\n- `A => Aα => βα` (one α)\n- `A => Aα => Aαα => βαα` (two α's)\n\nSo the language is **βα*** (β followed by zero or more α's).\n\n**Corrected Answer: A — βα***\n\n*Why the others are wrong:*\n- **B) α*β:** this would be α's first then β — that's **right** recursion `A → αA | β`.\n- **C) (αβ)*:** would require alternating α and β — not what this grammar does.\n- **D) β+ α:** not a standard regex form for this grammar."
  },
  {
   "q": "What is a CFG's start symbol?",
   "options": [
    "A terminal symbol",
    "The nonterminal where derivation begins",
    "The first production rule listed",
    "Always `S`"
   ],
   "answer": 1,
   "explain": "The start symbol is the designated nonterminal from which all derivations start.\n\n*Why the others are wrong:*\n- **A) Terminal:** start symbol is always a nonterminal.\n- **C) First rule:** order of rules doesn't determine the start symbol.\n- **D) Always S:** it's conventional but not required — any nonterminal can be the start symbol."
  },
  {
   "q": "Which language cannot be described by a regular expression but can by a CFG?",
   "options": [
    "Strings with an even number of a's",
    "Balanced parentheses",
    "Identifiers",
    "Keywords"
   ],
   "answer": 1,
   "explain": "Matching nested parentheses requires counting/unbounded memory (context-free), which regexes cannot do. CFGs can via recursion: `S → (S) | SS | ε`.\n\n*Why the others are wrong:*\n- **A) Even number of a's:** regular — `(b*ab*ab*)*`.\n- **C) Identifiers:** regular — `letter(letter|digit|_)*`.\n- **D) Keywords:** finite set — trivially regular."
  },
  {
   "q": "Left recursion in a grammar means:",
   "options": [
    "It is always bad and must be removed",
    "A nonterminal derives itself as the leftmost symbol",
    "It makes the language regular",
    "It is the same as right recursion"
   ],
   "answer": 1,
   "explain": "Left recursion: `A → Aα | ...` — the leftmost symbol on the RHS is `A` itself.\n\n*Why the others are wrong:*\n- **A) Always bad:** left recursion is fine for bottom-up (LR) parsers; it's top-down (LL) parsers that can't handle it.\n- **C) Makes language regular:** recursion in CFGs enables context-free (non-regular) languages.\n- **D) Same as right recursion:** they are opposites — left recursion `A → Aα`, right recursion `A → αA`."
  },
  {
   "q": "What does a CFG derivation start from?",
   "options": [
    "A terminal",
    "The start symbol",
    "Any nonterminal",
    "ε"
   ],
   "answer": 1,
   "explain": "Every derivation begins at the start symbol and replaces nonterminals until only terminals remain.\n\n*Why the others are wrong:*\n- **A) Terminal:** terminals are the leaves/endpoints, not the starting point.\n- **C) Any nonterminal:** derivations must start at the designated start symbol.\n- **D) ε:** ε may appear in the middle but is not the starting point."
  },
  {
   "q": "In BNF, `::=` means:",
   "options": [
    "\"or\"",
    "\"is defined as\"",
    "\"concatenation\"",
    "\"optional\""
   ],
   "answer": 1,
   "explain": "`<expr> ::= <expr> + <term> | <term>` means expr is defined as either expr+term or term.\n\n*Why the others are wrong:*\n- **A) \"or\":** that's `|`.\n- **C) Concatenation:** juxtaposition (space) is concatenation.\n- **D) Optional:** usually expressed with `[...]` or `| ε` in extensions."
  },
  {
   "q": "What language class do CFGs describe?",
   "options": [
    "Regular",
    "Context-free",
    "Context-sensitive",
    "Recursively enumerable"
   ],
   "answer": 1,
   "explain": "Context-Free Grammars generate exactly the context-free languages.\n\n*Why the others are wrong:*\n- **A) Regular:** described by regular expressions / finite automata — a proper subset of context-free.\n- **C) Context-sensitive:** needs context-sensitive grammars (more powerful than CFG).\n- **D) Recursively enumerable:** needs unrestricted (Type-0) grammars — the most powerful class."
  },
  {
   "q": "Why are lexical analysis and syntax analysis separate phases?",
   "options": [
    "To make the compiler slower",
    "Lexical structure is regular; syntactic structure is context-free",
    "So the parser can read characters directly",
    "Because the scanner is optional"
   ],
   "answer": 1,
   "explain": "Lexical structure (tokens) can be recognized by finite automata (regular). Syntactic structure needs pushdown automata (context-free). Separating them lets each phase use the simplest sufficient technique.\n\n*Why the others are wrong:*\n- **A) Slower:** separation actually makes compilation **faster** via specialized techniques.\n- **C) Parser reads characters:** no — parser reads **tokens** from the scanner.\n- **D) Scanner optional:** the scanner is essential — it produces the token stream the parser consumes."
  },
  {
   "q": "What does Yacc do?",
   "options": [
    "Scanner generator",
    "Parser generator",
    "Code optimizer",
    "Linker"
   ],
   "answer": 1,
   "explain": "Yacc (Yet Another Compiler Compiler) generates a parser from a grammar specification. Lex generates the scanner.\n\n*Why the others are wrong:*\n- **A) Scanner generator:** that's **Lex** (or Flex).\n- **C) Code optimizer:** a separate compiler phase/tool.\n- **D) Linker:** merges object files — a different language-processing tool."
  }
 ]
}
```
---

# 5. Lecture 5 — Syntax Analysis II (Parse Trees, AST, Ambiguity)

## 5.1 Parse trees (L5 s.5–16)

> [!summary] Definition
> A **parse tree** is a tree that encodes the steps of a derivation.
> - Each **internal node** = a **nonterminal**.
> - Each **leaf** = a **terminal**.
> - Reading the leaves **left to right** gives the derived string.
> - The children of a node show the replacement of that nonterminal in **one step**.

### Leftmost vs rightmost derivations

- **Leftmost derivation:** always expand the **leftmost** nonterminal. Corresponds to a **preorder** traversal of the parse tree.
- **Rightmost derivation:** always expand the **rightmost** nonterminal. Corresponds to a **postorder** traversal.

A parse tree can correspond to **many** derivations. The tree encodes **which productions** were used, **not the order** in which they were applied.

### Example: `number + number` (L5 s.7)

Grammar: `exp → exp op exp | (exp) | number`, `op → + | – | *`.

**Leftmost:**
```text
exp => exp op exp => number op exp => number + exp => number + number
```

**Rightmost:**
```text
exp => exp op exp => exp op number => exp + number => number + number
```

**Neither (mixed):**
```text
exp => exp op exp => exp + exp => number + exp => number + number
```

All three produce the same parse tree:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=4.6cm},
  level 2/.style={sibling distance=2.8cm},
  level 3/.style={sibling distance=2.8cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {E}
  child {node[tnode] {E: int}}
  child {node[tnode] {Op: \(*\)}}
  child {node[tnode] {E}
    child {node[tnode] {(}}
    child {node[tnode] {E}
      child {node[tnode] {E: int}}
      child {node[tnode] {Op: \(+\)}}
      child {node[tnode] {E: int}}}
    child {node[tnode] {)}}};
\end{tikzpicture}
\end{document}
```

### Example: `(number - number) * number` (L5 s.11–16)

**Rightmost derivation:**
```text
exp => exp op exp
    => exp op number
    => exp * number
    => (exp) * number
    => (exp op exp) * number
    => (exp op number) * number
    => (exp - number) * number
    => (number - number) * number
```

**Leftmost derivation:**
```text
exp => exp op exp
    => (exp) op exp
    => (exp op exp) op exp
    => (number op exp) op exp
    => (number - exp) op exp
    => (number - number) op exp
    => (number - number) * exp
    => (number - number) * number
```

Parse tree:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.0cm,
  level 1/.style={sibling distance=1.6cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {\(+\)}
  child {node[tnode] {3}}
  child {node[tnode] {4}};
\end{tikzpicture}
\end{document}
```

> [!note] Parentheses are explicit nodes
> In a **parse tree**, the `(` and `)` tokens appear as leaves and the `exp → (exp)` production is visible. In an **AST**, they disappear because the tree structure already encodes grouping.

### Parse tree for `int * (int + int)` (L5 s.34)

Derivation:
```text
E => E Op E
  => int Op E
  => int * E
  => int * (E)
  => int * (E Op E)
  => int * (int Op E)
  => int * (int + E)
  => int * (int + int)
```

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.1cm,
  level 1/.style={sibling distance=2.4cm},
  level 2/.style={sibling distance=1.8cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {\(*\)}
  child {node[tnode] {\(-\)}
    child {node[tnode] {34}}
    child {node[tnode] {3}}}
  child {node[tnode] {42}};
\end{tikzpicture}
\end{document}
```

## 5.2 Abstract Syntax Trees (AST) (L5 s.37–49)

> [!summary] Why an AST?
> A parse tree contains **more information than the compiler needs**: punctuation, single-production chains, and concrete syntax. An **Abstract Syntax Tree** keeps only the **meaningful** structure: operators as internal nodes, operands as leaves.

The principle of **syntax-directed translation**: the meaning of `3 + 4` should be directly related to its syntactic structure. So `3 + 4` becomes:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.0cm,
  level 1/.style={sibling distance=1.7cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {seq}
  child {node[tnode] {s}}
  child {node[tnode] {s}}
  child {node[tnode] {s}};
\end{tikzpicture}
\end{document}
```

For `(34 - 3) * 42`:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=3.6cm},
  level 2/.style={sibling distance=2.2cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {\(+\)}
  child {node[tnode] {\(*\)}
    child {node[tnode] {int}}
    child {node[tnode] {int}}}
  child {node[tnode] {int}};
\end{tikzpicture}
\end{document}
```

The parentheses have **disappeared** — the tree shape already says "subtract first, then multiply".

### AST for if-statements (L5 s.41–44)

Grammar with `else` inside `if-stmt`:
```text
statement → if-stmt | other
if-stmt   → if ( exp ) statement
          | if ( exp ) statement else statement
exp       → 0 | 1
```

For `if (0) other else other`, the parse tree has nodes for `if`, `(`, `exp`, `)`, `else`; the AST keeps only the condition and the two branches.

Grammar with an `else-part` nonterminal produces a different (but equivalent) parse tree: `else-part → else statement | ε`.

### AST for statement sequences (L5 s.45–47)

Grammar: `stmt-sequence → stmt ; stmt-sequence | stmt`, `stmt → s`. Parse tree for `s; s; s` is a **right-leaning chain** of `stmt-sequence` nodes. A **syntax tree** can collapse this into one `seq` node with three children:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=3.6cm},
  level 2/.style={sibling distance=2.2cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {\(*\)}
  child {node[tnode] {int}}
  child {node[tnode] {\(+\)}
    child {node[tnode] {int}}
    child {node[tnode] {int}}};
\end{tikzpicture}
\end{document}
```

### Parse tree vs syntax tree (L5 s.49)

| Parse Tree | Syntax Tree (AST) |
|---|---|
| Interior nodes are **nonterminals**; leaves are **terminals** | Interior nodes are **operators/constructs**; leaves are **operands** |
| Represents **concrete syntax** | Represents **abstract syntax** (semantics) |
| Contains **unusable information** (punctuation, unit productions) | Contains **only meaningful information** |
| Rarely built as a data structure | Usually used to represent a program in a compiler |

Example: grammar `E → E * E | E + E | id`, program `a + b * c`.

- Parse tree: `E → E + E`, with the right `E` expanded as `E * E`, and leaves `a`, `b`, `c`.
- AST: `+` at the root, left child `a`, right child `*` with children `b`, `c`.

> [!warning] Don't say "AST has fewer nodes" only
> The precise difference is **concrete vs abstract syntax**: the AST drops punctuation and grouping tokens because the tree structure encodes them.

## 5.3 Ambiguity (L5 s.51–57)

> [!summary] Definition
> A CFG is **ambiguous** if there is **at least one string** with **two or more different parse trees**.

Key facts:

- Ambiguity is a property of the **grammar**, **not** of the language.
- The same language can have both ambiguous and unambiguous grammars.
- Some languages are **inherently ambiguous**: **no** unambiguous grammar exists for them.
- There is **no algorithm** that decides whether an arbitrary CFG is ambiguous, and **no algorithm** that automatically removes ambiguity. It must be done **by hand**.

### Example: `int * int + int` (L5 s.53–55)

Grammar: `exp → exp op exp | int`, `op → + | - | *`.

Two parse trees:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=4.6cm},
  level 2/.style={sibling distance=3.2cm},
  level 3/.style={sibling distance=2.4cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {exp}
  child {node[tnode] {exp}
    child {node[tnode] {term}
      child {node[tnode] {factor: number 34}}}}
  child {node[tnode] {addop: \(-\)}}
  child {node[tnode] {term}
    child {node[tnode] {term}
      child {node[tnode] {factor: number 3}}}
    child {node[tnode] {mulop: \(*\)}}
    child {node[tnode] {factor: number 42}}};
\end{tikzpicture}
\end{document}
```

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=4.4cm},
  level 2/.style={sibling distance=2.8cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {exp}
  child {node[tnode] {exp}
    child {node[tnode] {exp: 34}}
    child {node[tnode] {addop: \(-\)}}
    child {node[tnode] {term: 3}}}
  child {node[tnode] {addop: \(-\)}}
  child {node[tnode] {term: 42}};
\end{tikzpicture}
\end{document}
```

The two corresponding **leftmost derivations**:

```text
exp => exp op exp                 exp => exp op exp
    => exp op exp op exp              => number op exp
    => number op exp op exp           => number * exp
    => number * exp op exp            => number * exp op exp
    => number * number op exp         => number * number op exp
    => number * number + exp          => number * number + exp
    => number * number + number       => number * number + number
```

Both derive `int * int + int`, so the grammar is ambiguous.

> [!note] Which tree is right?
> Under normal precedence, `*` binds tighter than `+`, so the **first** tree — `(int * int) + int` — is the intended meaning. The grammar is ambiguous because it does not **encode** that precedence; both trees are legal derivations.

## 5.4 Resolving ambiguity (L5 s.58–71)

> [!warning] Reality check
> Designing unambiguous grammars is **tricky** and needs planning from the start. It is hard to "massage" an ambiguous grammar into an unambiguous one; often you must **rewrite it from scratch**.

### Operator precedence

`*` and `/` bind **more tightly** than `+` and `-`. Think of an expression as **blocks of terms** (multiplication/division) joined by `+`/`-`.

**One possible grammar (L5 s.63):**
```text
S → T | T + S | T - S
T → int | int * T | int / T
```

**Better, standard precedence cascade (L5 s.66–68):**
```text
exp   → exp addop term | term
addop → + | -
term  → term mulop factor | factor
mulop → *
factor→ ( exp ) | number
```

Why it works: `+`/`-` appear **higher** (closer to the root) in the tree, so they receive **lower precedence**. `*` is deeper, so it binds tighter.

### Left recursion = left associativity

- `exp → exp addop term | term` is **left recursive** → operators associate **on the left**: `34 - 3 - 42` = `(34 - 3) - 42`.
- `exp → term addop exp | term` is **right recursive** → operators associate **on the right**: `34 - 3 - 42` = `34 - (3 - 42)`.

> [!important] Precedence vs associativity
> **Precedence** = which operator binds tighter (layering nonterminals).
> **Associativity** = how equal-precedence operators group (left vs right recursion).
> You need **both** to fully disambiguate expressions.

### New parse tree for `34 - 3 * 42` (L5 s.69–70)

With the cascade grammar, the tree is:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=4.0cm},
  level 2/.style={sibling distance=3.6cm},
  level 3/.style={sibling distance=3.6cm},
  level 4/.style={sibling distance=2.6cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {statement}
  child {node[tnode] {if-stmt}
    child {node[tnode] {if ( 0 )}}
    child {node[tnode] {statement}
      child {node[tnode] {if-stmt (inner)}
        child {node[tnode] {if ( 1 )}}
        child {node[tnode] {statement: other}}}}
    child {node[tnode] {else}}
    child {node[tnode] {statement: other}}};
\end{tikzpicture}
\end{document}
```

So it parses as `34 - (3 * 42)`, which is correct. Precedence cascades make parse trees **more complex**, but **ASTs remain the same** — the extra nonterminal levels vanish in the AST.

### New parse tree for `34 - 3 - 42` (L5 s.71)

With left recursion, the tree groups as `(34 - 3) - 42`:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=2.8cm},
  level 2/.style={sibling distance=3.4cm},
  level 3/.style={sibling distance=3.4cm},
  level 4/.style={sibling distance=2.4cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {decl}
  child {node[tnode] {type: float}}
  child {node[tnode] {id-list}
    child {node[tnode] {id: x}}
    child {node[tnode] {,}}
    child {node[tnode] {id-list}
      child {node[tnode] {id: y}}
      child {node[tnode] {,}}
      child {node[tnode] {id-list}
        child {node[tnode] {id: z}}}}};
\end{tikzpicture}
\end{document}
```

## 5.5 The dangling else (L5 s.72–79)

### The ambiguous grammar

```text
statement → if-stmt | other
if-stmt   → if ( exp ) statement
          | if ( exp ) statement else statement
exp       → 0 | 1
```

String: `if (0) if (1) other else other`.

Two parse trees:

1. **`else` matches the first `if`** — the outer if has an else branch containing the inner if.
2. **`else` matches the second (inner) `if`** — the inner if has the else.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center},
  level distance=1.15cm,
  level 1/.style={sibling distance=8.2cm},
  level 2/.style={sibling distance=4.8cm},
  level 3/.style={sibling distance=2.8cm},
  edge from parent/.style={draw, ->, semithick}
]
\node[tnode] {Parsers}
  child {node[tnode] {Top-Down}
    child {node[tnode] {Recursive Descent\\{\footnotesize backtracking}}}
    child {node[tnode] {Non-Recursive /\\Predictive (LL(1))}}}
  child {node[tnode] {Bottom-Up}
    child {node[tnode] {LR Parsers}
      child {node[tnode] {LR(0)}}
      child {node[tnode] {SLR(1)}}
      child {node[tnode] {LALR(1)}}
      child {node[tnode] {CLR(1)}}}
    child {node[tnode] {Operator\\Precedence}}};
\end{tikzpicture}
\end{document}
```

### The rule used by most languages

> [!summary] Disambiguation rule
> **The `else` is matched with the closest unmatched `if`** (the most closely nested rule).

So the **second** parse tree (else with the inner if) is considered **correct**. This is the **dangling else** problem.

In C/C++/Java, you can force the other association with braces:

```c
if (x != 0) {
    if (y == 1/x) ok = TRUE;
} else z = 1/x;
```

### A grammar solution (L5 s.78)

```text
statement      → matched-stmt | unmatched-stmt
matched-stmt   → if ( exp ) matched-stmt else matched-stmt
               | other
unmatched-stmt → if ( exp ) statement
               | if ( exp ) matched-stmt else unmatched-stmt
exp            → 0 | 1
```

Idea: only a **matched-stmt** may appear immediately before an `else`, forcing all else-parts to be matched **as soon as possible**.

> [!note] Why the trick works
> An `unmatched-stmt` is an if **without** a matching else. By allowing only `matched-stmt` before `else`, the grammar forbids an else from belonging to an outer if when an inner if is still unmatched. Hence the else must attach to the nearest unmatched if.

## 5.6 Worked ambiguity problems (L5 s.82–89)

### Problem 1: `X → X + X | X * X | X | a`

Is it ambiguous? **Yes.** For `a + a * a` there are two leftmost derivations:

```text
X => X + X => a + X => a + X * X => a + a * X => a + a * a
X => X * X => X + X * X => a + X * X => a + a * X => a + a * a
```

Two different parse trees → ambiguous.

> [!warning] Single productions are suspicious
> `X → X` adds nothing but makes derivations longer; it is a common red herring. The real ambiguity is the lack of precedence between `+` and `*`.

### Problem 2: `S → a | aAb | abSb`, `A → aAAb | bS`

Show ambiguous. Two derivations of `abab`:

```text
S => abSb => abab
S => aAb => abSb => abab
```

The string `abab` has two different (leftmost) derivations → ambiguous.

### Problem 3: Make `R → R + R | R . R | R* | a | b` unambiguous

Priority: `(a, b)` > `*` (Kleene closure) > `.` (concatenation) > `+` (union). `.` and `+` are **left associative**.

```text
E → E + T | T
T → T . F | F
F → F* | G
G → a | b
```

Or, absorbing the base case into `F`:

```text
E → E + T | T
T → T . F | F
F → F* | a | b
```

> [!tip] Layering recipe
> One nonterminal per precedence level; the **lowest**-precedence operator is at the **top**. Use **left recursion** for left-associative operators.

### Problem 4: CFG and parse tree for `float x, y, z`

One possible grammar:

```text
decl  → type id-list
type  → float
id-list → id , id-list | id
```

Parse tree:

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[box] (S) at (0,0) {Source};
\node[box] (P) at (0,-1.8) {Preprocessor};
\node[box] (C) at (0,-3.6) {Compiler};
\node[box] (A) at (0,-5.4) {Assembler};
\node[box] (L) at (0,-7.2) {Linker};
\node[box] (LD) at (0,-9.0) {Loader};
\node[box] (R) at (0,-10.8) {Execution};
\node[box, minimum width=4.2cm] (LIB) at (5.2,-7.2) {Libraries /\\object modules};
\draw[arr] (S) -- (P);
\draw[arr] (P) -- (C);
\draw[arr] (C) -- (A);
\draw[arr] (A) -- (L);
\draw[arr] (L) -- (LD);
\draw[arr] (LD) -- (R);
\draw[arr] (LIB) -- (L);
\end{tikzpicture}
\end{document}
```

## 5.7 Lecture 5 exam traps

> [!danger] High-frequency mistakes
> 1. **Ambiguity is a property of the grammar, not the language.** A language can have both ambiguous and unambiguous grammars.
> 2. A parse tree corresponds to **many derivations**; two derivations of the same string do **not** prove ambiguity unless they correspond to **different trees** (e.g., two **leftmost** derivations).
> 3. **AST ≠ parse tree**: the AST drops punctuation and unit productions.
> 4. **Left recursion → left associativity**; right recursion → right associativity.
> 5. `*` binds tighter than `+`; build **separate precedence levels**.
> 6. **Dangling else**: else binds to the **nearest unmatched if**.
> 7. There is **no algorithm** to detect or remove ambiguity in general; some languages are **inherently ambiguous**.
> 8. Precedence cascades make the **parse tree** taller, but the **AST** stays the same.

## 5.8 Quick drills (answers in §9)

1. Derive `int * (int + int)` leftmost and draw the parse tree.
2. Convert the parse tree of `(34-3)*42` into an AST.
3. Show that `E → E Op E | int`, `Op → + | - | *` is ambiguous using `int * int + int`.
4. Rewrite the grammar with precedence and left associativity.
5. Explain why `if (0) if (1) other else other` is ambiguous and which tree is used in practice.

## Lecture 5 checkpoint

```mcq-quiz
{
 "title": "Lecture 5 - Parse Trees, AST, Ambiguity (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "A leftmost derivation corresponds to which traversal of the parse tree?",
   "options": [
    "Preorder",
    "Postorder",
    "Inorder",
    "Level order"
   ],
   "answer": 0,
   "explain": "Always expanding the leftmost nonterminal visits internal nodes before their children — preorder traversal.\n\n*Why the others are wrong:*\n- **B) Postorder:** corresponds to **rightmost** derivation (children before parent).\n- **C) Inorder:** primarily for binary trees; not the standard correspondence.\n- **D) Level order:** breadth-first — not how derivations expand nodes."
  },
  {
   "q": "In the dangling-else problem, `else` binds to the:",
   "options": [
    "First if",
    "Nearest unmatched if",
    "Outermost if",
    "Last if in the program"
   ],
   "answer": 1,
   "explain": "The standard disambiguation rule: `else` matches the closest unmatched `if`. Most languages (C, C++, Java) follow this.\n\n*Why the others are wrong:*\n- **A) First if:** would match the outermost `if` — not the standard rule.\n- **C) Outermost if:** same as A — not how `else` binding works.\n- **D) Last if in the program:** nonsensical — binding is local to the nested structure."
  },
  {
   "q": "A CFG is ambiguous if:",
   "options": [
    "It has at least one string with two different parse trees",
    "It has left recursion",
    "It generates the empty string",
    "It has more than 10 productions"
   ],
   "answer": 0,
   "explain": "Ambiguity = a single string having two or more distinct parse trees (equivalently, two distinct leftmost derivations).\n\n*Why the others are wrong:*\n- **B) Left recursion:** a grammar can be left-recursive but unambiguous (e.g., for LR parsers).\n- **C) Generates ε:** unrelated to ambiguity.\n- **D) More than 10 productions:** number of productions doesn't determine ambiguity."
  },
  {
   "q": "What does an AST drop compared to a parse tree?",
   "options": [
    "Everything except operators",
    "Punctuation and unit productions",
    "All leaf nodes",
    "The root node"
   ],
   "answer": 1,
   "explain": "An AST keeps only meaningful structure: operators as internal nodes, operands as leaves. It drops `(`, `)`, `;`, and single-production chains (unit productions).\n\n*Why the others are wrong:*\n- **A) Everything except operators:** operands (leaves like numbers, identifiers) are kept too.\n- **C) All leaf nodes:** leaves (operands) are essential in an AST.\n- **D) The root node:** the AST always has a root (the start symbol or overall expression)."
  },
  {
   "q": "Under normal precedence, `*` binds tighter than `+`. How does `int * int + int` parse?",
   "options": [
    "(int * int) + int",
    "int * (int + int)",
    "Ambiguous — can't tell",
    "(int + int) * int"
   ],
   "answer": 0,
   "explain": "`*` has higher precedence, so multiplication groups first: `(int * int) + int`.\n\n*Why the others are wrong:*\n- **B) int * (int + int):** would require `+` to bind tighter than `*` — opposite of normal precedence.\n- **C) Ambiguous:** the **grammar** `exp → exp op exp | int` is ambiguous, but with standard precedence rules the intended parse is clear.\n- **D) (int + int) * int:** wrong grouping and wrong precedence."
  },
  {
   "q": "What is the difference between a parse tree and an AST?",
   "options": [
    "Parse tree has more detail (punctuation, unit productions); AST is abstracted",
    "AST is always larger than parse tree",
    "Parse tree shows meaning; AST shows syntax",
    "There is no difference"
   ],
   "answer": 0,
   "explain": "Parse trees include all tokens (including `(`, `)`, `;`) and unit productions. ASTs keep only essential structure.\n\n*Why the others are wrong:*\n- **B) AST larger:** opposite — AST is smaller (drops nodes).\n- **C) Parse tree shows meaning:** both show syntactic structure; neither directly shows \"meaning\" (semantics).\n- **D) No difference:** they differ in detail level — parse tree is concrete, AST is abstract."
  },
  {
   "q": "There is no algorithm that:",
   "options": [
    "Parses any CFG",
    "Decides whether an arbitrary CFG is ambiguous",
    "Converts regex to NFA",
    "Builds a parse tree"
   ],
   "answer": 1,
   "explain": "Ambiguity of CFGs is undecidable — no general algorithm exists. It must be resolved by hand (rewriting the grammar).\n\n*Why the others are wrong:*\n- **A) Parses any CFG:** algorithms like CYK, Earley, and GLR can parse any CFG.\n- **C) Converts regex to NFA:** Thompson's construction does this algorithmically.\n- **D) Builds a parse tree:** that's exactly what parsers do."
  },
  {
   "q": "Left recursion leads to:",
   "options": [
    "Right associativity",
    "Left associativity",
    "Ambiguity",
    "Regular language"
   ],
   "answer": 1,
   "explain": "Left-recursive rules like `exp → exp addop term` produce left-associative trees: `a - b - c` groups as `(a - b) - c`.\n\n*Why the others are wrong:*\n- **A) Right associativity:** comes from right recursion (`exp → term addop exp`).\n- **C) Ambiguity:** left recursion does not imply ambiguity — `exp → exp addop term | term` is unambiguous.\n- **D) Regular language:** left-recursive CFGs describe context-free (not regular) languages."
  },
  {
   "q": "The precedence cascade grammar uses separate nonterminals for:",
   "options": [
    "Each keyword",
    "Each precedence level (exp, term, factor)",
    "Each operator",
    "Each token"
   ],
   "answer": 1,
   "explain": "`exp → exp addop term | term`, `term → term mulop factor | factor`, `factor → (exp) | number` — each level encodes one precedence tier.\n\n*Why the others are wrong:*\n- **A) Keywords:** not what precedence levels are about.\n- **C) Each operator:** operators are terminals within levels, not separate nonterminals per operator.\n- **D) Each token:** too granular — precedence levels group operators, not individual tokens."
  },
  {
   "q": "What does the `*` bind tighter than `+` rule mean for AST construction?",
   "options": [
    "`*` becomes a leaf; `+` becomes the root",
    "`*` becomes a lower (deeper) node; `+` becomes a higher node",
    "They are at the same level",
    "`+` is always evaluated first"
   ],
   "answer": 1,
   "explain": "Tighter-binding operators appear lower in the AST (evaluated first conceptually); looser operators are higher (combine results).\n\n*Why the others are wrong:*\n- **A) `*` leaf; `+` root:** backwards — `+` is the root (combines), `*` is deeper.\n- **C) Same level:** would not encode precedence at all.\n- **D) `+` first:** opposite — `*` is evaluated first due to higher precedence."
  }
 ]
}
```
---

# 6. Lecture 6 — Syntax Analysis III (Top-Down / LL(1) Parsing)

## 6.1 Classification of parsers (L6 s.3–9)

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (A) at (0,0) {\(A\)};
\node[st] (B) at (-2.5,-2.0) {\(B\)};
\node[st] (D) at (2.5,-2.0) {\(D\)\\{\footnotesize dead}};
\node[acc] (C) at (0,-4.0) {\(C\)};
\draw[arr] (start) -- (A);
\draw[arr] (A) -- node[above left] {\(1\)} (B);
\draw[arr] (A) -- node[above right] {\(0\)} (D);
\draw[arr] (B) edge[loop left] node[left] {\(1\)} (B);
\draw[arr] (B) -- node[above left] {\(0\)} (C);
\draw[arr] (D) edge[loop right] node[right] {\(0, 1\)} (D);
\end{tikzpicture}
\end{document}
```

### Top-down parsers (L6 s.4–6)

- Build the parse tree by **expanding nonterminals**, starting from the **start symbol** and ending at the terminals.
- Use a **leftmost derivation**.
- Two kinds:
  1. **Recursive descent** (a.k.a. brute-force / backtracking): tries productions recursively; backtracks on failure. Simple but **inefficient** for large or ambiguous grammars.
  2. **Non-recursive descent** (a.k.a. **LL(1)**, predictive, without backtracking, dynamic): uses a **parsing table** instead of backtracking.

### Bottom-up parsers (L6 s.7–9)

- Build the tree by **compressing** strings into nonterminals, starting from the input and ending at the start symbol.
- Use the **reverse of a rightmost derivation**.
- Two kinds:
  1. **LR parser** — Left-to-right scan, **Rightmost** derivation in reverse. LR(0), SLR(1), LALR(1), CLR(1).
  2. **Operator precedence parser** — works for grammars with **no ε-productions** and **no two adjacent nonterminals** on any RHS.

> [!important] The one-line difference
> **Top-down = "what production do I use next?"** (expand, leftmost, preorder).
> **Bottom-up = "when do I reduce?"** (shift/reduce, reverse rightmost, postorder).

### The `abbcde` example (L6 s.10–11)

Grammar:
```text
S → aABe
A → Abc | b
B → d
```
String: `abbcde`.

- **Top-down** follows the **leftmost derivation**: `S => aABe => aAbcBe => ...` — it predicts **which production to use**.
- **Bottom-up** follows the **reverse rightmost derivation**: it scans `abbcde` and **reduces** `b` to `A`, `Abc` to `A`, `d` to `B`, then `aABe` to `S` — it decides **when to reduce**.

## 6.2 LL(1) parsing (L6 s.52–58)

> [!summary] What LL(1) means
> - **L** — scan the input **Left to right**.
> - **L** — produce a **Leftmost** derivation.
> - **(1)** — use **one token of lookahead** to choose the production.

LL(1) is **predictive**: when expanding a nonterminal, the next input token **forces** the choice of production. No backtracking. It uses a **parsing table**.

> [!warning] Requirements
> The grammar must be **unambiguous**, **without left recursion**, and usually **left-factored**. Not every grammar can be parsed by an LL(1) parser; predictive parsers are **fast but weak** (they trade expressiveness for speed).

## 6.3 The LL(1) parse table (L6 s.53–59)

The table has:

- **Rows:** nonterminals.
- **Columns:** terminals (plus `$`, the end-of-input marker — **not** part of the grammar).
- **Cell `T[A, a]`:** the production to use when the stack top is `A` and the lookahead is `a`.
- **Empty cell:** syntax **error**.

Running example grammar (the lecture's formal LL(1) example):

```text
(1) E  → int
(2) E  → ( E Op E )
(3) Op → +
(4) Op → *
```

| | int | ( | ) | + | * |
|---|---|---|---|---|---|
| **E** | 1 | 2 | – | – | – |
| **Op** | – | – | – | 3 | 4 |

> [!note] Why one token is enough here
> `E` starts with either `int` or `(`, and these are **different** terminals, so the lookahead decides immediately. `Op` starts with `+` or `*`, again distinct.

> [!warning] The lecture's motivating example is different
> Slides 21–49 animate `E → T | T + E`, `T → int | (E)` on `int + (int + int)`. There, deciding between `E → T` and `E → T + E` needs more than one token (slides highlight `int` **and** `+`). That example illustrates **lookahead**, not the formal LL(1) table. The table above is the one to reproduce.

## 6.4 Full LL(1) trace: `( int + ( int * int ) )` (L6 s.60–85)

**Stack convention:** top of stack is written on the **left**. Start with `E$`. The `$` marks end of input.

| Step | Stack | Input | Action |
|---|---|---|---|
| 1 | `E$` | `( int + ( int * int ) ) $` | Predict `E → ( E Op E )` |
| 2 | `( E Op E )$` | `( int + ( int * int ) ) $` | **Match** `(` |
| 3 | `E Op E )$` | `int + ( int * int ) ) $` | Predict `E → int` |
| 4 | `int Op E )$` | `int + ( int * int ) ) $` | **Match** `int` |
| 5 | `Op E )$` | `+ ( int * int ) ) $` | Predict `Op → +` |
| 6 | `+ E )$` | `+ ( int * int ) ) $` | **Match** `+` |
| 7 | `E )$` | `( int * int ) ) $` | Predict `E → ( E Op E )` |
| 8 | `( E Op E ) )$` | `( int * int ) ) $` | **Match** `(` |
| 9 | `E Op E ) )$` | `int * int ) ) $` | Predict `E → int` |
| 10 | `int Op E ) )$` | `int * int ) ) $` | **Match** `int` |
| 11 | `Op E ) )$` | `* int ) ) $` | Predict `Op → *` |
| 12 | `* E ) )$` | `* int ) ) $` | **Match** `*` |
| 13 | `E ) )$` | `int ) ) $` | Predict `E → int` |
| 14 | `int ) )$` | `int ) ) $` | **Match** `int` |
| 15 | `) )$` | `) ) $` | **Match** `)` |
| 16 | `)$` | `) $` | **Match** `)` |
| 17 | `$` | `$` | **Accept** ✅ |

> [!tip] How to read the table
> At every step there are only two possible actions:
> - **Match**: stack top is a **terminal** equal to the lookahead → pop both.
> - **Predict**: stack top is a **nonterminal** → look up `T[A, lookahead]` and replace `A` by the production's RHS (pushed so the **leftmost** symbol is on top).
> If the symbols differ, or the table cell is empty → **error**.

## 6.5 LL(1) error detection (L6 s.86–100)

### Example 1: `int + int $`

| Stack | Input | Action |
|---|---|---|
| `E$` | `int + int $` | Predict `E → int` |
| `int$` | `int + int $` | Match `int` |
| `$` | `+ int $` | **Error**: top is `$`, input is `+` |

The parser expected the end of input after `int`, but found `+`. A valid expression would have been `int + int` parsed as `E → (E Op E)`; this input is missing parentheses around the addition.

### Example 2: `( int ( int ) ) $`

| Stack | Input | Action |
|---|---|---|
| `E$` | `( int ( int ) ) $` | Predict `E → ( E Op E )` |
| `( E Op E )$` | `( int ( int ) ) $` | Match `(` |
| `E Op E )$` | `int ( int ) ) $` | Predict `E → int` |
| `int Op E )$` | `int ( int ) ) $` | Match `int` |
| `Op E )$` | `( int ) ) $` | **Error**: `T[Op, (]` is undefined |

After the first `int`, the parser needs an operator (`+` or `*`), but it sees `(`. The table has no entry for `Op` on `(`, so it reports an error immediately.

> [!important] Error detection is **table-driven**
> There is **no backtracking**. An empty cell or a terminal mismatch is an error. This is why LL(1) parsers are fast and why grammar design matters so much.

## 6.6 The LL(1) algorithm (L6 s.101)

> [!summary] Algorithm
> Given start symbol `S` and LL(1) table `T`, parse string ω:
> 1. Initialize the stack with **`S$`**.
> 2. Repeat until the stack is empty (or accept when top = `$` and input = `$`):
>    - Let `t` be the next input token.
>    - If the top of stack is a **terminal** `r`:
>      - If `r ≠ t`, **error**.
>      - Else consume `t` and pop `r`.
>    - Else the top is a **nonterminal** `A`:
>      - If `T[A, t]` is undefined, **error**.
>      - Else replace `A` on the stack with the RHS of `T[A, t]`.
> 3. **Accept** if the stack is empty (or `$` matches `$`).

```text
push S; push $
repeat
    A = top of stack
    t = current input token
    if A is a terminal or $ then
        if A == t then pop; advance input
        else error
    else
        if T[A, t] is empty then error
        else pop A; push RHS(T[A, t]) in reverse
until stack empty
accept
```

> [!warning] Push in reverse
> When the production is `E → ( E Op E )`, push `)`, `E`, `Op`, `E`, `(` (reverse order) so that `(` ends up on top. If you push left-to-right, the parser matches symbols in the wrong order.

## 6.7 Constructing an LL(1) parse table (L6 s.102–115)

### The grammar

```text
STMT → if EXPR then STMT        (1)
     | while EXPR do STMT       (2)
     | EXPR ;                   (3)

EXPR → TERM -> id               (4)
     | zero? TERM               (5)
     | not EXPR                 (6)
     | ++ id                    (7)
     | -- id                    (8)

TERM → id                       (9)
     | constant                 (10)
```

### Step 1: FIRST sets

The **FIRST** set of a nonterminal is the set of terminals that can begin a string derived from it.

- `FIRST(TERM) = { id, constant }`
- `FIRST(EXPR) = { id, constant, zero?, not, ++, -- }`
- `FIRST(STMT) = { if, while, id, constant, zero?, not, ++, -- }`

### Step 2: Fill the table

For each production `A → α`, put the production number in `T[A, a]` for every `a ∈ FIRST(α)`. (If α can derive ε, also use FOLLOW(A) — that is the next lecture.)

| | if | then | while | do | zero? | not | ++ | -- | -> | id | const | ; |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **STMT** | 1 | – | 2 | – | 3 | 3 | 3 | 3 | – | 3 | 3 | – |
| **EXPR** | – | – | – | – | 5 | 6 | 7 | 8 | – | 4 | 4 | – |
| **TERM** | – | – | – | – | – | – | – | – | – | 9 | 10 | – |

> [!important] Why `STMT` has six 3s
> `STMT → EXPR ;` can start with **any** token that can start `EXPR`: `zero?`, `not`, `++`, `--`, `id`, `constant`. So production 3 goes in all six columns.

> [!note] The `->` column is empty
> `->` is a terminal in the grammar, but no production **starts** with it. It appears only after `TERM`. So all cells under `->` are errors.

## 6.8 Top-down vs bottom-up (L6 s.116)

| Aspect | Top-Down | Bottom-Up |
|---|---|---|
| Direction | Start symbol → input (expand) | Input → start symbol (reduce) |
| Derivation | **Leftmost** | **Reverse rightmost** |
| Ambiguity | Struggles; choices made early | More powerful; handles a wider class |
| Conflicts | Fewer, simpler | Shift-reduce / reduce-reduce conflicts |
| Implementation | Easier to implement/debug | More complex |
| Error recovery | Easier | More challenging |
| Examples | Recursive descent, **LL(k)** | **LR(k)**, SLR, LALR, CLR, operator precedence |

## 6.9 What comes next (and why it matters now)

Lecture 6 ends by announcing the next topics:

1. **FIRST sets**
2. **FOLLOW sets**
3. **Left factoring**

These are the missing pieces for building LL(1) tables in general:

- **FIRST(α)** tells you which lookahead tokens can begin α → which cells get the production.
- **FOLLOW(A)** tells you which tokens can come **after** A → used when a production can derive ε (e.g., `A → ε` goes in `T[A, b]` for every `b ∈ FOLLOW(A)`).
- **Left factoring** removes common prefixes: `A → αβ | αγ` becomes `A → αA'`, `A' → β | γ`. Without it, the table would need two productions in the same cell → not LL(1).
- **Left recursion removal** (also required): `A → Aα | β` becomes `A → βA'`, `A' → αA' | ε`.

> [!tip] Preview formulas (useful for the next quiz)
> - `FIRST(X1X2…Xn)`: start with `FIRST(X1)`; if `X1` can derive ε, add `FIRST(X2)`, and so on.
> - `FOLLOW(S)` contains `$` for the start symbol.
> - If `A → αBβ`, then everything in `FIRST(β)` except ε is in `FOLLOW(B)`.
> - If `A → αB` or `A → αBβ` with `β ⇒* ε`, then `FOLLOW(A) ⊆ FOLLOW(B)`.

## 6.10 Lecture 6 exam traps

> [!danger] High-frequency mistakes
> 1. **LL(1)** = Left-to-right, **Leftmost**, **1** lookahead. Do not mix up the two L's.
> 2. Top-down uses **leftmost** derivations; bottom-up uses **reverse rightmost**.
> 3. **Recursive descent** can backtrack; **predictive/LL(1)** cannot.
> 4. Stack starts as **`S$`**; `$` is **not** a grammar symbol.
> 5. When predicting, **replace** the nonterminal with the RHS — do not push the nonterminal again.
> 6. **Match** only terminals; **predict** only nonterminals.
> 7. An empty table cell means **error**, not "do nothing".
> 8. LL(1) needs **no left recursion** and usually **left factoring**; otherwise one cell gets two productions (a conflict).
> 9. The parser accepts when **both** stack and input reach `$`.
> 10. Operator precedence parsing is **bottom-up**, not top-down.

## 6.11 Quick drills (answers in §9)

1. State the meaning of LL(1) and name the two actions a predictive parser performs.
2. Build the LL(1) table for `E → int | (E Op E)`, `Op → + | *`.
3. Trace `( int * int ) $` using the table.
4. Trace `int * $` and identify the error step.
5. Construct the LL(1) table for the STMT/EXPR/TERM grammar and explain why `STMT` has six 3s.
6. Why does `E → T | T + E` need more than one lookahead token?

## Lecture 6 checkpoint

```mcq-quiz
{
 "title": "Lecture 6 - Top-Down LL(1) Parsing (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "LL(1) stands for:",
   "options": [
    "Left-to-right, Leftmost derivation, 1 lookahead",
    "Left-to-right, Rightmost derivation, 1 lookahead",
    "Right-to-left, Leftmost derivation, 1 lookahead",
    "Left-to-right, Leftmost derivation, 1 stack"
   ],
   "answer": 0,
   "explain": "First L = scan input left-to-right. Second L = produce a leftmost derivation. (1) = one token of lookahead.\n\n*Why the others are wrong:*\n- **B) Rightmost derivation:** that's LR (bottom-up), not LL.\n- **C) Right-to-left:** LL scans left-to-right.\n- **D) 1 stack:** the (1) is lookahead, not stack count."
  },
  {
   "q": "When the stack top is a nonterminal in LL(1), the parser:",
   "options": [
    "Matches it against the lookahead",
    "Replaces it with the RHS of T[A, lookahead]",
    "Pushes $",
    "Consumes the lookahead"
   ],
   "answer": 1,
   "explain": "The parser looks up `T[A, a]` (stack-top nonterminal A, lookahead token a) and expands A using that production.\n\n*Why the others are wrong:*\n- **A) Matches against lookahead:** that's what you do when the stack top is a **terminal**.\n- **C) Pushes $:** `$` is pushed once at initialization, not on every nonterminal expansion.\n- **D) Consumes lookahead:** lookahead is consumed only when a terminal is matched, not when expanding a nonterminal."
  },
  {
   "q": "What does the first L in LL(1) mean?",
   "options": [
    "Lookahead",
    "Left-to-right scan",
    "Leftmost derivation",
    "Language"
   ],
   "answer": 1,
   "explain": "The first L is the input scan direction: left to right.\n\n*Why the others are wrong:*\n- **A) Lookahead:** that's the (1).\n- **C) Leftmost derivation:** that's the **second** L.\n- **D) Language:** not what any L stands for."
  },
  {
   "q": "What does the second L in LL(1) mean?",
   "options": [
    "Left-to-right scan",
    "Leftmost derivation",
    "Lookahead",
    "Left recursion"
   ],
   "answer": 1,
   "explain": "The second L means the parser produces a leftmost derivation (always expand the leftmost nonterminal).\n\n*Why the others are wrong:*\n- **A) Left-to-right scan:** that's the **first** L.\n- **C) Lookahead:** that's the (1).\n- **D) Left recursion:** LL(1) grammars **cannot** have left recursion — it causes infinite expansion."
  },
  {
   "q": "What does the (1) in LL(1) mean?",
   "options": [
    "One pass",
    "One lookahead token",
    "One stack",
    "One production"
   ],
   "answer": 1,
   "explain": "The parser inspects exactly one token of lookahead to decide which production to use.\n\n*Why the others are wrong:*\n- **A) One pass:** LL(1) can be single-pass, but (1) specifically means lookahead.\n- **C) One stack:** all shift-reduce/predictive parsers use a stack — not what (1) counts.\n- **D) One production:** a nonterminal can have multiple productions — the lookahead picks among them."
  },
  {
   "q": "An empty cell `T[A, a]` in the LL(1) parse table means:",
   "options": [
    "Accept",
    "Syntax error",
    "Skip token",
    "Push ε"
   ],
   "answer": 1,
   "explain": "If `T[A, lookahead]` is empty, no production applies — the input is syntactically invalid at that point.\n\n*Why the others are wrong:*\n- **A) Accept:** acceptance happens when stack and input are both exhausted (only `$` remains).\n- **C) Skip token:** LL(1) does not skip — it reports an error (error recovery is separate).\n- **D) Push ε:** ε-productions are explicit table entries, not empty cells."
  },
  {
   "q": "LL(1) grammars must NOT have:",
   "options": [
    "Right recursion",
    "Left recursion",
    "ε-productions",
    "Multiple productions"
   ],
   "answer": 1,
   "explain": "Left recursion (`A → Aα | ...`) causes a predictive parser to expand `A` forever without consuming input — infinite loop.\n\n*Why the others are wrong:*\n- **A) Right recursion:** allowed in LL(1) (e.g., `S → aS | b`).\n- **C) ε-productions:** allowed, but handled carefully via FOLLOW sets.\n- **D) Multiple productions:** normal — the lookahead decides among them."
  },
  {
   "q": "Top-down parsing builds the parse tree by:",
   "options": [
    "Starting from leaves and reducing",
    "Starting from start symbol and expanding nonterminals",
    "Scanning right to left",
    "Using reverse rightmost derivation"
   ],
   "answer": 1,
   "explain": "Top-down = start at the root (start symbol) and work down to leaves, choosing productions to match the input.\n\n*Why the others are wrong:*\n- **A) Leaves and reducing:** that's **bottom-up** parsing.\n- **C) Right to left:** top-down scans left-to-right.\n- **D) Reverse rightmost:** that's bottom-up (LR)."
  },
  {
   "q": "Bottom-up parsing uses:",
   "options": [
    "Leftmost derivation",
    "Reverse of rightmost derivation",
    "Preorder traversal",
    "No stack"
   ],
   "answer": 1,
   "explain": "Bottom-up starts from the input and reduces substrings to nonterminals, ending at the start symbol — equivalent to constructing a rightmost derivation backwards.\n\n*Why the others are wrong:*\n- **A) Leftmost derivation:** that's top-down.\n- **C) Preorder:** corresponds to leftmost (top-down), not bottom-up.\n- **D) No stack:** bottom-up parsers (LR) use a stack extensively."
  },
  {
   "q": "LR parsers are:",
   "options": [
    "Top-down",
    "Bottom-up",
    "Neither",
    "Both"
   ],
   "answer": 1,
   "explain": "LR = Left-to-right scan, Rightmost derivation in reverse — a bottom-up parsing strategy.\n\n*Why the others are wrong:*\n- **A) Top-down:** LL parsers are top-down; LR is bottom-up.\n- **C, D)** LR is clearly bottom-up, not neither or both."
  }
 ]
}
```
---

# 7. Cram Sheet — Definitions, Algorithms, Templates

## 7.1 Must-know definitions (one line each)

| Term | One-line definition |
|---|---|
| **Compiler** | Translates a source program into an equivalent target program |
| **Interpreter** | Translates and executes one statement at a time |
| **Preprocessor** | Removes comments, includes files, expands macros |
| **Assembler** | Translates assembly into an object file (machine code + data) |
| **Linker** | Merges object files/libraries, resolves references, makes addresses absolute |
| **Loader** | OS component that loads the executable into memory and starts it |
| **Lexeme** | Actual character sequence matching a pattern |
| **Token** | Category of lexemes (name + optional attributes) |
| **Pattern** | Rule (usually regex) describing a token's strings |
| **DFA** | Finite automaton with exactly one transition per (state, symbol) |
| **NFA** | Finite automaton allowing multiple transitions and ε-moves |
| **ε-closure(S)** | All states reachable from S using ε-edges only, including S |
| **GNFA** | NFA whose edges are labeled by regexes; one accept state, no in-edge to start, no out-edge from accept |
| **CFG** | 4-tuple (nonterminals, terminals, productions, start symbol) |
| **Derivation** | Sequence of production applications from start symbol to terminals |
| **Parse tree** | Tree encoding a derivation; internal = nonterminals, leaves = terminals |
| **AST** | Tree of operators/constructs and operands; drops concrete syntax |
| **Ambiguous grammar** | Some string has two or more parse trees |
| **LL(1)** | Left-to-right scan, leftmost derivation, one lookahead token |
| **Predictive parser** | LL(1) parser driven by a table, no backtracking |

## 7.2 Regex cheat sheet

| Language | Regex |
|---|---|
| one or more a's | `a+` = `aa*` |
| zero or more a's | `a*` |
| exactly k a's | `a^k` |
| even number of a's | `(aa)*` |
| odd number of a's | `(aa)*a` |
| contains `00` | `(0+1)*00(0+1)*` |
| contains `bb` | `(a+b)*bb(a+b)*` |
| begins with 1, ends with 0 | `1(0+1)*0` |
| no leading zeros | `[1-9][0-9]*` |
| identifier | `[a-zA-Z][a-zA-Z0-9_]*` |
| integer | `[0-9]+` |
| even a's then odd b's | `(aa)*(bb)*b` |
| strings of a's and b's | `(a+b)*` |
| email (alphabet a,@,.) | `a+(.a+)*@a+.a+(.a+)*` |

> [!warning] `+` overload
> Postfix (`a+`) = one or more. Infix (`a+b`) = union. The slides use infix `+` for union constantly.

## 7.3 DFA minimization in 4 lines

1. Remove inaccessible/dead states.
2. `P0` = {final} / {non-final}.
3. Split blocks whose states go to different blocks on some symbol; repeat until stable.
4. Each block = one state.

## 7.4 Table-driven DFA in 4 lines

```text
state ← start
while not error:
    next ← T[state, ch]
    if Advance[state, ch]: ch ← next input
    state ← next
accept iff Accept[state]
```

## 7.5 State elimination in 4 lines

1. New start `qi` (ε to old start), new accept `qf` (ε from old accepts).
2. Pick an intermediate state `k`.
3. For all `i → k → j`: `R_ij |= R_ik (R_kk)* R_kj`.
4. Delete `k`; repeat until only `qi → qf` remains.

## 7.6 CFG templates

| Need | Grammar |
|---|---|
| `a+` | `A → Aa \| a` (left) or `A → aA \| a` (right) |
| `a*` | `A → Aa \| ε` or `A → aA \| ε` |
| `a^n b^n` | `S → aSb \| ε` |
| palindromes over {a,b} | `S → ε \| a \| b \| aSa \| bSb` |
| statement sequence with trailing `;` | `S → stmt ; S \| stmt ;` |
| optional else | `else-part → else stmt \| ε` |
| expressions with precedence | `E → E + T \| T`, `T → T * F \| F`, `F → (E) \| id` |
| dangling else | `matched`/`unmatched` two-nonterminal grammar |

## 7.7 LL(1) in 4 lines

1. Start with `S$` on the stack.
2. Terminal on top: match with lookahead or error.
3. Nonterminal on top: replace with `T[A, lookahead]` or error.
4. Accept when stack and input are both `$`.

## 7.8 "If they ask for X, write Y"

| Question | What to produce |
|---|---|
| Build a DFA for a language | State diagram + transition table + mark start/accept |
| Minimize a DFA | Table, partitions `P0…Pk`, merged states, final diagram |
| Convert RE to DFA | Thompson NFA (rules), subset table with ε-closures |
| Convert DFA to RE | GNFA steps, eliminated states, final regex |
| Design a CFG | 4-tuple + productions + example derivation |
| Show ambiguity | One string + **two different parse trees** (or two leftmost derivations) |
| Make grammar unambiguous | Layered precedence grammar, left recursion for left associativity |
| Dangling else | Explain nearest unmatched if + matched/unmatched grammar |
| LL(1) table | Rows nonterminals, columns terminals, production numbers, `$` |
| LL(1) trace | Stack / input / action table, ending in accept or error |

---

# 8. MCQ Bank (with answer key)

> [!tip] How to use
> Answer each quiz, then click **Check answers**. Every question locks in with the correct option in green, a wrong pick in red, your score, and an explanation. Click **Reset** to try again. The static answer key at the end of the section is kept as a quick reference for when you are away from Obsidian.
> If a quiz shows raw JSON instead of options, enable **MCQ Checker** in Settings → Community plugins (or press `Ctrl+R` to reload Obsidian).

```mcq-quiz
{
 "title": "Warm-up: token, regex and LL(1) basics",
 "prefix": "W",
 "numberStart": 1,
 "questions": [
  {
   "q": "The scanner returns the token NUM(137). What is 137?",
   "options": [
    "The token name",
    "The attribute value (and the lexeme that matched)",
    "The pattern",
    "A parse-tree node"
   ],
   "answer": 1,
   "explain": "NUM is the token name and 137 is the attribute value; it is also the lexeme, the exact text that matched the pattern digit+. Lexemes and patterns are different things from the token itself."
  },
  {
   "q": "Which operator means one or more repetitions?",
   "options": [
    "R*",
    "R+",
    "R?",
    "R | ε"
   ],
   "answer": 1,
   "explain": "R+ is shorthand for RR*: at least one R, followed by any number of extra R's. R* allows zero, R? (or R | ε) makes R optional, and R | ε also allows the empty string."
  },
  {
   "q": "In LL(1), what does the 1 count?",
   "options": [
    "Parser passes",
    "Lookahead tokens",
    "Stack symbols",
    "Productions"
   ],
   "answer": 1,
   "explain": "The 1 is the number of lookahead tokens the parser may inspect before choosing a production. The two L's are the scan direction and the derivation order."
  }
 ]
}
```

```mcq-quiz
{
 "title": "Lecture 1 - The compiler and its phases (Q1-Q10)",
 "prefix": "Q",
 "numberStart": 1,
 "questions": [
  {
   "q": "Who wrote the first compiler, and for which language?",
   "options": [
    "Grace Hopper - A-0",
    "John Backus - FORTRAN",
    "Dennis Ritchie - C",
    "Niklaus Wirth - Pascal"
   ],
   "answer": 0,
   "explain": "Grace Hopper's A-0 (1952) is credited as the first compiler. Backus led the team that produced the first complete compiler for FORTRAN, which is the usual trap in this question."
  },
  {
   "q": "Which team produced the first complete compiler, and for which language?",
   "options": [
    "Hopper's team - A-0",
    "IBM team led by John Backus - FORTRAN",
    "Bell Labs - C",
    "Wirth's team - Pascal"
   ],
   "answer": 1,
   "explain": "The IBM team led by John Backus produced the first complete compiler for FORTRAN in 1954-1957. A-0 came earlier, but it is not the first complete compiler."
  },
  {
   "q": "Which of these is NOT a phase of the compiler itself?",
   "options": [
    "Lexical analysis",
    "Syntax analysis",
    "Linking",
    "Code generation"
   ],
   "answer": 2,
   "explain": "Linking happens after compilation, inside the language processing system: the linker merges object files and resolves external references. Lexical, syntax, semantic analysis and code generation are compiler phases."
  },
  {
   "q": "Which component merges object files and resolves external references?",
   "options": [
    "Linker",
    "Loader",
    "Assembler",
    "Preprocessor"
   ],
   "answer": 0,
   "explain": "The linker combines object files, resolves external symbols and assigns addresses to produce an executable. The loader is the operating system component that later loads that executable into memory."
  },
  {
   "q": "Which component is part of the operating system and loads the program into memory?",
   "options": [
    "Linker",
    "Loader",
    "Assembler",
    "Compiler"
   ],
   "answer": 1,
   "explain": "The loader belongs to the operating system. It allocates memory, loads the executable and starts execution; the linker only builds the executable file."
  },
  {
   "q": "What is the output of lexical analysis?",
   "options": [
    "A parse tree",
    "An annotated tree",
    "A token stream",
    "Assembly code"
   ],
   "answer": 2,
   "explain": "The scanner reads characters and produces a stream of tokens such as NUM(137). The parse tree comes from syntax analysis, and the annotated tree comes from semantic analysis."
  },
  {
   "q": "What is the output of semantic analysis?",
   "options": [
    "An annotated tree",
    "A token stream",
    "A parse tree",
    "Object code"
   ],
   "answer": 0,
   "explain": "Semantic analysis checks types and meaning, then annotates the parse tree (for example with types and resolved names). The token stream is the scanner's output and the parse tree is the parser's output."
  },
  {
   "q": "Which phases belong to the front end?",
   "options": [
    "Target code generation and optimization",
    "Lexical, syntax and semantic analysis plus intermediate code generation",
    "Linking and loading",
    "Assembly and linking"
   ],
   "answer": 1,
   "explain": "The front end is the machine-independent part: lexical, syntax and semantic analysis, then intermediate code generation. Target code generation and optimization form the machine-dependent back end."
  },
  {
   "q": "Which task belongs to the preprocessor?",
   "options": [
    "Build the symbol table",
    "Generate target code",
    "Delete comments, include files and perform macro substitution",
    "Resolve external references"
   ],
   "answer": 2,
   "explain": "The preprocessor handles source-level text: it removes comments, expands macros and includes header files. The symbol table is maintained during compilation, and external references are resolved by the linker."
  },
  {
   "q": "Which statement about compilers vs interpreters is correct?",
   "options": [
    "An interpreter always executes faster than a compiler",
    "A compiler produces no intermediate object code",
    "An interpreter scans the whole program before executing it",
    "A compiler analyzes more slowly but executes faster, and its object code needs linking"
   ],
   "answer": 3,
   "explain": "A compiler pays the translation cost up front, so analysis is slower but repeated execution is faster; it also produces object code that must be linked. An interpreter translates one statement at a time and has no object code, but overall execution is slower."
  }
 ]
}
```

```mcq-quiz
{
 "title": "Lecture 2 - Tokens and regular expressions (Q11-Q22)",
 "prefix": "Q",
 "numberStart": 11,
 "questions": [
  {
   "q": "The actual character sequence matched by a token pattern is called the:",
   "options": [
    "Token",
    "Lexeme",
    "Pattern",
    "Attribute"
   ],
   "answer": 1,
   "explain": "The lexeme is the concrete text, such as 137 or while. The token is the category (NUM, T_While), and the pattern is the rule (digit+) that describes which strings are lexemes."
  },
  {
   "q": "A token is best described as:",
   "options": [
    "The actual character sequence in the source",
    "A regular expression for a lexeme",
    "A category of lexemes, with a name and optional attributes",
    "A node in the parse tree"
   ],
   "answer": 2,
   "explain": "A token is an abstract category produced by the scanner, usually written as name(attribute), for example NUM(137). The character sequence is the lexeme, and the regex is the pattern."
  },
  {
   "q": "The rule that characterizes the set of strings for a token is the:",
   "options": [
    "Pattern",
    "Lexeme",
    "Token",
    "Attribute"
   ],
   "answer": 0,
   "explain": "The pattern describes the lexemes for one token, typically as a regular expression such as letter(letter|digit)*. A lexeme is one string that matches it."
  },
  {
   "q": "In NUM(137), what are NUM and 137?",
   "options": [
    "Attribute value and token name",
    "Lexeme and pattern",
    "Pattern and lexeme",
    "Token name and attribute value"
   ],
   "answer": 3,
   "explain": "NUM is the token name or category; 137 is the attribute value and the lexeme. Reversing these is the most common token/lexeme mistake."
  },
  {
   "q": "Which of the following does the scanner normally discard?",
   "options": [
    "Identifiers",
    "Whitespace and comments",
    "Operators",
    "Keywords"
   ],
   "answer": 1,
   "explain": "Whitespace and comments do not become tokens; the scanner skips them and passes only the token stream to the parser. Identifiers, operators and keywords are all tokens."
  },
  {
   "q": "Which automaton has a stack as temporary memory?",
   "options": [
    "DFA",
    "NFA",
    "Pushdown automaton (PDA)",
    "Turing machine"
   ],
   "answer": 2,
   "explain": "A PDA adds a stack to a finite automaton, which is why it can recognize context-free languages such as a^n b^n. A DFA or NFA has only states, and a Turing machine has a tape."
  },
  {
   "q": "Which automaton has random-access memory and the highest computing power?",
   "options": [
    "Turing machine",
    "PDA",
    "DFA",
    "NFA"
   ],
   "answer": 0,
   "explain": "A Turing machine has an unbounded tape it can read and write, giving it the highest power in this list. A PDA has only a stack, and finite automata have no temporary memory."
  },
  {
   "q": "Which is the correct precedence order for regex operators?",
   "options": [
    "Concatenation > star > union",
    "Union > star > concatenation",
    "Star > ∪ > concatenation",
    "Star > concatenation > union"
   ],
   "answer": 3,
   "explain": "Star binds tightest, then concatenation, then union. That is why ab* means a(b*) and a+b* means a + (b*)."
  },
  {
   "q": "R+ means:",
   "options": [
    "One or more",
    "Zero or more",
    "Optional",
    "Union"
   ],
   "answer": 0,
   "explain": "R+ is RR*: one occurrence followed by any number of extra occurrences. R* allows zero, and R? (or R | ε) is optional."
  },
  {
   "q": "What language does (aa)*(bb)*b describe?",
   "options": [
    "An odd number of a's followed by an even number of b's",
    "An even number of a's followed by an even number of b's",
    "An even number of a's followed by an odd number of b's",
    "Any string over {a,b}"
   ],
   "answer": 2,
   "explain": "(aa)* gives an even number of a's, and (bb)*b gives an even number of b's plus one final b, so the b count is odd. The block of a's must also come first."
  },
  {
   "q": "What language does (0+1)*00(0+1)* describe?",
   "options": [
    "Strings that start with 00",
    "Strings that contain 00 somewhere",
    "Strings that end with 00",
    "Strings with an even number of 0s"
   ],
   "answer": 1,
   "explain": "The leading and trailing (0+1)* allow arbitrary text on both sides, so 00 can appear anywhere. Requiring it at the start or the end would remove one of those stars."
  },
  {
   "q": "Which regex describes all strings over {a,b} containing bb?",
   "options": [
    "(a+b)*bb(a+b)*",
    "(a+b)*b(a+b)*",
    "(a+b)bb",
    "b*(a+b)*"
   ],
   "answer": 0,
   "explain": "The two mandatory b's sit between arbitrary prefixes and suffixes. The second option only requires one b, the third forces the string to end in bb, and the fourth does not require bb at all."
  }
 ]
}
```

```mcq-quiz
{
 "title": "Lecture 3 - DFA, NFA and minimization (Q23-Q36)",
 "prefix": "Q",
 "numberStart": 23,
 "questions": [
  {
   "q": "Which statement about DFA and NFA is correct?",
   "options": [
    "An NFA is faster to execute than a DFA",
    "A DFA is easier to construct directly from a regex than an NFA",
    "A DFA and an NFA always have the same number of states",
    "An NFA is easier to construct but harder to implement, while a DFA is faster to execute"
   ],
   "answer": 3,
   "explain": "Thompson's construction builds an NFA easily from a regex, but the NFA can have several moves at once. Subset construction turns it into a DFA, which is fast to run with a table but harder to build directly."
  },
  {
   "q": "ε-closure(S) contains:",
   "options": [
    "Every state reachable from S on any label",
    "Only S itself",
    "S itself plus every state reachable using ε-edges only",
    "Every state reachable in exactly one step"
   ],
   "answer": 2,
   "explain": "The closure always includes S itself (zero ε-steps), then follows only ε-edges. Forgetting S itself is the classic subset-construction error."
  },
  {
   "q": "In DFA minimization, the initial partition P0 separates:",
   "options": [
    "Final states from non-final states",
    "The start state from all other states",
    "Accepting states from dead states only",
    "States with identical transitions"
   ],
   "answer": 0,
   "explain": "P0 puts all accepting states in one group and all non-accepting states in another. Refinement then splits groups whose transitions disagree."
  },
  {
   "q": "In the lecture's Example 1 (q0 to q4), which states are merged?",
   "options": [
    "q0 and q1",
    "q0 and q2",
    "q1 and q2",
    "q3 and q4"
   ],
   "answer": 1,
   "explain": "q0 and q2 behave identically on both a and b, so the final partition is {q0,q2}{q1}{q3}{q4}. Merging them gives a four-state minimal DFA."
  },
  {
   "q": "The minimum-state DFA for a regular language is:",
   "options": [
    "Unique with exactly the same state names",
    "Unique up to renaming of states",
    "Always one of several minima with different languages",
    "Not guaranteed to exist"
   ],
   "answer": 1,
   "explain": "The minimal DFA is unique as a graph, but the state names are arbitrary. Two correct answers may label the states differently while accepting the same language."
  },
  {
   "q": "In table-driven DFA code, T[state, ch] stores:",
   "options": [
    "Whether to consume the input character",
    "The next state",
    "Whether the state is accepting",
    "The token's attribute value"
   ],
   "answer": 1,
   "explain": "T is the transition table: given the current state and input character, it returns the next state. Advance decides consumption, and Accept marks accepting states."
  },
  {
   "q": "In table-driven DFA code, Advance[state, ch] decides:",
   "options": [
    "Whether to consume the input character",
    "The next state",
    "Whether the state is accepting",
    "Which error message to print"
   ],
   "answer": 0,
   "explain": "Advance separates moving in the automaton from consuming input, which is essential for longest match and for the final lookahead character. T only gives the next state."
  },
  {
   "q": "Which is NOT an advantage of table-driven DFA over hand-written if/while code?",
   "options": [
    "The code is compact and systematic",
    "It is easier to modify when the automaton changes",
    "It eliminates the need for a transition table",
    "It avoids duplicated logic"
   ],
   "answer": 2,
   "explain": "Table-driven code uses a transition table; it does not eliminate it. Its advantages are compactness, systematic structure, easier modification and less duplicated logic."
  },
  {
   "q": "Thompson's construction converts:",
   "options": [
    "A regular expression to an NFA",
    "An NFA to a DFA",
    "A DFA to a regular expression",
    "A CFG to a PDA"
   ],
   "answer": 0,
   "explain": "Thompson's construction builds an NFA compositionally from the regex operators union, concatenation and star. Subset construction is the NFA-to-DFA step."
  },
  {
   "q": "Subset construction converts:",
   "options": [
    "A regular expression to an NFA",
    "A DFA to its minimal form",
    "An NFA to a DFA",
    "A DFA to a regular expression"
   ],
   "answer": 2,
   "explain": "Subset construction makes one DFA state for each set of NFA states, using ε-closures. It removes nondeterminism rather than minimizing an existing DFA."
  },
  {
   "q": "Which is a required property of a GNFA?",
   "options": [
    "It must have several accept states",
    "It has exactly one accept state, no edges into the start and no edges out of the accept",
    "It cannot contain self-loops",
    "Every state must be accepting"
   ],
   "answer": 1,
   "explain": "The generalized NFA used for state elimination has a single start, a single accept, no incoming edges to the start and no outgoing edges from the accept. This makes the final regex read directly from start to accept."
  },
  {
   "q": "When eliminating state k, the new edge label is:",
   "options": [
    "R_ij ∪ R_ik R_kj",
    "R_ij (R_kk)* R_kj",
    "R_ij ∪ R_ik (R_kk)* R_kj",
    "R_ik ∪ R_kj"
   ],
   "answer": 2,
   "explain": "The path i to k to j contributes R_ik (R_kk)* R_kj, and it is unioned with the existing i-to-j edge R_ij. The star is essential because the path may loop at k any number of times."
  },
  {
   "q": "In the state-elimination Example 1 (eliminating A then B), the resulting regex is:",
   "options": [
    "0(01)*",
    "0(10)*",
    "(10)*0",
    "01*0"
   ],
   "answer": 1,
   "explain": "Eliminating A gives qi to B on 0 and a B loop on 10. Eliminating B then gives 0(10)*. The reverse elimination order gives the equivalent (01)*0, which is not listed."
  },
  {
   "q": "What should you do with an inaccessible state before minimizing?",
   "options": [
    "Remove it and its edges",
    "Merge it with the dead state",
    "Mark it accepting",
    "Keep it so the DFA stays complete"
   ],
   "answer": 0,
   "explain": "An inaccessible state can never be reached from the start, so it cannot affect the language. Remove it and its edges before partitioning."
  }
 ]
}
```

```mcq-quiz
{
 "title": "Lecture 4 - Context-free grammars (Q37-Q44)",
 "prefix": "Q",
 "numberStart": 37,
 "questions": [
  {
   "q": "How many components does a CFG have?",
   "options": [
    "Three",
    "Five, including the symbol table",
    "Four: nonterminals, terminals, productions and a start symbol",
    "Four, but without a start symbol"
   ],
   "answer": 2,
   "explain": "A CFG is (V, Σ, P, S): nonterminals, terminals, productions and the start symbol. Omitting S is a common exam error."
  },
  {
   "q": "What language does E → E generate?",
   "options": [
    "ε",
    "∅",
    "{ε}",
    "All strings"
   ],
   "answer": 1,
   "explain": "The rule only rewrites E to E forever; no terminal string is ever produced, so the language is empty. To generate ε you need an ε-production such as E → ε."
  },
  {
   "q": "Which rule is left recursive?",
   "options": [
    "A → Aa",
    "A → aA",
    "A → a",
    "A → BA"
   ],
   "answer": 0,
   "explain": "Left recursion means the nonterminal appears as the first symbol on the right side, as in A → Aa. A → aA is right recursive, and A → BA is not recursion in A at the first position."
  },
  {
   "q": "A → A α | β generates:",
   "options": [
    "α* β",
    "(α β)*",
    "β α+",
    "β α*"
   ],
   "answer": 3,
   "explain": "The recursion builds β followed by any number of αs: β, β α, β α α, and so on, which is β α*. The form α* β is the right-recursive counterpart."
  },
  {
   "q": "Which grammar generates a*?",
   "options": [
    "A → Aa",
    "A → Aa | ε",
    "A → aA",
    "A → a"
   ],
   "answer": 1,
   "explain": "A → Aa | ε can derive ε, a, aa, and so on. A → Aa alone derives nothing, A → aA derives a+ only, and A → a derives exactly one a."
  },
  {
   "q": "What is the language of S → aSb | ε?",
   "options": [
    "{a^n b^n | n >= 0}",
    "{a^n b^n | n >= 1}",
    "a*b*",
    "All palindromes over {a,b}"
   ],
   "answer": 0,
   "explain": "Each recursive step adds one a on the left and one b on the right, and the ε-production stops with n = 0, giving ε, ab, aabb, and so on. Without ε it would start at n = 1."
  },
  {
   "q": "What does S → aSb (with no ε-production) generate?",
   "options": [
    "ε",
    "{a^n b^n | n >= 1}",
    "∅",
    "a*b*"
   ],
   "answer": 2,
   "explain": "There is no base case, so the recursion can never terminate in a string of terminals. The language is empty, not ε and not a^n b^n."
  },
  {
   "q": "Which CFG corresponds to the regex a*b?",
   "options": [
    "S → aSb | ε",
    "S → AB, A → aA | ε, B → bB | ε",
    "S → aA, A → b",
    "S → Ab, A → Aa | ε"
   ],
   "answer": 3,
   "explain": "A → Aa | ε generates a*, and S → Ab appends exactly one b, so the language is a*b. The second option generates a*b*, and the third generates only ab."
  }
 ]
}
```

```mcq-quiz
{
 "title": "Lecture 5 - Parse trees and ambiguity (Q45-Q52)",
 "prefix": "Q",
 "numberStart": 45,
 "questions": [
  {
   "q": "In a parse tree, reading the leaves left to right gives:",
   "options": [
    "The parse tree's grammar",
    "The derived terminal string",
    "The abstract syntax tree",
    "The start symbol"
   ],
   "answer": 1,
   "explain": "The leaves are the terminals left after the derivation, so reading them in order gives the derived string. The root is the start symbol, and the AST is a simplified tree, not the leaf sequence."
  },
  {
   "q": "A leftmost derivation corresponds to which traversal of the parse tree?",
   "options": [
    "Postorder",
    "Inorder",
    "Preorder",
    "Level order"
   ],
   "answer": 2,
   "explain": "A leftmost derivation expands the leftmost nonterminal first, which matches visiting the root before its children from left to right: preorder."
  },
  {
   "q": "Compared with a parse tree, an AST:",
   "options": [
    "Contains only meaningful information and drops punctuation and unit productions",
    "Keeps every token, including parentheses and semicolons",
    "Is always a smaller grammar",
    "Is exactly the same tree"
   ],
   "answer": 0,
   "explain": "The AST keeps operators, operands and structure but drops punctuation and chain productions such as E → T. That is why it is smaller and easier for the later phases."
  },
  {
   "q": "Ambiguity is a property of:",
   "options": [
    "The language",
    "Both the grammar and the language",
    "Neither the grammar nor the language",
    "The grammar, not the language"
   ],
   "answer": 3,
   "explain": "A grammar is ambiguous if one string has two different parse trees. The same language may have an ambiguous grammar and an unambiguous one, so ambiguity is a property of the grammar."
  },
  {
   "q": "Why is exp → exp op exp | int ambiguous for int * int + int?",
   "options": [
    "It has two leftmost derivations that produce the same tree",
    "It has two different parse trees: (int*int)+int and int*(int+int)",
    "It is left recursive",
    "It is missing the + operator"
   ],
   "answer": 1,
   "explain": "The grammar gives * and + the same precedence and no associativity, so the string can be grouped two ways. Two different trees, not merely two derivations of one tree, are what prove ambiguity."
  },
  {
   "q": "In the dangling-else problem, the else binds to:",
   "options": [
    "The first if",
    "The outermost if",
    "The closest unmatched (most closely nested) if",
    "The last if in the program"
   ],
   "answer": 2,
   "explain": "The usual rule is that else matches the nearest unmatched if, which is why the grammar needs a matched/unmatched distinction to remove the ambiguity."
  },
  {
   "q": "Left recursion in an expression grammar produces:",
   "options": [
    "Left associativity",
    "Right associativity",
    "No associativity",
    "Ambiguity in every string"
   ],
   "answer": 0,
   "explain": "A → A α | β builds the left operand first, so repeated operators group to the left: 34-3-42 means (34-3)-42. Right recursion gives right associativity."
  },
  {
   "q": "Which is true about inherently ambiguous languages?",
   "options": [
    "Their grammar can always be made unambiguous",
    "Only ambiguous grammars can describe them",
    "They are not context-free",
    "No unambiguous grammar exists for them"
   ],
   "answer": 3,
   "explain": "A language is inherently ambiguous when every grammar for it is ambiguous; no general algorithm removes the ambiguity. This is a property of some context-free languages, not of all of them."
  }
 ]
}
```

```mcq-quiz
{
 "title": "Lecture 6 - Top-down parsing and LL(1) (Q53-Q62)",
 "prefix": "Q",
 "numberStart": 53,
 "questions": [
  {
   "q": "LL(1) stands for:",
   "options": [
    "Left-to-right scan, Rightmost derivation, 1 lookahead",
    "Left-to-right scan, Leftmost derivation, 1 token lookahead",
    "Right-to-left scan, Leftmost derivation, 1 lookahead",
    "Left-to-right scan, Leftmost derivation, 1 stack"
   ],
   "answer": 1,
   "explain": "The first L is the input scan direction, the second L is the derivation order, and the 1 is the number of lookahead tokens. Mixing up the two L's is a common exam trap."
  },
  {
   "q": "A top-down parser uses which derivation?",
   "options": [
    "Leftmost",
    "Rightmost",
    "Reverse rightmost",
    "Any derivation order"
   ],
   "answer": 0,
   "explain": "Top-down parsing expands the start symbol and always works on the leftmost nonterminal, so it corresponds to a leftmost derivation. Bottom-up parsing corresponds to the reverse of a rightmost derivation."
  },
  {
   "q": "A bottom-up parser uses which derivation?",
   "options": [
    "Leftmost",
    "Preorder",
    "Reverse of the rightmost derivation",
    "Reverse of the leftmost derivation"
   ],
   "answer": 2,
   "explain": "A bottom-up parser reduces the input back to the start symbol, which is the reverse of a rightmost derivation. Top-down parsers use leftmost derivations."
  },
  {
   "q": "Recursive descent parsing is also called:",
   "options": [
    "Predictive parsing",
    "Brute-force or backtracking parsing",
    "LL(1) parsing",
    "LR parsing"
   ],
   "answer": 1,
   "explain": "Plain recursive descent may try a production, fail and backtrack, so it is a brute-force method. Predictive (LL(1)) parsing uses a table and never backtracks."
  },
  {
   "q": "In an LL(1) table, an empty cell means:",
   "options": [
    "A syntax error",
    "Accept",
    "Skip the token",
    "Reduce"
   ],
   "answer": 0,
   "explain": "No production is predicted for that nonterminal and lookahead, so the parser reports an error. Acceptance happens only when the stack and the input both reach $; the parser does not skip input."
  },
  {
   "q": "What is the initial stack content?",
   "options": [
    "$",
    "S",
    "ε",
    "S$"
   ],
   "answer": 3,
   "explain": "The stack starts with the start symbol S on top of the end marker $, written S$. The input also ends with $, and acceptance requires both to be consumed."
  },
  {
   "q": "When the stack top is a nonterminal, the parser:",
   "options": [
    "Matches it against the lookahead",
    "Pushes the same nonterminal again",
    "Replaces it with the right side of T[A, lookahead]",
    "Consumes the lookahead"
   ],
   "answer": 2,
   "explain": "The parser looks up T[A, a], pops A and pushes the production's right side in reverse order. Matching and consuming happen only for terminals."
  },
  {
   "q": "When the stack top is a terminal that differs from the lookahead, the parser:",
   "options": [
    "Pops the terminal",
    "Reports an error",
    "Pushes a new nonterminal",
    "Shifts the token"
   ],
   "answer": 1,
   "explain": "A terminal on the stack must match the next input token exactly. If it does not, no production can fix it at this point, so the parser reports a syntax error."
  },
  {
   "q": "Which parser is bottom-up?",
   "options": [
    "LL(1)",
    "Recursive descent",
    "Predictive parser",
    "Operator precedence parser"
   ],
   "answer": 3,
   "explain": "Operator precedence parsing, like LR parsing, is bottom-up: it reduces handles until the start symbol is reached. LL(1), recursive descent and predictive parsing are top-down."
  },
  {
   "q": "Which is required for an LL(1) grammar?",
   "options": [
    "Unambiguous, no left recursion and left-factored",
    "It may be ambiguous if the table is small",
    "Left recursion is allowed if the grammar is unambiguous",
    "It must not be left-factored"
   ],
   "answer": 0,
   "explain": "LL(1) needs an unambiguous grammar, no left recursion (otherwise the parser loops) and usually left factoring (otherwise one cell gets two productions). Without these, the table has conflicts."
  }
 ]
}
```

> [!success]- Answer key (click to expand)
> 1. **Grace Hopper**, 1952, for **A-0**. (L1 s.18)
> 2. **IBM team led by John Backus**, **FORTRAN**, 1954–1957. (L1 s.18)
> 3. **Linking** — linking happens after the compiler, in the language processing system. (L1 s.23–28)
> 4. **Linker.** (L1 s.27)
> 5. **Loader.** (L1 s.28)
> 6. **Token stream.** (L2 s.6)
> 7. **Annotated tree.** (L2 s.6)
> 8. **Lexical, syntax, semantic analysis + intermediate code generation.** (L2 s.6)
> 9. **Delete comments, include files, perform macro substitution.** (L1 s.24)
> 10. **Compiler: slower analysis, faster execution, generates object code needing linking.** (L1 s.36)
> 11. **Lexeme.** (L2 s.13)
> 12. **A category of lexemes, with a name and optional attributes.** (L2 s.13)
> 13. **Pattern.** (L2 s.13)
> 14. `NUM` = **token name/category**; `137` = **attribute value** (and the lexeme). (L2 s.18)
> 15. **Whitespace and comments.** (L2 s.12, s.32)
> 16. **Pushdown automaton (PDA).** (L2 s.48)
> 17. **Turing machine.** (L2 s.48)
> 18. **Star > concatenation > union.** (L2 s.60)
> 19. **One or more** (`RR*`). (L2 s.60)
> 20. **An even number of a's followed by an odd number of b's** (`a^{2n}b^{2m+1}`). (L2 s.67)
> 21. **All strings containing the substring `00`.** (L2 s.68)
> 22. **`(a+b)*bb(a+b)*`.** (L2 s.73–74)
> 23. **NFA is easier to construct but harder to implement; DFA is easier/faster to execute.** (L3 s.13)
> 24. **S itself plus all states reachable by ε-edges only.** (L3 s.44)
> 25. **Final states vs non-final states.** (L3 s.21)
> 26. **`q0` and `q2`.** (L3 s.24)
> 27. **Unique up to renaming of states.** (L3 s.20)
> 28. **The next state.** (L3 s.37)
> 29. **Whether to consume the input character.** (L3 s.37)
> 30. **"It eliminates the need for a transition table"** — the opposite is true; table-driven code *uses* tables. (L3 s.36–39)
> 31. **RE → NFA.** (L3 s.43)
> 32. **NFA → DFA.** (L3 s.44)
> 33. **Exactly one accept state, no arrows into the start, no arrows out of the accept.** (L3 s.51)
> 34. **`R_ij ∪ R_ik (R_kk)* R_kj`.** (L3 s.58)
> 35. **`0(10)*`** (eliminating A then B). (L3 s.62)
> 36. **Remove it (and its edges).** (L3 s.26–28)
> 37. **Four:** nonterminals, terminals, productions, start symbol. (L4 s.18)
> 38. **∅ — no terminal string can be derived.** (L4 s.24)
> 39. **`A → A a`.** (L4 s.35)
> 40. **`β α*`.** (L4 s.36)
> 41. **`A → Aa | ε`** (or `A → aA | ε`). (L4 s.34)
> 42. **`{a^n b^n | n ≥ 0}`.** (L4 s.44)
> 43. **Nothing (∅)** — no base case. (L4 s.41)
> 44. **`S → Ab`, `A → Aa | ε`.** (L4 s.42)
> 45. **The derived terminal string.** (L5 s.5)
> 46. **Preorder (root, then children left to right).** (L5 s.6)
> 47. **Contains only meaningful information (abstract syntax); drops punctuation/unit productions.** (L5 s.49)
> 48. **The grammar, not the language.** (L5 s.52)
> 49. **There are two different parse trees: `(int*int)+int` and `int*(int+int)` — the grammar has no precedence.** (L5 s.53–55)
> 50. **The closest unmatched (most closely nested) `if`.** (L5 s.76)
> 51. **Left associativity** (`34-3-42` = `(34-3)-42`). (L5 s.67–71)
> 52. **No unambiguous grammar exists for them.** (L5 s.52)
> 53. **Left-to-right scan, Leftmost derivation, 1 token lookahead.** (L6 s.52)
> 54. **Leftmost derivation.** (L6 s.4)
> 55. **Reverse of the rightmost derivation.** (L6 s.7)
> 56. **Brute-force / backtracking parser.** (L6 s.5)
> 57. **A syntax error.** (L6 s.101)
> 58. **`S$`** (start symbol + end marker). (L6 s.101)
> 59. **Predicts a production using `T[A, lookahead]` and replaces the nonterminal with its RHS.** (L6 s.101)
> 60. **Reports an error.** (L6 s.101)
> 61. **Operator precedence parser** (and LR). (L6 s.9)
> 62. **Unambiguous, no left recursion, left-factored.** (L6 s.18, s.117)

---

# 9. Written-Exam Bank (with model answers)

> [!tip] How to write answers that score
> 1. **Define** the object (diagram/4-tuple/table).
> 2. **Show every step** (partitions, ε-closures, stack, derivations).
> 3. **State the result** in a boxed sentence.
> 4. If a diagram is asked for, label **start** and **accepting** states.

## Problem 1 — Compiler phases and the language processing system

**Question:** Draw the language processing system and explain each stage. Then list the phases inside the compiler and say which are front-end/back-end.

**Model answer:**

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0) {};
\node[st] (qi) at (0,-1.3) {\(q_i\)};
\node[st] (A) at (0,-2.8) {\(A\)};
\node[st] (B) at (0,-4.3) {\(B\)};
\node[st] (qf) at (0,-5.8) {\(q_f\)};
\node[acc] (end) at (0,-7.4) {};
\draw[arr] (start) -- (qi);
\draw[arr] (qi) -- node[right] {\(\varepsilon\)} (A);
\draw[arr] (A) -- node[right] {\(0\)} (B);
\draw[arr] (B) edge[bend right=55] node[right=1pt] {\(1\)} (A);
\draw[arr] (B) -- node[right] {\(\varepsilon\)} (qf);
\draw[arr] (qf) -- (end);
\end{tikzpicture}
\end{document}
```

- **Preprocessor:** deletes comments, expands macros, includes headers.
- **Compiler:** translates preprocessed source to assembly; reports errors.
- **Assembler:** assembly → object file (machine instructions + relocation data).
- **Linker:** merges object files, resolves external symbols, assigns absolute addresses → executable.
- **Loader:** OS loads the executable into memory, allocates space, initializes registers, starts execution.

**Compiler phases:** lexical → syntax → semantic → intermediate code generation → intermediate optimization → target code generation → target optimization. Symbol table and error handling are used throughout.

**Front end:** lexical, syntax, semantic, IR generation (machine-independent).
**Back end:** target code generation and optimization (machine-dependent).

## Problem 2 — Compiler vs interpreter

**Question:** Compare compilers and interpreters in four points.

**Model answer:**

| Point | Compiler | Interpreter |
|---|---|---|
| Translation | Whole program at once | One statement at a time |
| Analysis time | Large | Small |
| Execution speed | Fast | Slow |
| Object code / memory | Generates intermediate object code, needs linking, more memory | No intermediate object code, memory efficient |
| Examples | C, C++ | JavaScript, Ruby |

**Concluding sentence:** A compiler pays translation cost up front for fast repeated execution; an interpreter pays per execution but needs no object file.

## Problem 3 — Tokenize a statement

**Question:** For `while (137 < i) ++i;`, list the lexemes, tokens, and attributes. What is discarded?

**Model answer:**

| Lexeme | Token | Attribute |
|---|---|---|
| `while` | `T_While` | — |
| `(` | `(` | — |
| `137` | `T_IntConst` | `137` |
| `<` | `<` | — |
| `i` | `T_Ident` | `"i"` |
| `)` | `)` | — |
| `++` | `++` | — |
| `i` | `T_Ident` | `"i"` |
| `;` | `;` | — |

**Discarded:** spaces, `\n`, `\t`, and comments. **Longest match:** `++` is one token, not two `+` tokens.

**Syntax tree:** `While` node; condition `<` with children `Ident(ip)`, `Ident(z)`; body `++` with child `Ident(ip)`.

## Problem 4 — Write regular expressions

**Question:** Over Σ = {a,b}, write regexes for:
(a) strings containing `bb`;
(b) strings made of an even number of a's followed by an odd number of b's;
(c) identifiers over letters/digits/underscore;
(d) an email address over {a, @, .}.

**Model answer:**

(a) `(a+b)*bb(a+b)*`.

(b) `(aa)*(bb)*b` — an even number of a's (possibly zero), then one or more b's with an even number before the final b, i.e. `a^{2n}b^{2m+1}`. This is the **block** form used in the lecture; it does not allow b's before the a-block.

(c) `[a-zA-Z][a-zA-Z0-9_]*`.

(d) `a+(.a+)*@a+.a+(.a+)*`.

## Problem 5 — DFA design and minimization

**Question:** (a) Build a DFA for strings over {0,1} that begin with 1 and end with 0. (b) Minimize the DFA of Lecture 3 Example 1.

**Model answer (a):**

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0.95) {};
\node[st] (A) at (0,0) {\(A\)};
\node[st] (B) at (-2.5,-2.0) {\(B\)};
\node[st] (D) at (2.5,-2.0) {\(D\)\\{\footnotesize dead}};
\node[acc] (C) at (0,-4.0) {\(C\)};
\draw[arr] (start) -- (A);
\draw[arr] (A) -- node[above left] {\(1\)} (B);
\draw[arr] (A) -- node[above right] {\(0\)} (D);
\draw[arr] (B) edge[loop left] node[left] {\(1\)} (B);
\draw[arr] (B) -- node[above left] {\(0\)} (C);
\draw[arr] (D) edge[loop right] node[right] {\(0, 1\)} (D);
\end{tikzpicture}
\end{document}
```

`A` start, `C` accepting, `D` dead. Transition table:

| State | 0 | 1 |
|---|---|---|
| → A | D | B |
| B | C | B |
| *C | – | – |
| D | D | D |

**Model answer (b):**

| State | a | b |
|---|---|---|
| → q0 | q1 | q2 |
| q1 | q1 | q3 |
| q2 | q1 | q2 |
| q3 | q1 | *q4 |
| *q4 | q1 | q2 |

- `P0 = {q0,q1,q2,q3}{q4}`
- `P1 = {q0,q1,q2}{q3}{q4}`
- `P2 = {q0,q2}{q1}{q3}{q4}`
- `P3 = P2` → stop. Merge `q0,q2`.

Minimal DFA: `A={q0,q2}` (start), `B=q1`, `C=q3`, `D=q4` (accept); transitions as in §3.4. **4 states.**

## Problem 6 — RE → NFA → DFA

**Question:** Convert `(a|ε)b*` to an NFA using Thompson's construction, then to a DFA using subset construction.

**Model answer:**

**Thompson:** build `a` (2 states), `ε` (2 states), combine them with a union (new start, new accept, ε-branches), then concatenate with `b*` (loop and ε-bypass). The result has 10 states with ε-edges.

**Subset construction:**

- `A = ε-closure({1}) = {1,2,3,4,6,7,8,10}` (start, accept)
- `B = ε-closure(move(A,a)) = {5,6,7,8,10}` (accept)
- `C = ε-closure(move(A,b)) = {8,9,10}` (accept)
- `B` on `a` → ∅; `B` on `b` → `C`
- `C` on `a` → ∅; `C` on `b` → `C`

| DFA state | a | b |
|---|---|---|
| → A | B | C |
| *B | ∅ | C |
| *C | ∅ | C |
| ∅ | ∅ | ∅ |

**Minimization:** `B` and `C` are equivalent (both accepting, same behavior on a/b), so merge. Final DFA: `A` (accept, start) —a,b→ `{B,C}` (accept), `{B,C}` —b→ `{B,C}`, `{B,C}` —a→ dead.

## Problem 7 — DFA → regular expression

**Question:** Convert the DFA below to a regex using state elimination.

```tikz
\usetikzlibrary{automata, positioning, arrows.meta}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=2.2mm]},
  every node/.style={font=\small},
  box/.style={draw, rounded corners=4pt, minimum width=2.8cm, minimum height=0.85cm, align=center},
  st/.style={box, minimum width=1.9cm},
  acc/.style={circle, draw, double, double distance=1.6pt, minimum size=0.95cm, align=center, inner sep=1pt},
  dot/.style={circle, fill=black, inner sep=2pt},
  arr/.style={->, semithick},
  barr/.style={<->, semithick},
  darr/.style={->, semithick, dashed},
  tnode/.style={draw, rounded corners=3pt, inner sep=3pt, minimum height=0.55cm, align=center}
]
\node[dot] (start) at (0,0) {};
\node[st] (qi) at (0,-1.3) {\(q_i\)};
\node[st] (A) at (0,-2.8) {\(A\)};
\node[st] (B) at (0,-4.3) {\(B\)};
\node[st] (qf) at (0,-5.8) {\(q_f\)};
\node[acc] (end) at (0,-7.4) {};
\draw[arr] (start) -- (qi);
\draw[arr] (qi) -- node[right] {\(\varepsilon\)} (A);
\draw[arr] (A) -- node[right] {\(0\)} (B);
\draw[arr] (B) edge[bend right=55] node[right=1pt] {\(1\)} (A);
\draw[arr] (B) -- node[right] {\(\varepsilon\)} (qf);
\draw[arr] (qf) -- (end);
\end{tikzpicture}
\end{document}
```

**Model answer:**

1. Add `qi` (new start) and `qf` (new accept) — already shown.
2. Eliminate `A`:
   - `qi → B`: `ε · 0 = 0`.
   - `B → B`: `1 · 0 = 10` (path `B → A → B`, since `A` has no loop).
3. Eliminate `B`: `qi → qf` = `0 (10)* · ε = 0(10)*`.

**Answer:** `0(10)*`.

> [!note] Check by elimination order
> Eliminating `B` first gives `(01)*0`. Since `0(10)* = (01)*0`, both are correct.

## Problem 8 — CFG design and derivation

**Question:** (a) Derive `int * (int + int)` leftmost using `E → int | E Op E | (E)`, `Op → +|-|*|/`, and draw the parse tree. (b) Design a CFG for `{a^n b^n | n ≥ 0}`. (c) Design a CFG for palindromes over {a,b}.

**Model answer (a):**

```text
E => E Op E
  => int Op E
  => int * E
  => int * (E)
  => int * (E Op E)
  => int * (int Op E)
  => int * (int + E)
  => int * (int + int)
```

Parse tree: root `E` → `E(int)`, `Op(*)`, `E`; the right `E` → `(`, `E`, `)`; the inner `E` → `E(int)`, `Op(+)`, `E(int)`.

**Model answer (b):**
```text
S → aSb | ε
```

**Model answer (c):**
```text
S → ε | a | b | aSa | bSb
```

## Problem 9 — Ambiguity

**Question:** Show that `E → E Op E | int`, `Op → + | - | *` is ambiguous using `int * int + int`. Then rewrite it unambiguously with `*` higher precedence and left associativity.

**Model answer:**

Two parse trees for `int * int + int`:

1. `+` at root, left child `*` with two `int`s, right child `int` → `(int * int) + int`.
2. `*` at root, left child `int`, right child `+` with two `int`s → `int * (int + int)`.

Since one string has two parse trees, the grammar is **ambiguous**.

Unambiguous grammar:
```text
exp    → exp addop term | term
addop  → + | -
term   → term mulop factor | factor
mulop  → *
factor → ( exp ) | int
```

`*` is deeper (higher precedence); left recursion makes `+`/`-` left-associative.

## Problem 10 — Dangling else

**Question:** Explain the dangling-else ambiguity for `if (0) if (1) other else other`. Which association is used in practice? Give an unambiguous grammar.

**Model answer:**

The grammar with `if-stmt → if (exp) statement | if (exp) statement else statement` allows two trees:

- else belongs to the **outer** if (the inner if has no else);
- else belongs to the **inner** if.

Most languages use the rule: **else matches the nearest unmatched if**, so the second tree is correct.

Unambiguous grammar:
```text
statement      → matched-stmt | unmatched-stmt
matched-stmt   → if ( exp ) matched-stmt else matched-stmt | other
unmatched-stmt → if ( exp ) statement
               | if ( exp ) matched-stmt else unmatched-stmt
exp            → 0 | 1
```

Only a matched statement may precede `else`, forcing else-parts to match as soon as possible.

## Problem 11 — LL(1) table and trace

**Question:** Build the LL(1) table for `E → int | (E Op E)`, `Op → + | *`, then trace `( int + ( int * int ) ) $`.

**Model answer:**

| | int | ( | ) | + | * |
|---|---|---|---|---|---|
| E | 1 | 2 | – | – | – |
| Op | – | – | – | 3 | 4 |

Trace: see the 17-step table in §6.4. Key actions: predict 2, match `(`, predict 1, match `int`, predict 3, match `+`, predict 2, match `(`, predict 1, match `int`, predict 4, match `*`, predict 1, match `int`, match `)`, match `)`, accept.

> [!warning] Show the stack
> A trace without the stack column loses most of the marks. Write `E$`, `(E Op E)$`, … exactly.

## Problem 12 — LL(1) error trace

**Question:** Using the same table, trace `int + int $` and identify the error.

**Model answer:**

| Stack | Input | Action |
|---|---|---|
| `E$` | `int + int $` | Predict `E → int` |
| `int$` | `int + int $` | Match `int` |
| `$` | `+ int $` | **Error** — top is `$`, lookahead is `+` |

Explanation: `E → int` consumed the whole expression, but input remains. The grammar has no production for a top-level `+` without parentheses; a correct input would be `( int + int ) $`.

## Problem 13 — LL(1) table construction

**Question:** Construct the LL(1) parse table for the STMT/EXPR/TERM grammar of §6.7 and explain the entries for `STMT → EXPR ;`.

**Model answer:**

The table is in §6.7. `STMT → EXPR ;` can begin with any terminal that can begin `EXPR`. Since `FIRST(EXPR) = {zero?, not, ++, --, id, constant}`, production 3 appears in **six** columns. `if` and `while` columns get productions 1 and 2 respectively; `then`, `do`, `->`, and `;` are empty (errors) because no `STMT` production starts with them.

## Problem 14 — Language of a grammar

**Question:** What is `L(S → aSb | ε)`? Why can no DFA recognize it?

**Model answer:**

`L = {a^n b^n | n ≥ 0}`. A DFA has only finitely many states and no stack, so it cannot remember an unbounded count of a's to match the b's. A pushdown automaton can push `a`s and pop on `b`s. Hence the language is context-free but **not regular**.

---

# 10. Top 25 Mistakes That Cost Marks

1. Saying the **compiler** produces the executable (it produces assembly; the **linker** produces the executable).
2. Confusing **linker** and **loader**.
3. Calling `137` a token instead of a **lexeme/attribute**.
4. Forgetting that the scanner **removes comments and whitespace**.
5. Saying a finite automaton has a stack (that is a **PDA**).
6. Writing `a+` for "a or more" when you mean union — use `|` or state the notation.
7. Forgetting **star > concatenation > union**.
8. Omitting the **dead state** in a DFA.
9. Forgetting **ε-closure includes the state itself**.
10. Minimizing before removing **inaccessible states**.
11. Merging states that differ on **one** symbol.
12. Saying minimization changes the **language** (it does not).
13. In table-driven code, thinking `T` decides whether to consume (that is **`Advance`**).
14. Consuming the lookahead that ends a token (violates **longest match**).
15. Giving a GNFA with multiple accept states or an in-edge to the start.
16. Forgetting the new start/accept states in **state elimination**.
17. Mixing `→` (production) and `=>` (derivation step).
18. Saying `E → E` generates `ε` (it generates **∅**).
19. Forgetting the **base case** in a recursive CFG (`S → aSb` alone generates nothing).
20. Saying ambiguity is a property of the **language** (it is a property of the **grammar**).
21. Proving ambiguity with two derivations that produce the **same tree** — you need **two different parse trees** (e.g., two **leftmost** derivations).
22. Reversing **left recursion ↔ left associativity**.
23. Saying the dangling `else` matches the **first** if (it matches the **nearest unmatched** if).
24. Writing the LL(1) stack without the **`$`** marker or starting with the wrong symbol.
25. In an LL(1) trace, pushing the production's RHS in the **wrong order** (push in reverse so the leftmost symbol is on top).

---

# 11. Three-Day Revision Plan

## Day 1 — Scanner (Lectures 1–3)

- [ ] Read §1 and redraw the **language processing system** from memory.
- [ ] Recite the **compiler phases** and the front-end/back-end split.
- [ ] Do MCQ Q1–Q22.
- [ ] Write the tokens for `while (137 < i) ++i;` without looking.
- [ ] Re-derive `(aa)*(bb)*b` and `(0+1)*00(0+1)*`.
- [ ] Minimize Example 1 from scratch (write `P0…P3`).
- [ ] Build the table-driven code for the identifier DFA and trace `abc123+`.
- [ ] Do one full **RE → NFA → DFA → minimal DFA** for `(a|ε)b*`.

## Day 2 — Parser foundations (Lectures 4–5)

- [ ] Write the **CFG 4-tuple** and the BNF for arithmetic expressions.
- [ ] Derive `(number - number) * number` leftmost and rightmost.
- [ ] Draw the **parse tree** and the **AST** for `int * (int + int)`.
- [ ] Explain **left vs right recursion** and the two `A → Aα | β` identities.
- [ ] Show `int * int + int` is ambiguous with two trees.
- [ ] Rewrite the expression grammar with **precedence + left associativity**.
- [ ] Solve the **dangling else** with the matched/unmatched grammar.
- [ ] Do MCQ Q37–Q52.

## Day 3 — LL(1) + mock exam (Lecture 6 + review)

- [ ] State what **LL(1)** means and list the two parser actions.
- [ ] Reproduce the **parse table** for `E → int | (E Op E)`, `Op → + | *`.
- [ ] Trace `( int + ( int * int ) ) $` on paper, then check §6.4.
- [ ] Trace the two **error** examples.
- [ ] Build the **STMT/EXPR/TERM** table and explain the six 3s.
- [ ] Do the full **MCQ bank** under timed conditions (45 min).
- [ ] Do Problems 5, 6, 7, 9, 11, 12 from the written bank (90 min).
- [ ] Re-read the **Top 25 Mistakes** and the **Cram Sheet**.

## Last hour before the exam

> [!important] Rapid-fire checklist
> - [ ] P-C-A-L-L order
> - [ ] Lexeme / token / pattern
> - [ ] Token attributes
> - [ ] FA vs PDA vs TM
> - [ ] Regex precedence and `+` overload
> - [ ] Minimization partitions
> - [ ] `T`, `Advance`, `Accept`
> - [ ] Thompson / subset / state elimination
> - [ ] GNFA conditions
> - [ ] CFG 4-tuple, `A → Aα | β` = `βα*`
> - [ ] Parse tree vs AST
> - [ ] Ambiguity = grammar property
> - [ ] Precedence cascade + left recursion
> - [ ] Dangling else = nearest unmatched if
> - [ ] LL(1) = Left-to-right, Leftmost, 1 lookahead
> - [ ] Stack `S$`, predict vs match, empty cell = error

---

> [!success] Final note
> The midterm rewards **procedure**: show the partitions, the ε-closures, the stack, and the two parse trees. Even if the final answer is wrong, the steps earn most of the marks. Good luck!

```chatgpt-ui
{"suggest_automation": {"label": "Run the three-question warm-up checkpoint at the start of each study session; if you miss one, re-read that section before continuing."}}
```

