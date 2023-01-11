from hashlib import sha256

def get_coin_id(parent_coin : bytes, puzzle_hash : bytes, amount : bytes):
    buffer = bytearray()
    buffer.extend(parent_coin)
    buffer.extend(puzzle_hash)
    buffer.extend(amount)
    sha256Hasher = sha256()
    sha256Hasher.update(buffer)
    return sha256Hasher.hexdigest()

'''
0x660ca330f8f41cf79cea9a2b813626b8730c0b3cce9ba7c194c1f8018876ae2b
'''