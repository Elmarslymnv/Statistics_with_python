import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from datetime import datetime
from dateutil.relativedelta import relativedelta
from data import time_arr

default_start_date_str = "2023-07-20"
default_end_date_str = "2023-08-10"
default_start_date = datetime.strptime(default_start_date_str, '%Y-%m-%d')
default_end_date = datetime.strptime(default_end_date_str, '%Y-%m-%d')
end_date_slider_val = (default_end_date - default_start_date).days


main_fig = plt.figure(figsize=(10, 10))
main_fig.subplots_adjust(hspace=0.5, bottom=0.15, top=0.9)

plot_ax_bugs = main_fig.add_subplot(2, 1, 1)
plot_ax_avg = main_fig.add_subplot(2, 1, 2)

start_date_slider_ax = plt.axes([0.2, 0.08, 0.65, 0.03], facecolor='lightgoldenrodyellow')
start_date_slider = Slider(start_date_slider_ax, 'Start Date', 0, end_date_slider_val, valinit=0, valstep=1, valfmt='%0.0f days')

end_date_slider_ax = plt.axes([0.2, 0.03, 0.65, 0.03], facecolor='lightgoldenrodyellow')
end_date_slider = Slider(end_date_slider_ax, 'End Date', 0, end_date_slider_val, valinit=end_date_slider_val, valstep=1, valfmt='%0.0f days')

sorted_names_bug_count, sorted_averages = [], []
ax1, ax2 = None, None
bars_bugs = None
bars_avg = None


def divide_by_name(arr):
    result = {}
    for name, date1, date2 in arr:
        if name not in result:
            result[name] = []
        result[name].append((name, date1, date2))
    return list(result.values())

def calculate_differences(data):
    result_dict = {}
    for idx, sublist in enumerate(data):
        for item in sublist:
            name = item[0]
            if item[2] < item[1]:
                difference = item[2] - item[1] + 31
            elif item[2]==item[1]:
                difference = 1
            else:
                difference = item[2] - item[1] 
            if name not in result_dict:
                result_dict[name] = []
            result_dict[name].append(f"{name}: {difference}")
    return list(result_dict.values())

def calculate_sums(data):
    result_dict = {}
    for sublist in data:
        for item in sublist:
            name, value = item.split(': ')
            value = int(value.split(' ')[0])  
            if name not in result_dict:
                result_dict[name] = 0
            result_dict[name] += value
    return result_dict

def divide_dictionaries(dict1, dict2):
    result_dict = {}
    for name in dict1:
        if name in dict2:
            result_dict[name] = round(dict1[name] / dict2[name], 2)
        else:
            result_dict[name] = 0
    return result_dict

def update_annotations(ax, bars):
    for bar in bars:
        bar_height = bar.get_height()
        bar_x_position = bar.get_x() + bar.get_width() / 2

        ax.annotate(f'{bar_height:.2f}', xy=(bar_x_position, bar_height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

    ax.relim()
    ax.autoscale_view()
    plt.draw()
def update_plot(val):
    global sorted_data, bars_bugs, ax1
    plot_ax_bugs.clear()  # Clear the previous plot
    start_date_idx = int(start_date_slider.val)
    new_start_date = default_start_date + relativedelta(days=start_date_idx)
    end_date_idx = int(end_date_slider.val)
    new_end_date = default_start_date + relativedelta(days=end_date_idx)
    start_date_slider.label.set_text(f'Start Date: {new_start_date.strftime("%Y-%m-%d")}')
    end_date_slider.label.set_text(f'End Date: {new_end_date.strftime("%Y-%m-%d")}')
    filtered_data = [item for item in sorted_data if new_start_date <= item[1] <= new_end_date]
    split_arrays = divide_by_name(filtered_data)
    num_bugs = {split_arrays[i][0][0]: len(split_arrays[i]) for i in range(len(split_arrays))}
    if not num_bugs:
        print("No bug data for the selected date range.")
        return
    sorted_names_bug_count, bug_count = zip(*num_bugs.items())
    
    # Sort data in descending order for start date = min, end date = max
    if new_start_date == default_start_date and new_end_date == default_end_date:
        sorted_names_bug_count, bug_count = zip(*sorted(num_bugs.items(), key=lambda x: x[1], reverse=True))
    
    if ax1 is None:
        ax1 = plot_ax_bugs
    if bars_bugs is not None:
        for bar in bars_bugs:
            bar.remove()
    bars_bugs = ax1.bar(sorted_names_bug_count, bug_count, label='Number of Bugs', color='green')
    update_annotations(ax1, bars_bugs)
    ax1.set_ylabel("Number of Bugs")
    ax1.set_title("Number of Bugs for Each Assignee", fontsize=16, fontweight='bold')
    plt.setp(ax1.get_xticklabels(), rotation=0, ha='center', fontsize=10)
    ax1.tick_params(axis='both', which='major', labelsize=12)
    plt.draw()

def update_avg_plot(val):
    global sorted_averages, bars_avg, ax2
    plot_ax_avg.clear()  # Clear the previous plot
    start_date_idx = int(start_date_slider.val)
    new_start_date = default_start_date + relativedelta(days=start_date_idx)
    end_date_idx = int(end_date_slider.val)
    new_end_date = default_start_date + relativedelta(days=end_date_idx)
    start_date_slider.label.set_text(f'Start Date: {new_start_date.strftime("%Y-%m-%d")}')
    end_date_slider.label.set_text(f'End Date: {new_end_date.strftime("%Y-%m-%d")}')
    filtered_data = [item for item in sorted_data if new_start_date <= item[1] <= new_end_date]
    split_arrays = divide_by_name(filtered_data)
    num_bugs = {split_arrays[i][0][0]: len(split_arrays[i]) for i in range(len(split_arrays))}
    result = calculate_differences(split_arrays)
    sums_dict = calculate_sums(result)
    average = divide_dictionaries(sums_dict, num_bugs)
    sorted_averages_desc = sorted(average.items(), key=lambda x: x[1], reverse=True)
    sorted_names_avg, sorted_averages = zip(*sorted_averages_desc)
    
    # Sort data in descending order for start date = min, end date = max
    if new_start_date == default_start_date and new_end_date == default_end_date:
        sorted_names_avg, sorted_averages = zip(*sorted(sorted_averages_desc, key=lambda x: x[1], reverse=True))
    
    if ax2 is None:
        ax2 = plot_ax_avg
    if bars_avg is not None:
        for bar in bars_avg:
            bar.remove()
    bars_avg = ax2.bar(sorted_names_avg, sorted_averages, label='Average Days', color='blue')
    update_annotations(ax2, bars_avg)
    ax2.set_ylabel("Average Days Spent on Bugs")
    ax2.set_title("Average Days Spent on Bugs for Each Assignee", fontsize=16, fontweight='bold')
    plt.setp(ax2.get_xticklabels(), rotation=0, ha='center', fontsize=10)
    ax2.tick_params(axis='both', which='major', labelsize=12)
    plt.draw()


def update_sliders(val):
    update_plot(val)
    update_avg_plot(val)

start_date_slider.on_changed(update_sliders)
end_date_slider.on_changed(update_sliders)
start_date_slider.on_changed(update_plot)
end_date_slider.on_changed(update_avg_plot)

time_arr = [
("Haqverdi Mustafayev", datetime(2023, 8, 2), datetime(2023, 8, 3)),("Haqverdi Mustafayev", datetime(2023, 8, 2), datetime(2023, 8, 3)),("Haqverdi Mustafayev", datetime(2023, 8, 1), datetime(2023, 8, 3)),
("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 8, 3)),("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 8, 2)),("Gunel Huseynova", datetime(2023, 8, 1), datetime(2023, 8, 2)),("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 7, 31)),("Haqverdi Mustafayev", datetime(2023, 7, 29), datetime(2023, 7, 31)),("Haqverdi Mustafayev", datetime(2023, 7, 29), datetime(2023, 7, 31)),("Gunel Huseynova", datetime(2023, 7, 29), datetime(2023, 7, 29)),("Gunel Huseynova", datetime(2023, 7, 29), datetime(2023, 7, 29)),("Gunel Huseynova", datetime(2023, 7, 29), datetime(2023, 7, 29)),("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 7, 29)),("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 7, 29)),("Rustam Abishzada", datetime(2023, 7, 25), datetime(2023, 7, 27)),("Zhala Mustafayeva", datetime(2023, 7, 25), datetime(2023, 7, 27)),("Gunel Huseynova", datetime(2023, 7, 25), datetime(2023, 7, 27)),("Gunel Huseynova", datetime(2023, 7, 25), datetime(2023, 7, 27)),("Gunel Huseynova", datetime(2023, 7, 25), datetime(2023, 7, 27)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 9)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 9)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 9)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 9)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 9)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 9)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 9)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 9)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 9)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 9)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 9)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 2), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 2), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 2), datetime(2023, 8, 8)),("Gunel Huseynova", datetime(2023, 8, 2), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 8)),("Zhala Mustafayeva", datetime(2023, 8, 4), datetime(2023, 8, 5)),("Zhala Mustafayeva", datetime(2023, 8, 4), datetime(2023, 8, 5)),("Zhala Mustafayeva", datetime(2023, 8, 4), datetime(2023, 8, 5)),("Zhala Mustafayeva", datetime(2023, 8, 4), datetime(2023, 8, 5)),("Zhala Mustafayeva", datetime(2023, 8, 4), datetime(2023, 8, 5)),("Zhala Mustafayeva", datetime(2023, 8, 4), datetime(2023, 8, 5)),("Zhala Mustafayeva", datetime(2023, 8, 9), datetime(2023, 8, 19)),("Gunel Huseynova", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 31), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 31), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 1), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 7, 31), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 9), datetime(2023, 8, 19)),("Gunel Huseynova", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 31), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 31), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 7, 29), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Rustam Abishzada", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Haqverdi Mustafayev", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Zhala Mustafayeva", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 7, 28), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 1), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 7, 31), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 9), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 7), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 3), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10)),("Gunel Huseynova", datetime(2023, 8, 4), datetime(2023, 8, 10))]


sorted_data = sorted(time_arr, key=lambda x: (x[0], x[2]))
end_date_idx = int(end_date_slider.val)
new_end_date = default_start_date + relativedelta(days=end_date_idx)
filtered_data = [item for item in sorted_data if default_start_date <= item[1] <= new_end_date]
split_arrays = divide_by_name(filtered_data)
num_bugs = {split_arrays[i][0][0]: len(split_arrays[i]) for i in range(len(split_arrays))}
if num_bugs:
    sorted_names_bug_count, bug_count = zip(*num_bugs.items())
    ax = plot_ax_bugs
    bars = ax.bar(sorted_names_bug_count, bug_count, label='Number of Bugs', color='green')
    for idx, bar in enumerate(bars):
        height = bar.get_height()
        width = bar.get_width()
        x_position = bar.get_x() + width / 2
        ax.annotate(f'{height}', xy=(x_position, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')
    ax.set_title("Number of Bugs for Each Assignee (Descending Order)", fontsize=16, fontweight='bold')
    plt.setp(ax.get_xticklabels(), rotation=0, ha='center', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=10)

    ax.relim()
    ax.autoscale_view()

    update_plot(0)
    update_avg_plot(0)

    plt.show()
    # print(a_list[0])

else:
    print("No bug data available.")

# print(sorted_data[0][0])