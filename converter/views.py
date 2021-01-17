from django.shortcuts import render

import json
from typing import List


class AConverter:
    def __init__(self,
                 max_string_len=4,
                 bin_num_length=8):
        self.max_string_len = max_string_len
        self.bin_num_length = bin_num_length
        self.encoded_length = max_string_len * bin_num_length

    def encode(self, s: str):
        return [self._encode(s[i:i + self.max_string_len]) for i in range(0, len(s), self.max_string_len)]

    def decode(self, code: List[int]):
        return ''.join(self._decode(n) for n in code)

    def _encode(self, s: str):
        # validate
        if len(s) > 4:
            raise ValueError(f'Converter: encode: the length of the received input is {len(s)}, expected: <=4')

        # convert each bit to 8byte string
        strings = [self._chr_to_8byte(char) for char in reversed(s)]
        # pad zeros if needed
        strings = ['0' * self.bin_num_length, ] * (self.max_string_len - len(strings)) + strings
        s = self._scramble(strings)
        # hex_string = self._bin_to_hex(s)
        # return int(hex_string, base=16)
        return int(s, base=2)

    def _decode(self, s: int):
        s = str(bin(s))[2:]
        s = '0' * (self.encoded_length - len(s)) + s
        unscrambled = self._unscramble(s)
        while unscrambled[0] == '0' * self.bin_num_length:
            unscrambled.pop(0)
        s = [self._8byte_to_chr(b) for b in reversed(unscrambled)]
        return ''.join(s)

    def _chr_to_8byte(self, s: str) -> str:
        s = str(bin(ord(s)))[2:]
        s = '0' * (self.bin_num_length - len(s)) + s  # enforce having 8 digits
        return s

    def _8byte_to_chr(self, s: str) -> str:
        # convert to char
        s = chr(int(s, base=2))
        return s

    def _scramble(self, strings: List[str]) -> str:
        # validate
        if len(strings) != self.max_string_len:
            raise ValueError(f"""
            Converter: _scramble:
            the length of the received list of strings is {len(strings)},
             expected: {self.max_string_len}
             """)
        for s in strings:
            if len(s) != self.bin_num_length:
                raise ValueError(f"""
                Converter: _scramble:
                 the length of one of the input strings is {len(strings)},
                  expected: {self.bin_num_length}
                  """)
        # scramble
        return ''.join(''.join(seq) for seq in zip(*strings))

    def _bin_to_hex(self, s: str) -> str:
        return hex(int(s, base=2))

    def _hex_to_bin(self, s: str) -> str:
        return str(bin(int(s, base=16)))[2:]

    def _unscramble(self, s: str) -> List[str]:
        # validate
        if len(s) != 32:
            raise ValueError(f"""
            Converter: _unscramble:
             the length of the received string is {len(s)}, expected: 32
             """)

        # unscramble
        decoded = list()
        for i in range(self.max_string_len):
            decoded.append(s[i::self.max_string_len])
        return decoded


def home_view(request):
    context = {'input':'', 'output':''}
    if request.method == 'POST':
        input = request.POST.get('input')
        c = AConverter()
        output = c.decode(json.loads(input)) if 'decode' in request.path else c.encode(input)
        context = {'input': input, 'output': output}
    return render(request, 'home.html', context)
