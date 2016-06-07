#!/bin/bash

mkdir -p results
docker run -v ${PWD}/results:/results alexbranciog/runner
