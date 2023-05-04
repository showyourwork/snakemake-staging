from pathlib import Path
from snakemake_staging import stages, utils

_restore = stages.get_stages_to_restore(config)
for name, stage in stages.STAGES.items():
    staging_dir = utils.working_directory(
        "staging", "stages", name, config=config
    )

    # Rules for restoring or snapshotting the staging directory based on the
    # restore configuration 
    if name in _restore:
        rule:
            name:
                utils.rule_name("restore", name)
            message:
                f"Restoring staging directory for '{name}'"
            output:
                [staging_dir / f for f in stage.files.keys()]
            run:
                stage.restore(staging_dir)

                # We check to make sure that all the files were restored
                for file in output:
                    if not file.exists():
                        raise RuntimeError(
                            f"File '{file}' was not sucessfully restored by "
                            f"stage '{name}'"
                        )

    else:
        rule:
            name:
                utils.rule_name("snapshot", name)
            message:
                f"Snapshotting stage '{name}'"
            input:
                [staging_dir / f for f in stage.files.keys()]
            output:
                touch(staging_dir.parent / f"{name}.snapshot")
            run:
                stage.snapshot(staging_dir)

    # Rules for copying files to and from the staging directory based on the
    # restore configuration
    for staged_filename, filename in stage.files.items():
        if name in _restore:
            rule:
                name:
                    utils.rule_name("restore", name, "copy", path=filename)
                message:
                    f"Copying file '{filename}' from stage '{name}'"
                input:
                    staging_dir / staged_filename
                output:
                    filename
                run:
                    utils.copy_file_or_directory(input[0], output[0])

        else:
            rule:
                name:
                    utils.rule_name("snapshot", name, "copy", path=filename)
                message:
                    f"Copying file '{filename}' to stage '{name}'"
                input:
                    filename
                output:
                    staging_dir / staged_filename
                run:
                    utils.copy_file_or_directory(input[0], output[0])
