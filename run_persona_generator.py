#!/usr/bin/env python3
"""Run script with proper environment setup."""

import os
import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_persona_generator.py <reddit_user_url>")
        print(
            "Example: python run_persona_generator.py https://www.reddit.com/user/kojied/"
        )
        return 1

    reddit_url = sys.argv[1]

    # Import and run the main function
    try:
        from reddit_persona_generator import main as generate_main

        # Temporarily replace sys.argv to pass the URL
        original_argv = sys.argv
        sys.argv = ['reddit_persona_generator.py', reddit_url]

        generate_main()

        # Restore original argv
        sys.argv = original_argv

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
