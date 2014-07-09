"""Script to run the webapp.
"""
import sys

def main():
    if "--test" in sys.argv:
        from broadgauge.tests import main
        main()  
    else:
        from broadgauge.main import main
        main()

if __name__ == "__main__":
    main()
