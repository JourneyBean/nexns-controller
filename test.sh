#!/bin/bash
set -e

./manage.py test nexns.client.tests
./manage.py test nexns.name.tests
./manage.py test nexns.user.tests
./manage.py test nexns.variable.tests
