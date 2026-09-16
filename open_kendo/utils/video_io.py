"""Video I/O and camera stream wrappers."""

from pathlib import Path
from typing import Generator, Optional, Tuple, Union
import numpy as np


class VideoReader:
    """Manages reading frames from a webcam device index or video file."""

    def __init__(
        self,
        source: Union[int, str, Path] = 0,
        target_size: Optional[Tuple[int, int]] = None,
        target_fps: Optional[int] = None,
    ) -> None:
        """Initialize video stream reader.

        Args:
            source: Webcam device index (e.g. 0) or video file path.
            target_size: Optional (width, height) to resize frames.
            target_fps: Desired frame rate target.
        """
        self.source = source
        self.target_size = target_size
        self.target_fps = target_fps
        self._cap = None

    def open(self) -> None:
        """Open video capture stream.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VideoReader.open is not implemented.")

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray], float]:
        """Read the next frame from the stream.

        Returns:
            Tuple[bool, Optional[np.ndarray], float]: Success flag, frame image (BGR),
            and timestamp in milliseconds.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VideoReader.read_frame is not implemented.")

    def stream(self) -> Generator[Tuple[np.ndarray, float], None, None]:
        """Yield frames and timestamps until stream termination.

        Yields:
            Tuple[np.ndarray, float]: Frame image and timestamp in milliseconds.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VideoReader.stream is not implemented.")

    def close(self) -> None:
        """Release video capture device."""
        pass


class VideoWriter:
    """Handles saving analyzed frames to an output video container."""

    def __init__(
        self,
        output_path: Union[str, Path],
        fps: int = 30,
        frame_size: Tuple[int, int] = (1280, 720),
        codec: str = "mp4v",
    ) -> None:
        """Initialize video writer.

        Args:
            output_path: Destination video file path.
            fps: Frame rate of output video.
            frame_size: Frame resolution as (width, height).
            codec: FourCC codec string.
        """
        self.output_path = Path(output_path)
        self.fps = fps
        self.frame_size = frame_size
        self.codec = codec
        self._writer = None

    def open(self) -> None:
        """Initialize video writer codec.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VideoWriter.open is not implemented.")

    def write_frame(self, frame: np.ndarray) -> None:
        """Append frame to output video file.

        Args:
            frame: BGR frame to encode.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VideoWriter.write_frame is not implemented.")

    def close(self) -> None:
        """Finalize video encoding and flush file to disk."""
        pass
