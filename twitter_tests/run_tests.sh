#!/bin/bash

results_folder=results_$(date +"%m-%d-%Y-%H.%M.%S")
mkdir $results_folder
nosetests --nologcapture --processes=4 --process-timeout=900 |& tee $results_folder/nose_output
cp -r $results_folder /results
