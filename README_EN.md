# Minecraft Server Manager - Guide (English)

This Flask app allows you to manage Minecraft server versions.

## Requirements

- Python 3
- `pip install flask`

## Run

To start the site:

```bash
python app.py
```

The site will be available at `http://localhost:5090`

## Features

- Homepage: shows all saved Minecraft versions
- Add: lets you add a new version
- Server management:
  - Download: downloads the `.jar` file from the saved link
  - Start: runs the server with Java
  - Restart: restarts the server
  - Stop: stops the server
  - Delete: removes the version from the database

## Add a Version

Example to use:

- Name: `1.20.4`
- Link: `https://piston-data.mojang.com/v1/objects/8dd1a28015f51b1803213892b50b7b4fc76e594d/server.jar`

You can find more versions here:  
👉 https://jars.vexyhost.com/

## Folders

Server files are saved in `./server-file/<version>`
