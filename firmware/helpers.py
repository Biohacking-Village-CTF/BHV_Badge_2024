import machine
import uhashlib
import urandom
import ubinascii

class Helpers:
    def __init__(self):
        self.device_name = None
        self.get_device_name()

    def pad_with_zeros(self, number, width):
        number_str = str(number)
        while len(number_str) < width:
            number_str = '0' + number_str
        return number_str

    def get_device_name(self):
        # Get the unique ID as bytes
        unique_id_bytes = machine.unique_id()
    
        # Calculate the hash of the unique ID using uhashlib
        unique_id_hash = uhashlib.sha256(unique_id_bytes).digest()
        # #print the last 4 bytes of the hash
        # print(ubinascii.hexlify(unique_id_hash[-3:]))
        # # Calculate the five-digit number
        # four_digit_number = sum(unique_id_hash) & 10000
        
        
        # # Pad the number with leading zeros to ensure it's five digits
        # device_number_str = self.pad_with_zeros(four_digit_number, 4)

        # Convert to a formatted device name
        self.device_name = 'AMB-' + ubinascii.hexlify(unique_id_hash[-3:]).decode()

        print('Device Name:', self.device_name)

    def generate_password(self, length=12):
        # Define character sets
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special_characters = '!@#$%&-'

        # Combine all character sets
        all_characters = lowercase + uppercase + digits + special_characters

        # Generate a random password
        password = ''.join(urandom.choice(all_characters) for _ in range(length))
        return password