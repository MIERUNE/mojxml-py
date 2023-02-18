"""Run conversion in parallel."""

import concurrent.futures
import os
from abc import abstractmethod, ABCMeta
from typing import Iterable

from ..parse import Feature, ParseOptions, parse_raw


class BaseExecutor(metaclass=ABCMeta):
    """Executor for processing files"""

    def __init__(self, options: ParseOptions):
        """TODO"""
        self.options = options

    @abstractmethod
    def iter_process(
        self,
        src_iter: Iterable[bytes],
    ) -> Iterable[list[Feature]]:
        """TODO"""
        ...


class WorkerPoolExecutor(BaseExecutor, metaclass=ABCMeta):
    """TODO"""

    @abstractmethod
    def get_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """TODO"""
        ...

    def iter_process(
        self,
        src_iter: Iterable[bytes],
    ) -> Iterable[list[Feature]]:
        """TODO"""
        max_workers = os.cpu_count() or 1
        with self.get_executor(max_workers=max_workers) as executor:
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
    """Process paralelly with ProcessPoolExecutor"""

    def get_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """TODO"""
        max_workers = os.cpu_count() or 1
        return concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)


class ThreadPoolExecutor(WorkerPoolExecutor):
    """Process paralelly with ThreadPoolExecutor"""

    def get_executor(self, max_workers: int) -> concurrent.futures.Executor:
        """TODO"""
        max_workers = (os.cpu_count() or 1) * 2
        return concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)


class SingleThreadExecutor(BaseExecutor):
    """Process files with normal iterator"""

    def iter_process(
        self,
        src_iter: Iterable[bytes],
    ) -> Iterable[list[Feature]]:
        """TODO"""
        for src in src_iter:
            yield parse_raw(src, options=self.options)


EXECUTOR_MAP: dict[str, type[BaseExecutor]] = {
    "multiprocess": ProcessPoolExecutor,
    "thread": ThreadPoolExecutor,
    "single": SingleThreadExecutor,
}
