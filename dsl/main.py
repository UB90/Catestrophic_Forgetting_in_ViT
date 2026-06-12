from parser import PreprocessingParser
from executor import PreprocessingTransformer, PreprocessingExecutor

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py script.imgprep")
        return

    with open(sys.argv[1], 'r') as f:
        script = f.read()

    parser = PreprocessingParser()
    tree = parser.parse(script)

    transformer = PreprocessingTransformer()
    actions = transformer.transform(tree)

    executor = PreprocessingExecutor(actions)
    executor.run()

if __name__ == "__main__":
    main()