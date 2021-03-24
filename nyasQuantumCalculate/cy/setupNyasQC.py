from distutils.core import setup
import os

from Cython.Build import cythonize

dirname = os.path.dirname(__file__)
pyxname = os.path.join(dirname, "nyasQC.pyx")

os.chdir(dirname)

setup(
    name="nyasQC",
    ext_modules=cythonize(
        module_list=[pyxname],
        #force=True,
        #annotate=True,
    ),
)
