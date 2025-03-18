import asyncio
import logging
import argparse

from aiopath import AsyncPath
from aioshutil import copyfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def copy_file(file_path: AsyncPath, output_folder: AsyncPath):
    """Копіює файл у відповідну підпапку на основі його розширення."""
    try:
        ext = file_path.suffix.lstrip('.') or 'unknown'
        dest_folder = output_folder / ext
        await dest_folder.mkdir(parents=True, exist_ok=True)
        
        dest_file = dest_folder / file_path.name
        await copyfile(file_path, dest_file)
        logging.info(f'Копійовано: {file_path} -> {dest_file}')
    except Exception as e:
        logging.error(f'Помилка копіювання {file_path}: {e}')

async def read_folder(source_folder: AsyncPath, output_folder: AsyncPath):
    """Рекурсивно читає файли та викликає copy_file для кожного."""
    tasks = []
    async for file_path in source_folder.rglob('*'):
        if await file_path.is_file():
            tasks.append(copy_file(file_path, output_folder))
    
    await asyncio.gather(*tasks)

async def main(source_path: str, output_path: str):
    source_folder = AsyncPath(source_path)
    output_folder = AsyncPath(output_path)
    
    if not await source_folder.exists() or not await source_folder.is_dir():
        logging.error(f'Вихідна папка не існує: {source_folder}')
        return
    
    await output_folder.mkdir(parents=True, exist_ok=True)
    await read_folder(source_folder, output_folder)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Копіює файли з однієї папки в іншу, сортує за розширенням.')
    parser.add_argument('source', help='Шлях до вихідної папки')
    parser.add_argument('output', help='Шлях до папки призначення')
    
    args = parser.parse_args()
    
    asyncio.run(main(args.source, args.output))