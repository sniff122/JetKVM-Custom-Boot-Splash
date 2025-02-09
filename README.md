# Custom JetKVM Boot Splash Screen

This allows you to convert a PNG image to a boot splash screen for JetKVM.

The boot splash screen is a framebuffer image that is stored at `/oem/usr/share/fb_init` on the JetKVM device.

There is a `convert.py` script that will convert a PNG image to the correct format, which you can manually write to the framebuffer over SSH like this:

```bash
python3 convert.py splash.png output.bin
cat output.bin | ssh root@<ip> "cat > /dev/fb0"
```

# Usage

Note that the image must be 240x300 and 8 bit color depth. Additionally, the display is rotated 90 degrees, so the image should be rotated accordingly (90 degrees clockwise).

1. Install the required dependencies:

```bash
pip3 install -Ur requirements.txt
```

2. Enable SSH on the JetKVM device:

  1. Go to the JetKVM web interface
  2. Go to `Settings` and scroll down to `Advanced`
  3. Enable Developer Mode and add your SSH key

3. Run the `convert-and-bootsplash.py` script:

```bash
python3 convert-and-bootsplash.py splash.png remote_host username ssh_key_path
```

This will convert your image to the correct format and write it to the boot splash screen on the JetKVM device. It will also make a backup of the existing boot splash screen as `fb_init.old` if it didn't already exist.

# Disclaimer

This script is provided as-is and may not work as expected. Use at your own risk. I am not responsible for any damage caused by this script.
