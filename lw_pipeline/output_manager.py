"""Output management system for pipeline steps."""

# Authors: The Lightweight Pipeline developers
# SPDX-License-Identifier: BSD-3-Clause

import json
import time
from datetime import datetime
from pathlib import Path


class OutputManager:
    """
    Manage output saving with consistent paths, metadata, and overwrite handling.

    This class provides a unified interface for saving various output types
    (figures, tables, MNE objects, etc.) with automatic:
    - Path generation (BIDS-compliant or custom)
    - Sidecar JSON creation with provenance metadata
    - Overwrite checking with multiple modes
    - Performance profiling (optional)
    - Step ID prefixing for output names

    Parameters
    ----------
    config : Config
        Configuration object containing output settings.
    step_id : str
        Short identifier for the pipeline step (e.g., "01", "02").
    step_description : str, optional
        Description of the pipeline step for metadata.

    Attributes
    ----------
    config : Config
        Configuration object.
    step_id : str
        Step identifier used for prefixing output names.
    step_description : str
        Step description for metadata.
    """

    def __init__(self, config, step_id, step_description=""):
        """Initialize the OutputManager."""
        self.config = config
        self.step_id = step_id
        self.step_description = step_description

    def _get_overwrite_mode(self):
        """Get the overwrite mode from config."""
        return getattr(self.config, "overwrite_mode", "never")

    def _should_overwrite(self, filepath):
        """
        Check if a file should be overwritten based on config.overwrite_mode.

        Parameters
        ----------
        filepath : str or Path
            Path to the file to check.

        Returns
        -------
        bool
            True if file should be overwritten, False otherwise.
        """
        filepath = Path(filepath)

        if not filepath.exists():
            return True

        mode = self._get_overwrite_mode()

        if mode == "always":
            return True
        elif mode == "never":
            print(
                f"⏩ File {filepath} already exists. "
                f"Skipping (overwrite_mode='never')."
            )
            return False
        elif mode == "ask":
            response = self.config.ask(
                f"File {filepath} exists. Overwrite? (y/n)", default="n"
            )
            return response.lower() in ["y", "yes"]
        elif mode == "ifnewer":
            # For ifnewer mode, we need a source file to compare
            # Return False by default - specific save methods can override
            print(
                f"⏩ File {filepath} already exists. "
                f"Skipping (overwrite_mode='ifnewer', no source to compare)."
            )
            return False
        else:
            print(f"⚠ Unknown overwrite_mode '{mode}', defaulting to 'never'.")
            return False

    def _should_overwrite_ifnewer(self, filepath, source_file):
        """
        Check if file should be overwritten based on modification time.

        Parameters
        ----------
        filepath : str or Path
            Path to the output file.
        source_file : str or Path
            Path to the source file to compare against.

        Returns
        -------
        bool
            True if source is newer than output or output doesn't exist.
        """
        filepath = Path(filepath)
        source_file = Path(source_file)

        if not filepath.exists():
            return True

        if not source_file.exists():
            print(f"⚠ Source file {source_file} does not exist. Cannot compare dates.")
            return False

        source_mtime = source_file.stat().st_mtime
        output_mtime = filepath.stat().st_mtime

        if source_mtime > output_mtime:
            return True
        else:
            print(f"⏩ File {filepath} is up to date. Skipping.")
            return False

    def _create_output_path(self, name, suffix=None, extension=None,
                           use_bids_structure=True, custom_dir=None,
                           **bids_params):
        """
        Create an output file path with step ID prefixing.

        Parameters
        ----------
        name : str
            Base name for the output (will be prefixed with step_id).
        suffix : str, optional
            BIDS suffix (e.g., "eeg", "plot", "table").
        extension : str, optional
            File extension (e.g., ".pdf", ".csv", ".png").
        use_bids_structure : bool, optional
            If True, use BIDS directory structure. Default is True.
        custom_dir : str or Path, optional
            Custom directory for output. If None, uses config.output_root or deriv_root.
        **bids_params : dict
            Additional BIDS parameters (subject, session, task, run, etc.).

        Returns
        -------
        Path
            Output file path.
        """
        # Prefix name with step ID if not already prefixed
        if not name.startswith(self.step_id):
            prefixed_name = f"{self.step_id}_{name}"
        else:
            prefixed_name = name

        # Determine base directory
        if custom_dir:
            base_dir = Path(custom_dir)
        else:
            base_dir = Path(
                getattr(self.config, "output_root", self.config.deriv_root)
            )

        if use_bids_structure:
            # Build BIDS-compliant path
            subject = bids_params.get("subject", None)
            session = bids_params.get("session", None)
            task = bids_params.get("task", None)
            run = bids_params.get("run", None)
            datatype = bids_params.get(
                "datatype", getattr(self.config, "bids_datatype", "eeg")
            )

            # Build path components
            path_parts = [base_dir]

            if subject:
                path_parts.append(f"sub-{subject}")
            if session:
                path_parts.append(f"ses-{session}")
            if datatype:
                path_parts.append(datatype)

            # Build filename
            filename_parts = []
            if subject:
                filename_parts.append(f"sub-{subject}")
            if session:
                filename_parts.append(f"ses-{session}")
            if task:
                filename_parts.append(f"task-{task}")
            if run:
                filename_parts.append(f"run-{run}")

            # Add description (prefixed name)
            filename_parts.append(f"desc-{prefixed_name}")

            if suffix:
                filename_parts.append(suffix)

            filename = "_".join(filename_parts)
            if extension:
                filename += extension
            
            path_parts.append(filename)
            output_path = Path(*path_parts)
        else:
            # Simple custom path
            filename = prefixed_name
            if suffix:
                filename += f"_{suffix}"
            if extension:
                filename += extension
            output_path = base_dir / filename

        return output_path

    def _create_sidecar_metadata(self, output_path, custom_metadata=None,
                                 timing_info=None, file_size=None):
        """
        Create sidecar JSON metadata.

        Parameters
        ----------
        output_path : str or Path
            Path to the output file.
        custom_metadata : dict, optional
            Custom metadata to merge into sidecar.
        timing_info : dict, optional
            Timing information (e.g., {'duration': 1.23, 'timestamp': '...'}).
        file_size : int, optional
            File size in bytes.

        Returns
        -------
        dict
            Metadata dictionary.
        """
        metadata = {
            "Pipeline": {
                "Version": self.config.get_version(),
                "Step": self.step_id,
                "StepDescription": self.step_description,
                "OutputFile": str(Path(output_path).name),
                "GeneratedAt": datetime.now().isoformat(),
            }
        }

        # Add profiling info if available
        if timing_info or file_size:
            metadata["Performance"] = {}
            if timing_info:
                metadata["Performance"].update(timing_info)
            if file_size:
                metadata["Performance"]["FileSizeBytes"] = file_size

        # Merge custom metadata
        if custom_metadata:
            metadata.update(custom_metadata)

        return metadata

    def _save_sidecar(self, output_path, metadata):
        """
        Save sidecar JSON file.

        Parameters
        ----------
        output_path : str or Path
            Path to the output file (sidecar will be saved alongside).
        metadata : dict
            Metadata to save in sidecar.
        """
        if not getattr(self.config, "sidecar_auto_generate", True):
            return

        output_path = Path(output_path)
        sidecar_path = output_path.with_suffix(output_path.suffix + ".json")

        # Ensure directory exists
        sidecar_path.parent.mkdir(parents=True, exist_ok=True)

        with open(sidecar_path, "w") as f:
            json.dump(metadata, f, indent=4)

        print(f"📝 Saved sidecar: {sidecar_path}")

    def save_generic(self, obj, name, save_func, suffix=None, extension=None,
                    use_bids_structure=True, custom_dir=None, metadata=None,
                    source_file=None, **kwargs):
        """
        Save any output type with consistent metadata and overwrite handling.

        Parameters
        ----------
        obj : object
            Object to save.
        name : str
            Output name (will be prefixed with step_id).
        save_func : callable
            Function to call for saving (e.g., fig.savefig, df.to_csv).
        suffix : str, optional
            BIDS suffix.
        extension : str, optional
            File extension.
        use_bids_structure : bool, optional
            Use BIDS directory structure. Default is True.
        custom_dir : str or Path, optional
            Custom output directory.
        metadata : dict, optional
            Custom metadata for sidecar.
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments passed to save_func and BIDS parameters.

        Returns
        -------
        Path
            Path to saved file.
        """
        # Separate BIDS parameters from save function kwargs
        bids_params = {
            k: v for k, v in kwargs.items()
            if k in ["subject", "session", "task", "run", "datatype"]
        }
        save_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in bids_params
        }

        # Create output path
        output_path = self._create_output_path(
            name, suffix=suffix, extension=extension,
            use_bids_structure=use_bids_structure,
            custom_dir=custom_dir, **bids_params
        )

        # Check overwrite
        if self._get_overwrite_mode() == "ifnewer" and source_file:
            should_save = self._should_overwrite_ifnewer(output_path, source_file)
        else:
            should_save = self._should_overwrite(output_path)

        if not should_save:
            return output_path

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Time the save operation if profiling is enabled
        timing_info = None
        if getattr(self.config, "output_profiling", False):
            start_time = time.time()

        # Save the object
        save_func(output_path, **save_kwargs)
        print(f"💾 Saved: {output_path}")

        # Collect profiling info
        if getattr(self.config, "output_profiling", False):
            duration = time.time() - start_time
            timing_info = {
                "Duration": f"{duration:.3f}s",
                "Timestamp": datetime.now().isoformat()
            }

        # Get file size
        file_size = output_path.stat().st_size if output_path.exists() else None

        # Create and save sidecar
        sidecar_metadata = self._create_sidecar_metadata(
            output_path, custom_metadata=metadata,
            timing_info=timing_info, file_size=file_size
        )
        self._save_sidecar(output_path, sidecar_metadata)

        return output_path

    def get_output_path(self, name, suffix=None, extension=None,
                       use_bids_structure=True, custom_dir=None, **bids_params):
        """
        Get output path without saving (useful for checking or manual saves).

        Parameters
        ----------
        name : str
            Output name (will be prefixed with step_id).
        suffix : str, optional
            BIDS suffix.
        extension : str, optional
            File extension.
        use_bids_structure : bool, optional
            Use BIDS directory structure. Default is True.
        custom_dir : str or Path, optional
            Custom output directory.
        **bids_params : dict
            BIDS parameters (subject, session, task, run, datatype).

        Returns
        -------
        Path
            Output file path.
        """
        return self._create_output_path(
            name, suffix=suffix, extension=extension,
            use_bids_structure=use_bids_structure,
            custom_dir=custom_dir, **bids_params
        )

    def save_figure(self, fig, name, format=None, suffix="plot", metadata=None,
                   source_file=None, **kwargs):
        """
        Save a matplotlib figure.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Figure to save.
        name : str
            Output name (will be prefixed with step_id).
        format : str, optional
            Figure format (e.g., "pdf", "png", "svg"). If None, detected from
            extension in kwargs or defaults to "pdf".
        suffix : str, optional
            BIDS suffix. Default is "plot".
        metadata : dict, optional
            Custom metadata for sidecar.
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments (BIDS params + savefig params like dpi, bbox_inches).

        Returns
        -------
        Path
            Path to saved figure.
        """
        # Determine extension
        if format:
            extension = f".{format}"
        else:
            extension = kwargs.pop("extension", ".pdf")

        # Create save function that calls fig.savefig
        def save_func(path, **fig_kwargs):
            fig.savefig(path, **fig_kwargs)

        return self.save_generic(
            fig, name, save_func, suffix=suffix, extension=extension,
            metadata=metadata, source_file=source_file, **kwargs
        )

    def save_dataframe(self, df, name, format="csv", suffix="table",
                      metadata=None, source_file=None, **kwargs):
        """
        Save a pandas DataFrame as CSV, TSV, or Excel.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame to save.
        name : str
            Output name (will be prefixed with step_id).
        format : str, optional
            Format: "csv", "tsv", or "xlsx". Default is "csv".
        suffix : str, optional
            BIDS suffix. Default is "table".
        metadata : dict, optional
            Custom metadata for sidecar.
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments (BIDS params + pandas to_csv/to_excel params).

        Returns
        -------
        Path
            Path to saved file.
        """
        def save_csv(p, **kw):
            df.to_csv(p, **kw)

        def save_tsv(p, **kw):
            df.to_csv(p, sep="\t", **kw)

        def save_xlsx(p, **kw):
            df.to_excel(p, **kw)

        format_map = {
            "csv": (".csv", save_csv),
            "tsv": (".tsv", save_tsv),
            "xlsx": (".xlsx", save_xlsx),
        }

        if format not in format_map:
            raise ValueError(
                f"Unsupported format '{format}'. "
                f"Supported: {list(format_map.keys())}"
            )

        extension, save_func = format_map[format]

        return self.save_generic(
            df, name, save_func, suffix=suffix, extension=extension,
            metadata=metadata, source_file=source_file, **kwargs
        )

    def save_mne_object(self, obj, name, suffix=None, metadata=None,
                       source_file=None, **kwargs):
        """
        Save an MNE object (Raw, Epochs, Evoked, etc.).

        Parameters
        ----------
        obj : mne.BaseRaw, mne.BaseEpochs, mne.Evoked, etc.
            MNE object to save.
        name : str
            Output name (will be prefixed with step_id).
        suffix : str, optional
            BIDS suffix (e.g., "eeg", "epochs"). If None, auto-detected.
        metadata : dict, optional
            Custom metadata for sidecar.
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments (BIDS params + MNE save params like overwrite).

        Returns
        -------
        Path
            Path to saved file.
        """
        # Detect object type and set defaults
        obj_type = type(obj).__name__

        if suffix is None:
            if "Raw" in obj_type:
                suffix = "eeg"
            elif "Epochs" in obj_type:
                suffix = "epo"
            elif "Evoked" in obj_type:
                suffix = "ave"
            else:
                suffix = "data"

        extension = ".fif"

        # Create save function based on object type
        def save_func(path, **mne_kwargs):
            # MNE objects have .save() method
            # Remove overwrite from kwargs since we handle it ourselves
            mne_kwargs.pop("overwrite", None)
            obj.save(path, overwrite=True, **mne_kwargs)

        return self.save_generic(
            obj, name, save_func, suffix=suffix, extension=extension,
            metadata=metadata, source_file=source_file, **kwargs
        )

    def save_numpy(self, arr, name, format="npy", suffix="array",
                  metadata=None, source_file=None, **kwargs):
        """
        Save a numpy array.

        Parameters
        ----------
        arr : numpy.ndarray
            Array to save.
        name : str
            Output name (will be prefixed with step_id).
        format : str, optional
            Format: "npy" (binary) or "txt" (text). Default is "npy".
        suffix : str, optional
            BIDS suffix. Default is "array".
        metadata : dict, optional
            Custom metadata for sidecar.
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments (BIDS params + numpy save params).

        Returns
        -------
        Path
            Path to saved file.
        """
        import numpy as np

        def save_npy(p, **kw):
            np.save(p, arr, **kw)

        def save_txt(p, **kw):
            np.savetxt(p, arr, **kw)

        if format == "npy":
            extension = ".npy"
            save_func = save_npy
        elif format == "txt":
            extension = ".txt"
            save_func = save_txt
        else:
            raise ValueError(
                f"Unsupported format '{format}'. Supported: ['npy', 'txt']"
            )

        return self.save_generic(
            arr, name, save_func, suffix=suffix, extension=extension,
            metadata=metadata, source_file=source_file, **kwargs
        )

    def save_json(self, data, name, suffix="data", metadata=None,
                 source_file=None, **kwargs):
        """
        Save data as JSON file.

        Parameters
        ----------
        data : dict or list
            Data to save as JSON.
        name : str
            Output name (will be prefixed with step_id).
        suffix : str, optional
            BIDS suffix. Default is "data".
        metadata : dict, optional
            Custom metadata for sidecar (note: data itself is JSON, sidecar is
            additional metadata).
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments (BIDS params + json.dump params like indent).

        Returns
        -------
        Path
            Path to saved file.
        """
        def save_func(path, **json_kwargs):
            # Set default indent if not specified
            if "indent" not in json_kwargs:
                json_kwargs["indent"] = 4
            with open(path, "w") as f:
                json.dump(data, f, **json_kwargs)

        return self.save_generic(
            data, name, save_func, suffix=suffix, extension=".json",
            metadata=metadata, source_file=source_file, **kwargs
        )

    def save_text(self, text, name, suffix="log", metadata=None,
                 source_file=None, **kwargs):
        """
        Save text content to a file.

        Parameters
        ----------
        text : str
            Text content to save.
        name : str
            Output name (will be prefixed with step_id).
        suffix : str, optional
            BIDS suffix. Default is "log".
        metadata : dict, optional
            Custom metadata for sidecar.
        source_file : str or Path, optional
            Source file for ifnewer comparison.
        **kwargs : dict
            Additional arguments (BIDS params + extension).

        Returns
        -------
        Path
            Path to saved file.
        """
        extension = kwargs.pop("extension", ".txt")

        def save_func(path, **write_kwargs):
            encoding = write_kwargs.pop("encoding", "utf-8")
            with open(path, "w", encoding=encoding) as f:
                f.write(text)

        return self.save_generic(
            text, name, save_func, suffix=suffix, extension=extension,
            metadata=metadata, source_file=source_file, **kwargs
        )
