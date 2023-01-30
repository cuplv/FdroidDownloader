FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y python python-pip git
RUN pip install boto3
RUN pip install arrow
RUN git clone https://github.com/cuplv/FdroidDownloader.git

CMD ["/bin/bash"]


