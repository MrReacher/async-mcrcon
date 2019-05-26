# async-mcrcon

## Description
- `async_mcrcon.py` is a module you can import from your own python code to send commands to a minecraft server and read responses.
- `async_mcrcon.py` is the async version of [mcrcon.py](https://github.com/barneygale/MCRcon/blob/master/mcrcon.py)

## Usage
```py
from async_mcrcon import MinecraftClient

async with MinecraftClient('1.3.3.7', 25575, 'password') as mc:
  output = await mc.send('list')
  print(output)
```

## Requirements
**Python3.5 or higher is required.**
