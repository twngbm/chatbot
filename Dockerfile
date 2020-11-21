FROM httpd:latest
RUN apt update && apt install -y python3.7 python3-pip python3.7-dev gcc --no-install-recommends \
    && python3.7 -m pip install setuptools --no-cache-dir\
    && python3.7 -m pip install --upgrade pip \
    && python3.7 -m pip install numpy==1.19.1 ckiptagger==0.1.1 tensorflow==1.15.2 python-Levenshtein==0.12.0 websockets==8.1 fuzzywuzzy==0.18.0 ckipnlp==0.9.1 nest_asyncio==1.4.0 requests==2.21.0 --no-cache-dir \
    && python3.7 -m pip uninstall setuptools -y \
    && apt remove python3-pip gcc -y && apt autoremove -y && rm -rf /var/lib/apt/lists/*
COPY data/embedding_character/ /root/chatbot/data/embedding_character
COPY data/embedding_word/ /root/chatbot/data/embedding_word
COPY data/model_pos/ /root/chatbot/data/model_pos
COPY data/model_ws/ /root/chatbot/data/model_ws
COPY reference/ /root/chatbot/reference
COPY html/ /usr/local/apache2/htdocs
COPY source/ /root/chatbot/source
WORKDIR /root/chatbot/source
CMD httpd-foreground & ./main.sh 