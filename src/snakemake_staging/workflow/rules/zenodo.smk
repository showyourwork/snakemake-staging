from snakemake_staging import stages, utils, zenodo

for name, stage in stages.STAGES.items():
    if not isinstance(stage, zenodo.ZenodoStage):
        continue

    # Rules for restoring or snapshotting the staging directory based on the
    # restore configuration
    if stage.restore:
        for file in stage.files.values():
            rule:
                name:
                    utils.rule_name("zenodo", name, "download", path=file)
                message:
                    f"Restoring file '{file}' for stage '{name}'"
                input:
                    stage.info_file
                output:
                    file
                run:
                    stage.download_file(input[0], file)

    else:
        rule:
            name:
                utils.rule_name("zenodo", name)
            message:
                f"Snapshotting stage '{name}'"
            input:
                list(stage.files.values())
            output:
                stage.info_file,
                touch(stage.upload_flag_file)
            run:
                stage.new_record(output[0], *input)
