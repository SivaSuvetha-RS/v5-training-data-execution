class PackingEngine:
    def pack(self, tokens, sequence_length=32, policy="default"):
        packed = []
        if not tokens:
            return packed

        for index in range(0, len(tokens), sequence_length):
            seq = tokens[index:index + sequence_length]
            if len(seq) < sequence_length:
                seq += [0] * (sequence_length - len(seq))
            packed.append(seq)

        if len(tokens) % sequence_length == 0:
            packed.append([0] * sequence_length)
            return packed

        if len(packed) == 0 or len(packed[-1]) == sequence_length:
            packed.append([0] * sequence_length)

        return packed

    def pack_with_padding(self, tokens, sequence_length=32):
        return self.pack(tokens, sequence_length=sequence_length)
