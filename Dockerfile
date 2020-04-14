FROM nielsbohr/projects-site:latest

ARG SERVER_NAME
ARG APP_NAME
ARG APP_DIR

ENV SERVERNAME=${SERVER_NAME}
ENV APPNAME=${APP_NAME}
ENV APPDIR=${APP_DIR}

# Setup configuration
# Also enable wsgi and header modules
COPY apache/apache2-http.conf /etc/apache2/sites-available/${SERVERNAME}.conf
RUN a2dissite 000-default.conf && \
	a2dissite projects.conf && \
    a2ensite ${SERVERNAME}.conf

RUN mkdir -p ${APPDIR}
# Prepare WSGI launcher script
COPY ./res ${APPDIR}/res
COPY ./apache/app.wsgi ${APPDIR}/wsgi/app.wsgi
COPY ./run.py ${APPDIR}/run.py
RUN mkdir -p ${APPDIR}/persistence && \
    chown root:www-data ${APPDIR}/persistence && \
    chmod 775 -R ${APPDIR}/persistence && \
    chmod 2755 -R ${APPDIR}/wsgi

# Copy in the source code
COPY . /app
WORKDIR /app

# Install the envvars script, code and cleanup
RUN pip3 install setuptools && \
    pip3 install wheel==0.30.0 && \
    python3 setup.py bdist_wheel && \
    pip3 install -r requirements.txt && \
    python3 setup.py install

RUN rm -r /app
WORKDIR ${APPDIR}

EXPOSE 80
