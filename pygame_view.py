import pygame
from go import Go, near_heap_of_stones


pygame.init()
pygame.font.init()
WIDTH = HEIGHT = 800
COMIC_SANS_MS = pygame.font.SysFont('Comic Sans MS', 25)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

GAME_SIZE = 9
game = Go(GAME_SIZE)

clock = pygame.time.Clock()

field_width, field_height = WIDTH // (game.width + 3), HEIGHT // (game.height + 3)
def drawing() -> None:
    for horizontal in range(1, game.width + 1):
        text = COMIC_SANS_MS.render(game.alphabet[horizontal - 1], False, (0, 0, 0))
        screen.blit(text, text.get_rect(center=((horizontal + 1) * field_width, field_height)))
    for vertical in range(1, game.height + 1):
        text = COMIC_SANS_MS.render(str(game.height - vertical + 1), False, (0, 0, 0))
        screen.blit(text, text.get_rect(center=(field_width, (vertical + 1) * field_height)))

    for horizontal in range(2, game.height + 2):
        pygame.draw.line(screen, (0, 0, 0), (field_width * 2, horizontal * field_height), (WIDTH - field_width * 2, horizontal * field_height))
    for vertical in range(2, game.width + 2):
        pygame.draw.line(screen, (0, 0, 0), (vertical * field_width, field_height * 2), (vertical * field_width, HEIGHT - field_height * 2))

    for i_index, line in enumerate(game.board):
        for j_index, element in enumerate(line):
            if element == "x":
                pygame.draw.circle(screen, (0, 0, 0), ((j_index + 2) * field_width, ((i_index + 2) * field_height)), min(field_width * 0.45, field_height * 0.45))
            elif element == "o":
                pygame.draw.circle(screen, (255, 255, 255), ((j_index + 2) * field_width, ((i_index + 2) * field_height)), min(field_width * 0.45, field_height * 0.45))


def main() -> None:
    ans = []

    while True:
        clock.tick(120)
        pygame.display.set_caption(str(int(clock.get_fps())))

        screen.fill((221, 134, 74))

        mouse_event = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_event = True

        if mouse_event:
            if pygame.mouse.get_pressed()[0]:
                x_coord, y_coord = pygame.mouse.get_pos()
                x_coord, y_coord = x_coord - field_width * 2, y_coord - field_height * 2
                x_coord, y_coord = (x_coord + field_width // 2) // field_width, (y_coord + field_height // 2) // field_height
                game.move(f"{GAME_SIZE - y_coord}{game.alphabet[x_coord]}")
            elif pygame.mouse.get_pressed()[2]:
                game.rollback(1)
                
        drawing()

        for coords in ans:
            pygame.draw.circle(screen, (255, 0, 0), ((coords[1] + 2) * field_height, (coords[0] + 2) * field_width), 5)

        pygame.display.flip()


if __name__ == "__main__":
    main()
