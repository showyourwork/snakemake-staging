from snakemake_staging import stages
from snakemake_staging.utils import rule_name

_restore = stages.get_stages_to_restore(config)
for stage, files in stages.STAGES.items():
    if name in _restore:
        rule:
            name:
                rule_name("stages", "restore", stage)
            message:
                f"Restoring {len(files)} files from snapshot for stage '{stage}'"
            output:
                files
            run:
                stages.restore_stage(config, stage)

    else:
        rule:
            name:
                rule_name("stages", "snapshot", stage)
            message:
                f"Snapshotting {len(files)} files for stage '{stage}'"
            input:
                files
            output:
                touch(f"stage_{stage}.snapshot")
            run:
                stages.snapshot_stage(config, stage)
