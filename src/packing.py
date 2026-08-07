class PackingEngine:
    def pack(self, tokens, sequence_length=32, policy="pad_only"):
        """Pack tokens into fixed-length sequences.

        Supported policies:
        - pad_only: split tokens into fixed-size sequences and pad the final sequence.
        - truncate: cut tokens into fixed-size sequences, dropping any remainder shorter than sequence_length.
        - concat: same as pad_only for a single stream of tokens.
        """
        if not tokens:
            return []

        packed = []
        if policy == "truncate":
            for index in range(0, len(tokens), sequence_length):
                seq = tokens[index:index + sequence_length]
                if len(seq) == sequence_length:
                    packed.append(seq)
            return packed

        for index in range(0, len(tokens), sequence_length):
            seq = tokens[index:index + sequence_length]
            if len(seq) < sequence_length:
                seq += [0] * (sequence_length - len(seq))
            packed.append(seq)

        return packed

    def pack_with_padding(self, tokens, sequence_length=32):
        return self.pack(tokens, sequence_length=sequence_length, policy="pad_only")
