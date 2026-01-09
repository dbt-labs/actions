#!/usr/bin/env python3
"""
Filter release branches action for GitHub workflows.

This action filters release branches according to dynamic selection rules:
1. Always include baseline branch.
2. Include the last 2 minor versions from existing branches
3. Optionally include main branch
"""

import json
import re
import os
import sys
import ast
from typing import List, Tuple


BASELINE = "1.7.latest"


def set_output(name, value):
    """Write output to GITHUB_OUTPUT file."""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"{name}={value}\n")


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
        except ValueError:
            print(f"::debug::Skipping invalid branch format: {branch}")
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
    """Main entry point for the action."""
    branches_input = os.environ.get('INPUT_BRANCHES', '[]')
    include_main = os.environ.get('INPUT_INCLUDE_MAIN', 'true').lower() == 'true'
    
    print(f"::debug::Raw branches input: {branches_input}")
    print(f"::debug::Include main: {include_main}")
    
    # Parse input - handle both JSON and Python list syntax
    try:
        branches = ast.literal_eval(branches_input)
        if not isinstance(branches, list):
            raise ValueError("BRANCHES must be a list")
    except (ValueError, SyntaxError) as e:
        print(f"::error::Invalid format in branches input: {e}")
        print(f"::error::Branches value: {branches_input}")
        sys.exit(1)
    
    print(f"::group::Filter Release Branches")
    print(f"Fetched branches: {branches}")
    
    # Apply filtering
    filtered = filter_branches(branches)
    print(f"Filtered branches: {filtered}")
    
    # Add main if requested
    if include_main and 'main' not in filtered:
        filtered.append('main')
        print(f"Added 'main' to branch list")
    
    print(f"Final branches to test: {filtered}")
    print(f"::endgroup::")
    
    # Output as JSON for matrix strategy
    output_json = json.dumps(filtered)
    set_output("filtered-branches", output_json)
    
    print(f"::notice::Filtered branches: {output_json}")


if __name__ == "__main__":
    main()
