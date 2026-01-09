#!/usr/bin/env python3
"""
Branch filtering logic for release-branch-tests workflow.

This script filters release branches according to dynamic selection rules:
1. Always include 1.7.latest (baseline)
2. Include the last 2 minor versions from existing branches
3. Includes main branch if `INCLUDE_MAIN` environment variable is true
"""

import json
import re
import os
import sys
import ast
from typing import List, Tuple


BASELINE = "1.7.latest"


def parse_version(branch: str) -> Tuple[int, int]:
    """
    Extract version numbers from branch name.
    
    Args:
        branch: Branch name in format "X.Y.latest"
    
    Returns:
        Tuple of (major, minor) version numbers
    
    Raises:
        ValueError: If branch format is invalid
    """
    match = re.match(r'^(\d+)\.(\d+)\.latest$', branch)
    if not match:
        raise ValueError(f"Invalid branch format: {branch}")
    return (int(match.group(1)), int(match.group(2)))


def filter_branches(branches: List[str]) -> List[str]:
    """
    Filter branches according to the dynamic selection rules.
    
    Rules:
    1. Always include baseline branch.
    2. Include the last 2 minor versions from existing branches
    3. Sort versions numerically
    
    Args:
        branches: List of branch names in format "X.Y.latest"
    
    Returns:
        Filtered list of branches to test, sorted by version
    """
    if not branches:
        return [BASELINE]
    
    version_map = {}
    for branch in branches:
        try:
            version = parse_version(branch)
            version_map[version] = branch
        except ValueError as e:
            print(f"Warning: Skipping invalid branch format: {branch}", file=sys.stderr)
            continue
    
    if not version_map:
        return [BASELINE]
    
    sorted_versions = sorted(version_map.keys())
    
    last_two = sorted_versions[-2:] if len(sorted_versions) >= 2 else sorted_versions
    
    baseline_version = parse_version(BASELINE)
    result_list = []
    
    if baseline_version not in last_two:
        result_list.append(BASELINE)
    
    result_list.extend(version_map[version] for version in last_two)
    
    return result_list

def main():
    """
    Reads branches from environment variable BRANCHES (JSON array),
    filters them, optionally adds 'main' branch, and outputs to GITHUB_OUTPUT.
    
    Environment variables:
    - BRANCHES: JSON array of branch names
    - INCLUDE_MAIN: 'true' or 'false' (default: 'true')
    """

    branches_json = os.environ.get('BRANCHES', '[]')
    include_main = os.environ.get('INCLUDE_MAIN', 'true').lower() == 'true'
    
    # We use ast.literal_eval instead of json.loads to handle inputs like "['1.7.latest']" where the list element contain single quote which doesn't follow JSON spec. 
    try:
        branches = ast.literal_eval(branches_json)
        if not isinstance(branches, list):
            raise ValueError("BRANCHES must be a list")
    except (ValueError, SyntaxError) as e:
        print(f"Error: Invalid format in BRANCHES environment variable: {e}", file=sys.stderr)
        print(f"BRANCHES value: {branches_json}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Fetched branches: {branches}")
    print(f"Include main: {include_main}")
    
    filtered = filter_branches(branches)
    
    print(f"Filtered branches: {filtered}")
    
    if include_main and 'main' not in filtered:
        filtered.append('main')
        print(f"Added 'main' to branch list")
    
    print(f"Final branches to test: {filtered}")

    output_formatted = json.dumps(filtered) 
    
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"full_branch_list={output_formatted}\n")
        print(f"Written to GITHUB_OUTPUT: {github_output}")
    else:
        # For local debugging, print to stdout
        print(f"\nOutput:")
        print(f"full_branch_list={output_formatted}")


if __name__ == "__main__":
    main()
