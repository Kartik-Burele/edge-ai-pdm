function a = load_csv_matlab(filename)


headerlines_no = 7;
first_row_no = 1;

% Wczytanie danych
C = dlmread(filename,';',headerlines_no,0);

%Sample;Time (s);CURRENT (V);ROTO (V);AI2 (V);AI3 (V);AI4 (V);AI5 (V);AI6 (V);AI7 (V)


a.SampleNo = (C(first_row_no:end,1));
a.Time = (C(first_row_no:end,2));
a.CURRENT =(C(first_row_no:end,3));
a.ROTO =(C(first_row_no:end,4));
% a.MEMS_X = (C(first_row_no:end,3));
% a.MEMS_Y = (C(first_row_no:end,4));
% a.MEMS_Z = (C(first_row_no:end,5));
% a.PIEZO_X = (C(first_row_no:end,6));
% a.PIEZO_Y = (C(first_row_no:end,7));
% a.PIEZO_Z = (C(first_row_no:end,8));

%a.FileName = filename;
a.Fs = 1/(a.Time(2) - a.Time(1));
