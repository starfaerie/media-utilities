"""
This script extracts a specific frame from a video file and saves it as an image.

The frame is chosen based on a provided frame number or a default value of 1.

The script uses ffprobe to get the video's frame rate and ffmpeg to extract the frame.

Example Usage:
python extract_single_frame_from_video.py -i C:/path/to/file.mov -o D:/path/to/output/file.jpg -f 240

This will extract the 240th frame from the video file at `C:/path/to/file.mov` 
and save it as a .jpg at the specified output path `D:/path/to/output/file.jpg`.

If the output path is not provided, the script will create a .jpg file in the same directory as the input video file.
The name of the output .jpg will be the name of the input file with _extractedFrame.jpg appended to it;
e.g. if `-i C:/path/to/example_file.mov` is the input and no output path is specified,
the output will be a .jpg file created at `C:/path/to/example_file_extractedFrame.jpg`.
"""

import argparse
import subprocess
import json
import os

def get_ffprobe_result(file_path:str) -> dict:
    """
    This function uses ffprobe to get information about the video file in json format.

    Args:
    file_path (str): The path of the video file.

    Returns:
    dict: The json output from ffprobe as a Python dictionary.
    """
    ffprobe_cmd:list[str] = ['ffprobe', '-i', file_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams']
    ffprobe_output:str = subprocess.check_output(ffprobe_cmd).decode('utf-8')
    return json.loads(ffprobe_output)

def extract_single_frame_from_video(video_path: str, frame: int = 1, output_path: str = "", overwrite_existing_files: bool = True) -> None:
    """
    This function calculates the time for the specified frame, extracts it from the video,
    and saves it as an image at the specified output path.

    Args:
    video_path (str): The path of the video file.
    frame (int, optional): The frame to extract. Defaults to 1.
    output_path (str, optional): The full path to save the output image. Defaults to None.
    overwrite_existing_files (bool, optional): Whether to overwrite existing files at the output path. Defaults to True.
    """
    
    if output_path is "":
        video_file: str = os.path.basename(video_path)
        output_name: str = video_file.split('.')[0] + '_extractedFrame.jpg'
        output_path = os.path.join(os.path.dirname(video_path), output_name)

    if not output_path.endswith('.jpg'):
        raise ValueError("The output path must end with a .jpg extension")
    
    # Check if the output file already exists to save on compute time and give helpful feedback to users
    if os.path.exists(output_path):
        if overwrite_existing_files:
            print(f"A file named {output_path} already exists and will be overwritten.")
        else:
            print(f"A file named {output_path} already exists and will not be overwritten. Please provide a different output path or enable overwriting.")
            return

    video_probe_result:dict = get_ffprobe_result(video_path)
    video_frame_rate = [s for s in video_probe_result['streams'] if s['codec_type'] == 'video'][0]['r_frame_rate']
    frame_rate:float = float(video_frame_rate.split('/')[0]) / float(video_frame_rate.split('/')[1])

    time_of_frame:float = frame / frame_rate
    hours, rem = divmod(time_of_frame, 3600)
    minutes, seconds = divmod(rem, 60)
    time_to_seek:str = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

    ffmpeg_cmd: list = ['ffmpeg', '-i', video_path, '-ss', time_to_seek, '-frames:v', '1', '-pix_fmt', 'yuvj420p', output_path]
    
    if overwrite_existing_files:
        ffmpeg_cmd.insert(1, '-y')  # Add the overwrite flag
    subprocess.run(ffmpeg_cmd)

def main(args=None) -> None:
    """
    This is the main function that parses the command-line arguments and calls the 
    get_neutral_frame_image function.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Input video file path')
    parser.add_argument('-o', '--output', default='', help='Output file path (output path is based on input file path if not provided)')
    parser.add_argument('-f', '--frame', type=int, default=1, help='Frame to extract from video')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files at the output path')
    parser.add_argument('--dev', '--debug', '--doctest', action="store_true", dest='doctest')
    args = parser.parse_args()

    if args.doctest:
        import doctest
        doctest.testmod()

    if args.output and not args.output.endswith('.jpg'):
        raise ValueError("The output path must end with a .jpg extension")
    
    # Notify user if file already exists and about their overwrite selection
    if args.output and os.path.exists(args.output):
        if args.overwrite:
            print(f"A file named {args.output} already exists and will be overwritten.")
        else:
            print(f"A file named {args.output} already exists and will not be overwritten. Please provide a different output path or use the '--overwrite' flag.")
            return

    extract_single_frame_from_video(args.input, args.frame, args.output)

if __name__ == "__main__":
    main()
