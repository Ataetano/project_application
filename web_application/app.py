import streamlit as st
import os
from melody_api import Melody
from dynamic_system.dynamic_system import *
import streamlit.components.v1 as components


def main():
    def expanded_index_function(n):
        if n == 2:
            index = 0
        elif n == 4:
            index = 1
        elif n == 8:
            index = 2
        elif n == 16:
            index = 3
        return index

    if 'x' not in st.session_state:
        st.session_state['x'] = 1.01
    if 'y' not in st.session_state:
        st.session_state['y'] = 1.01
    if 'z' not in st.session_state:
        st.session_state['z'] = 1.01
    if 'sigma' not in st.session_state:
        st.session_state['sigma'] = 10.0
    if 'rho' not in st.session_state:
        st.session_state['rho'] = 28.0
    if 'beta' not in st.session_state:
        st.session_state['beta'] = 2.67
    if 'method' not in st.session_state:
        st.session_state['method'] = "Classic"
    if 'option' not in st.session_state:
        st.session_state['option'] = 2
    if 'sequence_select' not in st.session_state:
        st.session_state['sequence_select'] = 0
    if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = None
    if 'save_path' not in st.session_state:
        st.session_state['save_path'] = None
    if 'method_index' not in st.session_state:
        st.session_state['method_index'] = 0
    if 'expanded_index' not in st.session_state:
        st.session_state['expanded_index'] = 0
    if 'html_component' not in st.session_state:
        st.session_state['html_component'] = None
    if 'original_path' not in st.session_state:
        st.session_state['original_path'] = None
    if 'new_path' not in st.session_state:
        st.session_state['new_path'] = None
    if 'midi_new_download_path' not in st.session_state:
        st.session_state['midi_new_download_path'] = None
    if 'pdf_original_path' not in st.session_state:
        st.session_state['pdf_original_path'] = None
    if 'pdf_new_path' not in st.session_state:
        st.session_state['pdf_new_path'] = None
    if 'generate_clicked' not in st.session_state:
        st.session_state['generate_clicked'] = False
    if 'complete_download' not in st.session_state:
        st.session_state['complete_download'] = False
    if 'original_pdf_bytes' not in st.session_state:
        st.session_state['original_pdf_bytes'] = None
    if 'new_midi_bytes' not in st.session_state:
        st.session_state['new_midi_bytes'] = None
    if 'new_pdf_bytes' not in st.session_state:
        st.session_state['new_pdf_bytes'] = None
    if 'track_list' not in st.session_state:
        st.session_state['track_list'] = None
    if 'backup_track_list' not in st.session_state:
        st.session_state['backup_track_list'] = None
    if 'under_process' not in st.session_state:
        st.session_state['under_process'] = None
    if 'file_exist' not in st.session_state:
        st.session_state['file_exist'] = 0

    st.set_page_config(layout="wide")

    # Initialize Melody object
    my_melody = Melody()

    # Page layout
    left_col, right_col = st.columns([1, 3])

    # MIDI file count variable
    file_count = 0

    # Left Column: Generate Music Button and File Upload
    with left_col:

        st.markdown(
            '<h1 style="font-size:30px;">Variate Music</h1>', 
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader("Upload a MIDI file", type=["mid", "midi"])

        css = '''
        <style>
            [data-testid='stFileUploader'] {
                width: max-content;
            }
            [data-testid='stFileUploader'] section {
                padding: 0;
                float: left;
            }
            [data-testid='stFileUploader'] section > input + div {
                display: none;
            }
            [data-testid='stFileUploader'] section + div {
                display: none;
            }
        </style>
        '''

        st.markdown(css, unsafe_allow_html=True)

        # Only update session state if a new file is uploaded

        if uploaded_file is not None:
            if st.session_state['file_exist'] == 1:
                print(f"now_file = {uploaded_file.name}")
                print(f"exist_file = {st.session_state['uploaded_file'].name}")
                if (uploaded_file.name != st.session_state['uploaded_file'].name):
                    st.session_state['track_list'] = None
                    st.session_state['backup_track_list'] = None
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['file_exist'] = 1

        if 'uploaded_file' in st.session_state and st.session_state['uploaded_file'] is not None:
            st.write("Uploaded file:", st.session_state['uploaded_file'].name)

            save_directory = os.path.join("static", "midi_file")
            os.makedirs(save_directory, exist_ok=True)

            if ' ' in str(st.session_state['uploaded_file'].name):
                st.warning('Warning: We can\'t save your MIDI file because your MIDI file name has spacing. Please fill the spacing with "_".', icon="⚠️")
            else:
                save_path = os.path.join(save_directory, st.session_state['uploaded_file'].name)

                # Reset file pointer to the beginning
                st.session_state['uploaded_file'].seek(0)

                # Save the uploaded file locally
                with open(save_path, "wb") as f:
                    f.write(st.session_state['uploaded_file'].read())
                st.success("File saved successfully!")

                # Reset file pointer again to read for MIDI processing
                st.session_state['uploaded_file'].seek(0)

                try:
                    # Load MIDI data
                    # midi_data = mido.MidiFile(file=BytesIO(st.session_state['uploaded_file'].read()))
                    # st.title("MIDI File Information")
                    # st.write(f"Number of Tracks: {len(midi_data.tracks)}")

                    # Load into your Melody object
                    st.session_state['save_path'] = save_path
                    my_melody.load(path=st.session_state['save_path'])
                except Exception as e:
                    st.error(f"Failed to read MIDI file: {e}")
        generate_botton = st.button('Variate')

    # Right Column: Tabs for Results and Settings
    with right_col:
        tabs = st.tabs(["Results", "Settings"])

        # Results Tab
        with tabs[0]:
            if generate_botton:
                st.session_state['generate_clicked'] = True

            if st.session_state['generate_clicked'] == False:
                st.image("intro.jpg")
                st.write("Start creating your variation by simply uploading a MIDI file and clicking \"Variate Music!\"")

            if 'uploaded_file' in st.session_state and st.session_state['uploaded_file'] is not None:
                if generate_botton == True:
                    #st.snow()
                    st.session_state['complete_download'] = False

                    #st.write("Waiting for our algorithm to generate a new variation!")
                    my_melody.set_dynamic_sequence(sequence=st.session_state['sequence_select'])
                    key_list = my_melody.fit(original_initial_condition=[st.session_state['x'], st.session_state['y'], st.session_state['z']],
                        method=st.session_state['method'], divisions=st.session_state['option'],
                        dynamic=le, d=st.session_state['sigma'], r=st.session_state['rho'], b=st.session_state['beta'])
                    if st.session_state['track_list'] == None:
                        st.session_state['track_list'] = [key for key in key_list]
                        st.session_state['backup_track_list'] = [key for key in key_list]
                    my_melody.variate(new_initial_condition=[1.5, 1.5, 1.5], track=st.session_state['track_list'])

                    original_path, new_path, midi_new_download_path = my_melody.export("midi")

                    st.session_state['original_path'] = original_path
                    st.session_state['new_path'] = new_path

                    st.session_state['midi_new_download_path'] = midi_new_download_path
                    with open(st.session_state['midi_new_download_path'], "rb") as file:
                        st.session_state['new_midi_bytes'] = file.read()

                    pdf_original_path, pdf_new_path = my_melody.export("pdf")

                    st.session_state['pdf_original_path'] = pdf_original_path
                    with open(st.session_state['pdf_original_path'], "rb") as file:
                        st.session_state['original_pdf_bytes'] = file.read()

                    st.session_state['pdf_new_path'] = pdf_new_path
                    with open(st.session_state['pdf_new_path'], "rb") as file:
                        st.session_state['new_pdf_bytes'] = file.read()

                    st.session_state['html_component'] = True

            # MIDI Player and Visualizer
            if 'html_component' in st.session_state and st.session_state['html_component'] is not None:
                components.html(
                f"""
                <h1 style="font-size:30px;">Original Music</h1>
                <center>
                <midi-player
                  src="{st.session_state['original_path']}"
                  sound-font visualizer="#myStaffVisualizer1">
                </midi-player>

                <midi-visualizer type="staff" id="myStaffVisualizer1" 
                  src="{st.session_state['original_path']}">
                </midi-visualizer>
                </center>
                <script src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.23.1/es6/core.js,npm/focus-visible@5,npm/html-midi-player@1.5.0"></script>
                """,
                height=300)

                original_col1, original_col2, original_col3, original_col4, original_col5 = st.columns([1,1,2,1,1])
                with original_col3:
                    st.download_button(
                        label="Download Original Music Sheet",
                        data=st.session_state['original_pdf_bytes'],
                        file_name=str(st.session_state['uploaded_file'].name) + "_original.pdf",
                        mime="application/pdf"
                        )

                components.html(
                f"""
                <h1 style="font-size:30px;">New Variation Music</h1>
                <center>
                <midi-player
                  src="{st.session_state['new_path']}"
                  sound-font visualizer="#myStaffVisualizer2">
                </midi-player>

                <midi-visualizer type="staff" id="myStaffVisualizer2" 
                  src="{st.session_state['new_path']}">
                </midi-visualizer>
                </center>
                <script src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.23.1/es6/core.js,npm/focus-visible@5,npm/html-midi-player@1.5.0"></script>
                """,
                height=300
                )

                new_col1, new_col2 = st.columns(2)
                with new_col1:
                    st.download_button(
                        label="Download MIDI File",
                        data=st.session_state['new_midi_bytes'],
                        file_name=str(st.session_state['uploaded_file'].name) + "_new.mid",
                        mime="audio/midi"
                    )
                with new_col2:
                    st.download_button(
                        label="Download New Music Sheet",
                        data=st.session_state['new_pdf_bytes'],
                        file_name=str(st.session_state['uploaded_file'].name) + "_new.pdf",
                        mime="application/pdf"
                    )
                st.session_state['complete_download'] = True
                st.write("Complete!")
                    

        # Settings Tab
        with tabs[1]:
            st.title("Settings")
        
            equation = st.selectbox(
                "Choose Chaotic Systems",
                ("Lorenz system", "Chaotic system"),
                index=0,
                placeholder="Choose Equation"
            )

            # Actions for Lorenz system
            if equation == "Lorenz system":
                # Variable selection 
                variable_Lorenz = st.selectbox(
                    "Select variable to display",
                    options=("x", "y", "z"),
                    index=0
                )

                # Create a two-column layout
                col1, col2 = st.columns(2)

                with col1:
                    # Display Variables
                    st.markdown("### Variables")
                    
                    # Sliders for variables
                    st.session_state['x'] = st.slider(
                        "x",
                        min_value=-5.0,
                        max_value=5.0,
                        value=1.01,
                        step=0.01
                    )
                    st.session_state['y'] = st.slider(
                        "y",
                        min_value=-5.0,
                        max_value=5.0,
                        value=1.01,
                        step=0.01
                    )
                    st.session_state['z'] = st.slider(
                        "z",
                        min_value=-5.0,
                        max_value=5.0,
                        value=1.01,
                        step=0.01
                    )
                    
                    # Set the variable based on selection
                    if variable_Lorenz == "x":
                        st.session_state['sequence_select'] = 0
                    elif variable_Lorenz == "y":
                        st.session_state['sequence_select'] = 1
                    elif variable_Lorenz == "z":
                        st.session_state['sequence_select'] = 2

                with col2:
                    # Display Parameters
                    st.markdown("### Parameters")
                    
                    # Sliders for parameters
                    st.session_state['sigma'] = st.slider(
                        r"$\sigma$",
                        min_value=0.0,
                        max_value=100.0,
                        value=10.0,
                        step=0.01
                    )
                    st.session_state['rho'] = st.slider(
                        r"$\rho$",
                        min_value=0.0,
                        max_value=100.0,
                        value=28.0,
                        step=0.01
                    )
                    st.session_state['beta'] = st.slider(
                        r"$\beta$",
                        min_value=0.0,
                        max_value=100.0,
                        value=2.67,
                        step=0.01
                    )

                # Check Chaotic Parameters
                if st.button('Check Parameters'):
                    my_melody.load(path=st.session_state['save_path'])
                    my_melody.set_dynamic_sequence(sequence=st.session_state['sequence_select'])
                    my_melody.fit(initial_condition=[st.session_state['x'],st.session_state['y'],st.session_state['z']], dynamic=le, d=st.session_state['sigma'], r=st.session_state['rho'], b=st.session_state['beta'])
                    checker = my_melody.is_chaotic()
                    if str(checker) == 'True':
                        st.write(f"Chaotic parameter")
                    else:
                        st.warning('Parameter not chaotic')

            elif equation == "Chaotic system":
                st.write("Soon...")
            if (st.session_state['complete_download'] == True) and (st.session_state['backup_track_list'] != None):
                options = st.multiselect(
                    "Select MIDI Tracks",
                    list(st.session_state['backup_track_list']),
                    default = list(st.session_state['backup_track_list'])
                )
                st.write(list(options))
                #print(list(options))
                st.session_state['track_list'] = list(options)

            # Additional Options
            st.session_state['method'] = st.selectbox(
                "Additional Options",
                ("Classic", "Expanded"),
                index=st.session_state['method_index'],
                placeholder="Choose Equation",
            )

            if st.session_state['method'] == "Classic":
                st.session_state['method_index'] = 0
                st.session_state['option'] = None

            elif st.session_state['method'] == "Expanded":
                st.session_state['method_index'] = 1
                st.session_state['option'] = st.selectbox(
                    "Expanded Number (Example: If you choose 4, our algorithm will expand 1 note into 4 notes in your MIDI file)",
                    (2, 4, 8, 16),
                    index=st.session_state['expanded_index'],
                )
                st.session_state['expanded_index'] = expanded_index_function(st.session_state['option']) 

if __name__ == "__main__":
    main()