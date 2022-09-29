from abc import ABC, abstractmethod, abstractproperty


class Player:
    def __init__(self, name):
        self.name = name


class Match(ABC):
    def __init__(self, num_holes: int, players: list[Player]):
        self.players = players
        self.num_holes = num_holes
        self.num_players = len(self.players)
        self.finished = False

        self.table = [[None for i in range(self.num_players)] for j in range(self.num_holes)]
        self.current_hole = 0
        self.current_player_num = 0
        self.current_round = 1
        self.win_func = None  # must be overridden in the derived class (min()/max())

    def set_scores_others(self, scores: int):
        for player_num in range(self.num_players):
            if self.table[self.current_hole][player_num] is None:
                self.table[self.current_hole][player_num] = scores

    def go_next_player(self):
        self.current_player_num = (self.current_player_num + 1) % self.num_players

    def go_next_hole(self, loss_scores: int):
        self.set_scores_others(loss_scores)
        self.current_hole += 1
        self.current_round = 1
        self.current_player_num = self.current_hole

    def set_scores(self, scores: int):
        self.table[self.current_hole][self.current_player_num] = scores

    def get_table(self) -> list[tuple]:
        table = [tuple([player.name for player in self.players])]  # set player names row
        for hole_num in range(self.num_holes):  # add scores on every hole in table
            table.append(tuple(self.table[hole_num]))
        return table

    def get_winners(self) -> list:
        if not self.finished:
            raise RuntimeError

        scores = [0 for i in range(self.num_players)]  # counting all scores
        for hole in self.table:
            scores = list(map(sum, list(zip(scores, hole))))
        min_score = self.win_func(scores)

        winners = []
        for pl_num in range(self.num_players):
            if scores[pl_num] == min_score:
                winners.append(self.players[pl_num])
        return winners

    @abstractmethod
    def hit(self):
        if self.finished:
            raise RuntimeError

    @abstractmethod
    def go_next(self):
        pass


class HitsMatch(Match):
    LOSS_SCORES = 10
    NUM_ROUNDS = 10

    def __init__(self, num_holes: int, players: list[Player]):
        super().__init__(num_holes, players)
        self.win_func = min

    def go_next(self):
        self.go_next_player()
        if self.current_player_num == self.current_hole:  # next round
            self.current_round += 1
        if self.current_round == HitsMatch.NUM_ROUNDS:  # next hole
            self.go_next_hole(HitsMatch.LOSS_SCORES)
        if self.current_hole == self.num_holes:  # holes are over
            self.finished = True

    def has_scores(self):
        return self.table[self.current_hole][self.current_player_num] is not None

    def hit(self, success=False):
        super().hit()
        if success:
            self.set_scores(scores=self.current_round)

        self.go_next()
        while not self.finished and self.has_scores():  # jump to a player who hasn't scored yet
            self.go_next()


class HolesMatch(Match):
    GOAL_SCORES = 1
    LOSS_SCORES = 0
    NUM_ROUNDS = 10

    def __init__(self, num_holes: int, players: list[Player]):
        super().__init__(num_holes, players)
        self.win_func = max

    def everyone_missed(self) -> bool:
        for scores in self.table[self.current_hole]:
            if isinstance(scores, int):
                return False
        return True

    def go_next(self):
        self.go_next_player()
        if self.current_player_num == self.current_hole:    # round passed
            if self.everyone_missed():  # next round
                self.current_round += 1
            else:
                self.current_round = HolesMatch.NUM_ROUNDS + 1
        if self.current_round > HolesMatch.NUM_ROUNDS:  # next hole
            self.go_next_hole(HolesMatch.LOSS_SCORES)
        if self.current_hole == self.num_holes:  # holes are over
            self.finished = True

    def hit(self, success=False):
        super().hit()

        if success:
            self.set_scores(HolesMatch.GOAL_SCORES)

        self.go_next()