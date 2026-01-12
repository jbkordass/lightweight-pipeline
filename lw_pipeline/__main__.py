"""Command-line interface for the pipeline."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import sys

from lw_pipeline.config import Config
from lw_pipeline.discovery import (
    find_all_step_classes,
    find_all_step_files,
    list_all_outputs,
)
from lw_pipeline.helper.report import generate_report
from lw_pipeline.pipeline import Pipeline


def _parse_outputs_argument(outputs_str):
    """
    Parse the --outputs command line argument.

    Parameters
    ----------
    outputs_str : str
        Comma-separated output specifications, optionally with step scoping.

    Returns
    -------
    dict or list
        If step-scoped (e.g., "01:plot,02:stats"), returns dict mapping
        step IDs to lists of patterns. Otherwise, returns list of patterns.

    Examples
    --------
    >>> _parse_outputs_argument("plot,stats")
    ['plot', 'stats']
    >>> _parse_outputs_argument("01:plot,01:stats,02:*")
    {'01': ['plot', 'stats'], '02': ['*']}
    >>> _parse_outputs_argument("*:plot")
    {'*': ['plot']}
    """
    outputs = [o.strip() for o in outputs_str.split(",")]

    # Check if any output uses step-scoped syntax
    has_step_scope = any(":" in o for o in outputs)

    if has_step_scope:
        # Parse into dict mapping step_id -> [patterns]
        result = {}
        for output in outputs:
            if ":" in output:
                step_id, pattern = output.split(":", 1)
                step_id = step_id.strip()
                pattern = pattern.strip()

                if step_id not in result:
                    result[step_id] = []
                result[step_id].append(pattern)
            else:
                # No step scope specified, treat as global wildcard
                if "*" not in result:
                    result["*"] = []
                result["*"].append(output)
        return result
    else:
        # Return simple list of patterns
        return outputs


def main():
    """Run pipeline from command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version="0.1")

    parser.add_argument("-r", "--run", action="store_true", help="Run the pipeline")

    parser.add_argument(
        "steps",
        metavar="TT",
        type=str,
        nargs="*",
        help="List of steps to run, separated by commas (only necessary to "
        "specify 00-99)",
    )

    parser.add_argument("-c", "--config", help="Path to the configuration file")

    parser.add_argument(
        "-l", "--list", action="store_true", help="List all steps in the step directory"
    )

    parser.add_argument(
        "--ignore-questions",
        action="store_true",
        help="Ignore questions, i.e. always respond with default answer to a question.",
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a report of the pipeline's derivatives.",
    )

    parser.add_argument(
        "--store-report",
        action="store_true",
        help="Store the report tables in .tsv files in the derivatives dir "
        "(pipeline_report_bids_dir.tsv, pipeline_report_deriv_dir.tsv).",
    )

    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate a full report (do not limit to subj, ses, task specification in"
        " the config) of the pipeline's derivatives.",
    )

    parser.add_argument(
        "--outputs",
        type=str,
        help="Comma-separated list of outputs to generate. "
        "Supports wildcards (e.g., 'plot*') and step-scoped syntax "
        "(e.g., '01:plot,02:*'). If not specified, all enabled outputs are generated.",
    )

    parser.add_argument(
        "--skip-outputs",
        type=str,
        help="Comma-separated list of outputs to skip. "
        "Supports wildcards (e.g., 'plot*') and step-scoped syntax "
        "(e.g., '01:plot,02:*'). Takes precedence over --outputs.",
    )

    parser.add_argument(
        "--list-outputs",
        action="store_true",
        help="List all registered outputs in the pipeline steps.",
    )

    options = parser.parse_args()

    config = Config(options.config, verbose=True)
    if options.ignore_questions:
        config.auto_response = "default"

    # Parse --outputs argument
    if options.outputs:
        config.outputs_to_generate = _parse_outputs_argument(options.outputs)

    # Parse --skip-outputs argument
    if options.skip_outputs:
        config.outputs_to_skip = _parse_outputs_argument(options.skip_outputs)

    if options.list_outputs:
        print("Registered Outputs:".center(80, "-"))
        list_all_outputs(config)
    elif options.run:
        # retrieve all steps script file names
        step_files = find_all_step_files(config.steps_dir)
        if not options.steps:
            print("Running entire pipeline")
        else:
            # filter step files based on steps specified in the command line argument
            step_files_specified = []
            for step_identifier in options.steps:
                step = [
                    step_file
                    for step_file in step_files
                    if step_file.startswith(step_identifier)
                ]
                if not step:
                    print(f"Error: Step file '{step_identifier}' not found.")
                    sys.exit(1)
                if len(step) > 1:
                    print(f"Error: Step file '{step_identifier}' is ambiguous.")
                    sys.exit(1)
                step_files_specified.append(step[0])
            step_files = step_files_specified
            print("Running the steps:", ", ".join(step_files))

        # Load step classes from files
        step_classes = find_all_step_classes(step_files, config)
        pipeline = Pipeline(step_classes)

        # Run the pipeline
        pipeline.run()
    elif options.list:
        print("Steps:".center(80, "-"))
        print("\n".join(find_all_step_files(config.steps_dir)))
    elif options.report or options.store_report or options.full_report:
        print(f"Generating {'limited ' if not options.full_report else 'full '}report")
        generate_report(config, options.store_report, options.full_report)
    else:
        # if no arguments implying actions are given, print help
        parser.print_help()


if __name__ == "__main__":
    main()
