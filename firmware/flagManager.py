from tinydb import TinyDB, Query
import ucryptolib
import ubinascii
import uhashlib
import os

class FlagManager:
    def __init__(self, device_id):
        dbName = 'encrypted_db.json'
        encryption_key = b'donothardcodekey'
        self.encryption_cipher = ucryptolib.aes(encryption_key, 1)
        self.decryption_cipher = ucryptolib.aes(encryption_key, 1)
        self.device_name = device_id.replace("-", "")        
        self.db = None
        self.table = None

        # Check If File Exists
        try:
            os.stat(dbName)
            print("DB File Exists")
            self.db = TinyDB(dbName)
            self.table = self.db.table('flags')
        except OSError:
            self.init_flags(dbName) 

    def capitalize_word(self, word):
        capitalized_word = word[0].upper() + word[1:]
        return capitalized_word

    def encrypt(self, data):
        data = data.encode()
        padded_data = data + b'\x00' * ((16 - (len(data) % 16)) % 16)
        encrypted_data = self.encryption_cipher.encrypt(padded_data)
        return ubinascii.hexlify(encrypted_data).decode('utf-8')

    def decrypt(self, data):
        try:
            encrypted_bytes = ubinascii.unhexlify(data.encode())
            decrypted_data = self.decryption_cipher.decrypt(encrypted_bytes)
            return decrypted_data.rstrip(b'\x00').decode('utf-8')
        except ValueError as e:
            return f"Decryption Error: {e}"

    def to_leet(self, text):
        leet_mapping = {
            'A': '4', 'B': '8', 'E': '3', 'G': '9', 'L': '1',
            'O': '0', 'S': '5', 'T': '7', 'Z': '2'
        }
        return ''.join(leet_mapping.get(char.upper(), char) for char in text)
    
    def last_5_characters_of_hash(self, text):
        hash_object = uhashlib.sha256(text.encode())
        hash_bytes = hash_object.digest()
        hex_digest = ubinascii.hexlify(hash_bytes).decode('utf-8')      
        return hex_digest[-5:].upper()

    def init_flags(self, dbName):
        print("Creating Encrypted Database")
        flags_data = {
            'easy': {}, 'comms': {}, 'dial': {}, 'credits': {},
            'firmware': {}, 'authorized': {}, 'respond': {}, 'secured': {}
        }
        self.db = TinyDB(dbName)
        self.table = self.db.table('flags')
        for index, flag in enumerate(flags_data):
            flag_data = self.to_leet(f"{flag}_{index}".upper().replace("-", ""))
            if( flag == 'credits' ):
                flag_value = f"BHV_{flag_data}_01234"
            elif( flag == 'firmware' ):
                flag_value = f"BHV_{flag_data}_56789"
            elif( flag == 'easy' ):
                flag_value = f"BHV_{flag_data}_NY9845"
            else:
                suffix = self.last_5_characters_of_hash(f"BHV_{self.device_name}_{flag_data}")
                flag_value = f"BHV_{self.device_name}_{flag_data}_{suffix}"
            encrypted_data = self.encrypt(flag_value)
            search_result = self.table.search(Query().flag == flag)
            if not search_result:
                self.table.insert({'flag': flag, 'data': encrypted_data, 'status': False})
            else:
                self.table.update({'data': encrypted_data, 'status': False}, Query().flag == flag)

    def check_flag(self, flag, guess):
        encrypted_guess = self.encrypt(guess)
        search_result = self.table.search(Query().flag == flag)[0]
        print(f"Search Result: {search_result['data']}")
        print(f"Encrypted Guess: {encrypted_guess}")
        return search_result['data'] == encrypted_guess

    def retrieve_flag(self, flag):
        search_result = self.table.search(Query().flag == flag)
        if search_result:
            decrypted_data = self.decrypt(search_result[0]['data'])
            return decrypted_data
        return None    
    
    def set_flag_status(self, flag, status):
        query = Query()
        result = self.table.search(query.flag == flag)
        if result:
            self.table.update({'status': status}, query.flag == flag)
            print(f"Status of '{flag}' updated to: {'Captured' if status else 'Not Captured'}")
        else:
            print(f"No such flag '{flag}' found in the database.")

    def get_flags_status(self):
        flags_status = {}
        for item in self.table:
            flags_status[self.capitalize_word(item['flag'])] = item['status']
        return flags_status
    
    def get_captured_flag_count(self):
        captured_flag_count = 0
        for item in self.table:
            if( item['status'] ):
                captured_flag_count = captured_flag_count + 1
        return captured_flag_count