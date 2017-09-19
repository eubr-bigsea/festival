FROM ubuntu:16.04
MAINTAINER Speed Labs <speed@dcc.ufmg.br>

ENV FESTIVAL_HOME /usr/local/festival
ENV FESTIVAL_CONFIG $FESTIVAL_HOME/conf/festival-config.yaml

RUN apt-get update && apt-get install -y  \
     python-pip \
   && rm -rf /var/lib/apt/lists/*

WORKDIR $FESTIVAL_HOME
COPY requirements.txt $FESTIVAL_HOME/requirements.txt
RUN pip install -r $FESTIVAL_HOME/requirements.txt

COPY . $FESTIVAL_HOME

CMD ["/usr/local/festival/sbin/festival-daemon.sh", "startf"]
