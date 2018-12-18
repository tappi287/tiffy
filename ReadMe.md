## Tiffy - Yet another Exiftool GUI

Tiffy was crafted for the simple need to transfer spreadsheet data to XMP-Metadata of several hundred tif and jpg files.
Tiffy uses `pipenv` and `pyinstaller` to create a virtual environment and executables.
The pipenv is defined by the `pipfile` and pyinstaller is configured by the `..._.spec` files.


### Download and run
  - navigate to the <a href="https://github.com/tappi287/tiffy/releases">Releases</a> page and download a executable
    for your OS/platform


#### Running Tiffy from your local Python Interpreter
1. Clone this repository
2. Goto <a href="https://python.org">python.org</a> and get a Python interpreter 3.7.1 for your OS
3. `path to python/python.exe -m pip install pipenv` to install <a href="https://pipenv.readthedocs.io/">pipenv</a>
4. `path to this project/pipenv update` (the path where you cloned this project and the pipfile lives)
5. `pipenv shell` to activate your newly created virtual environment
6. from the pipenv shell `python tiffy.py` to run this app


#### Building Tiffy with PyInstaller
1. Make sure you can run the app following the instructions above
2. From your venv/pipenv shell run `pyinstaller tiffy_win.spec`
   to eg. build a windows executable directory or `pyinstaller tiffy_osx.spec`
   to build a OSX app package
   
   
##### Jump into adapting the interesting parts
If you'd like to adapt this for your own GUI or would like to modify this GUI to your needs,
take a look at <a href="/modules/app_update_meta.py">app_update_meta.py</a> which contains:
 - *ImgMetaDataApp* class inheriting from QObject controlling and instancing:
 - *ImgMetaDataWorker* class inherting from QThread listing the files
   and sending commands to:
 - modules/exif_worker.py *Exif* class inheriting from QObject controlling a QThreadpool of
   *exiftool* process instances