FROM python:2.7

COPY src/phys_frames/ /phys_frames/
COPY src/external/cppcheck-1.80/ /cppcheck-1.80/
COPY requirements.txt /requirements.txt

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

WORKDIR /phys_frames

ENTRYPOINT ["python", "./phys_frames.py"]
