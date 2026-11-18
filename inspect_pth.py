import torch
import sys

class CustomDataset:
    pass

try:
    obj = torch.load('leaf_best.pth', map_location='cpu', weights_only=False)
    print("Type of loaded object:", type(obj))
    if isinstance(obj, dict):
        print("Keys:", obj.keys())
except Exception as e:
    print("Error:", e)
