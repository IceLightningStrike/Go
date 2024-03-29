from PIL import ImageDraw, ImageFont, Image
from cv2 import VideoWriter, imread
from go import Go

BACKGROUND_COLOR = (221, 134, 74)
WIDTH = HEIGHT = SIZE = 1000


def save_game_replay(board: Go, game_number: int, width: int = 1000, height: int = 1000, speed: int = 1) -> None:
    video = VideoWriter(f"static/game_links/{game_number}/Replay.mp4", 0, 1, (width, height))

    for elem in board.global_boards_history:
        obj = Go(board.width, board.height)
        obj.board = elem

        update_board_picture(obj, game_number, video_save=True)
        video.write(imread(f"static/game_links/{game_number}/clip_frame.jpeg"))
    
    video.release()


def update_board_picture(board: Go, game_number: int, video_save: bool = False) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
    drawer = ImageDraw.Draw(img)

    cell_size = int(SIZE / (board.width + 3))
    game_font = ImageFont.truetype("arial.ttf", cell_size // 2, encoding="unic")

    for index in range(2, board.width + 2):
        text_width = game_font.getlength("A")
        text_height = text_width * 1.62

        coordinates = (cell_size * index - text_width // 2, cell_size - text_height // 2)

        drawer.text((coordinates[0], coordinates[1]), board.alphabet[index - 2], fill=(0, 0, 0), font=game_font)
        drawer.text(
            (coordinates[0], coordinates[1] + cell_size * (board.height + 1)), board.alphabet[index - 2],
            fill=(0, 0, 0),
            font=game_font
        )
        
        text_width = game_font.getlength("0")
        text_height = text_width * 1.62

        if board.height - index + 2 >= 10:
            text_width = game_font.getlength("00") / 1.62
            text_height = text_width * 1.62

        coordinates = (cell_size * index - text_width, cell_size - text_height // 2)
        drawer.text((coordinates[1], coordinates[0]), str(board.height - index + 2), fill=(0, 0, 0), font=game_font)
        drawer.text(
            (coordinates[1] + cell_size * (board.width + 1), coordinates[0]), str(board.height - index + 2),
            fill=(0, 0, 0),
            font=game_font
        )

        coordinates = (cell_size * 2, cell_size * index), (cell_size * (board.width + 1), cell_size * index)
        drawer.line(((coordinates[0][0], coordinates[0][1]), (coordinates[1][0], coordinates[1][1])), fill=(0, 0, 0), width=5)
        drawer.line(((coordinates[0][1], coordinates[0][0]), (coordinates[1][1], coordinates[1][0])), fill=(0, 0, 0), width=5)

    for i_index, line in enumerate(board.board):
        for j_index, element in enumerate(line):
            coordinates = [
                ((j_index + 1.6) * cell_size, (i_index + 1.6) * cell_size),
                ((j_index + 2.4) * cell_size, (i_index + 2.4) * cell_size)
            ]

            if element == "x":
                drawer.ellipse(coordinates, fill=(0, 0, 0))
            elif element == "o":
                drawer.ellipse(coordinates, fill=(255, 255, 255))

    if video_save is False:
        img.save(f"static/game_links/{game_number}/game_picture.jpeg")
    else:
        img.save(f"static/game_links/{game_number}/clip_frame.jpeg")
