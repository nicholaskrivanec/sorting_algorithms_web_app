from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

sorting = False 
current_array = []

# Sorting algorithms
def bubble_sort(arr):
    global sorting
    n = len(arr)
    for i in range(n):
        if not sorting:
            return  # Stop sorting if flag is set to False
        for j in range(0, n-i-1):
            if not sorting:
                return  # Stop sorting mid-way if shuffle is triggered
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                socketio.emit('update', {'array': arr, 'swapped': [j, j+1]})
                socketio.sleep(0.1)  # Sleep to simulate animation delay

def quick_sort(arr, low, high):
    global sorting
    if not sorting:
        return  # Stop sorting if flag is set to False
    if low < high:
        pi = partition(arr, low, high)
        quick_sort(arr, low, pi-1)
        quick_sort(arr, pi+1, high)

def partition(arr, low, high):
    global sorting
    if not sorting:
        return high  # Stop sorting if flag is set to False
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if not sorting:
            return high  # Stop sorting mid-way
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            socketio.emit('update', {'array': arr, 'swapped': [i, j]})
            socketio.sleep(0.1)
    arr[i+1], arr[high] = arr[high], arr[i+1]
    socketio.emit('update', {'array': arr, 'swapped': [i+1, high]})
    return i + 1

def merge_sort(arr):
    global sorting

    # Helper function to merge two halves and emit updates
    def merge(arr, left, middle, right):
        left_half = arr[left:middle + 1]
        right_half = arr[middle + 1:right + 1]
        i = j = 0
        k = left
        
        while i < len(left_half) and j < len(right_half):
            if not sorting:
                return  # Stop sorting if flag is set to False
            if left_half[i] <= right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            # Emit the merged elements (highlight these)
            #print(f"Merging: {arr[k]} at index {k}")  # Debugging print statement
            socketio.emit('update', {'array': arr, 'swapped': [k]})  # Highlight the current index
            socketio.sleep(0.1)
            k += 1

        while i < len(left_half):
            if not sorting:
                return
            arr[k] = left_half[i]
            i += 1
            #print(f"Left half remaining: {arr[k]} at index {k}")  # Debugging print statement
            socketio.emit('update', {'array': arr, 'swapped': [k]})  # Highlight the current index
            socketio.sleep(0.1)
            k += 1

        while j < len(right_half):
            if not sorting:
                return
            arr[k] = right_half[j]
            j += 1
            #print(f"Right half remaining: {arr[k]} at index {k}")  # Debugging print statement
            socketio.emit('update', {'array': arr, 'swapped': [k]})  # Highlight the current index
            socketio.sleep(0.1)
            k += 1

    # Helper function to recursively split the array and merge
    def merge_sort_recursive(arr, left, right):
        if left < right:
            middle = (left + right) // 2
            #print(f"Sorting left part: {left} to {middle}")  # Debugging print statement
            merge_sort_recursive(arr, left, middle)
            #print(f"Sorting right part: {middle + 1} to {right}")  # Debugging print statement
            merge_sort_recursive(arr, middle + 1, right)
            #print(f"Merging parts: {left} to {right}")  # Debugging print statement
            merge(arr, left, middle, right)

    merge_sort_recursive(arr, 0, len(arr) - 1)

def bucket_sort(arr):
    global sorting
    if not arr:
        return arr

    # Create buckets
    num_buckets = 10  # You can adjust the number of buckets
    max_value = max(arr)
    size = max_value // num_buckets + 1

    buckets = [[] for _ in range(num_buckets)]

    # Distribute elements into buckets
    for num in arr:
        index = num // size
        buckets[index].append(num)
        # Emit the updated array and highlight the element being added to the bucket
        socketio.emit('update', {'array': arr, 'swapped': [arr.index(num)]})
        socketio.sleep(0.1)

    # Sort each bucket and concatenate
    sorted_array = []
    for bucket in buckets:
        if not sorting:
            return
        bucket.sort()  # Using Python's Timsort (built-in sort) for simplicity
        sorted_array.extend(bucket)
        # Emit the updated array after sorting each bucket
        for i in range(len(sorted_array)):
            socketio.emit('update', {'array': sorted_array, 'swapped': [i]})
            socketio.sleep(0.1)

    # Update the original array with the sorted array
    for i in range(len(arr)):
        arr[i] = sorted_array[i]
        # Emit the final array update after concatenating
        socketio.emit('update', {'array': arr, 'swapped': [i]})
        socketio.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global current_array
    current_array = random.sample(range(1, 101), 100)  # Randomize the list on initial page load
    emit('update', {'array': current_array, 'swapped': []})  # Emit the shuffled array to initialize chart

@socketio.on('start_sort')
def handle_sorting(data):
    global sorting
    global current_array
    sorting = True  # Set flag to True to start sorting

    # Run the chosen sorting algorithm on the current array
    algorithm = data['algorithm']
    if algorithm == 'bubble_sort':
        bubble_sort(current_array)
    elif algorithm == 'quick_sort':
        quick_sort(current_array, 0, len(current_array) - 1)
    elif algorithm == 'merge_sort':
        merge_sort(current_array)
    elif algorithm == 'bucket_sort':
        bucket_sort(current_array)

    emit('finished', {'message': 'Sorting complete!'})  # Signal sorting completion

@socketio.on('shuffle')
def handle_shuffle():
    global sorting
    global current_array
    sorting = False  # Stop sorting immediately when shuffle is pressed
    current_array = random.sample(range(1, 101), 100)  # Generate a new shuffled list of random values
    emit('update', {'array': current_array, 'swapped': []})  # Emit the shuffled array to the frontend

if __name__ == '__main__':
    socketio.run(app, debug=True)