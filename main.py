from win32gui import GetWindowText, GetForegroundWindow
from time import sleep
import pendulum
import pickle
import json
import analysis
        
class AppDict(dict):

    """
    Main app for the program

    When called, it runs in the background and records the time the user spends
    on any app on their computer.

    To exit the program, you should use keyboard interrupt
    This will automatially save the information to a pickle and json file

    The pickle file allows the data to be loaded back into memory next time
    While the json file is for your own data analysis.

    Sample:

    {
        'app_name1': 
        {
            'description1':[list of TimeEvents], 'description2': [lis...]}, 
        }
        'app_name2': 
        {
            'description1':[list of TimeEvents], 'description2': [lis...]}, 
        }
    }
    """

    ## File names
    pickle_file = "saved.pickle"
    json_file = "saved.json"

    def __init__(self):
        
        try:
            # Attempt to load existing info from pickle file
            with open(self.pickle_file, "rb") as pf:
                data = pickle.load(pf)
                self.update(data)
        except FileNotFoundError:
            pass

        # Debugging
        # print("self", self)

        # Set current app to None to start, to avoid errors
        self.current_app = None

    def __call__(self, sleep_for=2):
        
        if type(sleep_for) not in (int, float): 
            raise TypeError("sleep_for must be int or float")
        
        try:
            while True:
                # Program runs in the background until interrupted
                self.event()
                sleep(sleep_for)

                # Debugging
                # print(self) 

        except KeyboardInterrupt:

            # Finish the current event to record end_time
            self.event(closing=True)
            
            # Save data to pickle file
            with open(self.pickle_file, "wb") as pf:
                pickle.dump(self, pf)

            # Save data to json file
            with open(self.json_file, "w") as jf:
                json.dump(self, jf)

            # Show app times
            print(analysis.get_app_times(self))

    def event(self, closing=False):
        
        # Get the name of the active window
        active_win = GetWindowText(GetForegroundWindow())

        # If the app last in memory is not the same as the current one,
        # then this is a new app. 
        if self.current_app != active_win or closing:

            # If apps are different
            # Check to see if timer started for previous app
            # If it did, end the timer for it
            if self.current_app and self.current_app.start_time:
                self.current_app.end()
                
                # Create time event
                time_event = self.current_app.get_time_event()

                app, des = self.current_app.app, self.current_app.description

                # Ensure that current app and current app description exist in self{}
                if app not in self: self[app] = {}
                if des not in self[app]: self[app][des] = []

                # Add time event
                self[app][des].append(time_event._dict)

                if closing:
                    return

                # Debugging
                # print(self[app][des])

            # Else, this is the first app, or the timer was not started for the previous app
            # In either case, nothing needs to be done

            # Set the new current app
            self.current_app = ActiveApp(active_win)            

        # The app is the same as before
        elif self.current_app and not self.current_app.start_time:
            # The timer for the app was intentionally not started on previous iteration when it was new.
            # This is because it's silly to award 10 seconds to an app you're one for a fraction of a second
            # Now that one interval of time has passed, the timer should be started
            self.current_app.start()
            
class ActiveApp():
    """ 
    Contains information about the currently active window
    get_time_event() method employed by main AppDict class
    to save the time spend on the app.

    NOTE: of course, use the app a second time and this class
    will be called again. The data will not be overriden.
    """

    def __init__(self, active_win):

        self.active_win = active_win
        *d, self.app = active_win.split(' - ')
        self.description = ' '.join(d)
        
        self.start_time = None
        self.end_time = None

    def __eq__(self, value):
        return self.active_win == value

    def start(self):

        # Debugging
        # print("Starting timer for", self.active_win)
        
        self.start_time = pendulum.now()

    def end(self):

        # Debugging
        # print("Ending timer for", self.active_win)
        
        if not self.start_time:
            raise Exception("Must give start time first!")
        self.end_time = pendulum.now()

    def get_time_event(self):
        if not all([self.start_time, self.end_time]):
            raise Exception("Missing start or end time!")
        return TimeEvent(self.start_time, self.end_time)

class TimeEvent():
    """
    Given a start and an end time, allows for easy calculation of time difference

    In addition, _dict property allows for serialisation to pickle and json respectively
    by converting start and end times into strings.
    """
    def __init__(self, start, end):

        if not all(i.__class__.__name__ == "DateTime" for i in (start, end)):
            raise ValueError("TimeEvent passed non-datetime objects")
        
        self.start = start
        self.end = end

    @property
    def _dict(self):
        return {
            'start': self.start.to_datetime_string(),
            'end': self.end.to_datetime_string(),
            'seconds': self.seconds
        }

    @property
    def time_spent(self):
        return self.start.diff(self.end)

    @property
    def seconds(self):
        return self.time_spent.seconds

    @property
    def date():
        start_date = self.start.date()
        end_date = self.end.date()
        return start_date, end_date


if __name__ == "__main__":
    app_dict = AppDict()
    app_dict()
