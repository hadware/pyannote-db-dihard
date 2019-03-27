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

from typing import Dict

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

from pyannote.core import Segment, Timeline, Annotation
from pyannote.database import Database
from pyannote.database.protocol import SpeakerDiarizationProtocol
from pyannote.parser.timeline.uem import UEMParser
import pandas as pd
from pathlib import Path
import yaml

# this protocol defines a speaker diarization protocol: as such, a few methods
# needs to be defined: trn_iter, dev_iter, and tst_iter.

class DIHARD2SingleChannelProtocol(SpeakerDiarizationProtocol):
    """DIHARD speaker diarization protocol """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Pretty hacky: using the path specified for the
        #  DIHARD2 flacs in the db.yml
        with open("~/.pyannote/db.yml") as db_file:
            db_config = yaml.load(db_file)
        DIHARD2_path = Path(db_config["DIHARD2"])
        self.single_channel_path = DIHARD2_path.parent.parent
        self.scoring_regions: Dict[str, Timeline] = dict()
        self.recording_type: Dict[str, str] = dict()

    def load_RTTM_files(self):
        rttm_path = self.single_channel_path / Path("rttm")
        return list(rttm_path.iterdir())

    def load_UEM_files(self):
        uem_path = self.single_channel_path / Path("uem")
        return list(uem_path.iterdir())

    def parse_scoring_regions(self):
        for uem_filepath in self.load_UEM_files():
            # we're going to use subfiles, not the "all.uem", as they
            # can also tell us what is the type of the audio recording
            if uem_filepath.name == "all.uem":
                continue
            files_type = uem_filepath.stem
            parser = UEMParser()
            timelines = parser.read(uem_filepath)
            for uri in timelines.uris:
                self.scoring_regions[uri] = timelines(uri=uri)
                self.recording_type[uri] = files_type

    def dev_iter(self):

        # column names for RTTM annotations
        names = ["type", 'uri', 'channel', 'start', 'duration', 'ortography',
                 "speaker_type", "speaker", "confidence", "signal_lookahead"]
        for annot_filepath in self.load_RTTM_files():
            annot_uri = annot_filepath.stem
            annot_df = pd.read_csv(annot_filepath, delim_whitespace=True,
                                   names=names)
            annotation = Annotation(uri=annot_uri)
            for idx, row in annot_df.iterrows():
                segment = Segment(start=row['start'],
                                  end=row['start'] + row['duration'])
                annotation[segment, idx] = row["speaker"]

            current_file = {
                'database': 'DIHARD2',
                'uri': annot_uri,
                'channel': 1,
                'annotated': self.scoring_regions[annot_uri],
                'annotation': annotation,
                'recording_type': self.recording_type[annot_uri]}
            yield current_file

    def trn_iter(self):
        for _ in []:
            yield

    def tst_iter(self):
        for _ in []:
            yield


class DIHARD2MultiChannelProtocol(SpeakerDiarizationProtocol):
    pass


class DIHARD(Database):
    """MyDatabase database"""

    def __init__(self, preprocessors={}, **kwargs):
        super(DIHARD, self).__init__(preprocessors=preprocessors, **kwargs)
        self.register_protocol(
            'SpeakerDiarization', 'SingleChannel', DIHARD2SingleChannelProtocol)

        self.register_protocol(
            'SpeakerDiarization', 'MultiChannel', DIHARD2MultiChannelProtocol)
