from __future__ import print_function, with_statement, absolute_import
import sys
if sys.version_info < (3, 0):
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
    PY3 = False
else:
    from io import BytesIO as StringIO
    PY3 = True

import logging
from cloudpickle import CloudPickler
import os
import tempfile
import sys
from torchvision.models.resnet import resnet50
model = resnet50(pretrained=True)
model = model.cuda()
import io
from PIL import Image
from torch.autograd import Variable
import torchvision.transforms as transforms
import torch

min_img_size = 224
transform_pipeline = transforms.Compose([transforms.Resize(min_img_size),
                                         transforms.ToTensor(),
                                         transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                              std=[0.229, 0.224, 0.225])])

def predict(model, inputs):
    def _predict_one(one_input_arr):
        try:
            img = Image.open(io.BytesIO(one_input_arr))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img = transform_pipeline(img)
            img = img.unsqueeze(0)
            img = Variable(img)
            img = img.cuda()
            return [model(img).data.cpu().numpy().argmax()]
        except Exception as e:
            print(e)
            return []
        
    return [_predict_one(i) for i in inputs]

cur_dir = os.path.dirname(os.path.abspath(__file__))
PYTORCH_WEIGHTS_RELATIVE_PATH = "pytorch_weights.pkl"
PYTORCH_MODEL_RELATIVE_PATH = "pytorch_model.pkl"

def save_python_function(name, func):
    predict_fname = "func.pkl"

    # Serialize function
    s = StringIO()
    c = CloudPickler(s, 2)
    c.dump(func)
    serialized_prediction_function = s.getvalue()

    # Set up serialization directory
    serialization_dir = os.path.abspath(tempfile.mkdtemp(suffix='clipper'))
    print("Saving function to {}".format(serialization_dir))

    # Write out function serialization
    func_file_path = os.path.join(serialization_dir, predict_fname)
    if sys.version_info < (3, 0):
        with open(func_file_path, "w") as serialized_function_file:
            serialized_function_file.write(serialized_prediction_function)
    else:
        with open(func_file_path, "wb") as serialized_function_file:
            serialized_function_file.write(serialized_prediction_function)
    print("Serialized and supplied predict function")
    return serialization_dir


def serialize_object(obj):
    s = StringIO()
    c = CloudPickler(s, 2)
    c.dump(obj)
    return s.getvalue()

serialization_dir = save_python_function('pytorch-func',predict)
print(serialization_dir)
torch_weights_save_loc = os.path.join(serialization_dir,
                                          PYTORCH_WEIGHTS_RELATIVE_PATH)

torch_model_save_loc = os.path.join(serialization_dir,
                                        PYTORCH_MODEL_RELATIVE_PATH)

torch.save(model.state_dict(), torch_weights_save_loc)
serialized_model = serialize_object(model)
with open(torch_model_save_loc, "wb") as serialized_model_file:
            serialized_model_file.write(serialized_model)
