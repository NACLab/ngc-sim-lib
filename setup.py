from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'NGC-Lib'
LONG_DESCRIPTION = 'Simulation object back-end for ngc-learn.'

packages = find_packages()
# Ensure that we do not pollute the global namespace.
for p in packages:
    #print(p)
    assert p == 'ngclib' or p.startswith('ngclib.')

# Setting up software package construction
setup(
       # name of package must match the folder name 'ngclearn'
        name="ngclib",
        version=VERSION,
        author="William Gebhardt, Alex Ororbia",
        author_email="<wdg1351@g.rit.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=packages,
        license="BSD-3-Clause License",
        url='https://github.com/NACLab/ngclib',
        install_requires=[], # add any additional packages that need to be installed along with your package
        keywords=['python', 'ngclib', 'jax', 'biophysics', 'biomimetics', 'bionics'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD-3-Clause License",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Scientific/Engineering :: Cognitive Science",
            "Topic :: Scientific/Engineering :: Computational Neuroscience",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Operating System :: Linux :: Ubuntu"
        ]
)
