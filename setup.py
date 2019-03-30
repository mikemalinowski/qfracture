import os
import setuptools

short_description = 'qFracture is a lightweight UI atop of fracture'
if os.path.exists('README.md'):
    with open('README.md', 'r') as fh:
        long_description = fh.read()

else:
    long_description = short_description

setuptools.setup(
    name='qfracture',
    version='0.9.1',
    author='Mike Malinowski',
    author_email='mike@twisted.space',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikemalinowski/qfracture',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_data={
        '': ['_res/*.css', '_res/*.png', '_res/*.ui', 'delegates/*.py'],
    },
    install_requires=['factories', 'qute', 'scribble', 'fracture'],
    keywords="fracture data composite qfracture",
)
