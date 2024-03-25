from datetime import datetime
import json
import logging
import os
import shutil
from zipfile import ZipFile

logging.basicConfig(encoding='utf-8', format='%(asctime)s %(levelname)s:%(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)

pbix_file = 'filename.pbix'
pbix_dir = ''.join(pbix_file.split('.')[:-1])

def serialize_datetime(obj: object): 
    if isinstance(obj, datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable")

def walk_dir(dir, file_list: list[str]):
    items = os.scandir(dir)
    for item in items:
        path =  os.path.join(dir, item.name)
        if item.is_dir():
            file_list = walk_dir(path, file_list)
        else:
            file_list.append(path)
    return file_list

def main():
    if os.path.exists(pbix_dir):
        shutil.rmtree(pbix_dir)

    try:
        with ZipFile(pbix_file, 'r') as zfile: 
            zfile.extractall(path=pbix_dir)
    except:
        logger.error(f"Error opening file {pbix_file}")

    for file in walk_dir(pbix_dir, []):
        logger.debug(f"Processing {file}")
        logger.debug(os.stat(file))
        file_updated: bool = False
        file_ext = file.split('.')[-1]
        if file_ext == file:
            file_ext = ''
        logger.debug(f"file extension: {file_ext}")
        with open(file, 'r+', encoding="utf8") as f:
            try:
                data = f.read()
                logger.debug(data)
                if file_ext == 'xml':
                    logger.debug(f"Skipping XML file {file}")
                else:
                    try:
                        data_formatted = json.dumps(json.loads(data.encode("utf-8", "strict")), default=serialize_datetime, indent=4)
                        logger.debug(f"{data_formatted}\n")
                        f.seek(0)
                        f.writelines(data_formatted)
                        f.truncate()
                        file_updated = True
                    except:
                        logger.debug(f"Error parsing file {file} as JSON")
            except:
                logger.debug(f"Cannot open file {file}. Likely a binary file")
                if file == os.path.join(pbix_dir, 'DataModel'):
                    logger.debug(f"Zero out DataModel file from PBIX")
                    f.seek(0)
                    f.truncate()

        if file_updated and file_ext == '':
            os.rename(file, file + '.json')
            logger.debug(f"Renamed file {file} to {file + '.json'}")

if __name__ == "__main__":
    main()
