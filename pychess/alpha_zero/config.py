import os
import numpy as np

class PlayDataConfig:
    def __init__(self):
        self.min_elo_policy = 500 # 0 weight
        self.max_elo_policy = 1800 # 1 weight
        self.sl_nb_game_in_file = 250
        self.nb_game_in_file = 50
        self.max_file_num = 150


class PlayConfig:
    def __init__(self):
        self.max_processes = 3
        self.search_threads = 16
        self.vram_frac = 1.0
        self.simulation_num_per_move = 100
        self.thinking_loop = 1
        self.logging_thinking = False
        self.c_puct = 1.5
        self.noise_eps = 0.25
        self.dirichlet_alpha = 0.3
        self.tau_decay_rate = 0.99
        self.virtual_loss = 3
        self.resign_threshold = -0.8
        self.min_resign_turn = 5
        self.max_game_length = 1000

class ModelConfig:
    cnn_filter_num = 256
    cnn_first_filter_size = 5
    cnn_filter_size = 3
    res_layer_num = 7
    l2_reg = 1e-4
    value_fc_size = 256
    distributed = False
    input_depth = 18

class PlayWithHumanConfig:
    """
    Config for allowing human to play against an agent using uci

    """
    def __init__(self):
        self.simulation_num_per_move = 1200
        self.threads_multiplier = 2
        self.c_puct = 1 # lower  = prefer mean action value
        self.noise_eps = 0
        self.tau_decay_rate = 0  # start deterministic mode
        self.resign_threshold = None

    def update_play_config(self, pc):
        """
        :param PlayConfig pc:
        :return:
        """
        pc.simulation_num_per_move = self.simulation_num_per_move
        pc.search_threads *= self.threads_multiplier
        pc.c_puct = self.c_puct
        pc.noise_eps = self.noise_eps
        pc.tau_decay_rate = self.tau_decay_rate
        pc.resign_threshold = self.resign_threshold
        pc.max_game_length = 999999


class Options:
    new = False


class ResourceConfig:
    """
    Config describing all of the directories and resources needed during running this project
    """
    def __init__(self):
        self.project_dir = os.environ.get("PROJECT_DIR", _project_dir())
        self.data_dir = os.environ.get("DATA_DIR", _data_dir())

        self.model_best_config_path = os.path.join(self.data_dir, "config.json")
        self.model_best_weight_path = os.path.join(self.data_dir, "weight.h5")

    def create_directories(self):
        dirs = [self.project_dir, self.data_dir, ]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)

def flipped_uci_labels():
    """
    Seems to somehow transform the labels used for describing the universal chess interface format, putting
    them into a returned list.
    :return:
    """
    def repl(x):
        return "".join([(str(9 - int(a)) if a.isdigit() else a) for a in x])

    return [repl(x) for x in create_uci_labels()]


def create_uci_labels():
    """
    Creates the labels for the universal chess interface into an array and returns them
    :return:
    """
    labels_array = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    promoted_to = ['q', 'r', 'b', 'n']

    for l1 in range(8):
        for n1 in range(8):
            destinations = [(t, n1) for t in range(8)] + \
                           [(l1, t) for t in range(8)] + \
                           [(l1 + t, n1 + t) for t in range(-7, 8)] + \
                           [(l1 + t, n1 - t) for t in range(-7, 8)] + \
                           [(l1 + a, n1 + b) for (a, b) in
                            [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]
            for (l2, n2) in destinations:
                if (l1, n1) != (l2, n2) and l2 in range(8) and n2 in range(8):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)
    for l1 in range(8):
        l = letters[l1]
        for p in promoted_to:
            labels_array.append(l + '2' + l + '1' + p)
            labels_array.append(l + '7' + l + '8' + p)
            if l1 > 0:
                l_l = letters[l1 - 1]
                labels_array.append(l + '2' + l_l + '1' + p)
                labels_array.append(l + '7' + l_l + '8' + p)
            if l1 < 7:
                l_r = letters[l1 + 1]
                labels_array.append(l + '2' + l_r + '1' + p)
                labels_array.append(l + '7' + l_r + '8' + p)
    return labels_array


class Config:
    """
    Config describing how to run the application

    Attributes (best guess so far):
        :ivar list(str) labels: labels to use for representing the game using UCI
        :ivar int n_lables: number of labels
        :ivar list(str) flipped_labels: some transformation of the labels
        :ivar int unflipped_index: idk
        :ivar Options opts: options to use to configure this config
        :ivar ResourceConfig resources: resources used by this config.
        :ivar ModelConfig mode: config for the model to use
        :ivar PlayConfig play: configuration for the playing of the game
        :ivar PlayDataConfig play_date: configuration for the saved data from playing
        :ivar TrainerConfig trainer: config for how training should go
        :ivar EvaluateConfig eval: config for how evaluation should be done
    """
    labels = create_uci_labels()
    n_labels = int(len(labels))
    flipped_labels = flipped_uci_labels()
    unflipped_index = None

    def __init__(self, config_type="mini"):
        self.opts = Options()
        self.resource = ResourceConfig()

        self.model = ModelConfig()
        self.play = PlayConfig()
        self.play_data = PlayDataConfig()
        self.labels = Config.labels
        self.n_labels = Config.n_labels
        self.flipped_labels = Config.flipped_labels

    @staticmethod
    def flip_policy(pol):
        """

        :param pol policy to flip:
        :return: the policy, flipped (for switching between black and white it seems)
        """
        return np.asarray([pol[ind] for ind in Config.unflipped_index])

Config.unflipped_index = [Config.labels.index(x) for x in Config.flipped_labels]

def _project_dir():
    d = os.path.dirname
    return d(d(os.path.abspath(__file__)))


def _data_dir():
    return os.path.join(_project_dir(), "pretrained")