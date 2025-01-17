from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension


setup(
    name="matterhorn_cpp_extensions",
    ext_modules = [
        CppExtension(
            "matterhorn_cpp_extensions",
            [
                "api.cpp",
                "stdp.cpp"
            ],
            extra_compile_args = {
                "cxx": ["-g"]
            }
        ),
    ],
    cmdclass = {
        "build_ext": BuildExtension
    },
)