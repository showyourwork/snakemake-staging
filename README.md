```python
# File: Snakefile
import snakemake_staging as staging

# The staging configuration is handled by a global call to `staging.configure`,
# which and you can pass any custom options here. In particular, this should
# include a list of any stages that you want to snapshot or restore.
staging.configure(config["staging"])


stage = staging.GitStage(
    "stage",
    url="https://github.com/dfm/snakemake-staging.git",
    branch="stage",
)

rule expensive_computation:
    input:
        ...
    output:
        stage("path/to/output/file.txt")
    shell:
        ...

# Finally (this should be after all calls to `stage` have been made),
# include the provided Snakefile for handling staging and restoring files.
include: staging.snakefile()
```
