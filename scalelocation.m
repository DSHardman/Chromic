function location = scalelocation(inputcolor)
    % Linearly interpolate the position along the (nonlinear) scale from
    % the datasheet
    load("Scale.mat");
    errors = rssq(scale.'- inputcolor.');
    [~, ind] = min(errors);

    % Return output between zero and 1
    location = (ind-1)/(size(scale, 1)-1);
end