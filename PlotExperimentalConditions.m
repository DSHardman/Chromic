% Plot actual temperatures and forces recorded during experiment

experimentlog = readmatrix("Data/ExperimentB/log.txt");

subplot(3,1,1);
plot(experimentlog(:, 1));
ylabel("Finger Temperature");

subplot(3,1,2);
plot(experimentlog(:, 2));
ylabel("Force Applied");

subplot(3,1,3);
plot(experimentlog(:, 3)); % Note that light box temperature tended upwards over time
ylabel("External Temperature");
xlabel("Experiment Number");
ylim([23 27]);

set(gcf, 'color', 'w');