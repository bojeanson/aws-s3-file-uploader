#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License").
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import asyncio
import logging
from pathlib import Path
from typing import Annotated, List

import typer

from .log import LogLevel
from .main import main

cli = typer.Typer()


@cli.command()
def start_directory_uploader(
    bucket_name: Annotated[str, typer.Option(envvar="BUCKET_NAME")],
    directory_to_monitor: Annotated[
        Path, typer.Option(exists=True, dir_okay=True, readable=True, help="Local path to monitor for files.")
    ] = "monitored_dir",
    file_extensions_to_monitor: Annotated[List[str], typer.Option(help="File extensions to monitor.")] = ["*"],
    bucket_prefix: Annotated[str, typer.Option(help="Bucket prefix to add to the object name in S3.")] = "",
    log_level: Annotated[LogLevel, typer.Option(envvar="LOG_LEVEL")] = LogLevel.INFO,
    interval: Annotated[int, typer.Option(help="Time to sleep in seconds between two scans.")] = 1,
):
    logging.basicConfig(level=log_level.value)
    logger = logging.getLogger()

    logger.info(
        f"File uploader started with; directory_to_monitor={directory_to_monitor.as_posix()}, file_extensions_to_monitor={file_extensions_to_monitor}, bucket_name={bucket_name}, bucket_prefix={bucket_prefix}, interval={interval}"
    )
    asyncio.run(main(bucket_name, directory_to_monitor, file_extensions_to_monitor, bucket_prefix, logger, interval))


if __name__ == "__main__":
    cli()
