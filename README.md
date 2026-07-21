# PyGUI
A KMSDRM desktop environment written in Python!

## Description
This project is officially built for my other project: [PythOS](https://github.com/milo0622/PythOS.git), as a submodule.

## How to build an app with PyGUI's API
1. Create a Python script in the apps/ folder. It can be anything you like that ends with .py
2. In the script, you MUST import the SDK library of PyGUI in order to call its UI APIs:
    ```python3
    import sys
    sys.path.insert("/opt/pygui") # This adds the PyGUI SDK library temporarily to the current path variable of Python for easier absolute path importing
    from lib.guiSDK import * # Import PyGUI SDK
