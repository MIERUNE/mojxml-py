"""Convert .xml/.zip files to OGR format."""

import os
from typing import Iterable
import concurrent.futures

from abc import ABCMeta, abstractmethod

from ..parse import parse_raw, Feature


class BaseExecutor(metaclass=ABCMeta):
    """Executor for processing files"""

    @abstractmethod
    def process(
        self,
        src_iter: Iterable[bytes],
        include_chikugai: bool,
        include_arbitrary_crs: bool,
    ) -> Iterable[list[Feature]]:
        """TODO"""
        ...


class ProcessPoolExecutor(BaseExecutor):
    """Process files with ProcessPoolExecutor"""

    def process(
        self,
        src_iter: Iterable[bytes],
        include_chikugai: bool,
        include_arbitrary_crs: bool,
    ) -> Iterable[list[Feature]]:
        """TODO"""
        max_workers = os.cpu_count() or 1
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            futs = []
            for src in src_iter:
                fut = executor.submit(
                    parse_raw,
                    src,
                    include_chikugai=include_chikugai,
                    include_arbitrary_crs=include_arbitrary_crs,
                )
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


class ThreadPoolExecutor(BaseExecutor):
    """Process files with ThreadPoolExecutor"""

    def process(
        self,
        src_iter: Iterable[bytes],
        include_chikugai: bool,
        include_arbitrary_crs: bool,
    ) -> Iterable[list[Feature]]:
        """TODO"""

        max_workers = (os.cpu_count() or 1) * 2
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futs = []
            for src in src_iter:
                fut = executor.submit(
                    parse_raw,
                    src,
                    include_chikugai=include_chikugai,
                    include_arbitrary_crs=include_arbitrary_crs,
                )
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


class SingleThreadExecutor(BaseExecutor):
    """Process files with normal iterator"""

    def process(
        self,
        src_iter: Iterable[bytes],
        include_chikugai: bool,
        include_arbitrary_crs: bool,
    ) -> Iterable[list[Feature]]:
        """TODO"""
        for src in src_iter:
            yield parse_raw(
                src,
                include_chikugai=include_chikugai,
                include_arbitrary_crs=include_arbitrary_crs,
            )


EXECUTOR_MAP = {
    "multiprocess": ProcessPoolExecutor,
    "thread": ThreadPoolExecutor,
    "single": SingleThreadExecutor,
}
