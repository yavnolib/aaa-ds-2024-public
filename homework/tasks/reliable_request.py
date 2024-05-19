import abc

import httpx
import asyncio


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    """
    Одна из главных проблем распределённых систем - это ненадёжность связи.

    Ваша задача заключается в том, чтобы таким образом исправить этот код, чтобы он
    умел переживать возвраты ошибок и таймауты со стороны сервера, гарантируя
    успешный запрос (в реальной жизни такая гарантия невозможна, но мы чуть упростим себе задачу).

    Все успешно полученные результаты должны регистрироваться с помощью обсёрвера.
    """
    async with httpx.AsyncClient() as client:
        max_retries = 10
        retry = 0
        while retry < max_retries:
            try:
                response = await client.get(url, timeout=10.5)
                response.raise_for_status()
                
                data = response.content
                observer.observe(data)
                break  # Exit loop if request is successful
            except (
                httpx.HTTPStatusError,
                httpx.TimeoutException,
                httpx.NetworkError,
            ):
                retry += 1
                if retry == max_retries:
                    return
            await asyncio.sleep(0.5)
        return