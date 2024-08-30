runstring = '35_2.0'; % in format temp_force
nimages = 60;

% Show image so a pixel can be selected
I = imread("Data/ExperimentB/OutputImgs/"+runstring+"_4.png");
imshow(I);
title("Select pixel to track");
g = ginput(1);
g = [round(g(1)) round(g(2))];
close();

% Read and plot RGB values of that pixel over post-press 60s period
pixelvals = zeros([nimages 3]);
for i = 1:nimages
    I = imread("Data/ExperimentB/OutputImgs/"+runstring+"_"+string(i-1)+".png");
    pixelvals(i, :) = I(g(2), g(1), :);
end

subplot(2,1,1);
plot(0:nimages-1, pixelvals(:, 1), "LineWidth", 2, "Color", "r");
hold on
plot(0:nimages-1, pixelvals(:, 2), "LineWidth", 2, "Color", "g");
plot(0:nimages-1, pixelvals(:, 3), "LineWidth", 2, "Color", "b");
box off
set(gca, "LineWidth", 2, "FontSize", 15);
ylabel("Raw Pixel Values");
ylim([0 255]);
xlim([4 60]);

subplot(2,1,2);
interpolatedvals = zeros([nimages, 1]);
for i = 1:nimages
    interpolatedvals(i) = scalelocation(pixelvals(i, :));
end

plot(0:nimages-1, interpolatedvals, "LineWidth", 2, "Color", "k");
box off
set(gca, "LineWidth", 2, "FontSize", 15);
xlabel("Time (s)");
xlim([4 60]);
ylim([0 1]);
ylabel("Interpolated Position");

sgtitle("T = " + runstring(1:2) + "C, F = " + runstring(4:6) + "N, @[" + string(g(1)) + ", " + string(g(2)) + "]");

set(gcf, 'color', 'w');