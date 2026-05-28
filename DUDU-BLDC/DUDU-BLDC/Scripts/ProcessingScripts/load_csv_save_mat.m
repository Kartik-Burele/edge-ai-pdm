close all;
clear all;


% -----------------------------------------------------------------------------
%% Odczytanie listy plikow
data_folder = '../Analysis Data/';

%file_mask = "*-??_*_*_*.csv";     % Wszystkie dane
file_mask = '*.csv';     % Wszystkie dane

mat_filename = 'downsampling_1.mat';

% Wylistowanie wszystkich plikow
%list=dir("wszystkie/*-??_*_*_*.csv");

list = dir([data_folder file_mask]);

disp('Poczatek przetwarzanidata(x).');

data = [];

% -----------------------------------------------------------------------------
%% Wczytanie danych z plikow csv
disp('Data reading...');
for x=1:length(list)
    csv_filename = [data_folder list(x).name];
    str=['File: ',csv_filename];
    disp(str);
    d = load_csv(csv_filename);
    d.FileName = list(x).name;
    data = [data d];
end
disp('Data reading - END.');

down_scale = 10;

%% Downsampling
disp('Data downsapling...');
for x=1:length(data(:))
%     data(x).MEMS_X = decimate(data(x).MEMS_X, down_scale);
%     data(x).MEMS_Y = decimate(data(x).MEMS_Y, down_scale);
%     data(x).MEMS_Z = decimate(data(x).MEMS_Z, down_scale);
%     data(x).PIEZO_X = decimate(data(x).PIEZO_X, down_scale);
%     data(x).PIEZO_Y = decimate(data(x).PIEZO_Y, down_scale);
%     data(x).PIEZO_Z = decimate(data(x).PIEZO_Z, down_scale);
%    a.SampleNo = (C(first_row_no:end,1));
    data(x).SampleNo = downsample(data(x).SampleNo, down_scale);
    data(x).Time = downsample(data(x).Time, down_scale);
    data(x).ROTO = decimate(data(x).ROTO, down_scale);
    data(x).CURRENT = downsample(data(x).CURRENT, down_scale);
    data(x).Fs = data(x).Fs / down_scale;
end
disp('Data downsapling - END.');
%% Writing *.mat file
disp('Data writing...');

save([data_folder mat_filename],"data","-mat");

disp('Data writing - END.');
%% Writing csv file
dlm = ';';
disp('Data csv file writing...');
for x=1:length(data(:))
    A=[ ...
        (data(1).SampleNo)...
        (data(1).Time)...
        (data(1).ROTO)...
        (data(1).CURRENT)...
        ];
    T = array2table(A);
    T.Properties.VariableNames(1:4) = {'SampleNo','Time','ROTO','CURRENT'};
    new_file_name = [data_folder strrep(data(x).FileName,'.','_downsample_10x.')];
    writetable(T,new_file_name);
    
% % Przygotowanie nazw kolumn
% % Sample;Time (s);CURRENT (V);ROTO (V);
%     csv_names = ['Sample', dlm, ...
%                             'Time (s)', dlm ...
%                             'CURRENT (V)', dlm, ...
%                             'ROTO (V)', dlm, ...
%                             ];
% % Wlasciwy zapis do pliku
%     file = fopen('test.csv','w');
%     fprintf(file, csv_names);
%     fclose(file);

end
disp('Data csf file writing - END.');    