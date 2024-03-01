
from sym.modules.utils.openaiapi import create_dalle_image

if __name__ == "__main__":
    prompt = "NASA Astronauts Accidentally Drop Tool Bag During Spacewalk"
    image_url = create_dalle_image(prompt=prompt)
    print(prompt, image_url)