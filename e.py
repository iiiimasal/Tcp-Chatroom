def setPermutationOrder(key):
    keyMap = {}
    for i, char in enumerate(key):
        keyMap[char] = i
    return keyMap

def encryptMessage(msg, key):
    col = len(key)
    row = len(msg) // col
    if len(msg) % col:
        row += 1
    matrix = [['_' for _ in range(col)] for _ in range(row)]
    
    k = 0
    for i in range(row):
        for j in range(col):
            if msg[k] == '\0':
                matrix[i][j] = '_'
            elif msg[k].isalpha() or msg[k] == ' ':
                matrix[i][j] = msg[k]
            k += 1
    
    keyMap = setPermutationOrder(key)
    cipher = ''
    for _, j in sorted(keyMap.items()):
        for i in range(row):
            if matrix[i][j].isalpha() or matrix[i][j] == ' ' or matrix[i][j] == '_':
                cipher += matrix[i][j]
    
    return cipher

# Example usage
plaintext = "Geeks for Geeks"
key = "HACK"
encrypted_text = encryptMessage(plaintext, key)
print("Encrypted message:", encrypted_text)