import pandas as pd
import matplotlib.pyplot as plt
import os
from pyomo.environ import *

# Function to handle the logic for "with load control"
def with_load_control():
    exec(open("wlc.py").read())

# Function to handle the logic for "no load control"
def no_load_control():
    exec(open("nlc.py").read())

# Main function to execute the appropriate scenario
def main():
    # Check the current working directory
    print("Current Working Directory:", os.getcwd())

    # List files in the current working directory
    print("Files in the current working directory:", os.listdir(os.getcwd()))

    # Simulate the user choice for load control or no load control
    n2 = int(input("Enter 1 for load control or 2 for no load control: "))

    # Execute the appropriate function based on user choice
    if n2 == 1:
        with_load_control()
    else:
        no_load_control()

# Run the main function
if __name__ == "__main__":
    main()
