# Copyright 2023 Simons Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from snakemake_staging.config import configure as configure
from snakemake_staging.rules import snakefile as snakefile
from snakemake_staging.stages import (
    NoOpStage as NoOpStage,
    Stage as Stage,
)
from snakemake_staging.version import __version__ as __version__
from snakemake_staging.zenodo import ZenodoStage as ZenodoStage
