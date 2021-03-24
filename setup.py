from distutils.core import setup
import os
import sys

dirname = os.path.dirname(__file__)

os.chdir(dirname)

#########  build nyasQC.*.pyd
cy_path_src = os.path.join(dirname, "nyasQuantumCalculate", "cy")
pyds = [os.path.join(cy_path_src, name) for name in os.listdir(cy_path_src)
                    if name.startswith("nyasQC.") and name.endswith(".pyd")]

if len(pyds) == 0:
    setupNyasQC = os.path.join(cy_path_src, "setupNyasQC.py")
    commands = [
        "python",               # here should be your python run code
        f'"{setupNyasQC}"',
        "build_ext",
        "--inplace"
    ]

    exit_code = os.system(' '.join(commands))
    if exit_code != 0:
        raise RuntimeError


############  setup
setup(
    name = "nyasQuantumCalculate",
    version = "0.0.2",
    author = "nyasyamorina",
    author_email = "1275935966@qq.com",
    description = "A Simple Quantum Calculation Simulate Packge",
    url = "https://github.com/nyasyamorina/nyasQuantumCalculate",
    packages = ["nyasQuantumCalculate"],
)


############  copy *.pyd and *.pyi to setup path
site_paths = [path for path in sys.path
              if path.endswith("site-packages") and \
                  "lib" in path]

package_path = os.path.join(site_paths[0], "nyasQuantumCalculate")
assert os.path.exists(package_path)

cy_path_src = "nyasQuantumCalculate/cy"
cy_path_tar = os.path.join(package_path, "cy")
os.makedirs(cy_path_tar, exist_ok=True)
for name in os.listdir(cy_path_src):
    if name.endswith(".pyd") or name.endswith(".pyi"):
        with open(os.path.join(cy_path_src, name), "rb") as src:
            data = src.read()
        with open(os.path.join(cy_path_tar, name), "wb") as tar:
            tar.write(data)
