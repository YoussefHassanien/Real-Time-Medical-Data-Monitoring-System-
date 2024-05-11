# Medical Device Simulation Client-Server Project

This project simulates a medical device that generates temperature readings for patients. It consists of a client-side program representing patients and a server-side program that saves patient information in a Redis database. The server supports multithreading to handle multiple patient connections simultaneously.

## Features

- **Client Simulation**: Represents patients generating temperature readings.
- **Server**: Saves patient information (ID, name, temperature, date, time) in a Redis database.
- **Multithreading**: Server supports handling multiple patient connections concurrently.
- **GUI**: Built using PyQt, connected with the Redis database, displaying patient information in a table.
- **Temperature Graph**: Plot the temperature graph of a selected patient from the table.
- **Search Functionality**: Allows users to search for patients by specific ID.
- **Sorting**: Users can sort the table ascendingly or descendingly by ID or patient name.

## Requirements

- Python 3.x
- Redis Server
- Redis Python library (`pip install redis`)
- PyQt5 (Python GUI library, `pip install PyQt5`)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YoussefHassanien/Real-Time-Medical-Data-Monitoring-System-.git
```

2. Install required Python libraries:

```bash
pip install -r requirements.txt
```

3. Ensure Redis server is running.

## Usage

1. Start the server:

```bash
python server.py
```

2. Run the client(s):

```bash
python client.py
```

3. Launch the GUI:

```bash
python gui.py
```

4. Use the GUI to view patient information, plot temperature graphs, search for patients, and sort the table.

## Contributors

- [Youssef Hassanien](https://github.com/YoussefHassanien)
- [Ghada Elboghdady](https://github.com/ghada-elboghdady)

## Copyright

This project is developed as part of the Cairo University Biomedical and Healthcare Data Engineering Credit Hours System Medical Distributed Application Development Course. All rights reserved to Cairo University.

## Acknowledgements

This project is submitted to Eng Yahya Al-Ariny and Dr Hesham Aarafat for their guidance and support.