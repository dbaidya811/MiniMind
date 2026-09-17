from datasets import load_dataset

def load_custom_dataset(train_path="data/train.jsonl", val_path="data/val.jsonl"):
    """Load train and validation datasets from JSONL files."""
    data_files = {"train": train_path}
    if val_path:
        data_files["validation"] = val_path
    dataset = load_dataset("json", data_files=data_files)
    return dataset