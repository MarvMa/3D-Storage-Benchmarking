import base64

from pygltflib import GLTF2, Buffer, Scene


def create_embedded_dummy_gltf(filename, target_size_bytes):
    """Generates a minimal glTF 2.0 file with an embedded dummy buffer for testing.

        Creates a self-contained .gltf file  with a base64-encoded buffer
        of null bytes, approximating the target size when loaded by applications.

        Args:
            filename (str): Output path for the generated glTF file
            target_size_bytes (int): Desired *decoded* payload size in bytes.
                Actual file size will be ~33% larger due to base64 encoding.

        Note:
            Uses 1.35 divisor to approximate base64 inflation (1/0.74 ≈ 1.35).
            Buffer contains only null bytes (\\x00) for predictable compression.
        """
    raw_buffer_size = int(target_size_bytes / 1.35)
    data = b'\0' * raw_buffer_size
    encoded_data = base64.b64encode(data).decode("utf-8")
    data_uri = "data:application/octet-stream;base64," + encoded_data

    gltf = GLTF2()
    gltf.buffers = [Buffer(byteLength=raw_buffer_size, uri=data_uri)]
    gltf.scenes = [Scene(nodes=[])]
    gltf.scene = 0

    # Save the self-contained glTF file
    gltf.save(filename)
    print(f"Created {filename} with an embedded buffer of {raw_buffer_size} bytes.")


if __name__ == "__main__":
    """Generates test models with different payload sizes when executed directly.

        Creates three glTF files:
        - small_model.gltf:  ~0.5MB decoded (≈0.68MB file size)
        - medium_model.gltf: ~5MB decoded (≈6.8MB file size) 
        - large_model.gltf:  ~50MB decoded (≈68MB file size)

        Files contain no meshes or textures - only buffer data for size testing.
        """

    sizes = {
        "small_model": 1 * 512 * 1024,  # ~0.5MB
        "medium_model": 5 * 1024 * 1024,  # ~5MB
        "large_model": 50 * 1024 * 1024,  # ~50MB
    }

    for name, size in sizes.items():
        gltf_filename = f"{name}.gltf"
        create_embedded_dummy_gltf(gltf_filename, size)
