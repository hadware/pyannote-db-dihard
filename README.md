# DIHARD and DIHARD2 challenge plugin for pyannote.database

## Installation

```bash
$ pip install pyannote.db.dihard  # install from pip, or
$ pip install -e .  # install a local copy
```

Tell `pyannote` where to look for DIHARD and DIHARD2 audio files. 

```bash
$ cat ~/.pyannote/db.yml
DIHARD: 
  - /path/to/DIHARD/{uri}.wav
  - /path/to/DIHARD2/{uri}.wav
```

## Speaker diarization protocol

Protocol is initialized as follows:

```python
>>> from pyannote.database import get_protocol, FileFinder
>>> preprocessors = {'audio': FileFinder()}
>>> protocol = get_protocol('DIHARD.SpeakerDiarization.All',
...                         preprocessors=preprocessors)
```

### Test / Evaluation

```python
>>> # initialize evaluation metric
>>> from pyannote.metrics.diarization import DiarizationErrorRate
>>> metric = DiarizationErrorRate()
>>>
>>> # iterate over each file of the test set
>>> for test_file in protocol.test():
...
...     # process test file
...     audio = test_file['audio']
...     hypothesis = process_file(audio)
...
...     # evaluate hypothesis
...     reference = test_file['annotation']
...     uem = test_file['annotated']
...     metric(reference, hypothesis, uem=uem)
>>>
>>> # report results
>>> metric.report(display=True)
```