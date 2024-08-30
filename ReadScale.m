% Read scale provided by manufacturer to create matrix
I = imread("Scale.png");
scale = reshape(I(26, :, :), [936 3]);
scale = double(scale);
save("Scale.mat", "scale");

