#!/bin/bash

# The script is written assuming it will be run in a docker container.
# The container has a folder on the host mounted at /results so that
# it copies the results there after the run

results_folder=results_$(date +"%m-%d-%Y-%H.%M.%S")
mkdir $results_folder
nosetests --processes=2 --process-timeout=900 |& tee $results_folder/nose_output
cp -r $results_folder /results
