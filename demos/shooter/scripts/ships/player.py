# -*- coding: utf-8 -*-

# ####################################################################
#  Copyright (C) 2005-2009 by the FIFE team
#  http://www.fifengine.de
#  This file is part of FIFE.
#
#  FIFE is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# ####################################################################

from fife import fife
from scripts.ships.shipbase import *
from scripts.common.helpers import Rect
from scripts.weapons import *


class PlayerActionListener(ShipActionListener):
	def __init__(self, ship):
		super(PlayerActionListener, self).__init__(ship)

	def onInstanceActionFinished(self, instance, action):
		if action.getId() == 'explode':
			self._ship.respawn()
		if action.getId() == 'flash':
			if self._ship._flashnumber > 0:
				self._ship.instance.act('flash', self._ship.instance.getFacingLocation())
				self._ship._flashnumber -= 1	
			else:	
				self._ship._flashing = False
		
		
class Player(Ship):
	def __init__(self, scene, playerName):
		super(Player, self).__init__(scene, playerName)

		self._score = 0
		self._maxvelocity = 1.5
		
		self.width = 0.22
		self.height = 0.12		
		
		#give player the default weapon (the cannon)
		self.weapon = Cannon(self._scene, self, 200)
		
		self._lives = 3
		self._invulnerable = False
		
		self._isplayer = True
		self._dead = False
		
		self._actionlistener = PlayerActionListener(self)
		
	def init(self):
		self._lives = 3
	
	def _getScore(self):
		return self._score
		
	def respawn(self):
		if self._lives >= 0:
			self._dead = False
			self.setInvulnerable(20)

			campos = self._scene.camera.getLocation().getExactLayerCoordinates()
			location = self.location
			playerpos = location.getExactLayerCoordinates()
			
			playerpos.x = campos.x - 6.5
			playerpos.y = campos.y
			location.setExactLayerCoordinates(playerpos)
			self.location = location
		
		else:
			self._instance.get2dGfxVisual().setVisible(False)
		
	def setInvulnerable(self, seconds):
		self._invulnerable = True
		self.flash(seconds)
		
	def applyScore(self, sc):
		self._score += sc
		
	def destroy(self):
		if not self._invulnerable and not self._dead:
			self._instance.act('explode', self._instance.getFacingLocation())
			self._dead = True
			self._invulnerable = True
			self._lives -= 1		

	def update(self):
	
		key = False
		
		#player is no longer invulnerable
		if not self._flashing and self._invulnerable and not self._dead:
			self._invulnerable = False

		oldpos = self.location
		
		if not self._dead:
			if self._scene.keystate['UP']:
				self.applyThrust(fife.DoublePoint(0,-1.5))
				key = True
			if self._scene.keystate['DOWN']:
				self.applyThrust(fife.DoublePoint(0,1.5))
				key = True
			if self._scene.keystate['LEFT']:
				self.applyThrust(fife.DoublePoint(-1.5,0))
				key = True
			if self._scene.keystate['RIGHT']:
				self.applyThrust(fife.DoublePoint(1.5,0))
				key = True
		
			#fire the currently selected gun
			if self._scene.keystate['SPACE']:
				self.fire(fife.DoublePoint(1,0))
			
		if not key and self._velocity.length() > 0:
			self.applyBrake(1.5)
		
		super(Player, self).update()
		
		#set up the players camera bounds
		#TODO: grab screen resolution from somewhere
		topleft = self._scene.camera.toMapCoordinates(fife.ScreenPoint(0,0))
		bottomright = self._scene.camera.toMapCoordinates(fife.ScreenPoint(1024,768))

		camrect = Rect(topleft.x, topleft.y, bottomright.x - topleft.x, bottomright.y - topleft.y)
	
		#add the padding to the edge
		camrect.x += self._boundingBox.w
		camrect.y += self._boundingBox.h
		camrect.w -= 2*self._boundingBox.w
		camrect.h -= 2*self._boundingBox.h
		
		pos = oldpos.getExactLayerCoordinates()
		
		if not self._boundingBox.intersects(camrect):
			if (self._boundingBox.x + self._boundingBox.w) < camrect.x:
				self._velocity.x = 0
				pos.x += (camrect.x - (self._boundingBox.x + self._boundingBox.w))/self._xscale + 0.03
				pos.y += self._velocity.y * (self._scene.timedelta/1000.0)/self._yscale
				oldpos.setExactLayerCoordinates(pos)
			
#			elif (bbox.y + bbox.h) < camrect.y or (bbox.y - bbox.h) > camrect.y:
#				pos.x += self._velocity.x * (timedelta/1000.0)
#				oldpos.setExactLayerCoordinates(pos)
#				self._velocity.y = 0
			elif (self._boundingBox.y + self._boundingBox.h) < camrect.y or self._boundingBox.y > (camrect.y + camrect.h):
				pos.x += self._velocity.x * (self._scene.timedelta/1000.0)/self._xscale
				self._velocity.y = 0
				oldpos.setExactLayerCoordinates(pos)
			else:
				self._velocity.x = 0
				self._velocity.y = 0

			self.location = oldpos

	def _getLives(self):
		return self._lives
		
	def _getInvulnerable(self):
		return self._invulnerable

	def _setInvulnerable(self, inv):
		self._invulnerable = inv

	score = property(_getScore)
	lives = property(_getLives)
	invulnerable = property(_getInvulnerable, _setInvulnerable)