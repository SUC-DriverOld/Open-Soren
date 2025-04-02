<div align="center">

# Open Soren

</div>

Code comes from [Rast Sound Soren](https://rastsound.com/downloads/soren/) v1.1.0

Features:

- Automatic audio master
- Support custom mastering profiles
- Smaller software size

## Usage

Download the one-click starter from [releases](https://github.com/SUC-DriverOld/Open-Soren/releases), unzip and run `go-webui.bat`. Or following the steps below:

- Install python 3.12 and requirements.

```bash
conda create -n opensoren python=3.12.7 -y
conda activate opensoren
pip install -r requirements.txt
```

- Then, run `python webui.py` to start the web interface.

## Command Line Usage

- Run `python mastering.py -h` to see the usage of auto-mastering.

```bash
usage: mastering.py [-h] [-o OUTPUT_FOLDER] [-f {wav,flac,mp3}] [-r REFERENCE] [-g GENRE] [-l {soft,dynamic,normal,loud}] [-eq {Neutral,Warm,Bright,Fusion}] [-p] input_file

Audio Mastering Tool

positional arguments:
  input_file            Path to the input audio file

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                        Folder to save the output audio file, if not specified, the output will be saved in the same folder as the input file
  -f {wav,flac,mp3}, --format {wav,flac,mp3}
                        Output audio format
  -r REFERENCE, --reference REFERENCE
                        Path to a custom reference audio file
  -g GENRE, --genre GENRE
                        Genre profile to use for mastering (not including the extension), json file must be present in the genres folder. For example, 'Ambient'
  -l {soft,dynamic,normal,loud}, --loudness {soft,dynamic,normal,loud}
                        Loudness option
  -eq {Neutral,Warm,Bright,Fusion}, --eq-profile {Neutral,Warm,Bright,Fusion}
                        EQ profile to use for mastering
  -p, --preview         Process only the preview, 30 seconds of the audio file
```

- Run `python generate_profile.py -h` to see how to create a custom mastering profile.

```shell
usage: generate_profile.py [-h] [-n NAME] audio_file

Generate custom profiles for audio mastering

positional arguments:
  audio_file            Path to the audio file to extract features from

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name of the genre profile to create
```