#!/bin/bash

rm -rf .coverage cover/

nosetests -v -s \
          --with-coverage --cover-html --cover-package=ovs_vsctl \
          tests/
