%% Initialise
exp = "ExperimentB";

% Show image so a pixel can be selected
I = imread("Data/"+exp+"/OutputImgs/35_2.0_5.png");
imshow(I);
g = ginput(1);
g = [round(g(1)) round(g(2))];
close();

%% Plot over time
figure();
for i = 1:10
    subplot(1,10, i);
    pixelcolors = createheatmap(exp, g, 6*i-1);
    title("t = " + string(6*i -1) + "s");
end
set(gcf, 'color', 'w', 'position', [24 458 1454 300]);

%% Animate over time
figure();
for i = 4:60
    pixelcolors = createheatmap(exp, g, i-1);
    title(string(i-1));
    drawnow();
    set(gcf, 'color', 'w', 'position', [515   226   290   580]);
    pause(0.01);
    clf  
end


return % To stop accidentally overwriting the video below

%% Animate three locations
figure();
% Show image so three pixels can be selected
I = imread("Data/"+exp+"/OutputImgs/35_2.0_5.png");
imshow(I);
title("Select 3 pixels to monitor");
g = ginput(3);
g = round(g);
close();

clear v
v = VideoWriter('Animations/ThreeLocations');
v.FrameRate = 3;
v.Quality = 100;
open(v);

titles = ["A" "B" "C"];
for i = 4:60
    for j = 1:3
        subplot(1,3,j)
        pixelcolors = createheatmap(exp, g(j, :), i-1);
        title(titles(j));
    end
    sgtitle("t = " + string(i-1) + "s");
    drawnow();
    set(gcf, 'color', 'w', 'position', [137 304 1208 478]);
    v.writeVideo(getframe(gcf));
    % pause(0.1);
    clf
end
close(v);


%% Function
function pixelcolors = createheatmap(exp, g, frame)
    temps = 30:45;
    forces = ["0.5" "1.0" "1.5" "2.0"];

    pixelcolors = zeros([length(temps), length(forces), 3]);

    for i = 1:length(temps)
        for j = 1:length(forces)
            runstring = string(temps(i)) + "_" + forces(j);
            % Read and plot RGB values of that pixel over post-press 60s period
            I = imread("Data/"+exp+"/OutputImgs/"+runstring+"_"+string(frame)+".png");
            pixelcolors(i,j,:) = I(g(2), g(1), :);

            patch([double(forces(j))-0.25 double(forces(j))+0.25 double(forces(j))+0.25 double(forces(j))-0.25],...
                [temps(i)-0.5 temps(i)-0.5 temps(i)+0.5 temps(i)+0.5], 1/255*[pixelcolors(i,j,:)]);
            hold on
        end
    end
    xlim([double(forces(1))-0.25 double(forces(end))+0.25]);
    ylim([temps(1)-0.5 temps(end)+0.5]);
    set(gca, 'FontSize', 15);

end