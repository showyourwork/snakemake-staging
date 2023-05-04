Very much still a work in progress. Something like the following is the target:

```python
# File: Snakefile
import snakemake_staging as staging

stage = staging.GitStage(
    "stage",
    url="https://github.com/dfm/snakemake-staging.git",
    branch="stage",
    config=config["staging"],
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
