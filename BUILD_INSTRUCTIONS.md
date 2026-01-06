
# Build and Usage Instructions: C++ Integration

This document provides instructions on how to compile the Python karaoke scoring project into a shared library and how to build and run the C++ client application that uses this library.

## Overview

The process involves two main steps:
1.  **Compile the Python code**: We will use `PyInstaller` to bundle the Python script (`library_interface.py`) and all its dependencies (including the Python interpreter) into a single directory with a C-compatible shared library (`.dll` or `.so`).
2.  **Compile the C++ code**: We will use `CMake` and a C++ compiler to build the `scorer_client` executable.

## Step 1: Compile the Python Code into a Shared Library

We will use `PyInstaller` to create a distributable package for our Python code. This will include the Python interpreter, the scripts, and all required libraries.

### 1.1. Install PyInstaller

If you don't have PyInstaller, install it using pip:
```bash
pip install pyinstaller
```

### 1.2. Create a PyInstaller Spec File

PyInstaller uses a `.spec` file for configuration. Create a file named `build_library.spec` with the following content:

```python
# build_library.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['library_interface.py'],
             pathex=['d:/scoring karaoke'], # IMPORTANT: Use the absolute path to your project
             binaries=[],
             datas=[
                # If you have data files that your project needs (e.g., models),
                # you must include them here.
                # For CREPE, the model is downloaded automatically to a user directory,
                # so it might not need to be bundled if the user has run it once.
                # To be safe, you might need to locate the CREPE model path and add it.
             ],
             hiddenimports=[
                'crepe', 'scipy', 'numpy', 'librosa', 'fastdtw',
                'tensorflow', 'numba', 'resampy',
                # Add any other hidden imports pyinstaller might miss
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
             
# This creates a shared library build
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='libkaraoke_scorer', # The name of our library
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True ) # Use True for debugging, False for a background process

# This is the key part for creating a distributable folder
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='karaoke_scorer_dist')
```

### 1.3. Run PyInstaller

Open a command prompt in your project directory (`d:\scoring karaoke`) and run PyInstaller with the spec file:

```bash
pyinstaller build_library.spec
```

This command will create a `dist/karaoke_scorer_dist` folder. Inside this folder, you will find `libkaraoke_scorer.exe` (on Windows) or `libkaraoke_scorer` (on Linux), along with many other files (`python3x.dll`, etc.). **PyInstaller does not create a standard `.dll`/`.so` directly**, but the executable it creates can be treated as a shared library by a C++ application that knows how to interact with it.

**Important**: The `main.cpp` is written assuming a standard `.dll` or `.so`. PyInstaller's approach is different. The C++ code would need to be adapted to launch the generated executable and communicate with it (e.g., via standard I/O or a temporary file).

**Alternative (and better) approach**: For true shared library creation, `Cython` or `pybind11` are better tools. They can produce a standard `.pyd` (Windows) or `.so` (Linux) file that can be loaded as a true library. However, this is a more advanced topic. For this guide, we'll stick to the PyInstaller method and adjust the C++ usage.

## Step 2: Compile the C++ Client

### 2.1. Prerequisites

-   A C++ compiler (like GCC on Linux, or MSVC on Windows installed with Visual Studio).
-   `CMake`.

### 2.2. Build Steps

1.  **Create a build directory** for the C++ project:
    ```bash
    mkdir cpp_build
    cd cpp_build
    ```

2.  **Run CMake** to configure the project. Point it to the parent directory where `CMakeLists.txt` is located.
    ```bash
    cmake ..
    ```
    If CMake has trouble finding your Python installation, you may need to give it a hint:
    ```bash
    cmake .. -DPYTHON_EXECUTABLE="C:/Python39/python.exe"
    ```

3.  **Compile the C++ code**:
    ```bash
    cmake --build .
    ```
    This will create the `scorer_client.exe` (Windows) or `scorer_client` (Linux) executable in the `cpp_build` directory.

## Step 3: Run the Application

This is the final and most important part.

1.  **Copy Files**:
    -   Go to the PyInstaller output directory: `dist/karaoke_scorer_dist`.
    -   Copy the **entire contents** of this directory into your C++ build directory (`cpp_build`).
    -   Your `cpp_build` directory should now contain `scorer_client.exe` and all the Python files from the `dist` folder.

2.  **Modify `main.cpp` for PyInstaller**:
    The current `main.cpp` uses `LoadLibrary`. This will not work with the `PyInstaller` executable. You need to modify the C++ code to run the `libkaraoke_scorer.exe` as a separate process and communicate with it, for example, over stdin/stdout.

    This is a significant change. A simpler (but less robust) approach for a demonstration is to use Python's C API directly, which is what the `CMakeLists.txt` is set up for. To make that work, you would need to run the C++ app in an environment where the Python interpreter and all the `requirements.txt` packages are installed.

### Simplified Running Instructions (Without PyInstaller)

This method avoids the complexity of PyInstaller, but requires a Python environment on the machine running the C++ app.

1.  **Install Python and Dependencies**:
    Make sure Python is installed on the system and that you have installed all the required packages from `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Build the C++ Client**:
    Follow the C++ build steps from above.

3.  **Set Environment Variables**:
    The C++ application needs to find the Python scripts and the Python interpreter.
    -   **`PYTHONPATH`**: Set this to your project directory.
        -   Windows: `set PYTHONPATH=d:\scoring karaoke`
        -   Linux/macOS: `export PYTHONPATH=/path/to/scoring_karaoke`
    -   **`PATH`**: Make sure your Python `Scripts` and `DLLs` folder are in the system's `PATH`.

4.  **Run the application**:
    From your `cpp_build` directory, run the client. It should now be able to host the Python interpreter, import your `library_interface.py` script, and call the functions.
    ```bash
    ./scorer_client
    ```
    Remember to change the placeholder file paths in `main.cpp` to point to real audio files.

This second approach is more direct for development and testing, and is what the provided `CMakeLists.txt` and `main.cpp` are geared towards. The PyInstaller method is better for distribution to machines without a Python environment, but requires more complex inter-process communication.
