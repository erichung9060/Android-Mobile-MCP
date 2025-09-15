python setup.py sdist bdist_wheel && twine upload dist/*
rm -r build dist android_mobile_mcp.egg-info __pycache__ last_ui_dump.xml