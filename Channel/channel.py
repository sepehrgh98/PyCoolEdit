from Channel.channeldata import ChannelData
from Channel.channelform import ChannelForm


class Channel:
    def __init__(self, _id, _name):
        self._channel = ChannelData(_id, _name)
        self._plot = ChannelForm(_id, _name)

    @property
    def data(self):
        return self._channel

    @property
    def plot(self):
        return self._plot
