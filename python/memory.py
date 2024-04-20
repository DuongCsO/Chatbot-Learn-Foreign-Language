import re
from typing import List, Dict, Union


class Memory:
    def __init__(self):
        self._memory: List[Dict[str, Union[str, List[str]]]] = list()
        self._updates: List[Dict[str, Union[str, List[str], int]]] = list()

    def __getitem__(self, index):
        return self._memory[index]

    def __repr__(self):
        return str(self._memory)

    def __len__(self):
        return len(self._memory)

    @property
    def list(self) -> List[Dict[str, Union[str, List[str]]]]:
        return self._memory

    @property
    def updates(self) -> List[Dict[str, Union[str, List[str], int]]]:
        return self._updates

    def add(self, role, message) -> None:
        """
        Add new message to memory. also check if there are updates for this message and apply them (see `update` below)

        :param role: the role of the message sender ("system", "user" or "assistant")
        :param message: the message text
        :param recording: list of recording file of the text-to-speech engine
        :param user_recording: a file name of the user's recording
        """
        message = re.sub(r'[^\S\n]+', ' ', message)
        mem = {"role": role, "content": message}
        updates = [u.copy() for u in self._updates]
        updates = [u for u in updates if u["index"] == len(self._memory)]
        [u.pop("index") for u in updates]
        self._memory.append(mem)

    def update(self, index, **kwargs) -> None:
        """
        Update a saved message. Technically, due to parallelism, an update can be made before the message was
        actually added. This class takes care of this be keeping such updates in a special inner list called
        `self._updates`

        :param index: index of the message to update
        :param kwargs: key-value pairs of the values to update
        """
        if index < len(self._memory):
            self._memory[index].update(kwargs)
        else:
            update = kwargs
            update["index"] = index
            self._updates.append(update)

    def get_chat_history(self) -> List[dict]:
        """
        Get all chat messages in the ChatGPT format

        :return: list of messages (each message is a dict)
        """
        return [{"role": message["role"], "content": message["content"]} for message in self._memory]
