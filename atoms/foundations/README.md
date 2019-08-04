# Foundational Concepts in Programming

This atom contains the introductory materials to take geography students who have never programmed before from the 'hello world' level through to their first function. We deliberately ignore some of the subtleties of Python (classes, inheritance, etc.) in favour of getting students going as quickly as possible.

## Data Sets

Examples in this atom make use of the following data sets:
1. [UK_Major_Metro_Areas.csv](./data/UK_Major_Metro_Areas.csv) (Derived from Wikipedia data) -- this data set contains one header row and ten observations; it is intended to be easy to read for students so that they can understand what is going on when the read in the file. The file is provided by default with a Git checkout, and the permanent remote URL is: [https://github.com/pysal/geopyter/tree/master/atoms/foundations/data/UK_Metro_Areas.csv](https://github.com/pysal/geopyter/tree/master/atoms/foundations/data/UK_Metro_Areas.csv)
2. [UK_Metro_Areas.csv](./data/UK_Metro_Areas.csv) (Derived from Wikipedia data) -- this data set contains one header row and 73 observations; it is intended to demonstrate the value of computers in parsing data sets that do _not_ scan easily. The file is provided by default with a Git checkout, and the permanent remote URL is:  [https://github.com/pysal/geopyter/tree/master/atoms/foundations/data/UK_Metro_Areas.csv](https://github.com/pysal/geopyter/tree/master/atoms/foundations/data/UK_Metro_Areas.csv)
3. US Regional Income Data: this can be found in the `pysal.examples` directory under  `us_income/usjoin.csv`. 

Since the third data set is provided by default with PySAL it does not need to be downloaded from a remote URL or checked out of Git. You access this file using the following code:
```python
import os
import pysal as ps
f = ps.open(os.path.join(ps.examples.example_dir, 'us_income/usjoin.csv'))
```

## Sequencing

You are always free to import as much or as little of the atom as you need, but the intended sequence for the materials is:

- [Why Learn to Code?](Why_Code.ipynb)
- [Programming and Geography](Programming_and_Geography.ipynb)
- [Learning a (New) Language](Learning_a_Language.ipynb)
- [Programming in Python](Programming_in_Python.ipynb)
- [A Brief Note about Jupyter](Jupyter.ipynb)
- [Thinking Like a Computer](Getting_Started.ipynb)
- [The Basics](Basics.ipynb)
- [Dealing with Errors & Debugging](Debugging.ipynb)
- [Conditions](Conditions.ipynb) 
- [Lists](Lists.ipynb) 
- [Dictionaries](Dictionaries.ipynb) 
- [Iteration](Iteration.ipynb) 
- [Functions](Functions.ipynb) 

