# run_pyreverse.py
from pylint.pyreverse import main

if __name__ == '__main__':
    # Define the arguments as if they were passed from the command line.
    args = ['-o', 'png', '-p', 'CovoiUniv', '.']
    # Run Pyreverse with these arguments.
    main.Run(args)