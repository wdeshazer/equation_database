"""
Time keeping utilities for logging events in programs
"""
from datetime import datetime
from time import sleep
from dataclasses import dataclass
from typing import List


@dataclass
class LoggedTime:
    """Singleton Logged Event"""
    event_message: str = None
    event_time: datetime = None
    start_time: datetime = None
    delta_time = None
    fmt: str = '%Y-%m-%d %H%M:%S.%f'
    msg = None

    def __post_init__(self):
        self.event_time = datetime.now()

        msg = self.event_time.strftime(self.fmt) + ': ' + self.event_message

        if self.start_time is not None:
            self.delta_time = self.event_time - self.start_time
            msg += ' (Duration: ' + str(self.delta_time) + ')'

        self.msg = msg

    def message(self):
        """Print Message"""
        print(self.msg)


@dataclass
class TimeLogger:
    """Used to Log Times In the system"""
    start_time: LoggedTime = LoggedTime(event_message='Start Time')
    new_event_time: LoggedTime = None
    last_event_time: LoggedTime = None
    logged_times: List[LoggedTime] = None

    def __post_init__(self):
        self.last_event_time = self.start_time
        self.new_event_time = self.start_time
        self.logged_times = [self.start_time]
        self.start_time.message()

    def new_event(self, message: str):
        """The method to log events"""
        self.last_event_time = self.new_event_time
        self.new_event_time = LoggedTime(event_message=message, start_time=self.last_event_time.event_time)
        self.logged_times.append(self.new_event_time)
        self.new_event_time.message()

    def history(self):
        """Shows history of all logged events"""
        for event in self.logged_times:
            event.message()

    def delta_time(self):
        """Time between last event and current"""
        delta = self.new_event_time.event_time - self.last_event_time.event_time
        return delta

    def total_time(self):
        """Total Time recorded in Time Logger"""
        delta = self.logged_times[-1].event_time - self.logged_times[0].event_time
        return delta


def main():
    """Example Use of TimeLogger"""
    time_log = TimeLogger()
    sleep(1.445)
    time_log.new_event('First New Event')
    sleep(0.275)
    time_log.new_event('Second New Event')
    time_log.history()


if __name__ == '__main__':
    main()
