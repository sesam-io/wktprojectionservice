FROM sesam/python-web

EXPOSE 6543

COPY wktprojectionservice*.tar.gz wktprojectionservice.tar.gz

RUN pip3 install wktprojectionservice.tar.gz
USER sesam

CMD exec wktprojectionservice -c $SESAM_CONF/config.yaml -f $SESAM_LOGS/wktprojectionservice.log -l DEBUG
