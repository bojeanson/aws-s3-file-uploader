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
from unittest.mock import MagicMock

from stream_manager import (
    EventType,
    S3ExportTaskDefinition,
    Status,
    StatusContext,
    StatusLevel,
    StatusMessage,
)
from stream_manager.data import Message
from stream_manager.util import Util

from file_uploader.directory_watcher import DirectoryWatcher


class TestDirectoryUploader:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    def test_scan(self, tmp_path):
        # Given
        mock_client = MagicMock()
        append_mock = MagicMock()
        mock_client.append_message = append_mock
        du = DirectoryWatcher("test-bucket", tmp_path, ["*.csv"], "", self.logger, 1, stream_manager_client=mock_client)
        loop = asyncio.get_event_loop()

        # When
        loop.run_until_complete(du._DirectoryWatcher__scan(under_test=True))

        # Then
        append_mock.assert_not_called()

        # When
        f = open(tmp_path / "test1.csv", "a")
        f.write("test file 1!")
        f.close()
        loop.run_until_complete(du._DirectoryWatcher__scan(under_test=True))

        # Then
        append_mock.assert_called()

    def test_process_status(self, tmp_path):
        filename = tmp_path / "test1.csv"
        f = open(filename, "a")
        f.write("test file 1!")
        f.close()

        task_def = S3ExportTaskDefinition(input_url=filename.as_posix(), bucket="bucket", key="key")
        status_context = StatusContext(s3_export_task_definition=task_def, sequence_number=123)
        status_message = StatusMessage(
            event_type=EventType.S3Task,
            status_level=StatusLevel.INFO,
            status=Status.InProgress,
            status_context=status_context,
            message="message",
            timestamp_epoch_ms=1,
        )
        payload = Util.validate_and_serialize_to_json_bytes(status_message)
        test_message = Message(payload=payload)
        message_list = [test_message]

        mock_client = MagicMock()
        read_messages_mock = MagicMock()
        read_messages_mock.return_value = message_list
        mock_client.read_messages = read_messages_mock

        du = DirectoryWatcher("test-bucket", tmp_path, ["*.csv"], "", self.logger, 1, stream_manager_client=mock_client)
        loop = asyncio.get_event_loop()

        loop.run_until_complete(du._DirectoryWatcher__processStatus(under_test=True))
        assert filename.exists()

        status_message.status = Status.Success
        payload = Util.validate_and_serialize_to_json_bytes(status_message)
        test_message = Message(payload=payload)
        message_list = [test_message]
        read_messages_mock.return_value = message_list

        loop.run_until_complete(du._DirectoryWatcher__processStatus(under_test=True))
        assert filename.exists() is False

    def test_scan_dir_not_exist(self):
        fakedir = Path("/does/not/exists/")
        mock_client = MagicMock()
        append_mock = MagicMock()
        mock_client.append_message = append_mock

        mock_logger = MagicMock()
        mock_error = MagicMock()
        mock_logger.error = mock_error

        du = DirectoryWatcher("test-bucket", fakedir, ["*.cvs"], "", mock_logger, 1, stream_manager_client=mock_client)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(du._DirectoryWatcher__scan(under_test=True))
        mock_client.assert_not_called()
        mock_error.assert_called_once()

    def test_wrong_path(self, tmp_path):
        # testing what happens if the wildchar is not in the file name.
        # this should get caught as an invalid directory
        testdir = tmp_path / "testdir"
        testdir.mkdir()
        f = open(testdir / "test1.csv", "a")
        f.write("test file 1!")
        f.close()

        mock_client = MagicMock()
        append_mock = MagicMock()
        mock_client.append_message = append_mock

        mock_logger = MagicMock()
        mock_error = MagicMock()
        mock_logger.exception = mock_error

        du = DirectoryWatcher(
            "test-bucket", tmp_path, ["/test*/test1.csv"], "", mock_logger, 1, stream_manager_client=mock_client
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(du._DirectoryWatcher__scan(under_test=True))
        mock_client.assert_not_called()
        mock_error.assert_called_once()
