var socket = io();

var trace = {
    x: [...Array(100).keys()],
    y: Array(100).fill(0), 
    type: 'bar',
    orientation: 'v', 
    marker: {
        color: Array(100).fill('blue') 
    }
};

var layout = {
    title: 'Sorting Visualization',
    xaxis: {title: 'Index'},
    yaxis: {title: 'Value'}
};

Plotly.newPlot('chart', [trace], layout);

document.getElementById('startButton').onclick = function() {
    var algorithm = document.getElementById('algorithm').value;
    document.getElementById('startButton').disabled = true; // Disable the start button
    socket.emit('start_sort', {algorithm: algorithm});
};

document.getElementById('shuffleButton').onclick = function() {
    socket.emit('shuffle');
};

socket.on('update', function(data) {
    console.log("Updating chart with data:", data.array);  // Debug log for received data
    
    var updatedTrace = {
        x: [...Array(100).keys()],
        y: data.array,  // Set the y-values of the bars to the array sent from the backend
        type: 'bar',
        orientation: 'v',  // Ensure vertical bars
        marker: {
            color: Array(100).fill('blue')  // Reset all bars to blue initially
        }
    };

    if (data.swapped.length > 0) {
        data.swapped.forEach(index => {
            updatedTrace.marker.color[index] = 'red';  // Highlight the swapped elements in red
        });
    }

    Plotly.react('chart', [updatedTrace], layout);
});

socket.on('finished', function(data) {
    //alert(data.message);
    document.getElementById('startButton').disabled = false;  // Re-enable the start button
});
