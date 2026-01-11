"""Example step demonstrating output management features."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pandas as pd

from lw_pipeline import Pipeline_Step, register_output


class Analysis(Pipeline_Step):
    """
    Example analysis step demonstrating output management.

    This step shows how to:
    - Register multiple outputs with @register_output
    - Use should_generate_output() for conditional execution
    - Save different output types (figures, tables, arrays)
    - Customize output metadata
    - Handle different overwrite modes
    """

    def __init__(self, config):
        """Initialize the Analysis step."""
        super().__init__(
            "Demonstrate output management with various output types",
            config,
        )

    def step(self, data):
        """
        Execute the analysis step.

        This method generates various outputs to demonstrate the
        output management system.

        Parameters
        ----------
        data : object
            Input data (not used in this example).

        Returns
        -------
        dict
            Dictionary with analysis results.
        """
        print("Generating outputs based on configuration...")

        # Generate synthetic data for demonstration
        self.generate_data_table()
        self.generate_summary_plot()
        self.generate_detailed_plot()
        self.generate_statistics()
        self.generate_numpy_array()

        return {"status": "completed", "step": "00_analysis"}

    @register_output(
        "data_table",
        "Raw data table",
        enabled_by_default=True,
        check_exists=True,
        extension=".csv",
        suffix="table"
    )
    def generate_data_table(self):
        """Generate and save a data table."""
        print("  ✓ Generating data_table...")

        # Create synthetic data
        data = {
            "Subject": ["01", "02", "01", "02"],
            "Session": ["01", "01", "02", "02"],
            "Value": np.random.randn(4),
            "Accuracy": np.random.rand(4),
        }
        df = pd.DataFrame(data)

        # Save as CSV - extension and suffix from decorator defaults
        self.output_manager.save_dataframe(
            df,
            name="raw_data",
            format="csv",
            metadata={
                "Description": "Synthetic data for demonstration",
                "Units": {"Value": "arbitrary", "Accuracy": "proportion"},
            },
            use_bids_structure=False,
        )

        # Also save as TSV for demonstration
        self.output_manager.save_dataframe(
            df,
            name="raw_data",
            format="tsv",
            suffix="table",
            use_bids_structure=False,
        )

    @register_output(
        "summary_plot",
        "Summary plot",
        enabled_by_default=True,
        check_exists=True,
        extension=".png",
        suffix="summary"
    )
    def generate_summary_plot(self):
        """Generate and save a summary plot."""
        print("  ✓ Generating summary_plot...")

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("    ⚠ matplotlib not installed, skipping plot")
            return

        # Create a simple plot
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        ax.set_xlabel("Time")
        ax.set_ylabel("Amplitude")
        ax.set_title("Summary Plot")
        ax.grid(True)

        # Save - extension and suffix from decorator defaults
        self.output_manager.save_figure(
            fig,
            name="summary",
            dpi=150,
            bbox_inches="tight",
        )

        # Also save as PNG
        self.output_manager.save_figure(
            fig,
            name="summary",
            format="png",
            suffix="plot",
            use_bids_structure=False,
            dpi=150,
        )

        plt.close(fig)

    @register_output(
        "detailed_plot",
        "Detailed analysis plot (expensive)",
        enabled_by_default=False,
        check_exists=True,
        extension=".png",
        suffix="detailed"
    )
    def generate_detailed_plot(self):
        """Generate a detailed plot (disabled by default due to cost)."""
        print("  ✓ Generating detailed_plot (expensive operation)...")

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("    ⚠ matplotlib not installed, skipping plot")
            return

        # Simulate expensive computation
        import time
        time.sleep(0.1)  # Simulate computation time

        # Create a more complex plot
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        for i, ax in enumerate(axes.flat):
            x = np.linspace(0, 10, 1000)
            y = np.sin((i + 1) * x) * np.exp(-x / 10)
            ax.plot(x, y)
            ax.set_title(f"Component {i+1}")
            ax.grid(True)

        fig.suptitle("Detailed Analysis")
        fig.tight_layout()

        # Save with metadata
        self.output_manager.save_figure(
            fig,
            name="detailed_analysis",
            format="pdf",
            suffix="plot",
            metadata={
                "PlotType": "Detailed",
                "Description": "Comprehensive analysis with all components",
                "ComputationalCost": "High",
            },
            use_bids_structure=False,
        )

        plt.close(fig)

    @register_output("statistics", "Statistical summary", enabled_by_default=True)
    def generate_statistics(self):
        """Generate and save statistical summary."""
        if not self.should_generate_output("statistics"):
            print("  ⊗ Skipping statistics (not requested)")
            return

        print("  ✓ Generating statistics...")

        # Create synthetic statistics
        stats = {
            "mean": np.random.randn(),
            "std": np.random.rand(),
            "n_samples": 100,
            "confidence_interval": [np.random.randn(), np.random.randn()],
        }

        # Save as JSON
        self.output_manager.save_json(
            stats,
            name="summary_stats",
            suffix="stats",
            metadata={
                "Description": "Summary statistics from analysis",
                "Method": "Synthetic generation for demonstration",
            },
            use_bids_structure=False,
        )

    @register_output("numpy_array", "Processed numpy array", enabled_by_default=False)
    def generate_numpy_array(self):
        """Generate and save a numpy array."""
        if not self.should_generate_output("numpy_array"):
            print("  ⊗ Skipping numpy_array (not requested)")
            return

        print("  ✓ Generating numpy_array...")

        # Create synthetic array
        arr = np.random.randn(100, 50)

        # Save as binary numpy format
        self.output_manager.save_numpy(
            arr,
            name="processed_data",
            format="npy",
            suffix="array",
            metadata={
                "Description": "Processed data array",
                "Shape": str(arr.shape),
                "Dtype": str(arr.dtype),
            },
            use_bids_structure=False,
        )
