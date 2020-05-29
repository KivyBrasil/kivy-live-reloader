# Standard imports
import time
import importlib
import sys
import os
import subprocess
import threading
from _thread import interrupt_main

# External imports
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class Watcher(FileSystemEventHandler):
    def __init__(self, path = ".", 
                 reload_mode = 1, interval = 1):

        # reload mode | options: [1,2] | default: 1
        self._reload_mode = reload_mode
        
        # Store check interval
        self._interval = interval
        
        # Store whether force exit
        self._force_exit = False
        
        # Set of watch paths
        self._watched_path = path
        
        # Whether the watcher thread should stop
        self._watcher_stop = False
    
    def start_watcher_thread(self):
        # Create watcher thread
        watcher_thread = threading.Thread(
            target = self.run_watcher)
        
        # Set whether the thread is daemon
        watcher_thread.setDaemon(True)
        
        # Start watcher thread
        watcher_thread.start()
        
        # Return watcher thread
        return watcher_thread

    def run_watcher(self):
        # Create observer
        observer = Observer()
        
        # Start observer
        observer.start()
        
        # Run change check in a loop
        while not self._watcher_stop:
            try:
                # 2KGRW
                # Schedule a watch
                # self: `FileSystemEventHandler` instance
                # self._watched_path: File path to watch
                # recursive: Whether recursive
                self.watch_obj = observer.schedule(
                    self, self._watched_path, recursive = True
                )
                # print(self.watch_obj)
            # If have error
            except Exception as e:
                print('erro aqui óh: \n {e}')

            # Sleep before next check
            time.sleep(self._interval)
        
        if self._watcher_stop:
            observer.unschedule(self.watch_obj)

    def dispatch(self, event):
        # Get file path
        file_path = event.src_path

        # Call `reload` to a changed module.
        self.reload()

        # If the file path ends with `.pyc` or `.pyo`
        if file_path.endswith(('.pyc', '.pyo')):
            # Get `.py` file path
            file_path = file_path[:-1]
            print("Python compiled/object file")

        # If the file path ends with `.py`
        if file_path.endswith('.py'):
            # Get the file's directory path
            file_dir = os.path.dirname(file_path)
            print("Python file")

    def reload(self):
         # If reload mode is `exec`
        if self._reload_mode == 1:
            # Call `reload_using_exec`
            self.reload_using_exec()

        # If reload mode is `spawn_exit`
        elif self._reload_mode == 2:
            # Call `reload_using_spawn_exit`
            self.reload_using_spawn_exit()
        # If reload mode is none of above
        else:
            # Get error message and raise error
            raise ValueError(
                f'Invalid reload mode: {self._reload_mode}.')

    def reload_using_exec(self):
        # Create command parts
        cmd_parts = [sys.executable] + sys.argv

        # Get env dict copy
        env_copy = os.environ.copy()

        # Reload the program process
        # sys.executable: Program file path
        # cmd_parts: Command parts
        # env_copy: Env dict
        os.execvpe(sys.executable, cmd_parts, env_copy)

    def reload_using_spawn_exit(self):
        # Create command parts
        cmd_parts = [sys.executable] + sys.argv

        # Get env dict copy
        env_copy = os.environ.copy()

        # Spawn subprocess
        subprocess.Popen(cmd_parts, 
                         env = env_copy, close_fds = True)

        # If need force exit
        if self._force_exit:
            # Force exit
            os._exit(0)  # pylint: disable=protected-access

        # If not need force exit
        else:
            # Send interrupt to main thread
            interrupt_main()

        # Set the flag
        self._watcher_stop = True

        # Exit the watcher thread
        sys.exit(0)
