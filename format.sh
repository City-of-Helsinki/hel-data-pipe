#!/bin/bash

(cd endpoint ; black . && isort . && autoflake -i --remove-all-unused-imports --recursive . && flake8)
(cd parser ; black . && isort . && autoflake -i --remove-all-unused-imports --recursive . && flake8)
(cd persister ; black . && isort . && autoflake -i --remove-all-unused-imports --recursive . && flake8)
