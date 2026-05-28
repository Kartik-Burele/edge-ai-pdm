function a = load_csv(filename)
isOctave = exist('OCTAVE_VERSION', 'builtin');
if isOctave > 0
  a = load_csv_octave(filename);
else
  a = load_csv_matlab(filename);
end
