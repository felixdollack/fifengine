#!/usr/bin/python
from __init__ import *
import time

class MyTimeEvent(fife.TimeEvent):
	def __init__(self, period):
		fife.TimeEvent.__init__(self, period)
		self.counter = 0
	
	def updateEvent(self, curtime):
		print "testing timer event... %d, %d" % (curtime, self.counter)
		self.counter += 1

class TestTimer(unittest.TestCase):
	def setUp(self):
		self.engine = fife.Engine(True)
		self.timemanager = self.engine.getTimeManager()

	def tearDown(self):
		del self.engine
	
	def testEvents(self):
		e = MyTimeEvent(100)
		self.timemanager.registerEvent(e)

		for i in xrange(10):
			time.sleep(0.1)
			self.timemanager.update()

		self.timemanager.unregisterEvent(e)

TEST_CLASSES = [TestTimer]

if __name__ == '__main__':
    unittest.main()

