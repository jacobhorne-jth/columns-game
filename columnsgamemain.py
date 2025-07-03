import pygame
from columns_logic import Board
from errors import GameOverError, InvalidMoveError

class ColumnsGame:
    def __init__(self):
        self.grid_rows = 13
        self.grid_cols = 6
        self.tick_interval = 650
        self.colors = {
            'R': (255, 0, 0),
            'O': (255, 165, 0),
            'Y': (255, 255, 0),
            'G': (0, 255, 0),
            'C': (0, 255, 255),
            'B': (0, 0, 255),
            'P': (128, 0, 128),
            ' ': (200, 200, 200),
        }
        self.jewel_types = list(self.colors.keys())[:-1]  # Exclude ' '
        self.running = True
        self.last_tick = pygame.time.get_ticks()

        pygame.init()
        self.screen = pygame.display.set_mode((400, 800), pygame.RESIZABLE)
        pygame.display.set_caption("Columns Game")
        self.clock = pygame.time.Clock()

        self.board = Board(self.grid_rows, self.grid_cols)
        self.board.create_empty_board()
        self.board.create_random_faller(self.grid_cols, self.jewel_types)

    def draw_board(self):
        """Draw the game board and the faller on the screen."""
        game_board = self.board.get_board_state()
        faller = self.board.get_faller_state()

        window_width, window_height = self.screen.get_size()
        cell_width = window_width / self.grid_cols
        cell_height = window_height / self.grid_rows

        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                actual_row = r + 3
                cell = game_board[actual_row][c]
                if '*' in cell:
                    color = self.colors.get('M', self.colors[' '])
                else:
                    color = self.colors.get(cell.strip('*'), self.colors[' '])

                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(c * cell_width, r * cell_height, cell_width, cell_height),
                )
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    pygame.Rect(c * cell_width, r * cell_height, cell_width, cell_height),
                    1,
                )

        if faller:
            index = 0
            for color in faller.colors:
                faller_row = faller.row - index - 3
                if 0 <= faller_row < self.grid_rows:
                    faller_color = self.colors.get(color, (255, 255, 255))
                    border_color = (255, 255, 0) if faller.state == 'Landed' else (255, 255, 255)

                    pygame.draw.rect(
                        self.screen,
                        faller_color,
                        pygame.Rect(
                            (faller.column - 1) * cell_width,
                            faller_row * cell_height,
                            cell_width,
                            cell_height,
                        ),
                    )
                    pygame.draw.rect(
                        self.screen,
                        border_color,
                        pygame.Rect(
                            (faller.column - 1) * cell_width,
                            faller_row * cell_height,
                            cell_width,
                            cell_height,
                        ),
                        2,
                    )
                index += 1

    def handle_events(self):
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False
                if self.board.faller:
                    if event.key == pygame.K_LEFT:
                        try:
                            self.board.update_faller('L')
                        except InvalidMoveError:
                            pass
                    elif event.key == pygame.K_RIGHT:
                        try:
                            self.board.update_faller('R')
                        except InvalidMoveError:
                            pass
                    elif event.key == pygame.K_SPACE:
                        try:
                            self.board.faller.rotate()
                        except InvalidMoveError:
                            pass

    def update(self):
        """Update game logic."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_tick >= self.tick_interval:
            try:
                self.board.update_faller('D')
            except GameOverError:
                self.running = False

            matches = self.board.check_matches()
            if matches:
                for _ in range(3):
                    self.board.set_matches(matches)
                    self.draw_board()
                    pygame.display.flip()
                    pygame.time.delay(200)
                    self.board.clear_matches(matches)
                    self.draw_board()
                    pygame.display.flip()
                    pygame.time.delay(200)

                self.board.set_matches(matches)
                self.board.remove_marked_cells()
                self.board.settle_board()

            if not self.board.faller and not self.board.check_matches():
                self.board.create_random_faller(self.grid_cols, self.jewel_types)

            self.last_tick = current_time

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.screen.fill((255, 255, 255))
            self.draw_board()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = ColumnsGame()
    game.run()
