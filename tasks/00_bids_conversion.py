import model.pipeline_element as pe
import os
import shutil

import mne
from mne_bids import (
    BIDSPath,
    write_raw_bids,
    print_dir_tree,
)

class Bids_Conversion(pe.PipelineElement):
    def __init__(self):
        super().__init__("Preprocessing data")

    def process(self, data, config):

        # There is the root directory for where we will write our data.
        bids_root = os.path.join(config.data_dir, "ieeg_bids")

        # Delete to make sure it is empty
        if os.path.exists(bids_root):
            shutil.rmtree(bids_root)

        # Create a dictionary to store the BIDS paths
        bids_paths = {}

        for subj, subj_info in config.eeg_path.items():
            # check if config.subjects is empty (i.e. include all subjects) and 
            # if the current subject is in the list of subjects to include
            if config.subject and subj not in config.subjects:
                print(f"Skipping {subj}")
            else:
                bids_paths[subj] = {}
                for cond, cond_info in subj_info.items():
                    bids_paths[subj][cond] = {}
                    for task, task_info in cond_info.items():
                        run = 1
                        bids_paths[subj][cond][task] = []
                        for edf_file in config.eeg_path[subj][cond][task]:
                            bids_path = BIDSPath(
                                subject=subj, 
                                session=cond.replace("-",""), 
                                task=task, 
                                run=run, 
                                root=bids_root, 
                                acquisition='seeg', 
                                extension='.edf'
                            )
                            run += 1
                            bids_paths[subj][cond][task].append(bids_path)
                            raw = mne.io.read_raw_edf(config.data_dir + os.path.sep + edf_file)
                            write_raw_bids(
                                raw, 
                                bids_path, 
                                anonymize=dict(daysback=40000),
                                overwrite=True
                            )
                            print("Wrote bids", subj, cond, task, run, edf_file)

        # check 
        print_dir_tree(bids_root)

        return bids_paths