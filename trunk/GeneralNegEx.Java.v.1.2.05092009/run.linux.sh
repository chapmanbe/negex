#!/bin/bash

# Runs the wrapper on the test kit.
java CallKit negex_triggers.txt Annotations-1-120-random.txt > CallKit.results
java accuracy CallKit.results
