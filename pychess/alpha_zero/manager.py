import argparse
import sys
from .agent.player import ChessPlayer
from .agent.model import ChessModel
from .config import Config, PlayWithHumanConfig
from .env import ChessEnv


def setup(config: Config, args):
    """
    Sets up a new config by creating the required directories and setting up logging.

    :param Config config: config to create directories for and to set config from based on the args
    :param ArgumentParser args: args to use to control config.
    """
    config.opts.new = args.new
    config.resource.create_directories()


def start():
    """
    Starts one of the processes based on command line arguments.

    :return : the worker class that was started
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--new", help="run from new best model", action="store_true")
    parser.add_argument("--total-step", help="set TrainerConfig.start_total_steps", type=int)
    args = parser.parse_args()

    config = Config()
    setup(config, args)
    play(config)


def play(config: Config):
    PlayWithHumanConfig().update_play_config(config.play)
    env = ChessEnv().reset()
    me_player = get_player(config)

    turn = 1
    while True:
        env.render()
        if env.winner is not None:
            print(f"winner is {env.winner}")
            break
        if turn == 1:
            words = input("Player: ")
            if words == "newgame":
                env.reset()
            elif words == "help":
                action = me_player.action(env, False)
                print(f"bestmove {action}")
            elif words == "quit":
                break
            else:
                try:
                    env.step(words, True)
                    turn *= -1
                except:
                    print("bad input")
        else:
            action = me_player.action(env, False)
            print(f"CPU: {action}")
            env.step(action, True)
            turn *= -1

def get_player(config):
    model = ChessModel(config)
    if not model.load(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path):
        raise Exception(f"[*] weight not found. {model.config.resource.model_best_config_path} and {model.config.resource.model_best_weight_path}")
    return ChessPlayer(config, model.get_pipes(config.play.search_threads))