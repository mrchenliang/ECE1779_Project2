import base64
from io import BytesIO
from matplotlib.figure import Figure

def prepare_graph(rows):
    # prepare data to be graphed by having 2 dictionaries, 1 for the x-axis, and 1 for the y-axis
    x_data = {'x-axis': [] }
    y_data = { 'miss_rate': [], 'hit_rate': [], 'request_count': [], 'cache_size': [], 'cache_count': []}
    for row in rows:
        x_data['x-axis'].append(row['created_at'])
        y_data['request_count'].append(row['request_count'])
        if row['request_count'] == 0:
            y_data['miss_rate'].append(row['miss_count'])
            y_data['hit_rate'].append(row['hit_count'])
        else:
            y_data['miss_rate'].append(row['miss_count']/row['request_count'])
            y_data['hit_rate'].append(row['hit_count']/row['request_count'])
        y_data['cache_size'].append(row['cache_size'])
        y_data['cache_count'].append(row['key_count'])
    return (x_data, y_data)


def plot_graph(data_x_axis, data_y_axis, y_label):
    # plot the graph using matlab and return the graph as a png
    fig = Figure(tight_layout=True)
    ax = fig.subplots()
    ax.plot(data_x_axis, data_y_axis)
    ax.set(xlabel='Date-Time', ylabel=y_label)
    buf = BytesIO()
    fig.autofmt_xdate()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data