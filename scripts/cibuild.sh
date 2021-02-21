#!/bin/bash

# Exit code starts at 0 but is modified if any checks fail
EXIT=0

# Output a line prefixed with a timestamp
info()
{
	echo "$(date +'%F %T') |"
}

# Track number of seconds required to run script
START=$(date +%s)
echo "$(info) starting build checks."

# Syntax check all python source files
SYNTAX=$(find . -name "*.py" -type f -exec python -m py_compile {} \; 2>&1)
if [[ ! -z $SYNTAX ]]; then
	echo -e "$SYNTAX"
	echo -e "\n$(info) detected one or more syntax errors, failing build."
	EXIT=1
fi

# Check all built-in python source files for PEP 8 compliance, but explicitly
# ignore:
#  - W504: line break after binary operator
#  - E501: line greater than 80 characters in length
pycodestyle \
    --ignore=W504,E501 \
    --exclude=nautobot_root/scripts,nautobot_root/reports,nautobot_root/jobs,nautobot_root/git \
    contrib/ development/ nautobot_root/ tasks.py
RC=$?
if [[ $RC != 0 ]]; then
	echo -e "\n$(info) one or more PEP 8 errors detected, failing build."
	EXIT=$RC
fi

# Point to the testing nautobot_config file for use in CI
TEST_CONFIG=nautobot_root/nautobot/core/tests/nautobot_config.py

# Run Nautobot tests
coverage run --source="nautobot_root/" scripts/test_runner.py --config=$TEST_CONFIG test nautobot_root/
RC=$?
if [[ $RC != 0 ]]; then
	echo -e "\n$(info) one or more tests failed, failing build."
	EXIT=$RC
fi

# Show code coverage report
coverage report --skip-covered --omit *migrations*
RC=$?
if [[ $RC != 0 ]]; then
	echo -e "\n$(info) failed to generate code coverage report."
	EXIT=$RC
fi

# Show build duration
END=$(date +%s)
echo "$(info) exiting with code $EXIT after $(($END - $START)) seconds."

exit $EXIT
