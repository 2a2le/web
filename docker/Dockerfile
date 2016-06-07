FROM ubuntu
RUN apt-get -y update && apt-get install -y git
RUN apt-get install -y python2.7 && apt-get install -y --upgrade python-pip
RUN pip install --upgrade pip && pip install requests && pip install requests_oauthlib && pip install nose && pip install python-dateutil

CMD cd home && git clone https://github.com/2a2le/web.git && cd web/twitter_tests && /bin/bash run_tests.sh
