function UpdatePicture(canvas_object) {
    ctx = canvas_object.getContext('2d');

    let img = new Image();
    img.src = "/static/game_links/" + game_number + "/game_picture.jpeg";
    
    img.onload = function(){
        ctx.drawImage(img, 0, 0, canvas_object.width, canvas_object.height);
    }    
}

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
        url: "/trigger_function",
        data: {
            game_number: game_number,
            coordinates: input_coordinates,
            size: input_size
        },
        success: callbackFunc
    });
    location.reload(true);
}

function callbackFunc(response) {
    location.reload();
}


let url = String(document.URL);
let game_number = url.slice(url.lastIndexOf("/") + 1, url.length)

const canvas = document.querySelector('canvas')
canvas.addEventListener('mousedown', function(e) {
    getCursorPosition(canvas, e)
})

var canvas_object = document.getElementById("game_canvas");
canvas_object.width = 500;
canvas_object.height = 500;

UpdatePicture(canvas_object)

document.getElementById("game_update_button").onclick = function () { location.reload(); };
