# mktarball.py
#
# Creates a tarball that includes the contents of src/ directory.

import glob
import hashlib
import json
import os
import sys
import subprocess
import tarfile
import tempfile
import requests
import datetime

from pathlib import Path
from google.cloud import storage

NOTEBOOK_NAME = 'notebook.ipynb'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'src/secret/credentials.json'


def main():
    # Generate the list of files to include in the tarball.
    tarball_files = glob.glob('src/**/*', recursive=True)
    # Strip off the "src/" prefix from the file paths.
    tarball_paths = [str(Path(*Path(s).parts[1:])) for s in tarball_files]
    # A map from file path to archive name (name that file will be
    # stored as within the tarball).
    tarball_entries = dict(zip(tarball_files, tarball_paths))

    #print(json.dumps(tarball_entries, indent=2))

    if NOTEBOOK_NAME not in tarball_paths:
        raise Exception(f'missing {NOTEBOOK_NAME}')

    # Generate a hash of the contents that will be included in the tarball.
    m = hashlib.sha256()
    # To ensure that hash is canonical, we'll first update using the
    # contents of the notebook, and then on the rest of the included
    # files in sorted order (based on file path).
    notebook_entry = [path for path, arcname in tarball_entries.items() if arcname == NOTEBOOK_NAME]
    remaining_entry = [path for path, arcname in tarball_entries.items() if arcname != NOTEBOOK_NAME]
    remaining_entry.sort()
    hash_entry = []
    hash_entry.extend(notebook_entry)
    hash_entry.extend(remaining_entry)

    for entry in hash_entry:
        if os.path.isfile(entry):
            with open(entry, 'rb') as f:
                m.update(f.read())
    # Name of the output tarball.
    tarball_path = Path(f'{m.hexdigest()}.tar')
    # tarball_path = Path('fweet.tar')
    print(tarball_path)
  
    with tarfile.TarFile(tarball_path, 'w') as tarball:
        for path, arcname in tarball_entries.items():
            tarball.add(path, arcname=arcname, recursive=False)
    
    # upload tar
    client = storage.Client(project='Fweet')
    bucket = client.get_bucket('fweet')
    blob = bucket.blob(str(tarball_path))
    upload = blob.upload_from_filename(str(tarball_path))
    print("uploaded")
    
    rm_output = subprocess.call(['rm', str(tarball_path)])

    payload =  {
        "bucket": "fweet",
        "tarball": str(tarball_path),
        "event_id": "fweet event", 
        "event_timestamp": str(datetime.datetime.now()), 
        "key_parameters": "fweet=foo",
        "event_change": "google.storage.object.finalize"
    }
    # print(payload)
    # res = requests.post('http://localhost:8080', json=payload)
    # print("trigger pipeline")
    # print(res.json())
    # curl_output = subprocess.call([sys.executable, 
    #     'curl','localhost:8080',
    #     '-H', 'ContentType:application/json',
    #     '-d', payload])
    # print(curl_output)

if __name__ == '__main__':
    main()
