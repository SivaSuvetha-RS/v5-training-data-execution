def create_loss_mask(sequence):
    return [1 if token != 0 else 0 for token in sequence]


def create_attention_mask(sequence):
    return [1 if token != 0 else 0 for token in sequence]


def create_position_ids(sequence):
    return list(range(len(sequence)))