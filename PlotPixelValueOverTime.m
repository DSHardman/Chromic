runstring = "45_2.0"; % in format temp_force
nimages = 60;

% Show image so a pixel can be selected
I = imread("Data/ExperimentA/OutputImgs/"+runstring+"_4.png");
imshow(I);
g = ginput(1);
g = [round(g(1)) round(g(2))];
close();

% Read and plot RGB values of that pixel over post-press 60s period
pixelvals = zeros([nimages 3]);
for i = 1:nimages
    I = imread("Data/ExperimentA/OutputImgs/"+runstring+"_"+string(i-1)+".png");
    pixelvals(i, :) = I(g(2), g(1), :);
end

subplot(3,1,1);
plot(0:nimages-1, pixelvals(:, 1));
ylabel("Red");

subplot(3,1,2);
plot(0:nimages-1, pixelvals(:, 2));
ylabel("Green");

subplot(3,1,3);
plot(0:nimages-1, pixelvals(:, 3));
ylabel("Blue");
xlabel("Time (s)");

set(gcf, 'color', 'w');