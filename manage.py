#!/usr/bin/env python
import os
import sys
import hashlib
import importlib

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "katacoda.settings")
    try:
        def _non_security_md5(*args, **kwargs):
    kwargs['usedforsecurity'] = False
    return hashlib.md5(*args, **kwargs)

def monkey_patch_md5(modules_to_patch):
    """Monkey-patch calls to MD5 that aren't used for security purposes.

    Sets RHEL's custom flag `usedforsecurity` to False allowing MD5 in FIPS mode.
    `modules_to_patch` must be an iterable of module names (strings).
    Modules must use `import hashlib` and not `from hashlib import md5`.
    """
    # Manually load a module as a unique instance
    # https://stackoverflow.com/questions/11170949/how-to-make-a-copy-of-a-python-module-at-runtime
    HASHLIB_SPEC = importlib.util.find_spec('hashlib')
    patched_hashlib = importlib.util.module_from_spec(HASHLIB_SPEC)
    HASHLIB_SPEC.loader.exec_module(patched_hashlib)

    patched_hashlib.md5 = _non_security_md5  # Monkey patch MD5

    # Inject our patched_hashlib for all requested modules
    for module_name in modules_to_patch:
        module = importlib.import_module(module_name)
        module.hashlib = patched_hashlib
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
