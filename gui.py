"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import sys
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from matplotlib import colors
import numpy as np

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
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
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

        # Initialise some drawing settings                                          # TODO make a Settings option to change these (change values->clear canvas->redraw canvas)
        self.monitorheight = 30
        self.monitorspacing = 5
        self.monitorstep = 30

        # Initialise in light-mode
        self.textcolour = (0.0, 0.0, 0.0)  # Light mode text colour is black
        # Clear colour is already done in init_gl

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
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
        if self.monitorsshow:                                           # FIXME I don't know if this is broken or not but if it's buggy check this first
            self.render_monitors(0, 0)
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
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
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
        font = GLUT.GLUT_BITMAP_HELVETICA_12                    # TODO font options?

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def render_monitors(self, x_pos, y_pos):                    # TODO test this, need some other stuff working first
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
        hsv_colourbank =   [np.linspace(0, 1, no_monitors), 
                            np.zeros(no_monitors), 
                            np.zeros(no_monitors)]
        rgb_colourbank = colors.hsv_to_rgb(hsv_colourbank)
        
        # Draw
        index = 0
        for device_id, output_id in self.monitors.monitors_dictionary:
            
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]

            # Names
            y = y_pos+index*(self.monitorheight+self.monitorspacing)
            self.render_text(monitor_name, x_pos, y)
            
            # Traces
            GL.glColor3f(rgb_colourbank[index])
            index += 1
            GL.glBegin(GL.GL_LINE_STRIP)
            x = x_pos + self.fontsize*0.6*margin
            
            for signal in signal_list:
                x_last = x
                if signal == self.devices.HIGH:
                    y = y_pos + (index + 1) * self.monitorheight + index * self.monitorspacing # This shouldn't be necessary, just here for robustness
                    x += self.monitorstep
                if signal == self.devices.LOW:
                    y = y_pos+index*(self.monitorheight+self.monitorspacing) # This shouldn't be necessary, just here for robustness
                    x += self.monitorstep
                if signal == self.devices.RISING:
                    y = y_pos+index*(self.monitorheight+self.monitorspacing) # This shouldn't be necessary, just here for robustness
                    x += self.monitorstep/3 
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_last, y)
                    x_last = x
                    x += self.monitorstep/3
                    GL.glVertex2f(x, y+self.monitorheight)
                    GL.glVertex2f(x_last, y)
                    y += self.monitorheight
                    x_last = x
                    x += self.monitorstep/3
                if signal == self.devices.FALLING:
                    y = y_pos + (index + 1) * self.monitorheight + index * self.monitorspacing # This shouldn't be necessary, just here for robustness
                    x += self.monitorstep/3
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_last, y)
                    x_last = x
                    x += self.monitorstep/3
                    GL.glVertex2f(x, y-self.monitorheight)
                    GL.glVertex2f(x_last, y)
                    y -= self.monitorheight
                    x_last = x
                    x += self.monitorstep/3
                if signal == self.devices.BLANK:
                    # Skips one step ahead without drawing a line between, might leave a dot?
                    x += self.monitorstep
                    x_last = x
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_last, y)

            GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
    
    def toggledarkmode(self):
        if self.textcolour == [0.0, 0.0, 0.0]:
            # Now switching to dark mode
            self.textcolour = [1.0, 1.0, 1.0]   # Text is now white
            GL.glClearColor(0.1, 0.1, 0.1, 0.0) # Background is dark grey
        else:
            # Now switching to light mode
            self.textcolour = [0.0, 0.0, 0.0]   # Text is now black
            GL.glClearColor(1.0, 1.0, 1.0, 0.0) # Background is white



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

        # Set the background and text colours (default is light mode)
        self.lightmode = True
        self.textcolour = wx.Colour(0, 0, 0) # Black text
        self.SetBackgroundColour(wx.Colour(220, 220, 220)) # Background colour is light grey
        self.windowcolour = wx.Colour(255, 255, 255) # White windows

        # Variables for reading from the input text box
        self.character = "" # current character
        self.cursor = 0  # cursor position

        ## MENU BAR ##
        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_FILE, "&Show Description")            #TODO Implement description file readout
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")

        # Help Menu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_HELP_COMMANDS, "&Commands")           
        helpMenu.Append(wx.ID_HELP_CONTENTS, "&GUI")                #TODO Implement pop ups explaining each window
        menuBar.Append(helpMenu, "&Help")

        # Settings Menu
        settingsMenu = wx.Menu()
        settingsMenu.Append(wx.ID_SELECT_COLOR, "&Display Mode")    #TODO Implement Light/Dark mode
        menuBar.Append(settingsMenu, "&Settings")
        
        self.SetMenuBar(menuBar)


        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Log Box
        self.logstyle = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL
        self.log = wx.TextCtrl(self, 
                                wx.ID_ANY, 
                                size=(300,300),
                                style=self.logstyle)
        self.log.SetBackgroundColour(self.windowcolour)
        sys.stdout=self.log
        self.text_input = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
        self.text_input.SetBackgroundColour(self.windowcolour)


        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.spin.SetBackgroundColour(self.windowcolour)
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")         # TODO this button is useless atm

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_input.Bind(wx.EVT_TEXT_ENTER, self.on_text_input)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(left_sizer, 5, wx.EXPAND, 5)
        main_sizer.Add(side_sizer, 0,0)

        log_sizer.Add(self.log, 1, wx.TOP, 5)
        log_sizer.Add(self.text_input, 5, wx.BOTTOM, 5)

        left_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        left_sizer.Add(log_sizer, 1, wx.BOTTOM, 5)

        side_sizer.Add(self.text, 2, wx.TOP, 10)
        side_sizer.Add(self.spin, 2, wx.ALL, 5)
        side_sizer.Add(self.run_button, 2, wx.ALL, 5)
        
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):                                                       #TODO Go here to implement menu stuff
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()

        # File Tab
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

        # Help Tab
        if Id == wx.ID_HELP_COMMANDS:
            wx.MessageBox("User commands:"
                        "\nr N       - run the simulation for N cycles"
                        "\nc N       - continue the simulation for N cycles"
                        "\ns X N     - set switch X to N (0 or 1)"
                        "\nm X       - set a monitor on signal X"
                        "\nz X       - zap the monitor on signal X"
                        "\nh         - help (this command)"
                        "\nq         - quit the program",
                            "Command Help", wx.ICON_INFORMATION | wx.OK)

        # Settings Tab
        if Id == wx.ID_SELECT_COLOR:
            # Switch colours for everything
            self.canvas.toggledarkmode()        # FIXME for some reason this doesn't activate the first time, but does later so the canvas and everything else desync
            if self.lightmode:
                # Change to dark mode
                self.textcolour = wx.Colour(255, 255, 255) # White text
                self.SetBackgroundColour(wx.Colour(0, 0, 0)) # Background colour is black
                self.windowcolour = wx.Colour(20, 20, 20) # Dark Grey windows
                self.lightmode = False
            else:
                # Change to light mode
                self.textcolour = wx.Colour(0, 0, 0) # Black text
                self.SetBackgroundColour(wx.Colour(220, 220, 220)) # Background colour is light grey
                self.windowcolour = wx.Colour(255, 255, 255) # White windows
                self.lightmode = True
            # Trigger updates for everything to recolour
            self.Refresh()
            # Sub-windows
            self.log.SetBackgroundColour(self.windowcolour)
            self.text_input.SetBackgroundColour(self.windowcolour)
            self.spin.SetBackgroundColour(self.windowcolour)

                                                # TODO need to make text change colour as well

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        print("".join(["New spin control value: ", str(spin_value)]))
        

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        print("Run button pressed.")
        

    def on_text_input(self, event):
        """Handle the event when the user enters text."""
        self.cursor = 0 # lets it read more than just the first input by resetting the cursor each time
        self.text_input_value = self.text_input.GetValue()
        print(self.text_input_value)
        # Add integration with userint.py for running commands from the text box
        command = self.read_command()
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

        # Reset text_input to be empty
        self.text_input.SetValue("") # Might create a problem with whitespace being added to the input box

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

    def switch_command(self):
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
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self):
        """Remove the specified monitor."""
        monitor = self.read_signal_name()
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
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

    def run_command(self):
        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.read_number(0, None)

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_network(cycles):
                self.cycles_completed += cycles
            self.canvas.monitorsshow = True

    def continue_command(self):
        """Continue a previously run simulation."""
        cycles = self.read_number(0, None)
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_network(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))


#TODO Open a file browser to select definition file
#TODO Allow comments to be added at the end of the definition file?