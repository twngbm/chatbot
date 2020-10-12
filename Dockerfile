FROM httpd:latest
RUN apt update && apt install -y python3.7 python3-pip python3.7-dev gcc --no-install-recommends \
    && python3.7 -m pip install setuptools --no-cache-dir\
    && python3.7 -m pip install --upgrade pip \
    && python3.7 -m pip install numpy ckiptagger==0.1.1 tensorflow==1.15.2 PyJWT==1.7.1 python-Levenshtein==0.12.0 websockets==8.1 fuzzywuzzy ckipnlp nest_asyncio --no-cache-dir \
    && python3.7 -m pip uninstall setuptools -y \
    && apt remove python3-pip gcc -y && apt autoremove -y && rm -rf /var/lib/apt/lists/*
#COPY data/ /root/chatbot/data
#COPY reference/ /root/chatbot/reference
#COPY source/ /root/chatbot/source
#COPY html/ /usr/local/apache2/htdocs
WORKDIR /root/chatbot/source
CMD httpd-foreground & ./main.sh 