import json
import os
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from snakemake_staging.stages import Stage
from snakemake_staging.utils import PathLike, package_data, path_to_identifier
from snakemake_staging.version import __version__


class ZenodoStage(Stage):
    def __init__(
        self,
        name: str,
        info_file: PathLike,
        sandbox: bool = False,
        token: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name, config=config)
        self.info_file = Path(info_file)
        if self.info_file.exists():
            with open(self.info_file, "r") as f:
                info = json.load(f)
            self.sandbox = info.get("doi", "").startswith("10.5072")
        else:
            self.sandbox = sandbox
        self._token = token
        if sandbox:
            self.url = "https://sandbox.zenodo.org/api"
        else:
            self.url = "https://zenodo.org"

    def snakefile(self) -> PathLike:
        return package_data("workflow", "rules", "zenodo.smk")

    @cached_property
    def token(self) -> Optional[str]:
        if self._token is None:
            if self.sandbox:
                token = os.environ.get("SANDBOX_TOKEN", None)
            else:
                token = os.environ.get("ZENODO_TOKEN", None)
            return token
        else:
            return self._token

    @property
    def session(self) -> requests.Session:
        session = requests.Session()
        session.headers["User-Agent"] = f"snakemake-staging/v{__version__}"
        if self.token is not None:
            session.headers["Authorization"] = f"Bearer {self.token}"
        retry = Retry(
            backoff_factor=0.1,
            status_forcelist=[403],
            allowed_methods=["DELETE", "GET", "PUT", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def request(
        self,
        method: str,
        path: Optional[str] = None,
        url: Optional[str] = None,
        check: bool = True,
        require_token: bool = True,
        session: Optional[requests.Session] = None,
        **kwargs: Any,
    ) -> requests.Response:
        if require_token and self.token is None:
            raise ValueError(
                "A Zenodo access token is required but one was not provided"
            )
        if url is None:
            assert path is not None
            url = f"{self.url}{path}"
        if session is None:
            with self.session as session:
                response = session.request(method, url, **kwargs)  # type: ignore
        else:
            response = session.request(method, url, **kwargs)
        if check:
            try:
                response.raise_for_status()
            except requests.HTTPError:
                print(response.text)
                raise
        return response

    def new_record(self, info_file: PathLike, *files: PathLike, **metadata: Any) -> str:
        # Set default metadata for required fields
        metadata_proc: Dict[str, Any] = {
            "title": f"Staged Snakemake Workflow: {self.name}",
            "description": """
This is a a snapshot of the outputs of a Snakemake workflow
""",
            "creators": [{"name": f"snakemake-staging/v{__version__}"}],
            "upload_type": "dataset",
        }
        metadata_proc = dict(metadata_proc, **metadata)
        metadata_proc = {"metadata": metadata_proc}

        with self.session as session:
            # Create the deposition draft
            response = self.request(
                "POST",
                "/deposit/depositions",
                require_token=True,
                check=True,
                session=session,
                json=metadata_proc,
            )
            draft_data = response.json()
            dep_id = draft_data["id"]
            bucket_url = draft_data["links"]["bucket"]

            # Upload all of the target files
            for file in files:
                ident = path_to_identifier(file)
                with open(file, "rb") as f:
                    response = self.request(
                        "PUT",
                        url=f"{bucket_url}/{ident}",
                        require_token=True,
                        check=True,
                        session=session,
                        data=f,
                    )

            # Publish the record
            response = self.request(
                "POST",
                f"/deposit/depositions/{dep_id}/actions/publish",
                require_token=True,
                check=True,
                session=session,
            )

            # Save the draft data to the output file
            with open(info_file, "w") as f:
                json.dump(response.json(), f, indent=2)

            return dep_id

    def download_file(self, info_file: PathLike, file: PathLike) -> None:
        with open(info_file, "r") as f:
            info = json.load(f)

        # Search the info file for the file we want to download
        ident = path_to_identifier(file)
        download_url = None
        for file_info in info.get("files", []):
            if file_info["filename"] == ident:
                download_url = file_info["links"]["download"]
                break
        if download_url is None:
            raise RuntimeError(
                f"File {file} not found in record metadata file {info_file}"
            )

        # Stream from the download URL directly into the target file
        with self.session as session:
            with self.request(
                "GET",
                url=download_url,
                require_token=False,
                check=True,
                session=session,
                stream=True,
            ) as response:
                with open(file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
