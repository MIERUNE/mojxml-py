"""Run conversion process in parallel."""

import concurrent.futures
import os
from abc import ABCMeta, abstractmethod
from typing import Dict, Iterable, List, Type

from ..parse import Feature, ParseOptions, parse_raw


class BaseExecutor(metaclass=ABCMeta):
    """Executor for processing files"""

    def __init__(self, options: ParseOptions) -> None:
        """Initialize"""
        self.options = options

    @abstractmethod
    def iter_process(
        self,
        src_iter: Iterable[bytes],
    ) -> Iterable[List[Feature]]:
        """Convert XMLs to OGR features"""


class WorkerPoolExecutor(BaseExecutor, metaclass=ABCMeta):
    """Executor implemeted with worker pool"""

    @abstractmethod
    def _get_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """Get executor."""

    def iter_process(
        self,
        src_iter: Iterable[bytes],
    ) -> Iterable[List[Feature]]:
        """Convert XMLs to OGR features"""
        max_workers = os.cpu_count() or 1
        with self._get_executor(max_workers=max_workers) as executor:
            futs = []
            for src in src_iter:
                fut = executor.submit(parse_raw, src, self.options)
                futs.append(fut)
                if len(futs) >= max_workers:
                    (done, not_done) = concurrent.futures.wait(
                        futs, return_when=concurrent.futures.FIRST_COMPLETED
                    )
                    for fut in done:
                        yield fut.result()
                    futs = list(not_done)

            if futs:
                (done, not_done) = concurrent.futures.wait(
                    futs, return_when=concurrent.futures.ALL_COMPLETED
                )
                for fut in done:
                    yield fut.result()


class ProcessPoolExecutor(WorkerPoolExecutor):
    """Process in parallel with ProcessPoolExecutor"""

    def _get_executor(self, max_workers: int) -> concurrent.futures.Executor:
        max_workers = os.cpu_count() or 1
        return concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)


class ThreadPoolExecutor(WorkerPoolExecutor):
    """Process in parallel with ThreadPoolExecutor"""

    def _get_executor(self, max_workers: int) -> concurrent.futures.Executor:
        max_workers = (os.cpu_count() or 1) * 2
        return concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)


class SingleThreadExecutor(BaseExecutor):
    """Process files with single-thread (normal) iterator"""

    def iter_process(self, src_iter: Iterable[bytes]) -> Iterable[List[Feature]]:
        """Convert XMLs to OGR features"""
        for src in src_iter:
            yield parse_raw(src, options=self.options)


EXECUTOR_MAP: Dict[str, Type[BaseExecutor]] = {
    "multiprocess": ProcessPoolExecutor,
    "thread": ThreadPoolExecutor,
    "single": SingleThreadExecutor,
}
