#!/bin/bash
echo "This will fail if you don't activate a venv with nn installed"
ipython profile create ninja
cp -r ../notebook.ninja/src/cli/config/* $(ipython profile locate ninja)
python3 -m ipykernel install --user --name local --display-name "Python (local)" --profile ninja