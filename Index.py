# Zerofiles - Index.py
# Recreated json without using import json
# Will have extras features like comments!!!
# Removing strict syntaxis
# File type will be .zr
# Also adding attributes like date and etc

import time
import os
import sys
import zerofiles

def Parse():
    print("=" * 60)
    print(" Z E R O F I L E S   P A R S E R   &   S E R I A L I Z E R ")
    print("=" * 60)

    # 1. Load the example file
    filename = "example.zr"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return

    print(f"\n[1] Reading and parsing file: '{filename}'...")
    try:
        start_time = time.perf_counter()
        zf = zerofiles.load(filename)
        duration = (time.perf_counter() - start_time) * 1000
        print(f"--> Parsing completed in {duration:.3f} ms.")
    except Exception as e:
        print(f"--> Parse failed: {e}")
        return

    # 2. Display metadata
    print("\n--- EXTRACTED METADATA ---")
    if zf.metadata:
        for k, v in zf.metadata.items():
            print(f"  @{k}: {v}")
    else:
        print("  (No metadata found)")

    # 3. Display data structure
    print("\n--- PARSED PYTHON DATA ---")
    print(f"Type: {type(zf.data)}")
    print(f"Data: {zf.data}")

    # 4. Demonstrate modification
    print("\n[2] Modifying parsed data...")
    print("Adding dynamic items to 'features' list...")
    if "features" in zf:
        zf["features"].append("Dynamically parsed & modified!")
    print("Adding metadata field 'modified_by'...")
    zf.metadata["modified_by"] = "Antigravity AI Agent"

    # 5. Serialize and write back
    output_filename = "example_output.zr"
    print(f"\n[3] Serializing and saving back to '{output_filename}'...")

    try:
        start_time = time.perf_counter()
        # Serialize with indentation
        zerofiles.dump(zf, output_filename, indent=4)
        duration = (time.perf_counter() - start_time) * 1000
        print(f"--> Serialization and write completed in {duration:.3f} ms.")
        print("Note: The date header attribute was automatically updated.")
    except Exception as e:
        print(f"--> Serialization failed: {e}")
        return

    # 6. Verify result
    print(f"\n[4] Re-verifying output by parsing '{output_filename}'...")
    try:
        zf_verified = zerofiles.load(output_filename)
        print("--> Re-parsed successfully!")
        print("\n--- UPDATED METADATA ---")
        for k, v in zf_verified.metadata.items():
            print(f"  @{k}: {v}")
        print("\n--- UPDATED PYTHON DATA ---")
        print(f"Data: {zf_verified.data}")
    except Exception as e:
        print(f"--> Re-parse verification failed: {e}")

    print("\n" + "=" * 60)
    print(" SUCCESS: Zerofiles round-trip complete without 'import json'!")
    print("=" * 60)

def CLI():
    if len(sys.argv) < 2:
        Parse()
        return

    cmd = sys.argv[1].lower()
    if cmd == "format":
        if len(sys.argv) < 3:
            print("Usage: python Index.py format <filename.zr>")
            return
        filename = sys.argv[2]
        if not os.path.exists(filename):
            print(f"Error: {filename} not found.")
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            formatted = zerofiles.format_zr(content)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted)
            print(f"Successfully formatted and wrote back to {filename}")
        except Exception as e:
            print(f"Format error: {e}")

    elif cmd == "lint":
        if len(sys.argv) < 3:
            print("Usage: python Index.py lint <filename.zr>")
            return
        filename = sys.argv[2]
        if not os.path.exists(filename):
            print(f"Error: {filename} not found.")
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            issues = zerofiles.lint_zr(content)
            if not issues:
                print(f"Clean! No issues found in {filename}.")
            else:
                print(f"Found {len(issues)} issue(s) in {filename}:")
                for issue in issues:
                    itype = issue['type'].upper()
                    line = issue.get('line')
                    col = issue.get('column')
                    loc = f"Line {line}" if line is not None else ""
                    if col is not None:
                        loc += f", Col {col}"
                    loc_str = f" [{loc}]" if loc else ""
                    print(f"  * {itype}{loc_str}: {issue['message']}")
        except Exception as e:
            print(f"Linting failed: {e}")
    else:
        print(f"Unknown command: {cmd}")
        print("Supported commands: format, lint")

if __name__ == "__main__":
    CLI()
