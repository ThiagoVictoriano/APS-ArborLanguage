# Arbor Language Test Files

This directory contains test files for the Arbor programming language. Each file tests different aspects of the language.

## Test Files

1. `01_basic_arithmetic.arbor`
   - Tests basic arithmetic operations (+, -, *, /)
   - Tests operator precedence
   - Tests expression evaluation

2. `02_conditionals.arbor`
   - Tests if statements (branch/then)
   - Tests if-else statements
   - Tests all comparison operators (>, <, =, <=, >=, !=)
   - Tests nested conditionals

3. `03_loops.arbor`
   - Tests while loops (grow while)
   - Tests list iteration (grow in)
   - Tests nested loops
   - Tests loop control with counters

4. `04_lists_and_strings.arbor`
   - Tests list creation and manipulation
   - Tests string literals
   - Tests mixed data type lists
   - Tests list iteration with different types

5. `05_variable_scoping.arbor`
   - Tests variable declaration and assignment
   - Tests block scope in conditionals
   - Tests block scope in loops
   - Tests nested scopes
   - Tests variable visibility rules

## Running Tests

### Running a Single Test

To run a single test file:

```bash
python main.py tests/filename.arbor
```

### Running All Tests

To run all test files at once, use the PowerShell script:

```powershell
cd tests
.\run_all_tests.ps1
```

This will execute all `.arbor` files in the tests directory and show the results of each test.

Each test file includes comments explaining the expected output. 