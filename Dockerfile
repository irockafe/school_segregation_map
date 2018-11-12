# lightweight linux distro
FROM python:3
LABEL maintainer="Isaac Rockafellow <isaac.rockafellow@gmail.com>"
WORKDIR /home/

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
COPY environment.yml ./
RUN conda env create -f ./environment.yml
# Enter the env from environment.yml on startup
# Make the commands from the conda env accessible

#ENV PATH /opt/conda/envs/$(head -1 ./environment.yml | cut -d ' ' -f2)/bin:$PATH
#ENV PATH /opt/conda/envs/$(awk '/name:/ {print $2}' ./environment.yml)/bin:$PATH
#ENV PATH /opt/conda/envs/$(awk '/name:/ {print $2}' ./environment.yml)/bin:$PATH
# ENV PATH /opt/conda/envs/seg_map/bin/:$PATH
# set up so that the command "jupyter-notebook" will run 
# without typing a buncha mumbojumbo
# How to source hte bashrc file without having to run it?
SHELL ["/bin/bash", "-c"]
RUN echo "alias jupyter-notebook='jupyter-notebook --no-browser --ip=0.0.0.0 --allow-root'" >> ~/.bashrc 
RUN echo "PYTHONPATH=$PYTHONPATH:/home/code" >> ~/.bashrc
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 
# Star the environment. Might be unecessary..?
RUN awk '/name:/ {print $2}' ./environment.yml | xargs echo 'source activate' >> ~/.bashrc
CMD source activate $(awk '/name:/ {print $2}' ./environment.yml) && doit 2>&1 > doit.log
#ENV PATH /opt/conda/envs/seg_map/bin/:$PATH
