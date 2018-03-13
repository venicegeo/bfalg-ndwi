FROM developmentseed/geolambda:cloud

RUN \
    yum makecache fast; \
    yum install -y agg-devel;

ENV \
    POTRACE_VERSION=1.14

# install potrace
RUN \
    wget http://potrace.sourceforge.net/download/$POTRACE_VERSION/potrace-$POTRACE_VERSION.tar.gz; \
    tar -xzvf potrace-$POTRACE_VERSION.tar.gz; \
    cd potrace-$POTRACE_VERSION; \
    ./configure --with-libpotrace; \
    make && make install && cd .. && \
    rm -rf potrace-$POTRACE_VERSION*

COPY requirements*txt $BUILD/

RUN \
	pip install -r requirements.txt; \
	pip install -r requirements-dev.txt
