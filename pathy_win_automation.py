import os, json
import ahk

class AppCommandQueue:
    def __init__(self, pid):
        self.ahk = ahk.AHK()
        self.ahkScriptName = "temp.ahk"
        self.ahkScriptPath = os.path.join(".", self.ahkScriptName)
        self.ahkScript = open(self.ahkScriptPath, "w")
        self.ahkWindow = [match for match in ahk.find_windows(title="Path of Exile") if match.pid == pid][0]

        x, y, w, h = self.ahkWindow.get_position()
        isFullScreen = True if (x,y) == (0,0) else False
        self.x = 0 if isFullScreen else 10
        self.w = w if isFullScreen else w-20
        self.y = 0 if isFullScreen else 35
        self.h = h if isFullScreen else h-45

        # self.ahkScript.write("CoordMode, Mouse, Window\n")
        self.ahkScript.write("SetBatchLines, 1\n")
        self.ahkScript.write("SetMouseDelay, 1\n")
        self.ahkScript.write("WinActivate, ahk_pid %s\n" % pid)
        self.ahkScript.write("\n")

    def addLeftClick(self, x, y):
        self.ahkScript.write("Click %s %s\n" % (x, y))

    def addRightClick(self, x, y):
        self.ahkScript.write("Click, Right, %s, %s\n" % (x, y))

    def addCtrlClick(self, x, y):
        self.ahkScript.write("Send, ^{Click %s %s}\n" % (x, y))

    def addGridFunClick(self, left, top, right, bot, xMax, yMax, xStart, xEnd, yStart, yEnd, clickFun):
        xInc = (right - left) / (xMax-1)
        yInc = (bot - top) / (yMax-1)
        for x in range(xStart, xEnd):
            for y in range(yStart, yEnd):
                clickFun(left + xInc*x, top + yInc*y)

    def run(self):
        self.ahkScript.write("^e::ExitApp\n")
        self.ahkScript.close()
        self.ahk.run_script(self.ahkScriptName)

    def __del__(self):
        os.remove(self.ahkScriptPath)


class TransferGuildToNormalCoord:
    def __init__(self, pid):
        self.pid = pid
        self.acq = AppCommandQueue(pid)
        if os.path.exists("%s_%s.json" % (self.__class__.__name__, pid)):
            self.coords = json.load(open("%s_%s.json" % (self.__class__.__name__, pid), "r"))
        else:
            self.clickIndex = 0
            self.coords = {}
            ahk.add_hotkey('~LButton', callback=self.onClick)
            ahk.start_hotkeys()
            input("Click on a non-char moving location ...")

    def onClick(self):
        mCoord = ahk.mouse_position
        if self.clickIndex == 0:
            print("Path of exile window active ...")
            print("Click on location of outgoing stash ...")
        if self.clickIndex == 1:
            self.coords['outStashLoc'] = [mCoord.x, mCoord.y]
            print("Outgoing stash location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on 1st unit to be clicked in outgoing stash ...")
        if self.clickIndex == 2:
            self.coords['outStashTopLeft'] = [mCoord.x, mCoord.y]
            print("Outgoing stash 1st unit to be clicked location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on the last unit to be clicked outgoing stash ...")
        if self.clickIndex == 3:
            self.coords['outStashBottomRight'] = [mCoord.x, mCoord.y]
            print("Outgoing stash last unit to be clicked location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on 1st unit to be clicked in inventory ...")
        if self.clickIndex == 4:
            self.coords['inventoryTopLeft'] = [mCoord.x, mCoord.y]
            print("1st unit to be clicked in inventory location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on the last unit to be clicked inventory ...")
        if self.clickIndex == 5:
            self.coords['inventoryBottomRight'] = [mCoord.x, mCoord.y]
            print("Last unit to be clicked inventory location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on location of incoming stash ...")
        if self.clickIndex == 6:
            self.coords['inStashLoc'] = [mCoord.x, mCoord.y]
            print("Incoming stash location: %s, %s." % (mCoord.x, mCoord.y))
            print("Press enter to exit")
            with open("%s_%s.json" % (self.__class__.__name__, self.pid), "w") as f:
                f.write(json.dumps(self.coords, indent=4))
        self.clickIndex += 1

    def generateCommandQueue(self):
        for r in range(12):
            self.acq.addLeftClick(self.coords["outStashLoc"][0], self.coords["outStashLoc"][1])
            self.acq.addGridFunClick(self.coords["outStashTopLeft"][0], self.coords["outStashTopLeft"][1], self.coords["outStashBottomRight"][0], self.coords["outStashBottomRight"][1], 24, 24, 2*r, 2*r+2, 0, 24, self.acq.addCtrlClick)
            self.acq.addCtrlClick(self.coords["inStashLoc"][0], self.coords["inStashLoc"][1])
            self.acq.addGridFunClick(self.coords["inventoryTopLeft"][0], self.coords["inventoryTopLeft"][1], self.coords["inventoryBottomRight"][0], self.coords["inventoryBottomRight"][1], 12, 5, 0, 12, 0, 5, self.acq.addCtrlClick)
        self.acq.ahkScript.write("Send \"{Shift down}\"\n")
        self.acq.addRightClick(
            self.coords["outStashTopLeft"][0] + ((self.coords["outStashBottomRight"][0] - self.coords["outStashTopLeft"][0])/23) * 23,
            self.coords["outStashTopLeft"][1]
        )
        self.acq.addGridFunClick(self.coords["outStashTopLeft"][0], self.coords["outStashTopLeft"][1], self.coords["outStashBottomRight"][0], self.coords["outStashBottomRight"][1], 24, 24, 0, 24, 0, 24, self.acq.addLeftClick)
        self.acq.ahkScript.write("Send \"{Shift up}\"\n")

    def run(self):
        self.acq.run()


class ClearNormalCoord:
    def __init__(self, pid):
        self.acq = AppCommandQueue(pid)
        if os.path.exists("%s_%s.json" % (self.__class__.__name__, pid)):
            self.coords = json.load(open("%s_%s.json" % (self.__class__.__name__, pid), "r"))
        else:
            self.clickIndex = 0
            self.coords = {}
            ahk.add_hotkey('~LButton', callback=self.onClick)
            ahk.add_hotkey('^~LButton', callback=self.onClick)
            ahk.start_hotkeys()
            input("Click on a non-char moving location ...")

    def onClick(self):
        mCoord = ahk.mouse_position
        if self.clickIndex == 0:
            print("Path of exile window active ...")
            print("Click on location of outgoing stash ...")
        if self.clickIndex == 1:
            self.coords['outStashLoc'] = [mCoord.x, mCoord.y]
            print("Outgoing stash location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on 1st unit to be clicked in outgoing stash ...")
        if self.clickIndex == 2:
            self.coords['outStashTopLeft'] = [mCoord.x, mCoord.y]
            print("Outgoing stash 1st unit to be clicked location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on the last unit to be clicked outgoing stash ...")
        if self.clickIndex == 3:
            self.coords['outStashBottomRight'] = [mCoord.x, mCoord.y]
            print("Outgoing stash last unit to be clicked location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on 1st unit to be clicked in inventory ...")
        if self.clickIndex == 4:
            self.coords['inventoryTopLeft'] = [mCoord.x, mCoord.y]
            print("1st unit to be clicked in inventory location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on the last unit to be clicked inventory ...")
        if self.clickIndex == 5:
            self.coords['inventoryBottomRight'] = [mCoord.x, mCoord.y]
            print("Last unit to be clicked inventory location: %s, %s." % (mCoord.x, mCoord.y))
            print("Ctrl+Click on location of seller ...")
        if self.clickIndex == 6:
            self.coords['seller'] = [mCoord.x, mCoord.y]
            print("Seller location: %s, %s." % (mCoord.x, mCoord.y))
            print("Click on Accept button on seller window ...")
        if self.clickIndex == 7:
            self.coords['sellerAccept'] = [mCoord.x, mCoord.y]
            print("Seller accept button location: %s, %s." % (mCoord.x, mCoord.y))
            print("Press enter to exit")
            with open("%s_%s.json" % (self.__class__.__name__, self.pid), "w") as f:
                f.write(json.dumps(self.coords, indent=4))
        self.clickIndex += 1

    def generateQuadCommandQueue(self):
        for r in range(12):
            self.acq.addLeftClick(self.coords["outStashLoc"][0], self.coords["outStashLoc"][1])
            self.acq.addGridFunClick(self.coords["outStashTopLeft"][0], self.coords["outStashTopLeft"][1], self.coords["outStashBottomRight"][0], self.coords["outStashBottomRight"][1], 24, 24, 2*r, 2*r+2, 0, 24, self.acq.addCtrlClick)
            self.acq.addCtrlClick(self.coords["seller"][0], self.coords["seller"][1])
            self.acq.addGridFunClick(self.coords["inventoryTopLeft"][0], self.coords["inventoryTopLeft"][1], self.coords["inventoryBottomRight"][0], self.coords["inventoryBottomRight"][1], 12, 5, 0, 12, 0, 5, self.acq.addCtrlClick)
            self.acq.addLeftClick(self.coords["sellerAccept"][0], self.coords["sellerAccept"][1])

    def generateNormalCommandQueue(self):
        for r in range(3):
            self.acq.addLeftClick(self.coords["outStashLoc"][0], self.coords["outStashLoc"][1])
            self.acq.addGridFunClick(self.coords["outStashTopLeft"][0], self.coords["outStashTopLeft"][1], self.coords["outStashBottomRight"][0], self.coords["outStashBottomRight"][1], 12, 12, 4*r, 4*r+4, 0, 12, self.acq.addCtrlClick)
            self.acq.addCtrlClick(self.coords["seller"][0], self.coords["seller"][1])
            self.acq.addGridFunClick(self.coords["inventoryTopLeft"][0], self.coords["inventoryTopLeft"][1], self.coords["inventoryBottomRight"][0], self.coords["inventoryBottomRight"][1], 12, 5, 0, 12, 0, 5, self.acq.addCtrlClick)
            self.acq.addLeftClick(self.coords["sellerAccept"][0], self.coords["sellerAccept"][1])

    def run(self):
        self.acq.run()
