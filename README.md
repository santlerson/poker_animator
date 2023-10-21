# Texas Hold 'Em Animator
Animates games produced by the [Texas Hold 'Em Simulator](https://github.com/santlerson/texas_hold_em_simulator.git).

## Usage
```
python3 renderer.py <json_log_file>
```
This renders the game into a series of frames in the `frames` directory as PNG files. The frames can then be converted into a video using [ffmpeg](https://www.ffmpeg.org/):
```
ffmpeg -framerate 24 -i 'frames/img-%016d.png' -vf scale=1920:1080:flags=neighbor -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p output.mp4
```
Note: the passed framerate should be the same as `TARGET_FRAMERATE` in `constants.py`.

## Example




https://github.com/santlerson/poker_animator/assets/56686478/301cbf79-c431-406d-87dc-8d04d964e3eb




## Credits
- Font: [Grand9K Pixel](https://www.dafont.com/grand9k-pixel.font) by [Jayvee D. Enaguas (Grand Chaos)](https://www.dafont.com/jayvee-d-enaguas.d2725)
