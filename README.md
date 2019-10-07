# RPC_TALKER
A directory which talks to model containers via RPC system provided by CLIPPER. Only heartbeats messages implemented so far.
## Build Docker file for Clipper + Pytorch + CUDA
Follow the following steps - 
1. git clone <https://github.com/alindkhare/clipper.git>
2. cd clipper/
3. git checkout alind/cuda_pytorch1.2
4. cd examples/image_query
5. sh build_pytorch1.2_container.sh

This will build the docker image with the tag clipper/cuda10-pytorch1.2-py3.6-container .

## Running the docker file and setting up ENV variables
Type the following commands - 
1. In RPC_TALKER directory, run file save_model_and_func.py by the command *python save_model_and_func.py*
2. Note down the directory path printed while running this file (let's call this DIR). Keep this terminal tab open (call this tab A). 
3. In a new terminal window (call this tab B), type - *docker run --runtime=nvidia -it --network host --name my-clipper clipper/cuda10-pytorch36-container bash*
4. On tab A, fire the following commands -
    1. docker cp rpc.py my-clipper:/container/
    2. docker cp DIR/* my-clipper:/model/
5. On tab B, you are inside container. Do the following - 
      1. export CLIPPER_MODEL_VERSION=v1
      2. export CLIPPER_INPUT_TYPE=bytes
      3. export CLIPPER_PORT=7999
      4. export CLIPPER_MODEL_PATH=/model/
      5. export CLIPPER_MODEL_NAME=r50
## Running the RPC Talker
1. On TAB A, start RPC_talker by command - *python RPC_talker.py*
2. On TAB B (the docker container), run command - *sh container_entry.sh  "pytorch-container" pytorch_container.py*



