from distutils.core import setup
import autocomplete

long_description = open('README.md').read()

setup(
    name='autocomplete',
    version=autocomplete.VERSION,
    packages=['autocomplete', 
              ],
    description='Redis based autocompletion (build index and search query).',
    long_description=long_description,
    author='Feng Li',
    author_email='okidogii@gmail.com',
    license='MIT License',
    url='https://github.com/fengli/autocomplete-redis.git',
    platforms=["any"],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
