import imageio as iio

camera = iio.get_reader("<video1>")

for i in range(5):
    frame = camera.get_data(0)
    iio.imwrite('writehere'+str(i)+'.png', frame)


camera.close()