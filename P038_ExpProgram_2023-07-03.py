#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thurs June 22 13:49:04 2023

@author: cyruskirkman and Marco Vasconcelos

This is the main code for Dr. Marco Vasconcelos's P038 forced choice in the
ephemeral choice task that was run in the summer of 2023 when he was on 
sabbatical at UCLA. The experiment had two main session types: 
    
    1)  Instrumental pre-training: one of the two b/y stimuli were placed either
        on the left or right part of the screen and a single peck to either
        lead to reinforcement and the following trial. 
        
    2) Training in Ephemeral Reward: pigeons were split into two groups: one
        that recieved forced choice trials with a single option at a time 
        and one that only recieved choices between the sub/optimal choice
        alternatives. The "optimal" key allowed the pigeons to pick a second
        reinforcer for each trial, while the "suboptimal" key limited them
        to a single reinforcer each trial. Keys were quasi-randomly assigned
        left and right each trial and were differntiable via their color (either
        blue or yellow), which was counterbalanced across subjects. Subjects in
        the forced condition recieved a mixture of choice trials and forced
        suboptimal and optimal trials. Subject assignments were tracked and 
        differentiable via a .csv document within the same directory.
        
Pre-training sessions consisted of 60 reinforced trials within a session, while
each training session was made up of two sub-sessions (40 trials each) each day
with a 10 m ITI seperating the two. Pigeons were not removed from their boxes
during this interval.
"""

# The first variable declared is whether the program is the operant box version
# for pigeons, or the test version for humans to view. The variable below is 
# a T/F boolean that will be referenced many times throughout the program 
# when the two options differ (for example, when the Hopper is accessed or
# for onscreen text, etc.). It needs to be changed manually based on whether
# the program is running in operant boxes (True) or not (False).
operant_box_version = True

# Prior to running any code, its conventional to first import relevant 
# libraries for the entire script. These can range from python libraries (sys)
# or sublibraries (setrecursionlimit) that are downloaded to every computer
# along with python, or other files within this folder (like control_panel or 
# maestro).
from tkinter import Toplevel, Canvas, BOTH, TclError, Tk, Label, Button, \
    StringVar, OptionMenu, IntVar, Radiobutton
from datetime import datetime, timedelta, date
from time import time
from csv import writer, DictReader, QUOTE_MINIMAL
from os import getcwd, mkdir, path as os_path
from random import shuffle
from sys import setrecursionlimit, path as sys_path

# Import hopper/other specific libraries from files on operant box computers
try:
    if operant_box_version:
        cwd = getcwd()
        sys_path.insert(0, str(os_path.expanduser('~')+"/OneDrive/Desktop/Hopper_Software"))
        import polygon_fill
        from hopper import HopperObject
except ModuleNotFoundError:
    print("ERROR :-( \n Cannot find the hopper software folder. \n Maybe a bird moved it? \n Check the trash and desktop folders and drag it to the desktop <3")
    input()

# Below  is just a safety measure to prevent too many recursive loops). It
# doesn't need to be changed.
setrecursionlimit(5000)

"""
The code below jumpstarts the loop by first building the hopper object and 
making sure everything is turned off, then passes that object to the
control_panel. The program is largely recursive and self-contained within each
object, and a macro-level overview is:
    
    ControlPanel -----------> MainScreen ------------> PaintProgram
         |                        |                         |
    Collects main           Runs the actual         Gets passed subject
    variables, passes      experiment, saves        name, but operates
    to Mainscreen          data when exited          independently
    

"""

# The first of two objects we declare is the ExperimentalControlPanel (CP). It
# exists "behind the scenes" throughout the entire session, and if it is exited,
# the session will terminate. The purpose of the control panel is to input 
# relevant information (like pigeon name) and select any variations to occur 
# within the upcoming session (sub/phase, FR, etc.)
class ExperimenterControlPanel(object):
    # The init function declares the inherent variables within that object
    # (meaning that they don't require any input).
    def __init__(self):
        # First, setup the data directory in "Documents"
        self.doc_directory = str(os_path.expanduser('~'))+"/Documents/"
        # Next up, we need to do a couple things that will be different based
        # on whether the program is being run in the operant boxes or on a 
        # personal computer. These include setting up the hopper object so it 
        # can be referenced in the future, or the location where data files
        # should be stored.
        if operant_box_version:
            # Setup the data directory in "Documents"
            self.doc_directory = str(os_path.expanduser('~'))+"/Documents/"
            self.data_folder = "P038_data" # The folder within Documents where subject data is kept
            self.data_folder_directory = str(os_path.expanduser('~'))+"/OneDrive/Desktop/Data/" + self.data_folder
        # Set hopper object to be a variable of self, so it can be referenced...
            self.Hopper = HopperObject()
        else: # If not, just save in the current directory the program us being run in 
            self.data_folder_directory = getcwd() + "/Data/"
            self.Hopper = None
        
        # setup the root Tkinter window
        self.control_window = Tk()
        self.control_window.title("P038 Control Panel")
        ##  Next, setup variables within the control panel:
        # Subject ID list (need to build/alphabetize) - TBD
        self.pigeon_name_list = ["Itzamma", "Mario", "Jubilee", "Herriot",
                                 "Meat Loaf", "Odin", "Vonnegut", "Durrell",
                                 "Thoth", "Bowie"]
        self.pigeon_name_list.sort() # This alphabetizes the list
        self.pigeon_name_list.insert(0, "TEST")
        # Subject ID menu and label
        Label(self.control_window, text="Pigeon Name:").pack()
        self.subject_ID_variable = StringVar(self.control_window)
        self.subject_ID_variable.set("Select")
        self.subject_ID_menu = OptionMenu(self.control_window,
                                          self.subject_ID_variable,
                                          *self.pigeon_name_list,
                                          command=self.set_pigeon_ID).pack()
        
        # Training phases
        Label(self.control_window, text = "Select experimental phase:").pack()
        self.training_phase_variable = StringVar() # This is the literal text of the phase, e.g., "0: Autoshaping"
        self.training_phase_variable.set("Select") # Default
        self.training_phase_name_list = ["0: Pre-Training",
                                         "1: Training"
                                         ]
        self.training_phase_menu = OptionMenu(self.control_window,
                                          self.training_phase_variable,
                                          *self.training_phase_name_list)
        self.training_phase_menu.pack()
        
        # Record data variable? Y/N binary radio button
        Label(self.control_window,
              text = "Record data in seperate data sheet?").pack()
        self.record_data_variable = IntVar()
        self.record_data_rad_button1 =  Radiobutton(self.control_window,
                                   variable = self.record_data_variable,
                                   text = "Yes",
                                   value = True).pack()
        self.record_data_rad_button2 = Radiobutton(self.control_window,
                                  variable = self.record_data_variable,
                                  text = "No",
                                  value = False).pack()
        self.record_data_variable.set(True) # Default set to True
        
        
        # Start button
        self.start_button = Button(self.control_window,
                                   text = 'Start program',
                                   bg = "green2",
                                   command = self.build_chamber_screen).pack()
        
        # This makes sure that the control panel remains onscreen until exited
        self.control_window.mainloop() # This loops around the CP object
        
        
    def set_pigeon_ID(self, pigeon_name):
        # This function checks to see if a pigeon's data folder currently 
        # exists in the respective "data" folder within the Documents
        # folder and, if not, creates one.
        if operant_box_version:
            try:
                if not os_path.isdir(self.data_folder_directory + pigeon_name):
                    mkdir(os_path.join(self.data_folder_directory, pigeon_name))
                    print("\n ** NEW DATA FOLDER FOR %s CREATED **" % pigeon_name.upper())
            except FileExistsError:
                print("Data folder for %s exists." % pigeon_name)       
        else:
            parent_directory = getcwd() + "/data/"
            if not os_path.isdir(parent_directory + pigeon_name):
                mkdir(os_path.join(parent_directory, pigeon_name))
                print("\n ** NEW DATA FOLDER FOR %s CREATED **" % pigeon_name.upper())
                
    def build_chamber_screen(self):
        # Once the green "start program" button is pressed, then the mainscreen
        # object is created and pops up in a new window. It gets passed the
        # important inputs from the control panel. Importantly, it won't
        # run unless all the informative fields are filled in.
        if self.subject_ID_variable.get() in self.pigeon_name_list:
            if self.training_phase_variable.get() in self.training_phase_name_list:
                list_of_variables_to_pass = [self.Hopper,
                                             self.subject_ID_variable.get(),
                                             self.record_data_variable.get(), # Boolean for recording data (or not)
                                             self.data_folder_directory, # directory for data folder
                                             self.training_phase_variable.get(), # Which training phase
                                             self.training_phase_name_list # list of training phases
                                             ]
                print(f"{'SESSION STARTED': ^15}") 
                self.MS = MainScreen(*list_of_variables_to_pass)
            else:
                print("\nERROR: Input Experimental Phase Before Starting Session")
        else:
            print("\nERROR: Input Correct Pigeon ID Before Starting Session")
            

# Next, setup the MainScreen object
class MainScreen(object):
    # We need to declare several functions that are 
    # called within the initial __init__() function that is 
    # run when the object is first built:
    
    def __init__(self, Hopper, subject_ID, record_data, data_folder_directory,
                 training_phase, training_phase_name_list):
        ## Firstly, we need to set up all the variables passed from within
        # the control panel object to this MainScreen object. We do this 
        # by setting each argument as "self." objects to make them global
        # within this object.
        
        # Setup training phase
        self.training_phase = training_phase_name_list.index(training_phase) # Starts at 0 **
        self.training_phase_name_list = training_phase_name_list
        # Setup data directory
        self.data_folder_directory = data_folder_directory
        # Set the other pertanent variables given in the command window
        self.subject_ID = subject_ID
        self.record_data = record_data

        ## Next, set up the visual Canvas
        self.root = Toplevel()
        self.root.title("P038: " + self.training_phase_name_list[self.training_phase][3:]) # this is the title of the windows
        self.mainscreen_height = 600 # height of the experimental canvas screen
        self.mainscreen_width = 800 # width of the experimental canvas screen
        self.root.bind("<Escape>", self.exit_program) # bind exit program to the "esc" key
        
        # If the version is the one running in the boxes...
        if operant_box_version: 
            # Keybind relevant keys
            self.cursor_visible = True # Cursor starts on...
            self.change_cursor_state() # turn off cursor UNCOMMENT
            self.root.bind("<c>", # bind cursor on/off state to "c" key
                           lambda event: self.change_cursor_state()) 
            
            # Then fullscreen (on a 800x600p screen)
            self.root.attributes('-fullscreen', True)
            self.mastercanvas = Canvas(self.root,
                                   bg="black")
            self.mastercanvas.pack(fill = BOTH,
                                   expand = True)
        # If we want to run a "human-friendly" version outide the box
        else: 
            # No keybinds and  800x600p fixed window
            self.mastercanvas = Canvas(self.root,
                                   bg="black",
                                   height=self.mainscreen_height,
                                   width = self.mainscreen_width)
            self.mastercanvas.pack()
            
        # Setup hopper (passed from the control panel)
        self.Hopper = Hopper
        
        # Timing variables
        self.start_time = None # This will be reset once the session actually starts
        self.trial_start = None # Duration into each trial as a second count, resets each trial
        self.session_duration = datetime.now() + timedelta(minutes = 90) # Max session time is 90 min
        
        # Hopper and ITI duration per bird refereneced a settings sheet
        # self.ITI_duration = 10 * 1000 # duration of inter-trial interval (ms)
        self.ITI_color = "Slategray2"
        if self.subject_ID == "TEST":
            self.between_session_ITI_duration = 15 * 1000 # 15 seconds
        else:
            self.between_session_ITI_duration = 15 * 60 * 1000 # 15 minutes
        
        self.current_trial_counter = 0 # counter for current trial in session
        self.reinforcers_provided = 0 # number of trials where a reinforcer was provided
        # Max number of trials within a session differ by phase and was set 
        # later in the first-ITI function
        
        # Here are variables for data structuring 
        self.session_data_frame = [] #This where trial-by-trial data is stored
        header_list = ["SessionTime", "Xcord","Ycord", "LocationEvent",
                       "LeftKey", "RightKey", "TrialType", "ChoiceKeysActive",
                       "TrialTime", "TrialNum", "ReinforcersProvided",
                       "ITIDuration", "Subject", "Condition",
                       "TrainingPhase", "Date"] # Column headers
        
        self.session_data_frame.append(header_list) # First row of matrix is the column headers
        self.date = date.today().strftime("%y-%m-%d") # Today's date

        ## Finally, start the recursive loop that runs the program:
        self.place_birds_in_box()

    def place_birds_in_box(self):
        # This is the default screen run until the birds are placed into the
        # box and the space bar is pressed. It then proceedes to the ITI. It only
        # runs in the operant box version. After the space bar is pressed, the
        # "first_ITI" function is called for the only time prior to the first trial
        
        def first_ITI(event):
            # Is initial delay before first trial starts. It first deletes all the
            # objects off the mainscreen (making it blank), unbinds the spacebar to 
            # the first_ITI link, followed by a 30s pause before the first trial to 
            # let birds settle in and acclimate.
            self.mastercanvas.delete("all")
            self.root.unbind("<space>")
            self.start_time = datetime.now() # Set start time
            
            # Then we can read the settings .csv to set up subject-specific 
            # parameters for this session.
            if operant_box_version:
                settings_csv_directory = str(os_path.expanduser('~')+"/OneDrive/Desktop/P038/P038_Settings-Assignments.csv")
            else:
                settings_csv_directory = "P038_Settings-Assignments.csv"
            
            # Next, check if the csv file exists.
            settings_list = []
            if os_path.isfile(settings_csv_directory):
                # Read the content of the csv as a dictionary
                with open(settings_csv_directory, 'r', encoding='utf-8-sig') as data:
                    for line in DictReader(data):
                        settings_list.append(line)
            else:
                print("Error: cannot find settings csv file!")
                input()
            # After we have a list off the settings for all subjects converted 
            # into a Python-friendly data form (list of dictionaries), we can 
            # narrow it down to a single subject-specific dictionary
            settings_dict = "NA"
            try:
                for entry in settings_list:
                    if entry["Subject"] == self.subject_ID:
                        settings_dict = entry
            except KeyError:
                print("Error reading settings .csv.\n Make sure it is in comma-dilimeted form.")
                    
            # And we can then update subject-specific settings...
            print(settings_dict)
            try:
                self.hopper_duration = int(settings_dict["Hopper Duration (ms)"])
                self.ITI_duration = int(settings_dict["ITI Duration (ms)"])
                self.experimental_group = settings_dict["Group"]
                self.optimal_color = settings_dict["Optimal Color"]
                self.suboptimal_color = settings_dict["Suboptimal Color"]
            except TypeError:
                print("Error: Unable to import Settings Sheet for {self.subject_ID}")
                             
            # Next, we can set up the order of each trial within the session.
            # The total number of trials per session differs based on whether
            # the session is a pre-training (100% reinforced) or training 
            # (variably reinforced) session type.
            
            if self.training_phase == 0: # pre-training
                self.trials_per_session = 60 # 4 trial types * 15 iterations each
                self.trials_per_subsession = 60 # Only one subsession
                trial_option_list = [
                    "LO_trial", # left optimal
                    "RO_trial", # right optimal
                    "LS_trial", # left suboptimal
                    "RS_trial", # right suboptimal
                    ] * 15
                
            elif self.training_phase == 1: # rejection training
                self.trials_per_session = 80 
                self.trials_per_subsession = 40 # Two sub-sessions of 40 trials each
                # Two types of sessions (one for each group)
                if self.experimental_group == "Choice":
                    trial_option_list = ["LO_choice_trial",
                                         "RO_choice_trial"] * (self.trials_per_subsession//2)
                
                elif self.experimental_group == "Forced":
                    trial_option_list = [
                        "LO_choice_trial", # 12 total choice trials
                        "RO_choice_trial"]  * 6 + [
                            "LO_trial", # left optimal
                            "RO_trial", # right optimal
                            "LS_trial", # left suboptimal
                            "RS_trial", # right suboptimal
                            ] * 7
                            
            # Once we have the number of trials per session (and what type of
            # trials they will be), we can semi-randomly determine the order.
            # The key here will be that we're avoiding repeats of four or more
            # of the same trial type. We do this by shuffling the order of the 
            # trial option list until we get one that doesn't have any trials
            # that are repeated more than three times. Note that we ONLY do 
            # this for the Forced experimental  group, as the choice group has
            # uniformly  identical trials.
            self.trial_order_list = []
            
            while len(self.trial_order_list) != self.trials_per_session:
                shuffle(trial_option_list) # shuffle
                approved = True
                if self.training_phase == 0 or self.experimental_group == "Forced":
                    c = 0  # counter
                    # Cycle through the shuffled list...
                    while c < len(trial_option_list) and approved:
                        if c > 3:
                            a = trial_option_list[c]
                            if a == trial_option_list[c-1] and a == trial_option_list[c-2] and a == trial_option_list[c-3]:
                                approved = False
                        c += 1
                if approved:
                    for i in trial_option_list:
                        self.trial_order_list.append(i)
  
            # This is run until we reach the max number of trials per session
            # (so once for the pre-training phase and twice for the training
            # phase). We have the type of every sequential trial within the
            # session and we can get started! Let's set set up a timer and
            # move on to the ITI to start the first trial.
            if self.subject_ID == "TEST": # If test, don't worry about first ITI delay
                self.root.after(1, lambda: self.ITI())
            else: # Else, give 30 s for the first ITI to occur after the session begins
                self.root.after(30000, lambda: self.ITI())

        # This is outside of the "first_ITI()" function, but calls it with a 
        # space bar press
        self.root.bind("<space>", first_ITI) # bind cursor state to "space" key
        self.mastercanvas.create_text(350,300,
                                      fill="white",
                                      font="Times 20 italic bold",
                                      text=f"P037 \n Place bird in box, then press space \n Subject: {self.subject_ID} \n Training Phase {self.training_phase_name_list[self.training_phase]}")

    def ITI (self):
        # Every trial (including the first) "starts" with an ITI. The ITI function
        # does several different things:
        #   1) Checks to see if any session constraints have been reached
        #   2) Resets the hopper and any trial-by-trial variables
        #   3) Increases the trial counter by one
        #   4) Moves on to the next trial after a delay (ITI)
        
        # This function just clear the screen. It will be used a lot in the future, too.
        self.clear_canvas()

        # Make sure pecks during ITI are saved...
        self.mastercanvas.create_rectangle(0,0,
                                           self.mainscreen_width,
                                           self.mainscreen_height,
                                           fill = self.ITI_color,
                                           outline = self.ITI_color,
                                           tag = "bkgrd")
        self.mastercanvas.tag_bind("bkgrd",
                                   "<Button-1>",
                                   lambda event, 
                                   event_type = "ITI_peck": 
                                       self.write_data(event, event_type))
        
        # First, check to see if any session limits have been reached (e.g.,
        # if the max time or reinforcers earned limits are reached).
        if self.current_trial_counter  == self.trials_per_session:
            print("&&& Trial max reached &&&")
            self.exit_program("event")
            
# =============================================================================
#         elif datetime.now() >= (self.session_duration):
#             print("Time max reached")
#             self.exit_program("event")
# =============================================================================
        
        # Else, after a timer move on to the next trial. Note that,
        # although the after() function is given here, the rest of the code 
        # within this function is still executed before moving on.
        else: 
            # Print text on screen if a test (should be black if an experimental trial)
            if not operant_box_version or self.subject_ID == "TEST":
                self.mastercanvas.create_text(400,300,
                                              fill="purple2",
                                              font="Times 20 italic bold",
                                              text=f"ITI ({int(self.ITI_duration/1000)} sec.)")
                
            # This calls the Hopper function to turn it off, and resets other
            # variables. The hopper should be turned off in the previous function,
            # but this is an additional safeguard just to be safe.
            if operant_box_version:
                self.Hopper.change_hopper_state("Off")
                
            # Reset other variables for the following trial.
            self.trial_start = time() # Set trial start time (note that it includes the ITI, which is subtracted later)
            self.optimal_choice = False # Reset the choice tracker
            self.left_key = "NA" # reset state of left key
            self.right_key = "NA" # and right
            
            # Update data .csv file with previous trial's data
            self.write_comp_data(False)
                
            # Next up, set the string that tracks the trial type
            self.trial_type = self.trial_order_list[self.current_trial_counter]

            # Increment trial counter by one
            self.current_trial_counter += 1
            
            # If halfway through a training session, set up a 15 minute ITI
            # before the following trial. The screen should be black, here
            if self.training_phase == 1 and self.current_trial_counter ==  (self.trials_per_session//2 + 1):
                # Make sure pecks during ITI are saved...
                self.mastercanvas.create_rectangle(0,0,
                                                   self.mainscreen_width,
                                                   self.mainscreen_height,
                                                   fill = "black",
                                                   outline = "black",
                                                   tag = "bkgrd")
                self.mastercanvas.tag_bind("bkgrd",
                                           "<Button-1>",
                                           lambda event, 
                                           event_type = "between-session_ITI_peck": 
                                               self.write_data(event, event_type))
                # Onscreen feedback for testing...
                if not operant_box_version or self.subject_ID == "TEST":
                    self.mastercanvas.create_text(400,300,
                                                  fill="white",
                                                  font="Times 20 italic bold",
                                                  text=f"ITI ({int(self.between_session_ITI_duration/1000)} sec.)")
                # Then set a 15 m timer before continuing to the following trial
                self.root.after(self.between_session_ITI_duration,
                                lambda: self.build_keys())
                
                
            # If a regular ITI, set a shorter delay timer to proceed to the
            # next trial
            else:
                self.root.after(self.ITI_duration,
                                lambda: self.build_keys())
            
            # Finally, print terminal feedback "headers" for each event within the next trial
            print(f"\n{'*'*35} Trial {self.current_trial_counter} begins {'*'*35}") # Terminal feedback...
            print(f"{'Event Type':>30} | Xcord. Ycord. |  Session Time  | Trial Type")
        
    """
    Each trial is an iteration of the build_keys() funtion below. Because we
    are only using FR1 schedules, we don't need to build in any loops. During 
    choice trials, both optimal and suboptimal stimuli are presented together.
    If the suboptimal choice is selected, both stimuli are removed, food is 
    allocated, and the trial concludes and begins the ITI. If the optimal 
    choice is instead selected, the optimal choice is removed (but suboptimal
    remains onscreen), food is provided, and subjects are able to select the 
    suboptimal option as well to recieve an additional reinforcer before 
    the trial concludes.
    """
    
        
    def build_keys(self):
        # This is a function that builds the all the buttons on the Tkinter
        # Canvas. The Tkinter code (and geometry) may appear a little dense
        # here, but it follows many of the same rules. All keys will be built
        # during non-ITI intervals, but they will only be filled in and active
        # during specific times. However, pecks to keys will be differentiated
        # regardless of activity.
        
        # First, build the background. This basically builds a button the size of 
        # screen to track any pecks; buttons built on top of this button will
        # NOT count as background pecks but as "key" pecks, because the object is
        # covering that part of the background. Once a peck is made, an event line
        # is appended to the data matrix and eventually written to the data
        # file.
        self.clear_canvas() # Remove everything from the screen...
        
        # This calls the Hopper function to turn it off.
        if operant_box_version:
            self.Hopper.change_hopper_state("Off")
                
        self.mastercanvas.create_rectangle(0,0, # Top left
                                           self.mainscreen_width,
                                           self.mainscreen_height, # to bottom right
                                           fill = "black",
                                           outline = "black",
                                           tag = "bkgrd")
        self.mastercanvas.tag_bind("bkgrd",
                                   "<Button-1>",
                                   lambda event, 
                                   event_type = "background_peck": 
                                       self.write_data(event, event_type))

        # Coordinate dictionary for the shapes around a key. The keys are 
        # given in [x1, y1, x2, y2] coordinates
        self.key_coord_dict = {"left_choice_key": ["color", 200, 250, 300, 350],
                               "right_choice_key": ["color", 500, 250, 600, 350]}
        
        # Now we need to select the keys to build for this specific trial by
        # removing the others the dictionary above. First, we need to check 
        # whether this is the second half of an optimal choice trial. If so,
        # we need to remove the optimal choice such that only the suboptimal 
        # option is left available.
        if self.optimal_choice:
            if "L" in self.trial_type: # If left key...
                del self.key_coord_dict ["left_choice_key"]
            else:
                del self.key_coord_dict ["right_choice_key"]
                
        # Then do the opposite for non-choice trials
        elif "choice" not in self.trial_type: 
            if "L" in self.trial_type: # If left key...
                del self.key_coord_dict["right_choice_key"]
            else:
                del self.key_coord_dict ["left_choice_key"]
        
        # After we determine which keys to build, we can assign them a color (and
        # thereby differentiate their sub/optimal properties)
        for key in self.key_coord_dict:
            if key ==  "left_choice_key":
                if "LO" in self.trial_type:
                    self.left_key = "optimal"
                    self.key_coord_dict [key][0] = self.optimal_color
                elif "LS" in self.trial_type or ("RO" in self.trial_type and self.optimal_choice) or ("RO_choice" in self.trial_type):
                    self.left_key = "suboptimal"
                    self.key_coord_dict [key][0] = self.suboptimal_color
            elif key ==  "right_choice_key":
                if "RO" in self.trial_type:
                    self.right_key = "optimal"
                    self.key_coord_dict [key][0] = self.optimal_color
                elif "RS" in self.trial_type or ("LO" in self.trial_type and self.optimal_choice) or ("LO_choice" in self.trial_type):
                    self.right_key = "suboptimal"
                    self.key_coord_dict [key][0] = self.suboptimal_color
                    
                    
        # Now that we have all the coordinates and colors linked to each
        # specific key, we can use a for loop to build each one (or, in some
        # cases, only a single key).
        for key_string in self.key_coord_dict :
            # First up, build the actual circle that is around the key and will
            # contain the stimulus. Order is important here, as shapes built
            # on top of each other will overlap/cover each other. We 
            # have to build a little "active" space behind the key, first.
            self.mastercanvas.create_oval(
                self.key_coord_dict[key_string][1] - 25,
                self.key_coord_dict[key_string][2] - 25,
                self.key_coord_dict[key_string][3] + 25,
                self.key_coord_dict[key_string][4] + 25,
                fill = "", # No fill/color
                outline = "",
                tag = key_string # This tag allows us to bind a function to all related keys
                )

            # Then build the literal key...
            self.mastercanvas.create_oval(
                *self.key_coord_dict [key_string][1:], # coordinates
                fill = self.key_coord_dict[key_string][0], # color
                outline = "",
                tag = key_string)
                
            # And lastly tie a function to a key peck. The function is
            # key_press() for all the keys, but will be passed a different
            # "key_string" argument.
            self.mastercanvas.tag_bind(
                key_string,
                "<Button-1>",
                lambda event,
                    key_string = key_string:
                        self.key_press(event,
                                       key_string)
                        )
    
    def key_press(self, event, keytag):
        # This function is called every time a key press is called, regardless
        # of which key or whether that key is "active." If a key is active, 
        # that means that the hopper is not currently up and subjects have
        # the opportunity for additional reinforcement (hence, the
        # self.feeding_interval boolean is False). If the key is not active, 
        # a data point will be recorded, but nothing will functionally change
        # within the trial.
        
        # We need two different processes for the two different phases.
        # For pretraining, we give food no matter what
        if self.training_phase == 0:
            # Write data for the peck
            self.write_data(event, (f"{keytag}_peck"))
            self.provide_food()
                
        # For the training task, it's a bit more complicated...
        elif self.training_phase == 1:
            # We have to contruct a matrix of coordinates that need to be 
            # covered after a choice is made. If optimal trial type and choice:
            if ("LO" in self.trial_type and "left" in keytag) or ("RO" in self.trial_type and "right" in keytag):
                # Write data for the peck
                self.write_data(event, "optimal_peck")
                self.optimal_choice = True
            # Else if a suboptimal choice...
            else:
                # Write data for the peck
                self.write_data(event, "suboptimal_peck")
                self.optimal_choice = False

            # Then provide food if the hopper isn't already activated
            self.provide_food()
    
    def provide_food(self):
        # This function is contingent upon correct and timely choice key
        # response. It opens the hopper and then either leads to ITI after a preset
        # reinforcement interval (i.e., hopper down duration) in the pre-training
        # phase or with suboptimal choice, OR cycles back into the build_keys()
        # function for the opportunity to earn a second reinforcer.
        self.write_data(None, "reinforcer_provided")
        self.reinforcers_provided += 1 # We also need to add one to the reinforcement counter
        self.clear_canvas()
        # Make sure pecks during feeding interval are saved...
        
        self.mastercanvas.create_rectangle(0,0,
                                           self.mainscreen_width,
                                           self.mainscreen_height,
                                           fill = "black",
                                           tag = "bkgrd")
        self.mastercanvas.tag_bind("bkgrd",
                                   "<Button-1>",
                                   lambda event, 
                                   event_type = "hopper_up_peck": 
                                       self.write_data(event, event_type))


        # Turn on hopper
        if operant_box_version:
            self.Hopper.change_hopper_state("On") 
        
        # If optimal choice, the trial continues
        if self.optimal_choice:
            self.root.after(self.hopper_duration,
                lambda: self.build_keys())
        # Otherwise, it concludes
        else:
            self.root.after(self.hopper_duration,
                            lambda: self.ITI())
        
        # If testing, give onscreen feedback...
        if not operant_box_version or self.subject_ID == "TEST":
            self.mastercanvas.create_text(400,400,
                                          fill="white",
                                          font="Times 20 italic bold", 
                                          text=f"Food accessible ({int(self.hopper_duration/1000)} s)") # just onscreen feedback

    # Outside of the main loop functions, there are several additional
    # repeated functions that are called either outside of the loop or 
    # multiple times across phases:
    
    def change_cursor_state(self):
        # This function toggles the cursor state on/off. 
        # May need to update accessibility settings on your machince.
        if self.cursor_visible: # If cursor currently on...
            self.root.config(cursor="none") # Turn off cursor
            print("### Cursor turned off ###")
            self.cursor_visible = False
        else: # If cursor currently off...
            self.root.config(cursor="") # Turn on cursor
            print("### Cursor turned on ###")
            self.cursor_visible = True
    
    def clear_canvas(self):
         # This is by far the most called function across the program. It
         # deletes all the objects currently on the Canvas. A finer point to 
         # note here is that objects still exist onscreen if they are covered
         # up (rendering them invisible and inaccessible); if too many objects
         # are stacked upon each other, it can may be too difficult to track/
         # project at once (especially if many of the objects have functions 
         # tied to them. Therefore, its important to frequently clean up the 
         # Canvas by literally deleting every element.
        try:
            self.mastercanvas.delete("all")
        except TclError:
            print("No screen to exit")
        
    def exit_program(self, event): 
        # This function can be called two different ways: automatically (when
        # time/reinforcer session constraints are reached) or manually (via the
        # "End Program" button in the control panel or bound "esc" key).
            
        # The program does a few different things:
        #   1) Return hopper to down state, in case session was manually ended
        #       during reinforcement (it shouldn't be)
        #   2) Turn cursor back on
        #   3) Writes compiled data matrix to a .csv file 
        #   4) Destroys the Canvas object 
        #   5) Calls the Paint object, which creates an onscreen Paint Canvas.
        #       In the future, if we aren't using the paint object, we'll need 
        #       to 
        def other_exit_funcs():
            if operant_box_version:
                self.Hopper.change_hopper_state("Off")
                # root.after_cancel(AFTER)
                if not self.cursor_visible:
                	self.change_cursor_state() # turn cursor back on, if applicable
            self.write_comp_data(True) # write data for end of session
            self.root.destroy() # destroy Canvas
            print("\n GUI window exited")
            
        self.clear_canvas()
        other_exit_funcs()
        print("\n You may now exit the terminal and operater windows now.")
        if operant_box_version:
            polygon_fill.main(self.subject_ID) # call paint object
        
    
    def write_data(self, event, outcome):
        # This function writes a new data line after EVERY peck. Data is
        # organized into a matrix (just a list/vector with two dimensions,
        # similar to a table). This matrix is appended to throughout the 
        # session, then written to a .csv once at the end of the session.
        if event != None: 
            x, y = event.x, event.y
        else: # There are certain data events that are not pecks.
            x, y = "NA", "NA"

        print(f"{outcome:>30} | x: {x: ^3} y: {y:^3} | {str(datetime.now() - self.start_time)} | {self.trial_type}")
        # print(f"{outcome:>30} | x: {x: ^3} y: {y:^3} | Target: {self.current_target_location: ^2} | {str(datetime.now() - self.start_time)}")
        self.session_data_frame.append([
            str(datetime.now() - self.start_time), # SessionTime as datetime object
            x, # X coordinate of a peck
            y, # Y coordinate of a peck
            outcome, # Type of event (e.g., background peck, target presentation, session end, etc.)
            self.left_key,
            self.right_key,
            self.trial_type, # Trial type (e.g., "training", "CBE.1", etc.)
            round((time() - self.trial_start - (self.ITI_duration/1000)), 5), # Time into this trial minus ITI (if session ends during ITI, will be negative)
            self.current_trial_counter, # Trial count within session (1 - max # trials)
            self.reinforcers_provided, # Reinforced trial counter
            self.ITI_duration, # ITI duration
            self.subject_ID, # Name of subject (same across datasheet)
            self.experimental_group, # Either Forced or Choice
            self.training_phase, # Phase of training as a number (0 - 7)
            date.today() # Today's date as "MM-DD-YYYY"
            ])
        
        
        header_list = ["SessionTime", "Xcord","Ycord", "LocationEvent",
                       "LeftKey", "RightKey", "TrialType",
                       "TrialTime", "TrialNum", "ReinforcersProvided",
                       "ITIDuration", "Subject", "Condition",
                       "TrainingPhase", "Date"] # Column headers


        
    def write_comp_data(self, SessionEnded):
        # The following function creates a .csv data document. It is either 
        # called after each trial during the ITI (SessionEnded ==False) or 
        # one the session finishes (SessionEnded). If the first time the 
        # function is called, it will produce a new .csv out of the
        # session_data_matrix variable, named after the subject, date, and
        # training phase. Consecutive iterations of the function will simply
        # write over the existing document.
        if SessionEnded:
            self.write_data(None, "SessionEnds") # Writes end of session to df
        if self.record_data : # If experimenter has choosen to automatically record data in seperate sheet:
            myFile_loc = f"{self.data_folder_directory}/{self.subject_ID}/{self.subject_ID}_{self.start_time.strftime('%Y-%m-%d_%H.%M.%S')}_P037_data-Phase{self.training_phase}.csv" # location of written .csv
            # This loop writes the data in the matrix to the .csv              
            edit_myFile = open(myFile_loc, 'w', newline='')
            with edit_myFile as myFile:
                w = writer(myFile, quoting=QUOTE_MINIMAL)
                w.writerows(self.session_data_frame) # Write all event/trial data 
            print(f"\n- Data file written to {myFile_loc}")
                
#%% Finally, this is the code that actually runs the program:
if __name__ == '__main__':
    cp = ExperimenterControlPanel()


    
