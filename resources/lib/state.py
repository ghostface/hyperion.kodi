import math
import xbmc
import xbmcaddon
import binascii

from hyperion.Hyperion import Hyperion
from misc import log
from misc import notify


class DisconnectedState:
    '''
    Default state class when disconnected from the Hyperion server
    '''
    def __init__(self, settings):
        '''Constructor
          - settings: Settings structure
        '''
        log("Entering disconnected state")
        self.__settings = settings

    def execute(self):
        '''Execute the state
          - return: The new state to execute
        '''
        # check if we are enabled
        if not self.__settings.grabbing():
            xbmc.sleep(500)
            return self

        # we are enabled and want to advance to the connected state
        try:
            nextState = ConnectedState(self.__settings)
            return nextState
        except Exception as e:
            # unable to connect. notify and go to the error state
            if self.__settings.showErrorMessage:
                notify(xbmcaddon.Addon().getLocalizedString(32100))
                self.__settings.showErrorMessage = False

            # continue in the error state
            return ErrorState(self.__settings)


class ConnectedState:
    '''
    State class when connected to Hyperion and grabbing video
    '''

    def __init__(self, settings):
        '''Constructor
          - settings: Settings structure
        '''
        log("Entering connected state")

        self.__settings = settings
        self.__hyperion = None
        self.__capture = None
        self.__captureState = None
        self.__data = None

        # try to connect to hyperion
        self.__hyperion = Hyperion(self.__settings.address, self.__settings.port)

        # Force clearing of priority (mainly for Orbs)
        self.clear_priority()

        # create the capture object
        self.__capture = xbmc.RenderCapture()
        self.__capture.capture(self.__settings.capture_width, self.__settings.capture_height)

    def __del__(self):
        '''Destructor
        '''
        del self.__hyperion
        del self.__capture
        del self.__captureState
        del self.__data

    def clear_priority(self):
        # Force clearing of priority (mainly for Orbs)
        xbmc.sleep(1000)
        self.__hyperion.clear(self.__settings.priority)
        xbmc.sleep(1000)
        self.__hyperion.clear(self.__settings.priority)

    def execute(self):
        '''Execute the state
          - return: The new state to execute
        '''
        # check if we still need to grab
        if not self.__settings.grabbing():
            self.clear_priority()

            # return to the disconnected state
            return DisconnectedState(self.__settings)
        # capture an image
        startReadOut = False

        self.__data = self.__capture.getImage()
        hexdata = binascii.b2a_hex(self.__data)
        if len(self.__data) > 0 and not hexdata.startswith(bytes.fromhex('0000000000000000')) and not hexdata.startswith(bytes.fromhex('000000ff000000ff')):
            startReadOut = True

        if startReadOut:
            # retrieve image data and reformat into rgb format
            if self.__capture.getImageFormat() == 'BGRA':
                del self.__data[3::4]
                self.__data[0::3], self.__data[2::3] = self.__data[2::3], self.__data[0::3]

            try:
                # send image to hyperion
                self.__hyperion.sendImage(self.__capture.getWidth(), self.__capture.getHeight(), str(self.__data),
                                          self.__settings.priority, -1)
            except Exception as e:
                # unable to send image. notify and go to the error state
                notify(xbmcaddon.Addon().getLocalizedString(32101))
                return ErrorState(self.__settings)
        else:
            # Force clearing of priority (mainly for Orbs)
            self.clear_priority()

        # Sleep if any delay is configured
        sleeptime = self.__settings.delay

        if self.__settings.useDefaultDelay == False:
            try:
                videofps = math.ceil(float(xbmc.getInfoLabel('Player.Process(VideoFPS)')))
                if videofps == 24:
                    sleeptime = self.__settings.delay24
                if videofps == 25:
                    sleeptime = self.__settings.delay25
                if videofps == 50:
                    sleeptime = self.__settings.delay50
                if videofps == 59:
                    sleeptime = self.__settings.delay59
                if videofps == 60:
                    sleeptime = self.__settings.delay60
            except ValueError:
                pass

        # log('Sleeping for (ms): %d :: %.3f' % (sleeptime, videofps))
        xbmc.sleep(sleeptime)
        return self


class ErrorState:
    '''
    State class which is activated upon an error
    '''

    def __init__(self, settings):
        '''Constructor
          - settings: Settings structure
        '''
        log("Entering error state")
        self.__settings = settings

    def execute(self):
        '''Execute the state
          - return: The new state to execute
        '''
        # take note of the current revision of the settings
        rev = self.__settings.rev

        # stay in error state for the specified timeout or until the settings have been changed
        i = 0
        while (i < self.__settings.timeout) and (rev == self.__settings.rev):
            if self.__settings.abort:
                return self
            else:
                xbmc.sleep(1000)
            i += 1

        # continue in the disconnected state
        return DisconnectedState(self.__settings)
