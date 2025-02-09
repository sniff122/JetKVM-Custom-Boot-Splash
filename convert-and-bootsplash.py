from PIL import Image
import numpy as np
import sys
import paramiko
import getpass


def convert_to_rgb565(image_path, width=240, height=300):
    """
    Converts an image to correctly-sized RGB565 little-endian format (240x300, 144,000 bytes).
    """
    # Open the image, resize to 240x300, and convert to RGB mode
    img = Image.open(image_path).convert("RGB").resize((width, height))

    # Convert image to NumPy array
    arr = np.array(img, dtype=np.uint16)

    # Extract RGB components and pack into 16-bit RGB565 format
    red = (arr[:, :, 0] >> 3) & 0x1F  # 5 bits for red
    green = (arr[:, :, 1] >> 2) & 0x3F  # 6 bits for green
    blue = (arr[:, :, 2] >> 3) & 0x1F  # 5 bits for blue

    # Pack into RGB565 format (R5 G6 B5) and store as uint16
    rgb565 = ((red << 11) | (green << 5) | blue).astype(np.uint16)

    # Convert to little-endian byte order correctly
    rgb565_le = rgb565.astype(
        "<u2"
    ).tobytes()  # Explicitly enforce little-endian 16-bit storage

    return rgb565_le


def send_via_ssh(host, username, key_path, binary_data):
    """
    Sends the given binary data over SSH to a remote machine using an SSH key.
    """
    remote_path = "/oem/usr/share/fb_init"
    try:
        # Create an SSH client instance
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load SSH key with passphrase prompt if necessary
        try:
            private_key = paramiko.RSAKey(filename=key_path)
        except paramiko.ssh_exception.PasswordRequiredException:
            passphrase = getpass.getpass("Enter passphrase for the private key: ")
            private_key = paramiko.RSAKey(filename=key_path, password=passphrase)

        # Connect to the remote server
        ssh.connect(host, port=22, username=username, pkey=private_key)

        # Check if backup file exists, if not, make a copy
        command = "[ ! -f /oem/usr/share/fb_init.old ] && cp /oem/usr/share/fb_init /oem/usr/share/fb_init.old"
        ssh.exec_command(command)

        # Open a shell and send binary data using `dd`
        command = f"cat > {remote_path}"
        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.write(binary_data)
        stdin.channel.shutdown_write()

        # Wait for write to complete
        stdout.channel.recv_exit_status()

        print(
            f"Boot splash image successfully sent to your JetKVM ({host}), rebooting now..."
        )

        command = "reboot"
        ssh.exec_command(command)

        # Close SSH connection
        ssh.close()

    except Exception as e:
        print(f"Error sending data via SSH: {e}")


# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            f"Usage: python {sys.argv[0]} input_image.png remote_host username key_path"
        )
        sys.exit(1)

    input_image_path = sys.argv[1]
    remote_host = sys.argv[2]
    username = sys.argv[3]
    key_path = sys.argv[4]

    # Convert image to RGB565 binary data
    binary_data = convert_to_rgb565(input_image_path)

    # Send binary data over SSH
    send_via_ssh(remote_host, username, key_path, binary_data)
