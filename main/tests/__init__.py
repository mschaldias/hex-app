# import os
# from django import setup
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp.test_settings")
# setup()

from django.conf import settings

if not settings.configured:
    import unittest
    import os
    from django import setup

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp.settings")
    setup()

    from django.test.utils import (
        setup_test_environment,
        teardown_test_environment,
        teardown_databases,
        setup_databases,
    )

    VERBOSITY = 1
    INTERACTIVE = False

    def djangoSetUpTestRun(self):
        setup_test_environment()
        self._django_db_config = setup_databases(VERBOSITY, INTERACTIVE)

    def djangoTearDownTestRun(self):
        teardown_databases(self._django_db_config, VERBOSITY)
        teardown_test_environment()

    setattr(unittest.TestResult, "startTestRun", djangoSetUpTestRun)
    setattr(unittest.TestResult, "stopTestRun", djangoTearDownTestRun)