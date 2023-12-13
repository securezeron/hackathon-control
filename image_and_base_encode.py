from stegano import lsb
from PIL import Image

import base64

# Encode a message into base64--------------------------------------------
def encode_to_base64(message):
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message

# Decode a base64 message
def decode_from_base64(base64_message):
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    decoded_message = message_bytes.decode('utf-8')
    return decoded_message
# Encode a message into base64--------------------------------------------


#steganogarphy-------------------------------------------------------------
# Encode message into image
def encode_message(image_path, message, output_path):
    secret = lsb.hide(image_path, message)
    secret.save(output_path)

# Decode message from image
def decode_message(image_path):
    secret = lsb.reveal(image_path)
    return secret
#steganogarphy-------------------------------------------------------------

# Example usage
image_path = "static/images/myimage.jpg"
message_to_hide = "zero_one-level-1-000000000111101909091111"

# Encode the message into base64
encoded_message = encode_to_base64(message_to_hide)
print("Encoded Message:", encoded_message)

# Encode the message into the image
encoded_image_path = "static/images/image.png"
encode_message(image_path, encoded_message, encoded_image_path)


