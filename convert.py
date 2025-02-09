from PIL import Image
import numpy as np
import sys


def convert_to_rgb565(image_path, output_path, width=240, height=300):
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

    # Save to output file
    with open(output_path, "wb") as f:
        f.write(rgb565_le)

    print(f"RGB565 binary saved to: {output_path} (Size: {len(rgb565_le)} bytes)")

    # Debugging Output
    print(
        "First 10 packed RGB565 values:", rgb565.flatten()[:10]
    )  # Expect: [65535, 65535, ...]
    print(
        "First 20 bytes in output:", list(rgb565_le[:20])
    )  # Expect: [255, 255, 255, 255, ...]


# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} input_image.png output_file.bin")
        sys.exit(1)

    input_image_path = sys.argv[1]
    output_binary_path = sys.argv[2]

    convert_to_rgb565(input_image_path, output_binary_path)
