import matplotlib.pyplot as plt


def plot_graph(data_x_axis, data_y_axis):
    # plot the graph using matlab

    plt.plot(data_x_axis, data_y_axis)

    # set the graph title
    plt.title("Cache Replacement Policy: Least Recently Used")

    # set the x label and the y label of the graph
    plt.xlabel("Request_numbers")
    plt.ylabel("Throughput(20:80 read/write ratio)")

    plt.xlim(0, 10)

    plt.legend()
    plt.show()
