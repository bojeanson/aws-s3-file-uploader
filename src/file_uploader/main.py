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


import logging
import time
from pathlib import Path
from typing import List

from stream_manager import StreamManagerClient

from .directory_watcher import DirectoryWatcher


async def main(
    bucket_name: str,
    directory_to_monitor: Path,
    file_extensions_to_monitor: List[str],
    bucket_prefix: str,
    logger: logging.Logger,
    interval: int,
    stream_manager_host: str,
    stream_manager_port: int,
):

    logger.info("==== main ====")

    while True:
        du = None
        try:
            stream_manager = StreamManagerClient(host=stream_manager_host, port=stream_manager_port)
            du = DirectoryWatcher(
                bucket_name=bucket_name,
                directory_to_monitor=directory_to_monitor,
                file_extensions_to_monitor=file_extensions_to_monitor,
                bucket_prefix=bucket_prefix,
                interval=interval,
                logger=logger,
                stream_manager_client=stream_manager,
            )
            await du.run()
        except Exception as exc:
            logger.exception("Exception while running: {exc}")
        finally:
            if du is not None:
                du.close()
        # something very wrong happened. Let's pause for 1 minute and start again
        time.sleep(60)
