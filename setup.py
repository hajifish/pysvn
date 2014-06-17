from setuptools import setup, find_packages 

setup(
    name = "pysvn",
    version = "0.0.1",
    author = 'xcluo',
    author_email = 'xcluo.mr@gmail.com',
    description = 'Python operate svn server.',

    packages = find_packages(),
    keywords = ('pysvn', 'svn', 'python'),
    ##cmdclass = cmdclasses,
    ##data_files = data_files,
    #scripts = ['scripts/pyssh.py'],
)
