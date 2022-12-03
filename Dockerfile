FROM continuumio/anaconda3

RUN apt-get update
RUN python3 -m pip install --upgrade pip

# Install requried python packages
COPY requirements.txt .
#RUN pip install --ignore-installed scikit-learn==0.24.0
RUN pip install -r requirements.txt

# Create a /work directory within the container, copy everything from the
# build directory and switch there.
RUN mkdir /work
COPY . /work
WORKDIR /work
RUN python run.py