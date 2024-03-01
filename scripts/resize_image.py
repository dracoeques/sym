from PIL import Image

def resize_image(input_image_path, output_image_path, size):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize(size)
    resized_image.save(output_image_path)

def create_various_sizes(input_image_path):
    base_path, extension = input_image_path.rsplit('.', 1)

    # Define sizes for tiny, small, and medium
    sizes = {
        'tiny': (64, 64),  # Tiny size
        'small': (128, 128),  # Small size
        'medium': (256, 256)  # Medium size
    }

    # Loop through each size category and resize + save the image
    for size_name, dimensions in sizes.items():
        output_path = f"{base_path}_{size_name}.{extension}"
        resize_image(input_image_path, output_path, dimensions)
        print(f"Image saved as {output_path} with size {dimensions}")

# Example usage
input_image_path = './data/sym-avatar.png'  # Update this path to your image file
create_various_sizes(input_image_path)
