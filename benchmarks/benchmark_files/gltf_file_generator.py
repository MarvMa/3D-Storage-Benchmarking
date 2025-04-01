import base64

from pygltflib import GLTF2, Buffer, Scene
import os


def create_embedded_dummy_gltf(filename, target_size_bytes):

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
    sizes = {
        "small_model": 0.5 * 1024 * 1024,  # ~0.5MB
        "medium_model": 5 * 1024 * 1024,  # ~5MB
        "large_model": 50 * 1024 * 1024,  # ~50MB
    }

    for name, size in sizes.items():
        gltf_filename = f"{name}.gltf"
        create_embedded_dummy_gltf(gltf_filename, size)
