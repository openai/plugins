"""Package marker for earnings-deep-dive script modules."""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Package marker. Use run_plan.py, validate_plan.py, or verify_tearsheet.py for CLI workflows."
    )
    parser.parse_args()
    print("This is a package marker. Use a concrete earnings-deep-dive script for execution.")
