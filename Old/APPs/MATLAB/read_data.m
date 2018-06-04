count = Inf;
data_file = fopen (".\Data\data.raw", 'rb');
if (data_file < 0)
	v = 0;
else
	data = fread (data_file, [2, count], 'float');
	fclose (data_file);
	signal = data(1,:) + data(2,:)*i;
end

plot(abs(signal));
