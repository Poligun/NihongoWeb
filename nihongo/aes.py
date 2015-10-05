import math, hashlib, random

BitMask = [1 << i for i in range(8)]

Modulus = [1, 1, 0, 1, 1, 0, 0, 0, 1]

def addBytes(byte1, byte2):
    """
    >>> addBytes(0x57, 0x83) == 0xd4
    True
    """
    return byte1 ^ byte2

def trimArray(array):
    """
    >>> trimArray([0 for _ in range(10)]) == [0]
    True
    >>> trimArray([1, 0, 0, 0, 0, 0, 0, 0])
    [1]
    """
    for i in range(len(array) - 1, -1, -1):
        if array[i] != 0:
            return array[:i + 1]
    return [0]

def byteToArray(byte):
    return [1 if byte & BitMask[i] else 0 for i in range(len(BitMask))]

def arrayToByte(array):
    byte = 0
    for i in range(len(array) - 1, -1, -1):
        byte <<= 1
        if array[i] == 1:
            byte += 1
    return byte

def addArray(array1, array2):
    if len(array1) < len(array2):
        array1, array2 = array2, array1
    sum = array1[:]
    for i in range(len(array2)):
        sum[i] ^= array2[i]
    return trimArray(sum)

def mulArray(array1, array2):
    result = [0 for i in range(len(array1) + len(array2) - 1)]
    for i in range(len(array1)):
        for j in range(len(array2)):
            if array1[i] == 1 and array2[j] == 1:
                result[i + j] += 1
    return trimArray([1 if v & 1 else 0 for v in result])

def divArray(array1, array2):
    remainder = array1[:]
    quotient = [0 for _ in range(len(array1))]
    lengthOfArray2 = len(array2)
    for i in range(len(remainder) - 1, lengthOfArray2 - 2, -1):
        if remainder[i] == 0:
            continue
        for j in range(lengthOfArray2):
            remainder[i - j] ^= array2[lengthOfArray2 - j - 1]
        quotient[i - lengthOfArray2 + 1] = 1
    return trimArray(quotient), trimArray(remainder)

def mulBytes(byte1, byte2):
    """
    >>> mulBytes(0x57, 0x83) == 0xc1
    True
    """
    counter = [0 for i in range(15)]
    for i in range(8):
        for j in range(8):
            if byte1 & BitMask[i] and byte2 & BitMask[j]:
                counter[i + j] += 1
    counter = [1 if v & 1 else 0 for v in counter]
    quotient, remainder = divArray(counter, Modulus)
    return arrayToByte(remainder)

def extendedGCD(array1, array2):
    s, oldS = [0], [1]
    t, oldT = [1], [0]
    r, oldR = array2, array1
    while r != [0]:
        quotient, remainder = divArray(oldR, r)
        oldR, r = r, addArray(oldR, mulArray(quotient, r))
        oldS, s = s, addArray(oldS, mulArray(quotient, s))
        oldT, t = t, addArray(oldT, mulArray(quotient, t))
    return oldS, oldT, oldR

def mulInverse(byte):
    """
    >>> mulInverse(0x00) == 0x00
    True
    """
    x, y, gcd = extendedGCD(byteToArray(byte), Modulus)
    quotient, remainder = divArray(x, Modulus)
    return arrayToByte(remainder)

MulInverseTable = [mulInverse(i) for i in range(0xff + 1)]

SBox = [
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
    [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
    [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
    [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
    [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
    [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
    [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
    [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
    [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
    [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
    [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16],
]

InverseSBox = [
    [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb],
    [0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb],
    [0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e],
    [0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25],
    [0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92],
    [0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84],
    [0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06],
    [0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b],
    [0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73],
    [0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e],
    [0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b],
    [0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4],
    [0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f],
    [0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef],
    [0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61],
    [0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d],
]

"""
InverseSBox = [[0 for c in range(16)] for r in range(16)]
for r in range(16):
    for c in range(16):
        byte = SBox[r][c]
        InverseSBox[byte >> 4][byte & 0x0f] = (r << 4) + c
"""

def subBytes(state):
    return list(map(lambda byte: SBox[byte >> 4][byte & 0x0f], state))

def inverseSubBytes(state):
    return list(map(lambda byte: InverseSBox[byte >> 4][byte & 0x0f], state))

ShiftAmount = { 4: [0, 1, 2, 3] }

def shiftRows(state, Nb = 4):
    newState = []
    for c in range(Nb):
        for r in range(4):
            col = (c + ShiftAmount[Nb][r]) % Nb
            newState.append(state[col * 4 + r])
    return newState

def inverseShiftRows(state, Nb = 4):
    newState = [0 for _ in range(len(state))]
    for c in range(Nb):
        for r in range(4):
            col = (c + ShiftAmount[Nb][r]) % Nb
            newState[col * 4 + r] = state[c * 4 + r]
    return newState

def mixColumns(state, Nb = 4):
    newState = []
    for c in range(Nb):
        newState += mulWords([0x02, 0x01, 0x01, 0x03], state[c * 4 : (c + 1) * 4])
    return newState

def inverseMixColumns(state, Nb = 4):
    newState = []
    for c in range(Nb):
        newState += mulWords([0x0e, 0x09, 0x0d, 0x0b], state[c * 4 : (c + 1) * 4])
    return newState

def addRoundKey(state, expandedKey, round, Nb = 4):
    newState = []
    for c in range(Nb):
        for r in range(4):
            newState.append(state[c * 4 + r] ^ expandedKey[round * Nb + c][r])
    return newState

def addWords(word1, word2):
    return [word1[i] ^ word2[i] for i in range(len(word1))]

def mulWords(word1, word2):
    return [
        mulBytes(word1[0], word2[0]) ^ mulBytes(word1[3], word2[1]) ^ mulBytes(word1[2], word2[2]) ^ mulBytes(word1[1], word2[3]),
        mulBytes(word1[1], word2[0]) ^ mulBytes(word1[0], word2[1]) ^ mulBytes(word1[3], word2[2]) ^ mulBytes(word1[2], word2[3]),
        mulBytes(word1[2], word2[0]) ^ mulBytes(word1[1], word2[1]) ^ mulBytes(word1[0], word2[2]) ^ mulBytes(word1[3], word2[3]),
        mulBytes(word1[3], word2[0]) ^ mulBytes(word1[2], word2[1]) ^ mulBytes(word1[1], word2[2]) ^ mulBytes(word1[0], word2[3])
    ]
    """
    return [
        (word1[0] * word2[0]) ^ (word1[3] * word2[1]) ^ (word1[2] * word2[2]) ^ (word1[1] * word2[3]),
        (word1[1] * word2[0]) ^ (word1[0] * word2[1]) ^ (word1[3] * word2[2]) ^ (word1[2] * word2[3]),
        (word1[2] * word2[0]) ^ (word1[1] * word2[1]) ^ (word1[0] * word2[2]) ^ (word1[3] * word2[3]),
        (word1[3] * word2[0]) ^ (word1[2] * word2[1]) ^ (word1[1] * word2[2]) ^ (word1[0] * word2[3])
    ]
    """

def subWord(word): 
    return [SBox[byte >> 4][byte & 0x0f] for byte in word]

def rotWord(word):
    return word[1:] + word[:1]

def bytesToHexString(bytes):
    return ''.join('%2.2x' % b for b in bytes)

def hexStringToBytes(string, hexLength = 2):
    return [int(string[i : i + hexLength], 16) for i in range(0, len(string), hexLength)]

def expandKey(key, Nb = 4):
    """
    >>> key128 = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    >>> bytesToHexString(expandKey(key128)[-1])
    'b6630ca6'
    >>> key192 = [0x8e, 0x73, 0xb0, 0xf7, 0xda, 0x0e, 0x64, 0x52, 0xc8, 0x10, 0xf3, 0x2b, 0x80, 0x90, 0x79, 0xe5, 0x62, 0xf8, 0xea, 0xd2, 0x52, 0x2c, 0x6b, 0x7b]
    >>> bytesToHexString(expandKey(key192)[-1])
    '01002202'
    >>> key256 = [0x60, 0x3d, 0xeb, 0x10, 0x15, 0xca, 0x71, 0xbe, 0x2b, 0x73, 0xae, 0xf0, 0x85, 0x7d, 0x77, 0x81, 0x1f, 0x35, 0x2c, 0x07, 0x3b, 0x61, 0x08, 0xd7, 0x2d, 0x98, 0x10, 0xa3, 0x09, 0x14, 0xdf, 0xf4]
    >>> bytesToHexString(expandKey(key256)[-1])
    '706c631e'
    """
    Nk = len(key) // 4
    Nr = 10 if Nk == 4 else 12 if Nk == 6 else 14

    Rcon = [0, 1]
    for i in range(2, Nb * (Nr + 1) // Nk + 1):
        Rcon.append(Rcon[i - 1] << 1)
        if Rcon[i] > 0xff:
            Rcon[i] = (Rcon[i] & 0xff) ^ 0x1b
    Rcon = [[v, 0, 0, 0] for v in Rcon]

    expandedKey = [[key[4 * i], key[4 * i + 1], key[4 * i + 2], key[4 * i + 3]] for i in range(Nk)]
    for i in range(Nk, Nb * (Nr + 1)):
        temp = expandedKey[i - 1]
        if i % Nk == 0:
            temp = addWords(subWord(rotWord(temp)), Rcon[i // Nk])
        elif Nk > 6 and i % Nk == 4:
            temp = subWord(temp)
        expandedKey.append(addWords(expandedKey[i - Nk], temp))
    return expandedKey

def generateKey(length = 128):
    random.seed()
    return [random.randint(0x00, 0xff) for _ in range(length)]

def stateToString(state, Nb = 4):
    return '\n'.join(' '.join('%2.2x' % state[c * 4 + r] for c in range(Nb)) for r in range(4))

def cipher(input, expandedKey, Nr, Nb = 4):
    """
    >>> inputBytes = [0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d, 0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34]
    >>> cipherKey  = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    >>> bytesToHexString(cipher(inputBytes, expandKey(cipherKey), 10))
    '3925841d02dc09fbdc118597196a0b32'
    """
    state = addRoundKey(input, expandedKey, round = 0)
    for round in range(1, Nr):
        state = subBytes(state)
        state = shiftRows(state)
        state = mixColumns(state)
        state = addRoundKey(state, expandedKey, round = round)
    state = subBytes(state)
    state = shiftRows(state)
    state = addRoundKey(state, expandedKey, round = Nr)
    return state

def inverseCipher(input, expandedKey, Nr, Nb = 4):
    """
    >>> cipherKey  = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    >>> bytesToHexString(inverseCipher(hexStringToBytes('3925841d02dc09fbdc118597196a0b32'), expandKey(cipherKey), 10))
    '3243f6a8885a308d313198a2e0370734'
    """
    state = addRoundKey(input, expandedKey, round = Nr)
    for round in range(Nr - 1, 0, -1):
        state = inverseShiftRows(state)
        state = inverseSubBytes(state)
        state = addRoundKey(state, expandedKey, round = round)
        state = inverseMixColumns(state)
    state = inverseShiftRows(state)
    state = inverseSubBytes(state)
    state = addRoundKey(state, expandedKey, round = 0)
    return state

def integerToDword(integer):
    dword = []
    for _ in range(8):
        dword.append(integer & 0xff)
        integer >>= 8
    return dword

def dwordToInteger(dword):
    integer = 0
    for i in range(7, -1, -1):
        integer = (integer << 8) + dword[i]
    return integer

def encryptBytes(inputBytes, key, sha1Hash = False):
    Nb = 4
    Nk = len(key) // 4
    Nr = 10 if Nk == 4 else 12 if Nk == 6 else 14
    expandedKey = expandKey(key, Nb = Nb)

    if sha1Hash:
        inputBytes = integerToDword(len(inputBytes)) + list(hashlib.sha1(inputBytes).digest()) + list(inputBytes)
    else:
        inputBytes = integerToDword(len(inputBytes)) + list(inputBytes)

    if len(inputBytes) % (Nb * 4) != 0:
        inputBytes += [0 for _ in range(math.ceil(len(inputBytes) / (Nb * 4)) * Nb * 4 - len(inputBytes))]

    outputBytes = []
    for i in range(0, len(inputBytes), Nb * 4):
        outputBytes += cipher(inputBytes[i : i + Nb * 4], expandedKey, Nr)

    return outputBytes

def encryptString(string, key, encoding = 'utf8'):
    return bytesToHexString(encryptBytes(string.encode(encoding), key))

def decryptBytes(inputBytes, key, sha1Hash = False):
    Nb = 4
    Nk = len(key) // 4
    Nr = 10 if Nk == 4 else 12 if Nk == 6 else 14
    expandedKey = expandKey(key, Nb = Nb)

    outputBytes = []
    for i in range(0, len(inputBytes), Nb * 4):
        outputBytes += inverseCipher(inputBytes[i : i + Nb * 4], expandedKey, Nr)

    byteLength = dwordToInteger(outputBytes[:8])
    if (sha1Hash and 28 + byteLength > len(outputBytes)) or \
       (not sha1Hash and 8 + byteLength > len(outputBytes)):
        raise Exception('Byte length doesn\'t match the meta data.')

    if sha1Hash:
        sha1Digest = outputBytes[8:28]
        outputBytes = bytes(outputBytes[28 : 28 + byteLength])
        newDigest = list(hashlib.sha1(outputBytes).digest())
        if newDigest != sha1Digest:
            raise Exception('Sha1 digest doesn\'t match the meta data.')
    else:
        outputBytes = bytes(outputBytes[8: 8 + byteLength])
    return outputBytes

def decryptString(hexCipherString, key, encoding = 'utf8'):
    return decryptBytes(hexStringToBytes(hexCipherString), key).decode(encoding)

def encryptFile(inputPath, outputPath, key):
    outputBytes = encryptBytes(open(inputPath, 'rb').read(), key)
    open(outputPath, 'wb').write(bytes(outputBytes))

def decryptFile(inputPath, outputPath, key):
    outputBytes = decryptBytes(open(inputPath, 'rb').read(), key)
    open(outputPath, 'wb').write(bytes(outputBytes))

if __name__ == '__main__':
    import time
    key = [0x60, 0x3d, 0xeb, 0x10, 0x15, 0xca, 0x71, 0xbe, 0x2b, 0x73, 0xae, 0xf0, 0x85, 0x7d, 0x77, 0x81, 0x1f, 0x35, 0x2c, 0x07, 0x3b, 0x61, 0x08, 0xd7, 0x2d, 0x98, 0x10, 0xa3, 0x09, 0x14, 0xdf, 0xf4]
    startTime = time.time()
    encryptFile('aes.py', 'aes.py.encrypted', key)
    endTime = time.time()
    print('Time Cost: {:2F}ms'.format((endTime - startTime) * 1000))
    #decryptFile('aes.py.encrypted', 'aes.py.decrypted', key)
