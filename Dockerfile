FROM jupyter/scipy-notebook:307ad2bb5fce

LABEL maintainer="Serge Rey <sjsrey@gmail.com>"

#RUN conda config --add channels conda-forge --force

USER root
COPY .condarc /home/jovyan/.condarc
COPY geopyter.yml /home/jovyan/geopyter.yml
COPY develop.sh /home/jovyan/develop.sh
RUN conda config --set channel_priority strict
RUN conda config --set safety_checks disabled
RUN conda install -c conda-forge -c defaults --quiet --yes \
  'contextily'\
  'geopandas'\
  'ipython'\
  'ipywidgets'\
  'jupyter'\
  'jupyterlab'\
  'mplleaflet'\
  'networkx'\
  'nodejs'\
  'osmnx'\
  'palettable'\
  'pillow' \
  'rasterio'\
  'requests'\
  'scikit-learn'\
  'seaborn'\
  'statsmodels'\
  'xlrd'\
  'xlsxwriter'

RUN pip install -U gitpython geopy markdown nbdime  nbformat polyline pysal
RUN pip install gitdb


# Switch back to user to avoid accidental container runs as root
USER $NB_UID
