from PIL import ImageDraw, ImageFont, Image
from go import Go

BACKGROUND_COLOR = (221, 134, 74)
WIDTH = HEIGHT = SIZE = 2000

def update_board_picture(game_number: int, board: Go) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
    drawer = ImageDraw.Draw(img)

    cell_size = int(SIZE / (board.width + 3))
    game_font = ImageFont.truetype("arial.ttf", cell_size // 2, encoding="unic")

    for index in range(2, board.width + 2):
        text_width = game_font.getlength("A")
        text_height = text_width * 1.62
        coords = (cell_size * index - text_width // 2, cell_size - text_height // 2)
        drawer.text((coords[0], coords[1]), board.alphabet[index - 2], fill=(0, 0, 0), font=game_font)
        drawer.text(
            (coords[0], coords[1] + cell_size * (board.height + 1)), board.alphabet[index - 2],
            fill=(0, 0, 0),
            font=game_font
        )
        
        text_width = game_font.getlength("0")
        text_height = text_width * 1.62
        if board.height - index + 2 >= 10:
            text_width = game_font.getlength("00") / 1.62
            text_height = text_width * 1.62


        coords = (cell_size * index - text_width, cell_size - text_height // 2)
        drawer.text((coords[1], coords[0]), str(board.height - index + 2), fill=(0, 0, 0), font=game_font)
        drawer.text(
            (coords[1] + cell_size * (board.width + 1), coords[0]), str(board.height - index + 2),
            fill=(0, 0, 0),
            font=game_font
        )

        coords = (cell_size * 2, cell_size * index), (cell_size * (board.width + 1), cell_size * index)
        drawer.line(((coords[0][0], coords[0][1]), (coords[1][0], coords[1][1])), fill=(0, 0, 0), width=10)
        drawer.line(((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0])), fill=(0, 0, 0), width=10)

    for i_index, line in enumerate(board.board):
        for j_index, element in enumerate(line):
            coords = [
                ((j_index + 1.6) * cell_size, (i_index + 1.6) * cell_size),
                ((j_index + 2.4) * cell_size, (i_index + 2.4) * cell_size)
            ]

            if element == "x":
                drawer.ellipse(coords, fill=(0, 0, 0))
            elif element == "o":
                drawer.ellipse(coords, fill=(255, 255, 255))

    img.save(f"static/game_links/{game_number}/game_picture.jpeg")
