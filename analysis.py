
def get_app_times(data):
    """ 
    This is horrible; 
    I aim to make this func into a comprehension at some point.
    
    Gets list of tuples containing apps and the
    time spent on them, sorted by the latter 
    """
    app_times = {}
    for app, descs in data.items():
        seconds_on_app = 0
        for desc, time_entries in descs.items():
            for time_entry in time_entries:
                seconds_on_app += time_entry['seconds']
        app_times[app] = seconds_on_app
    return sorted(app_times.items(), key=lambda x:x[1], reverse=True)
        
