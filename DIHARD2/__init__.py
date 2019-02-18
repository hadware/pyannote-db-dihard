#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2017 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import os
from pyannote.core import Segment, Timeline, Annotation
from pyannote.database import Database
from pyannote.database.protocol import SpeakerDiarizationProtocol
from pandas import read_table
from pathlib import Path

# this protocol defines a speaker diarization protocol: as such, a few methods
# needs to be defined: trn_iter, dev_iter, and tst_iter.


class Full(SpeakerDiarizationProtocol):
    """DIHARD2 speaker diarization protocol """

    def trn_iter(self):

        # absolute path to 'data' directory where annotations are stored
        data_dir = Path(__file__).parent / 'data'

        # in this example, we assume annotations are distributed in MDTM format.
        # this is obviously not mandatory but pyannote.parser conveniently
        # provides a built-in parser for MDTM files...
        annotations = data_dir / f'protocol1.train.mdtm'
        names = ['uri', 'channel', 'start', 'duration',
                 'NA1', 'NA2', 'gender', 'speaker']
        annotations = read_table(annotations, delim_whitespace=True, names=names)
        AnnotationGroups = annotations.groupby(by='uri')
        # iterate over each file in training set
        for uri, annotations in AnnotationGroups:
            annotation = Annotation(uri=uri)
            channel = None
            file_duration = None
            for t, turn in enumerate(annotations.itertuples()):
                segment = Segment(start=turn.start,
                                  end=turn.start + turn.duration)
                file_duration = Segment(start=0, end=turn.start + turn.duration)
                annotation[segment, t] = turn.speaker

            current_file = {
                'database': 'DIHARD2',
                'uri': uri,
                'channel': channel,
                'annotated': Timeline(uri=uri, segments=[file_duration]),
                'annotation': annotation}
            yield current_file

            # optionally, an 'annotated' field can be added, whose value is
            # a pyannote.core.Timeline instance containing the set of regions
            # that were actually annotated (e.g. some files might only be
            # partially annotated).

            # this field can be used later to only evaluate those regions,
            # for instance. whenever possible, please provide the 'annotated'
            # field even if it trivially contains segment [0, file_duration].


    def dev_iter(self):
        # here, you should do the same as above, but for the development set
        for _ in []:
            yield

    def tst_iter(self):
        # here, you should do the same as above, but for the test set
        for _ in []:
            yield

# this is where we define each protocol for this database.
# without this, `pyannote.database.get_protocol` won't be able to find them...


class DIHARD2(Database):
    """MyDatabase database"""

    def __init__(self, preprocessors={}, **kwargs):
        super(DIHARD2, self).__init__(preprocessors=preprocessors, **kwargs)

        # register the first protocol: it will be known as
        # MyDatabase.SpeakerDiarization.MyFirstProtocol
        self.register_protocol(
            'SpeakerDiarization', 'All', Full)
