# This Python file uses the following encoding: utf-8

"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import sys
from fileinput import filename

import numpy as np
import wx
import wx.glcanvas as wxcanvas
from matplotlib import colors
from OpenGL import GL, GLUT
from PIL import Image

from devices import Devices
from monitors import Monitors
from names import Names
from network import Network
from parse import Parser
from scanner import Scanner


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(
            parent,
            -1,
            attribList=[
                wxcanvas.WX_GL_RGBA,
                wxcanvas.WX_GL_DOUBLEBUFFER,
                wxcanvas.WX_GL_DEPTH_SIZE,
                16,
                0,
            ],
        )
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.monitors = monitors
        self.devices = devices
        self.monitorsshow = False

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Initialise some drawing settings
        self.monitorheight = 20
        self.monitorspacing = 15
        self.monitorstep = 30

        # Initialise in light-mode
        self.textcolour = (0.0, 0.0, 0.0)       # Light mode text colour is black
        self.clearcolour = (1.0, 1.0, 1.0, 0.0) # Background is white
        self.gridcolour = (0.8, 0.8, 0.8)       # Lines are a very light grey

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glClearColor(*self.clearcolour) 
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue >>> glColor3f(R, G, B)
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_last = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_last, y)
        GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True
        if (
            self.monitorsshow
        ):  
            self.render_monitors(30, 30)
        else:
            self.render("Monitor traces will appear after the circuit is run")

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
        if event.GetWheelRotation() < 0:
            self.zoom *= 1.0 + (event.GetWheelRotation() / (20 * event.GetWheelDelta()))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= 1.0 - (event.GetWheelRotation() / (20 * event.GetWheelDelta()))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(*self.textcolour)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        self.fontsize = 12
        font = GLUT.GLUT_BITMAP_HELVETICA_12  # TODO font options?

        for character in text:
            if character == "\n":
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def render_monitors(
        self, x_pos, y_pos
    ):  # TODO test this, need some other stuff working first
        "Render the monitor traces."
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Get some info about what needs to be drawn
        no_monitors = len(self.monitors.monitors_dictionary)
        margin = self.monitors.get_margin()

        # Create list of colours to draw from later
        hsv_colourbank = np.ones((no_monitors, 3))
        hsv_colourbank[:, 0] = np.linspace(0, 1-1/no_monitors, no_monitors)

        rgb_colourbank = 0*hsv_colourbank # need the rgb bank to be the same shape
        for i in range(no_monitors):
            rgb_colourbank[i, :] = colors.hsv_to_rgb(hsv_colourbank[i, :])

        # Monitor Traces
        index = 0
        for device_id, output_id in self.monitors.monitors_dictionary:

            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]

            # Colour
            [r, g, b] = rgb_colourbank[index, :]

            # Background Lines & Names
            y = y_pos + index * (self.monitorheight + self.monitorspacing)
            x = x_pos + self.fontsize * margin # Can add in another multiplier here, depends on spacing between signal names and the traces
            for line in range(len(signal_list)):
                # Linecolour is always a middle-grey
                GL.glColor3f(*self.gridcolour)
                GL.glBegin(GL.GL_LINES)
                GL.glVertex2f(x + line*self.monitorstep, y)
                GL.glVertex2f(x + line*self.monitorstep, y + self.monitorheight + self.monitorspacing)
                GL.glEnd()
            self.render_text(monitor_name, x_pos, y)

            # Traces
            GL.glColor3f(r, g, b)
            GL.glBegin(GL.GL_LINE_STRIP)

            for signal in signal_list:
                x_last = x
                if signal == self.devices.HIGH:
                    y = (
                        y_pos
                        + (index + 1) * self.monitorheight
                        + index * self.monitorspacing
                    )  # This shouldn't be necessary, just here for robustness
                    x += self.monitorstep
                if signal == self.devices.LOW:
                    y = y_pos + index * (
                        self.monitorheight + self.monitorspacing
                    )  # This shouldn't be necessary, just here for robustness
                    x += self.monitorstep
                if signal == self.devices.RISING:
                    y = y_pos + index * (
                        self.monitorheight + self.monitorspacing
                    )  # This shouldn't be necessary, just here for robustness
                    x_last = x
                    x += self.monitorstep / 3
                    GL.glVertex2f(x_last, y)
                    GL.glVertex2f(x, y + self.monitorheight)
                    y += self.monitorheight
                    x_last = x
                    x += 2*self.monitorstep / 3
                if signal == self.devices.FALLING:
                    y = (
                        y_pos
                        + (index + 1) * self.monitorheight
                        + index * self.monitorspacing
                    )  # This shouldn't be necessary, just here for robustness
                    x_last = x
                    x += self.monitorstep / 3
                    GL.glVertex2f(x_last, y)
                    GL.glVertex2f(x, y - self.monitorheight)
                    y -= self.monitorheight
                    x_last = x
                    x += 2*self.monitorstep / 3
                GL.glVertex2f(x_last, y)
                GL.glVertex2f(x, y)
                if signal == self.devices.BLANK:
                    # Skips one step ahead without drawing a line between, might leave a dot?
                    x += self.monitorstep
                    x_last = x

            index += 1
            GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def toggledarkmode(self):
        if self.textcolour == (0.0, 0.0, 0.0):
            # Now switching to dark mode
            self.textcolour = (1.0, 1.0, 1.0)       # Text is now white
            self.clearcolour = (0.1, 0.1, 0.1, 0.0) # Background is dark grey
            self.gridcolour = (0.2, 0.2, 0.2)       # Grid is now dark grey
        else:
            # Now switching to light mode
            self.textcolour = (0.0, 0.0, 0.0)       # Text is now black
            self.clearcolour = (1.0, 1.0, 1.0, 0.0) # Background is white
            self.gridcolour = (0.8, 0.8, 0.8)       # Grid is now light grey
        self.init = False
        self.on_paint(0) # Repaint the canvas

    def save_image(self, filepath):
        # Check the filepath is correct
        if "." in filepath:
            dot_index = filepath.find(".")
            post_dot = filepath[dot_index + 1 :]
            if post_dot not in ["png", "jpg", "jpeg"]:
                print(post_dot)
                print(
                    "There might be an issue with the file extension you have provided."
                )
        else:
            filepath += ".jpg"
        # Creates image from buffer info
        size = self.GetClientSize()
        img_pixels = GL.glReadPixels(
            0, 0, size.width, size.height, GL.GL_RGB, GL.GL_UNSIGNED_BYTE
        )
        image = Image.frombytes("RGB", (size.width, size.height), img_pixels).transpose(
            Image.FLIP_TOP_BOTTOM
        )

        image.save(filepath)


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))
        self.names = names
        self.devices = devices
        self.monitors = monitors
        self.network = network
        self.path = path

        # Set the background and text colours (default is light mode)
        self.lightmode = True
        self.textcolour = wx.Colour(0, 0, 0)  # Black text
        self.SetBackgroundColour(
            wx.Colour(220, 220, 220)
        )  # Background colour is light grey
        self.windowcolour = wx.Colour(255, 255, 255)  # White windows

        # Variables for reading from the input text box
        self.character = ""  # current character
        self.cursor = 0  # cursor position

        # This is from the initialisation of userint.py and is required for lots of the simulation tasks
        self.cycles_completed = 0  # number of simulation cycles completed

        ## MENU BAR ##
        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&? About")
        fileMenu.Append(wx.ID_FILE, "&… Show Description\tCtrl+D")
        fileMenu.Append(wx.ID_SAVE, "&💾 Save Monitor Graphs\tCtrl+S")
        fileMenu.Append(wx.ID_EXIT, "&❌ Exit\tCtrl+Q")
        menuBar.Append(fileMenu, "&File")

        # Help Menu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_HELP_COMMANDS, "&! Commands\tCtrl+Shift+C")
        menuBar.Append(helpMenu, "&Help")

        # Settings Menu
        settingsMenu = wx.Menu()
        settingsMenu.Append(wx.ID_SELECT_COLOR, "&◑ Toggle Dark Mode\tCtrl+T")
        settingsMenu.Append(wx.ID_SELECT_FONT, "&⎍ Modify Monitor Trace Settings")
        menuBar.Append(settingsMenu, "&Settings")

        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Log Box
        self.logstyle = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        self.log = wx.TextCtrl(self, wx.ID_ANY, size=(350, 300), style=self.logstyle)
        self.log.SetBackgroundColour(self.windowcolour)
        sys.stdout = self.log
        self.input_title = wx.StaticText(self, wx.ID_ANY, "Command Input")
        self.text_input = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE
        )
        self.text_input.SetBackgroundColour(self.windowcolour)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10", min = 1)
        self.spin.SetBackgroundColour(self.windowcolour)
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.run_button.SetBackgroundColour(self.windowcolour)
        self.switch_title = wx.StaticText(self, wx.ID_ANY, "Toggle Switches\n☐=0, ☑=1")

        # Constructs the switch list in a way that doesn't cause problems before stuff is connected
        try:
            self.switch_list_ids = self.devices.find_devices(
                self.devices.SWITCH
            )  # Gets all the switches
            self.switch_list_names = []
            self.switch_list = []
            for switch_id in self.switch_list_ids:
                switch_name = self.names.get_name_string(switch_id)
                self.switch_list_names.append(switch_name)
                switch = self.devices.get_device(switch_id)
                self.switch_list.append(switch)
        except AttributeError:
            print("An error occured while loading the switches")
            self.switch_list_ids = [1, 2, 3]
            self.switch_list = [1, 2, 3] # This should be a list of device objects, but that doesn't really work here
            self.switch_list_names = [
                "Placeholder",
                "Switch",
                "Names",
            ]  # This can go if the file is only run with a definition already in place (maybe switch to something empty later?)
        self.switch_toggles = wx.CheckListBox(
            self,
            wx.ID_ANY,
            choices=self.switch_list_names,
            name="Toggle Switches",
            style=wx.HSCROLL,
        )
        for switch in range(len(self.switch_list_names)):
            try:
                if self.switch_list[switch].switch_state == 1:
                    self.switch_toggles.Check(switch)
                else:
                    pass
            except AttributeError:  # I guessed the errors and it worked, this might cause issues later
                self.switch_toggles.SetCheckedItems([0, 2])

        # Repeat the above for monitor trace toggling
        self.monitor_title = wx.StaticText(self, wx.ID_ANY, "Toggle Monitors\n☐=off, ☑=on")
        try:
            (
                self.monitored_list,
                self.unmonitored_list,
            ) = (
                self.monitors.get_signal_names()
            )  # Gets the monitored and unmonitored signals
        except AttributeError:
            print("An error occured while loading the monitors")
            self.monitored_list = ["Placeholder_On"]
            self.unmonitored_list = ["Off1", "Off2", "Off4"]
        self.all_monitors = self.monitored_list + self.unmonitored_list
        self.monitor_toggles = wx.CheckListBox(
            self,
            wx.ID_ANY,
            choices=self.all_monitors,
            name="Monitor Toggles",
            style=wx.HSCROLL,
        )
        if len(self.monitored_list) == 1:
            self.monitor_toggles.Check(0)
        elif len(self.monitored_list) > 1:
            self.monitor_toggles.SetCheckedItems(range(len(self.monitored_list)))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_input.Bind(wx.EVT_TEXT_ENTER, self.on_text_input)
        self.switch_toggles.Bind(wx.EVT_CHECKLISTBOX, self.on_switch_check)
        self.monitor_toggles.Bind(wx.EVT_CHECKLISTBOX, self.on_monitor_check)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(left_sizer, 5, wx.EXPAND, 5)
        main_sizer.Add(side_sizer, 0, wx.ALL, 5)

        log_sizer.Add(self.log, wx.EXPAND, 1, wx.TOP, 1)
        log_sizer.Add(input_sizer, 1, wx.LEFT | wx.TOP | wx.BOTTOM, 5)

        input_sizer.Add(self.input_title, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        input_sizer.Add(self.text_input, 8, wx.EXPAND, 0)
        input_sizer.SetMinSize(150, 300)

        left_sizer.Add(self.canvas, 1, wx.EXPAND)
        left_sizer.Add(log_sizer, 0, wx.TOP, 5)

        side_sizer.Add(self.text, 0, 1)
        side_sizer.Add(self.spin, 0, 1)
        side_sizer.Add(self.run_button, 0, 1)
        side_sizer.Add(self.switch_title, 1, wx.ALIGN_CENTER | wx.TOP, 10)
        side_sizer.Add(self.switch_toggles, wx.EXPAND, 1, 1)
        side_sizer.Add(self.monitor_title, 1, wx.ALIGN_CENTER | wx.TOP, 10)
        side_sizer.Add(self.monitor_toggles, wx.EXPAND, 1, 1)
        self.switch_toggles.SetMaxSize(wx.Size(120, 500))
        self.monitor_toggles.SetMaxSize(wx.Size(120, 500))
        self.switch_toggles.SetMinSize(wx.Size(120, 100))
        self.monitor_toggles.SetMinSize(wx.Size(120, 100))

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()

        # File Tab
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
                "Logic Simulator\nCreated by Mojisola Agboola\n2017\n"
                "Group 19 \\ im475 --- tjad2  --- tjb94\n 2022",
                "About Logsim",
                wx.ICON_INFORMATION | wx.OK,
            )
        if Id == wx.ID_SAVE:
            ask = wx.TextEntryDialog(
                self,
                "Please input the filepath you would like to save the image to\nThe default extension is .jpg",
            )
            if ask.ShowModal():
                image_name = ask.GetValue()
                self.canvas.save_image(image_name)
        if Id == wx.ID_FILE:
            file = open(self.path, "r")
            filetxt = file.read()
            resp = wx.MessageBox(
                "".join([filetxt, "\n\n---------------------\nPrint this in GUI log?"]),
                "Description File",
                wx.ICON_INFORMATION | wx.YES | wx.NO,
            )
            if resp == wx.YES:
                print(filetxt)

        # Help Tab
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox(
                "User commands:"
                "\nr N       - run the simulation for N cycles"
                "\nc N       - continue the simulation for N cycles"
                "\ns X N     - set switch X to N (0 or 1)"
                "\nm X       - set a monitor on signal X"
                "\nz X       - zap the monitor on signal X"
                "\nh         - help (this command)"
                "\nq         - quit the program",
                "Command Help",
                wx.ICON_INFORMATION | wx.OK,
            )

        # Settings Tab
        if Id == wx.ID_SELECT_FONT:
            # Change Monitor Trace Settings
            mtDialog = MonitorSetDialog(self, self, id=wx.ID_ANY, title="Change Monitor Trace Settings")
            mtDialog.ShowModal()
        if Id == wx.ID_SELECT_COLOR:
            # Switch colours for everything
            self.canvas.toggledarkmode()
            if self.lightmode:
                # Change to dark mode
                self.textcolour = wx.Colour(255, 255, 255)  # White text
                self.SetBackgroundColour(
                    wx.Colour(0, 0, 0)
                )  # Background colour is black
                self.windowcolour = wx.Colour(20, 20, 20)  # Dark Grey windows
                self.lightmode = False
            else:
                # Change to light mode
                self.textcolour = wx.Colour(0, 0, 0)  # Black text
                self.SetBackgroundColour(
                    wx.Colour(220, 220, 220)
                )  # Background colour is light grey
                self.windowcolour = wx.Colour(255, 255, 255)  # White windows
                self.lightmode = True
            # Trigger updates for background to recolour
            self.Refresh()
            # Sub-windows
            self.log.SetBackgroundColour(self.windowcolour)
            self.log.SetForegroundColour(self.textcolour)
            self.text_input.SetBackgroundColour(self.windowcolour)
            self.text_input.SetForegroundColour(self.textcolour)
            self.input_title.SetForegroundColour(self.textcolour)
            self.spin.SetBackgroundColour(self.windowcolour)
            self.spin.SetForegroundColour(self.textcolour)
            self.run_button.SetBackgroundColour(self.windowcolour)
            self.run_button.SetForegroundColour(self.textcolour)
            self.text.SetForegroundColour(
                self.textcolour
            )  # TODO See if scrollbars can be done if they aren't wx.ScrollBar?
            self.switch_title.SetForegroundColour(self.textcolour)
            self.monitor_title.SetForegroundColour(self.textcolour)
            self.switch_toggles.SetBackgroundColour(self.windowcolour)
            self.monitor_toggles.SetBackgroundColour(self.windowcolour)
            for switch in range(len(self.switch_list_ids)):
                self.switch_toggles.SetItemBackgroundColour(switch, self.windowcolour)
                self.switch_toggles.SetItemForegroundColour(switch, self.textcolour)
            for monitor in range(len(self.all_monitors)):
                self.monitor_toggles.SetItemBackgroundColour(monitor, self.windowcolour)
                self.monitor_toggles.SetItemForegroundColour(monitor, self.textcolour)

    ## Sidebar events ##
    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        print("".join(["New spin control value: ", str(spin_value)]))

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        print("Run button pressed.")
        self.run_command(self.spin.GetValue())

    def on_switch_check(self, event):  
        """Handle the event when the user clicks one of the switch checkboxes"""
        switch_index = event.GetInt()
        switch = self.switch_list[switch_index]
        switch_id = switch.device_id
        switch_name = self.switch_list_names[switch_index]
        switch_before = switch.switch_state
        switch_after = 1 - switch_before
        print(
            "".join(
                [
                    str(switch_name),
                    " has been changed from ",
                    str(switch_before),
                    " to ",
                    str(switch_after),
                ]
            )
        )
        if self.devices.set_switch(switch_id, switch_after):
            print("Successfully set switch.")
        else:
            print("Error! Invalid switch.")

    def on_monitor_check(
        self, event
    ): 
        """Handle the event when the user clicks on one of the monitor checkboxes"""
        monitor_index = event.GetInt()
        monitor_name = self.all_monitors[monitor_index]
        # Check if monitor was active or inactive before
        [device, port] = self.id_from_name(monitor_name)
        if monitor_name in self.monitored_list:
            print("".join(["The signal ", monitor_name, " is no longer monitored"]))
            if self.monitors.remove_monitor(device, port):
                print("Monitor removed successfully.")
                # Remove the monitor from the monitored list and add it to the unmonitored list
                self.monitored_list.remove(monitor_name)
                self.unmonitored_list.append(monitor_name)
                self.canvas.on_paint(0)
            else:
                print("Error! Invalid monitor.")
        elif monitor_name in self.unmonitored_list:
            print("".join(["The signal ", monitor_name, " is now being monitored"]))
            code = self.monitors.make_monitor(device, port, self.cycles_completed)
            if  code == self.monitors.NO_ERROR:
                print("Monitor added successfully.")
                # Remove the monitor from the unmonitored list and add it to the monitored list
                self.unmonitored_list.remove(monitor_name)
                self.monitored_list.append(monitor_name)
                self.canvas.on_paint(0)
            elif code == self.monitors.NOT_OUTPUT:
                print("Error! Invalid monitor output.")
            elif code == self.network.DEVICE_ABSENT:
                print("Error! Can't find the device to monitor.")
            elif code == self.monitors.MONITOR_PRESENT:
                print("Error! This signal is already monitored.")
        else:
            print(
                "Something has gone wrong: the monitor list doesn't seem to be reading correctly."
            )  # This really shouldn't ever happen

    # Get signal (& port) ids from their names
    def id_from_name(self, name):
        parts = name.split(".", 1)
        if len(parts) == 1:
            dev_name = parts[0]
            dev_id = self.names.query(dev_name)
            port_id = None
        elif len(parts) == 2:
            [dev_name, port_name] = parts
            dev_id = self.names.query(dev_name)
            port_id = self.names.query(port_name)
        return [dev_id, port_id]


    ## Text command events ##
    def on_text_input(self, event):
        """Handle the event when the user enters text."""
        self.cursor = 0  # lets it read more than just the first input by resetting the cursor each time
        self.text_input_value = self.text_input.GetValue()
        print(self.text_input_value)
        # Add integration with userint.py for running commands from the text box
        command = self.read_command()
        try:
            if command == "h":
                self.help_command()
            elif command == "s":
                self.switch_command()
            elif command == "m":
                self.monitor_command()
            elif command == "z":
                self.zap_command()
            elif command == "r":
                self.run_command()
            elif command == "c":
                self.continue_command()
            elif command == "q":
                self.Close(True)
            else:
                print("Invalid command. Enter 'h' for help.")
        except AttributeError:
            print("This function has not been implemented yet. Enter 'h' for help.")
            pass

        # Reset text_input to be empty
        self.text_input.SetValue(
            ""
        )  # FIXME Might create a problem with whitespace being added to the input box

    ## userint.py functions for the command line input
    def read_command(self):
        """Return the first non-whitespace character."""
        self.skip_spaces()
        return self.character

    def get_character(self):
        """Move the cursor forward by one character in the user entry."""
        if self.cursor < len(self.text_input_value):
            self.character = self.text_input_value[self.cursor]
            self.cursor += 1
        else:  # end of the line
            self.character = ""

    def skip_spaces(self):
        """Skip whitespace until a non-whitespace character is reached."""
        self.get_character()
        while self.character.isspace():
            self.get_character()

    def read_string(self):
        """Return the next alphanumeric string."""
        self.skip_spaces()
        name_string = ""
        if not self.character.isalpha():  # the string must start with a letter
            print("Error! Expected a name.")
            return None
        while self.character.isalnum():
            name_string = "".join([name_string, self.character])
            self.get_character()
        return name_string

    def read_name(self):
        """Return the name ID of the current string if valid.

        Return None if the current string is not a valid name string.
        """
        name_string = self.read_string()
        if name_string is None:
            return None
        else:
            name_id = self.names.query(name_string)
        if name_id is None:
            print("Error! Unknown name.")
        return name_id

    def read_signal_name(self):
        """Return the device and port IDs of the current signal name.

        Return None if either is invalid.
        """
        device_id = self.read_name()
        if device_id is None:
            return None
        elif self.character == ".":
            port_id = self.read_name()
            if port_id is None:
                return None
        else:
            port_id = None
        return [device_id, port_id]

    def read_number(self, lower_bound, upper_bound):
        """Return the current number.

        Return None if no number is provided or if it falls outside the valid
        range.
        """
        self.skip_spaces()
        number_string = ""
        if not self.character.isdigit():
            print("Error! Expected a number.")
            return None
        while self.character.isdigit():
            number_string = "".join([number_string, self.character])
            self.get_character()
        number = int(number_string)

        if upper_bound is not None:
            if number > upper_bound:
                print("Number out of range.")
                return None

        if lower_bound is not None:
            if number < lower_bound:
                print("Number out of range.")
                return None

        return number

    def help_command(self):
        """Print a list of valid commands."""
        print("User commands:")
        print("r N       - run the simulation for N cycles")
        print("c N       - continue the simulation for N cycles")
        print("s X N     - set switch X to N (0 or 1)")
        print("m X       - set a monitor on signal X")
        print("z X       - zap the monitor on signal X")
        print("h         - help (this command)")
        print("q         - quit the program")

    def switch_command(self, level="Read text"):
        """Set the specified switch to the specified signal level."""
        switch_id = self.read_name()
        if switch_id is not None:
            switch_state = self.read_number(0, 1)
            if switch_state is not None:
                if self.devices.set_switch(switch_id, switch_state):
                    print("Successfully set switch.")
                else:
                    print("Error! Invalid switch.")

    def monitor_command(self):
        """Set the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(
                device, port, self.cycles_completed
            )
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
                self.canvas.on_paint(0)
            else:
                print("Error! Could not make monitor.")

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
                self.canvas.on_paint(0)
            else:
                print("Error! Could not zap monitor.")

    def run_network(self, cycles):
        """Run the network for the specified number of simulation cycles.

        Return True if successful.
        """
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False
        self.monitors.display_signals()
        return True

    def run_command(self, cycles="Read text"):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        if cycles == "Read text":
            cycles = self.read_number(0, None)
        elif type(cycles) != int or cycles <= 0:
            print("Invalid number of cycles (must be integer). Enter 'h' for help.")
            cycles = None # Will stop the run_command here
        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles
            self.canvas.monitorsshow = True
            self.canvas.on_paint(0)

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(
                    " ".join(
                        [
                            "Continuing for",
                            str(cycles),
                            "cycles.",
                            "Total:",
                            str(self.cycles_completed),
                        ]
                    )
                )
                self.canvas.on_paint(0)


# TODO Open a file browser to select definition file
# TODO Allow comments to be added at the end of the definition file?

class MonitorSetDialog(wx.Dialog):
    "Used to modify monitor trace settings"
    def __init__(self, Gui, *args, **kw):
        super(MonitorSetDialog, self).__init__(*args, **kw)

        self.monitorheight = Gui.canvas.monitorheight
        self.monitorspacing = Gui.canvas.monitorspacing
        self.monitorstep = Gui.canvas.monitorstep
        self.Gui = Gui
        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Change Monitor Trace Settings")

    def InitUI(self):

        panel = wx.Panel(self)
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Monitor trace height"))
        self.mheight_spin = wx.SpinCtrl(panel, wx.ID_ANY, initial=self.monitorheight, min=1)
        main_sizer.Add(self.mheight_spin)
        main_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Monitor trace time step horizontal spacing"))
        self.mstep_spin = wx.SpinCtrl(panel, wx.ID_ANY, initial=self.monitorstep, min=1)
        main_sizer.Add(self.mstep_spin)
        main_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Vertical spacing between traces"))
        self.mspace_spin = wx.SpinCtrl(panel, wx.ID_ANY, initial=self.monitorspacing, min=1)
        main_sizer.Add(self.mspace_spin)

        panel.SetSizer(main_sizer)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Apply')
        closeButton = wx.Button(self, label='Close')
        button_sizer.Add(okButton)
        button_sizer.Add(closeButton)

        dialog_sizer.Add(panel)
        dialog_sizer.Add(button_sizer)

        self.SetSizer(dialog_sizer)

        okButton.Bind(wx.EVT_BUTTON, self.OnOk)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnOk(self, e):

        self.Gui.canvas.monitorheight = self.mheight_spin.GetValue()
        self.Gui.canvas.monitorspacing = self.mspace_spin.GetValue()
        self.Gui.canvas.monitorstep = self.mstep_spin.GetValue()
        self.Gui.canvas.on_paint(0)
        print("Updated settings")

    def OnClose(self, e):

        self.Destroy()
