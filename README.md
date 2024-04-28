# Billiards Pool Game
Developed a comprehensive billiards game spanning from a C-based physics library to a Python-backed web server. Integrated C and Python seamlessly to provide live animation and enable user interactions. Utilized SQL (SQLite3 library) in Python for efficient data management of pool tables, enhancing backend functionality. This resulted in an engaging web application that provides immersive billiards gameplay with live animations, using both backend development and web interface design.

## How to Use

1. Install Required Packages: Open a terminal or command prompt and install the necessary packages using the following commands:

    #### Backend
    ```shell
    npm install
    npm install swig
    ```

2. Open a terminal in the project location

    #### Terminal

    ```shell
    cd PoolGame
    make
    export LD_LIBRARY_PATH=`pwd`
    python3 server.py ###
    ```

#### Where ### represents the port number where you wish to host the server.
#### Return back to the terminal and enter 'ctrl + c' to end backend processes if you wish to quit.