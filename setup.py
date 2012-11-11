from setuptools import setup, find_packages

setup(
    name = "galah",
    version = "0.1rc3",
    packages = find_packages( 
        exclude = [
            "galah.sheep*", 
            "galah.shepherd*"
        ]
    ),

    include_package_data = True,
    zip_safe = False,
    
    entry_points = {
        "console_scripts": [
            "create_admin.py = utils.create_admin:main",
            "api_client.py = utils.api_client:main"
        ]
    },

    install_requires = [
        "Flask>=0.8", 
        "Flask-Login>=0.1.3", 
        "Flask-WTF>=0.6",
        "WTForms>=1.0.1",
        "mongoengine>=0.6.9",
        "decorator>=3.4.0",
        "requests>=0.14.1",
        "google-api-python-client>=1.0"
    ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        "web": ["*.html", "*.css"],
    },

    # metadata for upload to PyPI
    author = "John Sullivan",
    author_email = "jsull003@ucr.edu",
    description = "Galah is a utility to allow better professer student communication",
    license = "GPLv3",
)
