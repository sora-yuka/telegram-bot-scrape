import aiohttp


async def get_file_size(url: str) -> int | None:
    timeout = aiohttp.ClientTimeout(total=15, connect=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(url) as response:
                content_length = response.headers.get('Content-Length')
                return int(content_length) if content_length else None
    except Exception as e:
        print(f'Error getting file size: {e}')
        return None
