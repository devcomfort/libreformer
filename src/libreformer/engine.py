from typing import Sequence, Iterator, Dict, overload, AsyncIterator
from abc import ABC, abstractmethod
import asyncio
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import os
import subprocess

from .schemas import Succeed, Failed
from .utils import check_install, get_path, install
from .logging import log_elapsed_time, async_log_elapsed_time
from .formats import FormatRegistry, DocumentCategory
from .schemas.format_info import FormatInfo


class BaseEngine(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def transform(self, file_path: str, to: str) -> Succeed | Failed: ...

    @overload
    def transform_parallel(
        self, file_paths: Sequence[str], to: str
    ) -> Iterator[Succeed | Failed]: ...
    @overload
    def transform_parallel(
        self, file_paths: Sequence[str], to: Sequence[str]
    ) -> Iterator[Succeed | Failed]: ...
    def transform_parallel(
        self,
        file_paths: Sequence[str],
        to: str | Sequence[str],
    ) -> Iterator[Succeed | Failed]:
        """병렬로 파일을 변환하고 결과를 이터레이터로 반환합니다.

        각 작업이 완료되는 순서대로 :class:`Succeed` 혹은 :class:`Failed` 인스턴스를
        `yield` 합니다.
        """
        # Validate 'to' parameter when it is a sequence of strings
        if not isinstance(to, str):
            # Ensure 'to' is a sequence with same length as file_paths
            if len(to) != len(file_paths):
                raise ValueError(
                    f"Length of 'to' ({len(to)}) must match number of file_paths ({len(file_paths)})"
                )
        file_path_map: Dict[concurrent.futures.Future, str] = {}

        with ProcessPoolExecutor() as executor:
            # 각 파일에 대해 transform 메서드를 병렬로 실행하고 future와 파일 경로 매핑
            for idx, file_path in enumerate(file_paths):
                target = to if isinstance(to, str) else to[idx]
                future = executor.submit(self.transform, file_path, target)
                file_path_map[future] = file_path

            # 결과가 준비되는 대로 yield
            for future in concurrent.futures.as_completed(list(file_path_map.keys())):
                file_path = file_path_map[future]
                try:
                    result = future.result()
                    yield result
                except Exception as e:
                    yield Failed(file_path=Path(file_path), error_message=str(e))

    # ---------------------------------------------------------------------
    # Callable interface
    # ---------------------------------------------------------------------
    @overload
    def __call__(self, file_path: str, to: str) -> Succeed | Failed: ...

    @overload
    def __call__(
        self, file_paths: Sequence[str], to: str | Sequence[str]
    ) -> Iterator[Succeed | Failed]: ...

    def __call__(self, file_path_or_paths, to):
        if isinstance(file_path_or_paths, str):
            return self.transform(file_path_or_paths, to)  # type: ignore[arg-type]
        else:
            return self.transform_parallel(file_path_or_paths, to)  # type: ignore[arg-type]


class LibreOfficeEngine(BaseEngine):
    def __init__(
        self,
        auto_install: bool = True,
        max_concurrency: int | None = None,
        timeout: float = 300.0,
    ):
        """
        LibreOfficeEngine 클래스 초기화

        Args:
            auto_install: LibreOffice가 설치되어 있지 않을 때 자동으로 설치할지 여부
            max_concurrency: 비동기 최대 동시 변환 수. None이면 os.cpu_count() 사용.
            timeout: 단일 변환 작업 타임아웃(초). 기본값 300초.
        """
        super().__init__()

        if max_concurrency is not None and max_concurrency < 1:
            raise ValueError(f"max_concurrency must be >= 1, got {max_concurrency}")
        if timeout <= 0:
            raise ValueError(f"timeout must be > 0, got {timeout}")

        self._max_concurrency = max_concurrency or os.cpu_count() or 4
        self._timeout = timeout
        self._semaphore: asyncio.Semaphore | None = None

        if auto_install and not check_install():
            install()

        # LibreOffice 실행 파일 경로 저장
        self.libreoffice_path = get_path()

    @log_elapsed_time("LibreOffice file transformation")
    def transform(self, file_path: str, to: str) -> Succeed | Failed:
        """단일 파일을 변환하고 변환된 파일 경로를 반환합니다.

        Args:
            file_path: 변환할 원본 파일 경로
            to: 변환할 목표 형식 (예: "pdf", "docx" 등)

        Returns:
            Succeed: 변환 성공 시 (원본 경로, 출력 경로 포함)
            Failed: 변환 실패 시 (에러 메시지 포함)
        """
        # 실제 변환 수행 (headless soffice 사용)
        input_path = Path(file_path)
        if not input_path.exists():
            return Failed(file_path=input_path, error_message="File not found")

        output_dir = str(input_path.parent)

        # self.libreoffice_path가 None일 수 있으므로 체크
        if not self.libreoffice_path:
            return Failed(
                file_path=input_path, error_message="LibreOffice not found in PATH"
            )

        # Unique user installation directory to avoid lock conflicts during parallel execution
        import uuid
        import shutil

        user_installation_dir = Path(f"/tmp/libreoffice_conversion_{uuid.uuid4()}")

        cmd = [
            self.libreoffice_path,
            f"-env:UserInstallation=file://{user_installation_dir}",
            "--headless",
            "--norestore",
            "--nolockcheck",
            "--convert-to",
            to,
            "--outdir",
            output_dir,
            str(input_path),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            # Clean up temporary user installation directory
            if user_installation_dir.exists():
                shutil.rmtree(user_installation_dir, ignore_errors=True)

            if result.returncode != 0:
                return Failed(
                    file_path=Path(file_path),
                    error_message=result.stderr.strip()
                    or result.stdout.strip()
                    or "Conversion failed",
                )
            # 변환된 파일 경로 구성
            output_path = input_path.with_suffix(f".{to}")
            if not output_path.exists():
                # 일부 형식은 soffice가 .pdf 등 다른 확장자를 사용하므로 디렉터리에서 찾아봄
                for f in os.listdir(output_dir):
                    if f.startswith(input_path.stem) and f.lower().endswith(
                        f".{to.lower()}"
                    ):
                        output_path = Path(output_dir) / f
                        break

            # 출력 파일 존재 확인
            if not output_path.exists():
                return Failed(
                    file_path=Path(file_path),
                    error_message=f"Conversion succeeded but output file not found: {output_path}",
                )

            # Return a Succeed instance with original and output paths
            return Succeed(file_path=Path(file_path), output_path=output_path.resolve())
        except Exception as e:
            return Failed(file_path=input_path, error_message=str(e))

    # -----------------------------------------------------------------
    # Async API (신규)
    # -----------------------------------------------------------------
    def _get_semaphore(self) -> asyncio.Semaphore:
        """이벤트 루프별로 Semaphore를 지연 생성한다."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrency)
        return self._semaphore

    @async_log_elapsed_time("LibreOffice async file transformation")
    async def async_transform(self, file_path: str, to: str) -> Succeed | Failed:
        """단일 파일을 비동기로 변환하고 결과를 반환합니다.

        Args:
            file_path: 변환할 원본 파일 경로
            to: 변환할 목표 형식 (예: ``"pdf"``, ``"docx"`` 등)

        Returns:
            변환 성공 시 ``Succeed``, 실패 시 ``Failed``.
        """
        import uuid
        import shutil

        input_path = Path(file_path)
        if not input_path.exists():
            return Failed(file_path=input_path, error_message="File not found")

        if not self.libreoffice_path:
            return Failed(
                file_path=input_path, error_message="LibreOffice not found in PATH"
            )

        output_dir = str(input_path.parent)
        user_installation_dir = Path(f"/tmp/libreoffice_conversion_{uuid.uuid4()}")

        cmd = [
            self.libreoffice_path,
            f"-env:UserInstallation=file://{user_installation_dir}",
            "--headless",
            "--norestore",
            "--nolockcheck",
            "--convert-to",
            to,
            "--outdir",
            output_dir,
            str(input_path),
        ]

        semaphore = self._get_semaphore()
        async with semaphore:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=self._timeout
                    )
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                    return Failed(
                        file_path=input_path,
                        error_message=f"Conversion timed out after {self._timeout}s",
                    )
                finally:
                    # Clean up temporary user installation directory
                    if user_installation_dir.exists():
                        shutil.rmtree(user_installation_dir, ignore_errors=True)

                if proc.returncode != 0:
                    stderr_text = stderr.decode().strip() if stderr else ""
                    stdout_text = stdout.decode().strip() if stdout else ""
                    return Failed(
                        file_path=input_path,
                        error_message=stderr_text or stdout_text or "Conversion failed",
                    )

                # 변환된 파일 경로 구성
                output_path = input_path.with_suffix(f".{to}")
                if not output_path.exists():
                    for f in os.listdir(output_dir):
                        if f.startswith(input_path.stem) and f.lower().endswith(
                            f".{to.lower()}"
                        ):
                            output_path = Path(output_dir) / f
                            break

                if not output_path.exists():
                    return Failed(
                        file_path=input_path,
                        error_message=f"Conversion succeeded but output file not found: {output_path}",
                    )

                return Succeed(file_path=input_path, output_path=output_path.resolve())
            except asyncio.TimeoutError:
                return Failed(
                    file_path=input_path,
                    error_message=f"Conversion timed out after {self._timeout}s",
                )
            except Exception as e:
                return Failed(file_path=input_path, error_message=str(e))

    @overload
    async def async_transform_parallel(
        self, file_paths: Sequence[str], to: str
    ) -> AsyncIterator[Succeed | Failed]: ...
    @overload
    async def async_transform_parallel(
        self, file_paths: Sequence[str], to: Sequence[str]
    ) -> AsyncIterator[Succeed | Failed]: ...
    async def async_transform_parallel(
        self,
        file_paths: Sequence[str],
        to: str | Sequence[str],
    ) -> AsyncIterator[Succeed | Failed]:
        """복수 파일을 비동기 병렬로 변환하고 완료 순서대로 결과를 yield합니다.

        Args:
            file_paths: 변환할 원본 파일 경로 목록
            to: 단일 포맷 문자열 또는 파일별 포맷 목록

        Yields:
            완료 순서대로 ``Succeed`` 또는 ``Failed`` 인스턴스.

        Raises:
            ValueError: ``to``가 Sequence이고 길이가 ``file_paths``와 다를 때.
        """
        if not isinstance(to, str):
            if len(to) != len(file_paths):
                raise ValueError(
                    f"Length of 'to' ({len(to)}) must match number of file_paths ({len(file_paths)})"
                )

        tasks: list[asyncio.Task[Succeed | Failed]] = []
        for idx, fp in enumerate(file_paths):
            target = to if isinstance(to, str) else to[idx]
            task = asyncio.create_task(self.async_transform(fp, target))
            tasks.append(task)

        for coro in asyncio.as_completed(tasks):
            result = await coro
            yield result

    # -----------------------------------------------------------------
    # Format convenience methods (Engine → FormatRegistry 통합)
    # -----------------------------------------------------------------
    @staticmethod
    def supported_input_formats() -> set[str]:
        """지원하는 입력 포맷 확장자 집합을 반환한다."""
        return FormatRegistry.supported_input_formats()

    @staticmethod
    def supported_output_formats() -> set[str]:
        """지원하는 출력 포맷 확장자 집합을 반환한다."""
        return FormatRegistry.supported_output_formats()

    @staticmethod
    def can_convert(from_ext: str, to_ext: str) -> bool:
        """입력→출력 변환 가능 여부를 반환한다."""
        return FormatRegistry.can_convert(from_ext, to_ext)

    @staticmethod
    def formats_by_category(
        category: str | DocumentCategory,
    ) -> list[FormatInfo]:
        """카테고리별 포맷 목록을 반환한다."""
        return FormatRegistry.formats_by_category(category)
