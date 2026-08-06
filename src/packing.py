class PackingEngine:

    def pack(self, tokens, sequence_length=32):
        packed = []

        for i in range(0, len(tokens), sequence_length):
            seq = tokens[i:i+sequence_length]

            if len(seq) < sequence_length:
                seq += [0] * (sequence_length - len(seq))

            packed.append(seq)

        return packed
