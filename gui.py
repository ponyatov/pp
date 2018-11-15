## @file
## @brief native client GUI

# https://github.com/ponyatov/pyFORTH/blob/master/FORTH.py

## @defgroup gui Native client GUI
## @frief wxWidgets
## @{

import wx, wx.stc, threading

from sym import *
from forth import *

import time

## wx application
app = wx.App()

## generic GUI window
class GUI_window(wx.Frame):
    
    ## @name initialization
    
    ## define constructor parameters to default values specific for our app
    ## @param[in] title window title
    ## @param[in] filename file name will be used on save console content
    def __init__(self,parent=None,title='KB/wx',filename=sys.argv[0]+'.save'):
        wx.Frame.__init__(self,parent,title='%s:%s'%(title,filename))
        ## file name will be used for console content save/load
        self.filename = filename
        self.initMenu()
        self.initEditor()
    ## initialize menu
    def initMenu(self):
        ## menu bar
        self.menubar = wx.MenuBar() ; self.SetMenuBar(self.menubar)
        
        ## file submenu
        self.file = wx.Menu() ; self.menubar.Append(self.file,'&File')
        ## file/save console content
        self.save = self.file.Append(wx.ID_SAVE,'&Save')
        self.Bind(wx.EVT_MENU,self.onSave,self.save)
        ## file/quit
        self.quit = self.file.Append(wx.ID_EXIT,'&Quit')
        self.Bind(wx.EVT_MENU,self.onQuit,self.quit)
        
        ## debug submenu
        self.debug = wx.Menu() ; self.menubar.Append(self.debug,'&Debug')
        ## debug/update
        self.update = self.debug.Append(wx.ID_REFRESH,'&Update\tF12')
        self.Bind(wx.EVT_MENU,self.onUpdate,self.update)
        
    ## @name event callbacks
    
    ## quit event callback
    def onQuit(self,event):
        wnMain.Close() ; wnStack.Close() ; wnWords.Close()
    ## save console content callback
    def onSave(self,event):
        with open(self.filename,'w') as F: F.write(self.editor.GetValue())
    ## reload last file
    def onLoad(self,event):
        try:
            with open(self.filename,'r') as F: self.editor.SetValue(F.read())
        except IOError: pass
        
    ## update callback
    def onUpdate(self,event):
        wnStack.Show() ; wnWords.Show()

    ## @name script editor
    
    ## initialize script editor widget
    def initEditor(self):
        ## script editor widget (Scintilla)
        self.editor = wx.stc.StyledTextCtrl(self)
        # reload last file
        self.onLoad(None)
        # configure style & colors
        self.initColorizer()
        
    ## @name colorizer
    
    ## init colorizer styles & lexer
    def initColorizer(self):
        ## monospace font from system
        self.font = wx.Font(14, wx.FONTFAMILY_MODERN,
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # configure default editor font
        self.editor.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,
        "face:%s,size:%d" % (self.font.GetFaceName(), self.font.GetPointSize()))
        # configure styles
        ## default style
        self.style_DEFAULT = wx.stc.STC_STYLE_DEFAULT
        self.editor.StyleSetSpec(self.style_DEFAULT,'fore:lightgreen,back:black')
        self.editor.StyleClearAll()
        self.editor.SetCaretForeground('red')
#         # bind colorizer event
#         self.editor.Bind(wx.stc.EVT_STC_STYLENEEDED,self.onStyle)
        
    ## colorizer callback
    def onStyle(self,event):
        text = self.editor.GetValue()
        self.editor.StartStyling(0,0xFF)
        self.editor.SetStyling(len(text),self.style_DEFAULT)
        
## main window
wnMain = GUI_window(filename=sys.argv[0]+'.console') ; wnMain.Show()

## stack window
wnStack = GUI_window(filename=sys.argv[0]+'.stack')

## words window
wnWords = GUI_window(filename=sys.argv[0]+'.words')
        
# start application
app.MainLoop()

# ## GUI works in a separate thread to let UI work in parallel with Forth VM
# class GUI_thread(threading.Thread):
#     ## construct main window
#     def __init__(self):
#         threading.Thread.__init__(self)
#         ## main window
#         self.main = GUI_window()
#     ## activate GUI event loop thread
#     def run(self):
#         self.main.Show()
# 
# ## singleton thread processes all GUI events
# gui_thread = GUI_thread()
# 
# ## start GUI system
# def GUI(): gui_thread.start() ; gui_thread.join()
# F << GUI
# 
# if __name__ == '__main__': GUI()

## @}
