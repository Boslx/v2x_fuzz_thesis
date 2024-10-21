import matplotlib.pyplot as plt
import re
import os
import numpy as np

# Specify the folder paths
heap_folder_path = r"output/heap/queue"
stack_folder_path = "output/stack/queue"

# Regular expression pattern to extract the value of "mem"
pattern = r"mem_(\d+)"


# Function to process files and extract data
def process_files(folder_path):
    file_size_list = []
    file_mem_list = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            match = re.search(pattern, filename)
            if match:
                mem_value = int(match.group(1))
            else:
                continue

            file_size = os.path.getsize(file_path)
            file_size_list.append(file_size)
            file_mem_list.append(mem_value)

    return file_size_list, file_mem_list


# Function to find the maximum y value
def find_max_y(x_values, y_values, n):
    max_y = 0
    for x, y in zip(x_values, y_values):
        if x < n:
            max_y = max(max_y, y)
    return max_y


# Process heap files
heap_file_size_list, heap_file_mem_list = process_files(heap_folder_path)
heap_max_value = find_max_y(heap_file_size_list, heap_file_mem_list, 1500)
heap_median_value = np.median(heap_file_mem_list)
heap_percentage_difference = ((heap_max_value - heap_median_value) / heap_median_value) * 100

print(f"Max Heap: {heap_max_value}")
print(f"Median Heap: {heap_median_value}")
print(f"The max value is {heap_percentage_difference:.2f}% bigger than the median.")

# Process stack files
stack_file_size_list, stack_file_mem_list = process_files(stack_folder_path)
stack_max_value = find_max_y(stack_file_size_list, stack_file_mem_list, 1500)
stack_median_value = np.median(stack_file_mem_list)
stack_percentage_difference = ((stack_max_value - stack_median_value) / stack_median_value) * 100

print(f"Max Stack: {stack_max_value}")
print(f"Median Stack: {stack_median_value}")
print(f"The max value is {stack_percentage_difference:.2f}% bigger than the median.")

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 5))

# Heap plot
ax1.set_xlim([0, 1500])
ax1.set_ylim([0, 370000])
ax1.scatter(heap_file_size_list, heap_file_mem_list, s=10, alpha=0.7, edgecolors="k")
ax1.set_xlabel('input size in bytes')
ax1.set_ylabel('heap memory in bytes')
ax1.set_title('Heap Memory')

# Stack plot
ax2.set_xlim([0, 1500])
ax2.scatter(stack_file_size_list, stack_file_mem_list, s=10, alpha=0.7, edgecolors="k")
ax2.set_xlabel('input size in bytes')
ax2.set_ylabel('peak length of call stack')
ax2.set_title('Stack Length')

plt.tight_layout()
plt.show()
