# -*- coding: utf-8 -*-

import os
import lzma
import struct
from functools import cached_property, partial
from enum import IntFlag, unique
from typing import Optional

__all__ = ('Keys', 'ReplayFrame', 'Replay')

"""\
a simple osu! replay parser, for all your replay parsing needs..

Basic usage:
```
  r = Replay.from_str('1234567.osr')
  if not r:
	# file not found
	...

  # replay objects have pretty much everything
  # you can imagine for an osu! replay. :P

  print(r.player_name, r.mode, r.mods, r.osu_version, ...)

  for frame in r.frames:
	print(r.delta, r.x, r.y, r.keys)

  # etc
  ...
```

i'm sure it'll get cleaned up more over time, basically
wrote it with the same style as the beatmap parser.
"""

def _isdecimal(s: str, _float: bool = False,
			   _negative: bool = False) -> None:
	if _float:
		s = s.replace('.', '', 1)

	if _negative:
		s = s.replace('-', '', 1)

	return s.isdecimal()

@unique
class Keys(IntFlag):
	M1    = 1 << 0
	M2    = 1 << 1
	K1    = 1 << 2
	K2    = 1 << 3
	Smoke = 1 << 4

class ReplayFrame:
	def __init__(self, **kwargs) -> None:
		self.delta: Optional[int] = kwargs.get('delta', None)
		self.x: Optional[float] = kwargs.get('x', None)
		self.y: Optional[float] = kwargs.get('y', None)
		self.keys: Optional[Keys] = kwargs.get('keys', None)

	@cached_property
	def as_bytes(self) -> bytes:
		buf = bytearray()
		buf.extend(self.delta.to_bytes(4, 'little', signed=True))
		buf.extend(struct.pack('<ff', self.x, self.y))
		buf.append(self.keys)

		return bytes(buf)

	@cached_property
	def as_str(self) -> str:
		# we want to display the keys as an integer.
		fmt_dict = self.__dict__ | {'keys': int(self.keys)}
		return '{delta}|{x}|{y}|{keys}'.format(**fmt_dict)

	@classmethod
	def from_str(cls, s: str):
		if len(split := s.split('|')) != 4:
			return

		isdecimal_n = partial(_isdecimal, _negative=True)
		isfloat_n = partial(isdecimal_n, _float=True)

		if not all(isdecimal_n(x) for x in (split[0], split[3])):
			return

		if not all (isfloat_n(x) for x in (split[1], split[2])):
			return

		kwargs = {
			'delta': int(split[0]),
			'x': float(split[1]),
			'y': float(split[2]),
			'keys': Keys(int(split[3]))
		}

		return cls(**kwargs)

class Replay:
	def __init__(self) -> None:
		""" replay headers"""
		self.mode: Optional[int] = None # gm
		self.osu_version: Optional[int] = None

		self.map_md5: Optional[str] = None
		self.player_name: Optional[str] = None
		self.replay_md5: Optional[str] = None

		self.n300: Optional[int] = None
		self.n100: Optional[int] = None
		self.n50: Optional[int] = None
		self.ngeki: Optional[int] = None
		self.nkatu: Optional[int] = None
		self.nmiss: Optional[int] = None

		self.score: Optional[int] = None
		self.max_combo: Optional[int] = None
		self.perfect: Optional[int] = None
		self.mods: Optional[int] = None

		""" additional info"""
		self.life_graph: Optional[list[tuple[int, float]]] = None # zz
		self.timestamp: Optional[int] = None
		self.score_id: Optional[int] = None
		self.mod_extras: Optional[float] = None
		self.seed: Optional[int] = None

		""" replay frames """
		self.frames: Optional[list[ReplayFrame]] = None

		""" internal reader use only """
		self._data: Optional[bytes] = None
		self._offset: Optional[int] = None

	@property
	def data(self) -> bytes:
		return self._data[self._offset:]

	@classmethod
	def from_file(cls, filename: str):
		if not os.path.exists(filename):
			return

		r = cls()

		with open(filename, 'rb') as f:
			r._data = f.read()
			r._offset = 0

		r._parse()
		return r

	def _parse(self) -> None:
		""" parse replay headers """
		self.mode = self._read_byte()
		self.osu_version = self._read_int()
		self.map_md5 = self._read_string()
		self.player_name = self._read_string()
		self.replay_md5 = self._read_string()
		self.n300 = self._read_short()
		self.n100 = self._read_short()
		self.n50 = self._read_short()
		self.ngeki = self._read_short()
		self.nkatu = self._read_short()
		self.nmiss = self._read_short()
		self.score = self._read_int()
		self.max_combo = self._read_short()
		self.perfect = self._read_byte()
		self.mods = self._read_int()
		self.life_graph = self._read_string() # TODO
		self.timestamp = self._read_long()

		""" parse lzma """
		self.frames = self._read_frames()

		""" parse additional info """
		self.score_id = self._read_long()

		if self.mods & 1 << 23: # target practice
			self.mod_extras = self._read_double()

	def _read_byte(self):
		val = self.data[0]
		self._offset += 1
		return val

	def _read_short(self):
		val, = struct.unpack('<h', self.data[:2])
		self._offset += 2
		return val

	def _read_int(self):
		val, = struct.unpack('<i', self.data[:4])
		self._offset += 4
		return val

	def _read_float(self):
		val, = struct.unpack('<f', self.data[:4])
		self._offset += 4
		return val

	def _read_long(self):
		val, = struct.unpack('<q', self.data[:8])
		self._offset += 8
		return val

	def _read_double(self):
		val, = struct.unpack('<d', self.data[:8])
		self._offset += 8
		return val

	def _read_uleb128(self):
		val = shift = 0

		while True:
			b = self._read_byte()

			val |= ((b & 0b01111111) << shift)
			if (b & 0b10000000) == 0x00:
				break

			shift += 7

		return val

	def _read_raw(self, length: int):
		val = self.data[:length]
		self._offset += length
		return val

	def _read_string(self):
		if self._read_byte() == 0x00:
			return ''

		uleb = self._read_uleb128()
		return self._read_raw(uleb).decode()

	def _read_frames(self):
		frames = []

		lzma_len = self._read_int()
		lzma_data = lzma.decompress(self._read_raw(lzma_len))

		actions = [x for x in lzma_data.decode().split(',') if x]

		for action in actions[:-1]:
			frame = ReplayFrame.from_str(action)

			if not frame:
				continue

			frames.append(frame)

		self.seed = int(actions[-1].rsplit('|', 1)[1])
		return frames



def UnsupportedMode(Exception):
	pass


def open_replay(filedir: str):
	''' have checker thing to check if mode is std '''

	if (r := Replay.from_file(filedir)):
		if r.mode != 0:
			raise UnsupportedMode

		return r
		