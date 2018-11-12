# lightweight linux distro
FROM python:3
LABEL maintainer="Isaac Rockafellow <isaac.rockafellow@gmail.com>"
WORKDIR /home/
#SHELL ["/bin/bash", "-c"]

# Go from least-often changed to most often changed, i.e.
#First get OS packages you want - apt-get install everything you need

# Install conda
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 
ENV PATH /opt/conda/bin:$PATH
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    cp ~/.bashrc /home/ && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> .bashrc && \
    echo "conda activate base" >> .bashrc 


# Then get packages needed for installation i.e. conda install things
# or npm install things
COPY environment.yml ./project/
RUN conda env create -f ./project/environment.yml

# set up so that the command "jupyter-notebook" will run 
# without typing a buncha mumbojumbo
# How to source hte bashrc file without having to run it?
RUN echo "alias jupyter-notebook='jupyter-notebook --no-browser --ip=0.0.0.0 --allow-root'" >> .bashrc 
RUN echo "PYTHONPATH=$PYTHONPATH:/home/project/code" >> .bashrc
RUN ["/bin/bash", "-c", "source /home/.bashrc"]
