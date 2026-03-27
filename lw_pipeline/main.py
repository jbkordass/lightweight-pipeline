"""Command-line interface for lw_pipeline."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import logging
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
    """
    outputs = [o.strip() for o in outputs_str.split(",")]

    has_step_scope = any(":" in o for o in outputs)

    if has_step_scope:
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
                if "*" not in result:
                    result["*"] = []
                result["*"].append(output)
        return result

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
    logger = logging.getLogger(__name__)
    if options.ignore_questions:
        config.auto_response = "default"

    if options.outputs:
        config.outputs_to_generate = _parse_outputs_argument(options.outputs)

    if options.skip_outputs:
        config.outputs_to_skip = _parse_outputs_argument(options.skip_outputs)

    if options.list_outputs:
        logger.info("Registered outputs")
        list_all_outputs(config)
    elif options.run:
        step_files = find_all_step_files(config.steps_dir)
        if not options.steps:
            logger.info("Running entire pipeline")
        else:
            step_files_specified = []
            for step_identifier in options.steps:
                step = [
                    step_file
                    for step_file in step_files
                    if step_file.startswith(step_identifier)
                ]
                if not step:
                    logger.error("Step file '%s' not found.", step_identifier)
                    sys.exit(1)
                if len(step) > 1:
                    logger.error("Step file '%s' is ambiguous.", step_identifier)
                    sys.exit(1)
                step_files_specified.append(step[0])
            step_files = step_files_specified
            logger.info("Running steps: %s", ", ".join(step_files))

        step_classes = find_all_step_classes(step_files, config)
        pipeline = Pipeline(step_classes)
        pipeline.run()
    elif options.list:
        step_names = "\n".join(find_all_step_files(config.steps_dir))
        logger.info("Steps:\n%s", step_names)
    elif options.report or options.store_report or options.full_report:
        report_scope = "full" if options.full_report else "limited"
        logger.info("Generating %s report", report_scope)
        generate_report(config, options.store_report, options.full_report)
    else:
        parser.print_help()
