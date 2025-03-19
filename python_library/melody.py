import music21
from music21 import stream, midi, scale, converter, instrument
from datetime import datetime as dt
import numpy as np
import subprocess 
import os
import pathlib
import matplotlib.pyplot as plt

class Melody:
    
    def __init__(self):
        self.tracks = {}
        self.maps = {}
        self.dynamic = self.lorenz_system

        # Main Instance Attributes
        self.original_midi_data = None
        self.new_midi_data = None
        
        # Additional Instance Attributes
        self.newtracks = {}
        self.main_stream = None
        self.new_stream = None
        self.duration = {}
        self.new_duration = {}
        self.original_initial_condition = None
        self.new_initial_condition = None
        self.dynamic_sequence = 0
        self.notetrack = {}
        self.tracks_index = {}
        self.dynamic_parameter = {}

        # Support Instance Attributes
        self.method = None
        self.divisions = None
        self.backtrack_expand_index = []

        # self.original_time = None
        # self.new_time = None
        # self.original_trajectory = None
        # self.new_trajectory = None

        # Path
        self.lilypond_path = str(pathlib.Path("__file__").parent.resolve()) + "\\lilypond-2.24.4\\bin\\lilypond.exe"

        # etc.
        self.filename = None
        # self.dummy1 = None
        # self.dummy2 = None

    #########################
    # Main Method
    #########################
    
    def load(self, path):
        midi_file = midi.MidiFile()
        midi_file.open(path)
        midi_file.read()
        midi_file.close()

        self.original_midi_data = midi.translate.midiFileToStream(midi_file)
        self.new_midi_data = midi.translate.midiFileToStream(midi_file)

        self.main_stream = midi.translate.midiFileToStream(midi_file)
        self.new_stream = midi.translate.midiFileToStream(midi_file)
        self.filename = str(pathlib.Path(path).stem)

    def fit(self, original_initial_condition, method="classic", divisions=None):
        self.original_initial_condition = original_initial_condition
        self.method = method
        self.divisions = divisions

        if self.method == "classic":
            for index in range(len(self.main_stream)):
                instruments = self.main_stream[index][0].getElementsByClass(instrument.Instrument)
                if instruments:
                    instrument_name = str(instruments[0].instrumentName) + "_" + str(index)
                else:
                    instrument_name = "track_" + str(index)
                music_list = []
                duration_list = []
                for part in self.main_stream[index]:
                    for n in part.flat.notesAndRests:
                        dur = n.duration.quarterLength
                        if n.isRest:
                            note_num = "<REST>"
                            music_list.append(note_num)
                            duration_list.append(dur)
                        else:
                            if len(n.pitches) == 1:
                                note_num = n.pitches[0].midi
                                music_list.append(note_num)
                                duration_list.append(dur)
                            else: 
                                note_num = sorted(set([p.midi for p in n.pitches]))
                                music_list.append(list(note_num))
                                duration_list.append(dur)
                string_music_list = [element for element in music_list]
                for i in range(len(music_list)):
                    try:
                        string_music_list[i] = self.note_converter(music_list[i])
                    except TypeError:
                        for j in range(len(music_list[i])):
                            string_music_list[i][j] = self.note_converter(music_list[i][j])
                
                time, solution = self.rk4(time=[0, 0.01*(len(music_list) - 1)], f=self.dynamic, ini=self.original_initial_condition, **self.dynamic_parameter)
                main_sequence = solution[:, self.dynamic_sequence]
                
                print(solution[0:110:5, 0])
                print("-"*50)
                print("-"*50)
                print(solution[0:110:5, 1])
                print("-"*50)
                print("-"*50)
                print(solution[0:110:5, 2])
                print("*"*50)
                print("*"*50)
                #self.original_time = time
                # self.original_trajectory = main_sequence

                self.notetrack.update({instrument_name:string_music_list})
                self.duration.update({instrument_name:duration_list})
                self.tracks.update({instrument_name:main_sequence})
                self.tracks_index.update({instrument_name:index})
            for key in self.tracks.keys():
                dummy_list = []
                for i in range(len(self.notetrack[key])):
                    dummy_list.append([self.tracks[key][i], self.notetrack[key][i]])
                self.maps.update({key:dummy_list})
        elif self.method == "expand":
            for index in range(len(self.main_stream)):
                instruments = self.main_stream[index][0].getElementsByClass(instrument.Instrument)
                if instruments:
                    instrument_name = str(instruments[0].instrumentName) + "_" + str(index)
                else:
                    instrument_name = "track_" + str(index)
                duration_list = []
                for part in self.main_stream[index]:
                    for n in part.flat.notesAndRests:
                        dur = n.duration.quarterLength
                        if n.isRest:
                            duration_list.append(dur)
                        else:
                            if len(n.pitches) == 1:
                                duration_list.append(dur)
                            else:
                                duration_list.append(dur)
                self.duration.update({instrument_name:duration_list})
            for index in range(len(self.main_stream)):
                self.expand_note_durations(s=self.main_stream[index], divisions=self.divisions)
                instruments = self.main_stream[index][0].getElementsByClass(instrument.Instrument)
                if instruments:
                    instrument_name = str(instruments[0].instrumentName) + "_" + str(index)
                else:
                    instrument_name = "track_" + str(index)
                music_list = []
                #duration_list = []
                for part in self.main_stream[index]:
                    for n in part.flat.notesAndRests:
                        dur = n.duration.quarterLength
                        if n.isRest:
                            note_num = "<REST>"
                            music_list.append(note_num)
                            #duration_list.append(dur)
                        else:
                            if len(n.pitches) == 1:
                                note_num = n.pitches[0].midi
                                music_list.append(note_num)
                                #duration_list.append(dur)
                            else: 
                                note_num = sorted(set([p.midi for p in n.pitches]))
                                music_list.append(list(note_num))
                                #duration_list.append(dur)
                string_music_list = [element for element in music_list]
                for i in range(len(music_list)):
                    try:
                        string_music_list[i] = self.note_converter(music_list[i])
                    except TypeError:
                        for j in range(len(music_list[i])):
                            string_music_list[i][j] = self.note_converter(music_list[i][j])
                self.backtrack_expand_index = [index for index in range(0, len(music_list) - 1, self.divisions)]
                time, solution = self.rk4(time=[0, 0.01*(len(music_list) - 1)], f=self.dynamic, ini=self.original_initial_condition, **self.dynamic_parameter)
                main_sequence = solution[:, self.dynamic_sequence]
                #self.original_time = time
                # self.original_trajectory = main_sequence

                self.notetrack.update({instrument_name:string_music_list})
                self.tracks.update({instrument_name:main_sequence})
                self.tracks_index.update({instrument_name:index})
            for key in self.tracks.keys():
                dummy_list = []
                for i in range(len(self.notetrack[key])):
                    dummy_list.append([self.tracks[key][i], self.notetrack[key][i]])
                self.maps.update({key:dummy_list})
        else:
            raise Exception("Out of Option!")
        #return self.maps
        # return self.tracks.keys()
        #return print(self.tracks.keys())

    def variate(self, new_initial_condition, track=None, criteria="right", add_note=0):
        self.new_initial_condition = new_initial_condition
        if track == None:
            track = list(self.tracks.keys())
        if add_note != 0:
            for key in track:
                for each_note in range(add_note):
                    # Access parts from the stream
                    parts = self.new_stream.getElementsByClass('Part')
                    target_part = parts[self.tracks_index[key]]
            
                    # Determine the last measure in the part
                    if target_part.measure(-1):
                        last_measure = target_part.measure(-1)  # Get the last measure
                    else:
                        # If no measures exist, create the first one
                        last_measure = music21.stream.Measure()
                        target_part.append(last_measure)
            
                    # Create the new note
                    new_note = music21.note.Note('C4')
                    duration_len = len(self.duration[key])
                    new_note.quarterLength = self.duration[key][each_note % duration_len]
            
                    # Append the new note to the last measure
                    last_measure.append(new_note)
                #print(target_part[-1].show("text"))
                #print("-"*100)
        
        if self.method == "expand":
            for index in range(len(self.new_stream)):
                self.expand_note_durations(s=self.new_stream[index], divisions=self.divisions)
                instruments = self.new_stream[index][0].getElementsByClass(instrument.Instrument)
                if instruments:
                    instrument_name = str(instruments[0].instrumentName) + "_" + str(index)
                else:
                    instrument_name = "track_" + str(index)
                duration_list = []
                for part in self.new_stream[index]:
                    for n in part.flat.notesAndRests:
                        dur = n.duration.quarterLength
                        duration_list.append(dur)
                self.new_duration.update({instrument_name:duration_list})
            #self.duration = self.new_duration
        
        for key in track:
            sorted_tracks = sorted(self.maps[key], key=lambda x: x[0])
            if self.method == "classic":
                dummy_list = [None]*(len(self.tracks[key]) + add_note)
                time, solution = self.rk4(time=[0, 0.01*(len(dummy_list) - 1)], f=self.dynamic, ini=self.new_initial_condition, **self.dynamic_parameter)
                main_sequence = solution[:, self.dynamic_sequence]
                
                print(solution[0:110:5, 0])
                print("-"*50)
                print("-"*50)
                print(solution[0:110:5, 1])
                print("-"*50)
                print("-"*50)
                print(solution[0:110:5, 2])
                print("*"*50)
                print("*"*50)
            elif self.method == "expand":
                dummy_list = [None]*(len(self.tracks[key]) + add_note)*self.divisions
                time, solution = self.rk4(time=[0, 0.01*(len(dummy_list) - 1)], f=self.dynamic, ini=self.new_initial_condition, **self.dynamic_parameter)
                main_sequence = solution[:, self.dynamic_sequence]
                # self.new_time = time
                # self.new_trajectory = main_sequence
            else:
                raise Exception("Out of Option!")

            if criteria == "right":
                for i in range(len(main_sequence) if len(main_sequence) == len(dummy_list) else len(main_sequence) - 1):
                    for j in range(len(sorted_tracks)):
                        if main_sequence[i] <= sorted_tracks[j][0]:
                            dummy_list[i] = sorted_tracks[j][1]
                            break
                        elif main_sequence[i] > sorted_tracks[-1][0]:
                            dummy_list[i] = sorted_tracks[-1][1]
                            break
            elif criteria == "left":
                for i in range(len(main_sequence) if len(main_sequence) == len(dummy_list) else len(main_sequence) - 1):
                    for j in range(len(sorted_tracks)):
                        if main_sequence[i] <= sorted_tracks[j][0]:
                                dummy_list[i] = sorted_tracks[j - 1][1]
                                break
                        elif main_sequence[i] > sorted_tracks[-1][0]:
                            dummy_list[i] = sorted_tracks[-1][1]
                            break
                        elif (main_sequence[i] <= sorted_tracks[0][0]) and (j - 1 < 0):
                            main_sequence[i] = sorted_tracks[0][0]
                            break
            else:
                raise Exception("Out of Option!")

            self.newtracks.update({key:dummy_list})
        #return self.newtracks

    def export(self, format_type):
        exist_track = [track for track in self.newtracks.keys()]
        exist_new_stream = self.new_midi_data
        if self.method == "classic":
            for key in self.tracks.keys():
                if key in exist_track:
                    index = 0
                    for element in exist_new_stream[self.tracks_index[key]].recurse():
                        if isinstance(element, (music21.note.Note, music21.chord.Chord, music21.note.Rest)):
                            replacement = self.newtracks[key][index]
                            duration_value = self.duration[key][index]
                            if replacement == '<REST>':
                                new_element = music21.note.Rest()
                            elif isinstance(replacement, list):
                                new_element = music21.chord.Chord(replacement)
                            else:
                                new_element = music21.note.Note(replacement)
                            new_element.duration = music21.duration.Duration(duration_value)
                            element.activeSite.replace(element, new_element)
                            #print(f"{element} --> {replacement}")
                            if index < len(self.newtracks[key]) - 1:
                                index += 1
                            else:
                                break
        elif self.method == "expand":
            for key in self.tracks.keys():
                if key in exist_track:
                    index = 0
                    for element in exist_new_stream[self.tracks_index[key]].recurse():
                        if isinstance(element, (music21.note.Note, music21.chord.Chord, music21.note.Rest)):
                            replacement = self.newtracks[key][self.backtrack_expand_index[index]]
                            duration_value = self.duration[key][index]
                            if replacement == '<REST>':
                                new_element = music21.note.Rest()
                            elif isinstance(replacement, list):
                                new_element = music21.chord.Chord(replacement)
                            else:
                                new_element = music21.note.Note(replacement)
                            new_element.duration = music21.duration.Duration(duration_value)
                            element.activeSite.replace(element, new_element)
                            #print(f"{element} --> {replacement}")
                            if index < len(self.backtrack_expand_index) - 1:
                                index += 1
                            else:
                                break
                #print("-"*50)
        #print(self.new_stream.show("text"))
        current_path = pathlib.Path("__file__").parent.resolve()
        date = str(dt.now().isoformat())[:-7]
        filepath = str(current_path) + "\\" + "file_store" + "\\" + self.filename #+ date.replace(":", "-")
        isExist = os.path.exists(filepath)
        if not isExist:
            os.makedirs(filepath)
        original = self.original_midi_data
        new = self.new_midi_data
        if format_type == "midi":
            # original.metadata = music21.metadata.Metadata()
            original.write('midi', filepath + "\\" + self.filename + '_original.mid')
            # new.metadata = music21.metadata.Metadata()
            new.write('midi', filepath + "\\" + self.filename + '_new.mid')
        elif format_type == "pdf":
            us = music21.environment.UserSettings()
            us['lilypondPath'] = self.lilypond_path
            
            original.metadata = music21.metadata.Metadata()
            original.metadata.title = self.filename.replace("_", " ") #+ " Original"
            conv = music21.converter.subConverters.ConverterLilypond()
            original_filepath = filepath + "\\" + self.filename + '_original'
            conv.write(original, fmt='lilypond', fp=original_filepath, subformats = ['pdf'])
            
            new.metadata = music21.metadata.Metadata()
            new.metadata.title = "Our Variation" #self.filename.replace("_", " ") + " New"
            new_conv = music21.converter.subConverters.ConverterLilypond()
            new_filepath = filepath + "\\" + self.filename + '_new'
            conv.write(new, fmt='lilypond', fp=new_filepath, subformats = ['pdf'])

    #########################
    # Additional Method
    #########################

    def show_all_track(self):
        return self.tracks.keys()

    def set_dynamic(self, dynamic, *args, **kwargs):
        self.dynamic = dynamic
        self.dynamic_parameter.update(*args, **kwargs)

    def set_dynamic_sequence(self, sequence):
        self.dynamic_sequence = sequence - 1

    # def plot_trajectory(self):
    #     plt.figure(figsize=(12,6), dpi=240)
    #     plt.xlabel("time")
    #     plt.ylabel("trajectory value at time")
    #     plt.plot(self.original_time, self.original_trajectory, label="Original Trajectory")
    #     plt.plot(self.new_time, self.new_trajectory, label="New Trajectory")
    #     plt.grid()
    #     plt.legend()
    #     plt.show()

    
    #########################
    # Support Method
    #########################

    def lorenz_system(self, t, x, sigma=10, rho=28, beta=8/3):
        """
        Computes the derivatives of the Lorenz system at a given time t.
        Parameters:
        t (int or float): Time variable (not explicitly used in computation).
        x (array_like): State vector at time t, given as a list or NumPy array [x_1, x_2, x_3].
        sigma (float): Lorenz system parameter (must be greater than 0).
        rho (float): Lorenz system parameter (must be greater than 0).
        beta (float): Lorenz system parameter (must be greater than 0).
        
        Returns:
        numpy.ndarray: The time derivatives [dx/dt, dy/dt, dz/dt] as a NumPy array.
        """
        x_1, x_2, x_3 = x
        xdot = sigma * (x_2 - x_1)
        ydot = x_1 * (rho - x_3) - x_2
        zdot = x_1 * x_2 - beta * x_3
        return np.array([xdot, ydot, zdot])
    
    def rk4(self, time, ini, f, h=0.01, *args, **kwargs):
        t = np.arange(time[0], time[1]+h, h)
        row = len(t)
        try:
            var = len(ini)
        except TypeError:
            var = 1
        x = np.zeros((row, var))
        x[0, :] = ini
        for j in range(0, len(t)-1):
            k1 = f(t[j], x[j], *args, **kwargs)
            k2 = f(t[j] + 0.5*h, x[j] +0.5*h*k1, *args, **kwargs)
            k3 = f(t[j] + 0.5*h, x[j] + 0.5*h*k2, *args, **kwargs)
            k4 = f(t[j] + h, x[j] + h*k3, *args, **kwargs)
            x[j+1, :] = x[j] + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
        return t, x

    def is_chaotic(self):
        T = [0, 100]
        
        # Initial state and parameters
        initial_state = np.array([1.0, 1.0, 1.0])
    
        # Integrate system
        #sol = solve_ivp(lorenz, t_span, initial_state, t_eval=t_eval, rtol=1e-9, atol=1e-9)
        time, sol = self.rk4(time=T, ini=initial_state, f=self.dynamic, **self.dynamic_parameter)
        
        # Perturb the initial state slightly
        perturbed_state = np.array([1.00001, 1.0, 1.0])
        
        #perturbed_sol = solve_ivp(lorenz, t_span, perturbed_state, t_eval=t_eval, rtol=1e-9, atol=1e-9)
        time, perturbed_sol = self.rk4(time=T, ini=perturbed_state, f=self.dynamic, **self.dynamic_parameter)
        
        # Compute divergence between trajectories
        divergence = np.linalg.norm(sol - perturbed_sol, axis=1)
        
        # Estimate Lyapunov exponent
        divergence_rate = np.log(divergence + 1e-10)  # Avoid log(0)
        lyapunov_exponent = np.mean(divergence_rate[time > 10])  # Ignore transient phase
        
        # Chaos detected if Lyapunov exponent is positive
        return lyapunov_exponent > 0

    def note_converter(self, midi_note):
        """
        This function convert single midi note value to readable musical note.
        Important parameter:
        midi_note: midi note value;
                   60 ----> C4
        """
        if midi_note == '<REST>':
            return '<REST>'
        else:
            if 0 <= midi_note <= 127:
                pitches = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
                octave = (midi_note // 12) - 1
                pitch_index = midi_note % 12
    
                pitch = pitches[pitch_index]
                return f"{pitch}{octave}"
            else:
                return "Invalid MIDI note value. Must be between 0 and 127."
    
    def expand_note_durations(self, s, divisions):
        for measure in s.getElementsByClass(stream.Measure):
            for element in measure:
                if isinstance(element, music21.note.Note):
                    duration = element.duration.quarterLength
                    expanded_duration = (1 / divisions) * duration
                    offset = element.offset
                    measure.remove(element)
                    for i in range(divisions):
                        new_note = music21.note.Note(element.pitch)
                        new_note.duration.quarterLength = expanded_duration
                        measure.insert(offset + i * expanded_duration, new_note)
                elif isinstance(element, music21.chord.Chord):
                    duration = element.duration.quarterLength
                    expanded_duration = (1 / divisions) * duration
                    offset = element.offset
                    measure.remove(element)
                    for i in range(divisions):
                        new_chord = music21.chord.Chord(element.pitches)
                        for note_in_chord in new_chord:
                            note_in_chord.duration.quarterLength = expanded_duration
                        measure.insert(offset + i * expanded_duration, new_chord)
                elif isinstance(element, music21.note.Rest):
                    duration = element.duration.quarterLength
                    expanded_duration = (1 / divisions) * duration
                    offset = element.offset
                    measure.remove(element)
                    for i in range(divisions):
                        new_rest = music21.note.Rest()
                        new_rest.duration.quarterLength = expanded_duration
                        measure.insert(offset + i * expanded_duration, new_rest)