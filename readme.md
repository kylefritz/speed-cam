# Speed Camera

I mounted an AWS Deep Lense camera at my house. I'm using this repo to develop a computer vision system for tracking the speed of passing cars.

<table>
    <tr>
        <td><img src="build-photos/outside.jpg" height="300"></td>
        <td><img src="build-photos/outside-closeup.jpg" height="300"></td>
    </tr>
    <tr>
        <td><img src="build-photos/inside.jpg" height="300"></td>
        <td><img src="build-photos/inside-closeup.jpg" height="300"></td>
    </tr>
</table>

## setup
```
pip install -r requirements.txt
honcho start
# setup STORAGE_ROOT, hardcoded to /mnt/usb-sd
```


## env suggestions
 * use [pyenv](https://github.com/pyenv/pyenv)
 * `pyenv install` will install the right python from the `.python-version` file
