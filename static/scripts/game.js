function getCursorPosition(canvas, event) {
    const rect = canvas.getBoundingClientRect();

    const width = rect.width;
    const height = rect.height;
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    postData(x + ";" + y, width + ";" + height);
}


function postData(input_coordinates, input_size) {
    $.ajax({
        type: "POST",
        url: "/game_callback_answer",
        data: {
            game_number: game_number,
            coordinates: input_coordinates,
            size: input_size
        },
        success: callbackFunc,
    });
}


function give_up() {
    $.ajax({
        type: "POST",
        url: "/give_up",
        data: {
            game_number: game_number,
        },
        success: callbackFunc,
    });
}


function pass_move() {
    $.ajax({
        type: "POST",
        url: "/pass_move",
        data: {
            game_number: game_number,
        },
        success: callbackFunc,
    });
}



function callbackFunc(response) {
    console.log(response);
}


let url = String(document.URL);
let game_number = url.slice(url.lastIndexOf("/") + 1, url.length)
let counter = 0;

const canvas = document.querySelector('canvas')
canvas.addEventListener('mousedown', function(e) {
    getCursorPosition(canvas, e)
})

canvas_object = document.getElementById("game_canvas");
canvas_object.width = 500;
canvas_object.height = 500;

setInterval(function UpdatePicture() {
    canvas_object = document.getElementById("game_canvas");
    ctx = canvas_object.getContext('2d');

    counter++;

    img = new Image();
    img.src = "/static/game_links/" + game_number + "/game_picture.jpeg?" + counter;
    img.onload = function(){
        ctx.drawImage(img, 0, 0, canvas_object.width, canvas_object.height);
    }
}, 100);
